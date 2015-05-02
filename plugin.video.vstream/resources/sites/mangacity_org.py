#-*- coding: utf-8 -*-
#Venom.
from resources.lib.gui.hoster import cHosterGui #system de recherche pour l'hote
from resources.lib.handler.hosterHandler import cHosterHandler #system de recherche pour l'hote
from resources.lib.gui.gui import cGui #system d'affichage pour xbmc
from resources.lib.gui.guiElement import cGuiElement #system d'affichage pour xbmc
from resources.lib.handler.inputParameterHandler import cInputParameterHandler #entrer des parametres
from resources.lib.handler.outputParameterHandler import cOutputParameterHandler #sortis des parametres
from resources.lib.handler.requestHandler import cRequestHandler #requete url
from resources.lib.config import cConfig #config
from resources.lib.parser import cParser #recherche de code
#from resources.lib.util import cUtil
import urllib2,urllib,re
import unicodedata,htmlentitydefs

def unescape(text):
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)

def DecryptMangacity(chain):
    oParser = cParser()
    sPattern = '(.+?),\[(.+?)\],\[(.+?)\]\)'
    aResult2 = oParser.parse(chain, sPattern)
    d = ''
    
    if (aResult2[0] == True):

        a = aResult2[1][0][0]
        b = aResult2[1][0][1].replace('"','').split(',')
        c = aResult2[1][0][2].replace('"','').split(',')

        d = a
        for i in range(0, len(b)):
            d = d.replace( b[i], c[i])
        
        d = d.replace('%26', '&')
        d = d.replace('%3B', ';')
        
    return d
    
def DecoTitle(string):
    string = string.replace('(VF)','[COLOR teal][VF][/COLOR]')
    string = string.replace('(VOSTFR)','[COLOR teal][VOSTFR][/COLOR]')
    return string

#------------------------------------------------------------------------------------    
    
SITE_IDENTIFIER = 'mangacity_org'
SITE_NAME = 'MangaCity.org'
SITE_DESC = 'Anime en streaming'

URL_MAIN = 'http://www.mangacity.org/'

ANIM_ANIMS = ('http://www.mangacity.org/animes.php?liste=SHOWALPHA', 'ShowAlpha')
ANIM_GENRES = (True, 'showGenre')
ANIM_NEW = ('http://www.mangacity.org/nouveautees.php', 'showMovies')

URL_SEARCH = ('', 'showMovies')
FUNCTION_SEARCH = 'showMovies'


def load(): #function charger automatiquement par l'addon l'index de votre navigation.
    oGui = cGui() #ouvre l'affichage

    oOutputParameterHandler = cOutputParameterHandler() #apelle la function pour sortir un parametre
    oOutputParameterHandler.addParameter('siteUrl', 'http://venom/') # sortis du parametres siteUrl oublier pas la Majuscule
    oGui.addDir(SITE_IDENTIFIER, 'showSearch', 'Recherche', 'search.png', oOutputParameterHandler)
    
    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', ANIM_NEW[0])
    oGui.addDir(SITE_IDENTIFIER, ANIM_NEW[1], 'Animes Nouveaute', 'films.png', oOutputParameterHandler)
    
    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', ANIM_ANIMS[0])
    oGui.addDir(SITE_IDENTIFIER, ANIM_ANIMS[1], 'Liste Animes', 'films.png', oOutputParameterHandler)
    
    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', ANIM_GENRES[0])
    oGui.addDir(SITE_IDENTIFIER, ANIM_GENRES[1], 'Anime Genres', 'genres.png', oOutputParameterHandler)
            
    oGui.setEndOfDirectory() #ferme l'affichage

def showSearch():
    oGui = cGui()

    sSearchText = oGui.showKeyBoard()
    if (sSearchText != False):
        sUrl = sSearchText
        showMovies(sUrl)
        oGui.setEndOfDirectory()
        return  
    
    
def showGenre(): #affiche les genres
    oGui = cGui()

    oInputParameterHandler = cInputParameterHandler()
    sUrl = 'http://www.mangacity.org/animes.php?liste=SHOWALPHA'

    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()
    
    sPattern = '<a href="(categorie\.php\?watch=.+?)" onmouseover=.+?decoration:none;">(.+?)<\/a>'
    
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)
    #print aResult
    
    if (aResult[0] == True):
        total = len(aResult[1])
        dialog = cConfig().createDialog(SITE_NAME)
        
        for aEntry in aResult[1]:
            cConfig().updateDialog(dialog, total)
            if dialog.iscanceled():
                break
            
            sGenre = aEntry[1]
            Link = aEntry[0]
            
            sGenre = unicode(sGenre,'iso-8859-1')
            sGenre = unicodedata.normalize('NFD', sGenre).encode('ascii', 'ignore')
            sGenre = sGenre.encode('ascii', 'ignore').decode('ascii')
            
            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', str(URL_MAIN) + Link)
            oGui.addMovie(SITE_IDENTIFIER, 'showMovies', '[B][COLOR red]' + sGenre + '[/COLOR][/B]', '', '', '', oOutputParameterHandler)
 
        cConfig().finishDialog(dialog)

    oGui.setEndOfDirectory()

def ShowAlpha():
    oGui = cGui()

    oInputParameterHandler = cInputParameterHandler()
    sUrl = 'http://www.mangacity.org/animes.php?liste=SHOWALPHA'

    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()
    
    sPattern = "<a href='(.+?)' class='button light'><headline6><font color='black'>([A-Z#])<\/font><\/headline6><\/a>"
    
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)
    #print aResult
    
    if (aResult[0] == True):
        total = len(aResult[1])
        dialog = cConfig().createDialog(SITE_NAME)
        
        for aEntry in aResult[1]:
            cConfig().updateDialog(dialog, total)
            if dialog.iscanceled():
                break
            
            sLetter = aEntry[1]
            Link = aEntry[0]
            
            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', str(URL_MAIN) + Link)
            oGui.addMovie(SITE_IDENTIFIER, 'showMovies', '[B][COLOR red]' + sLetter + '[/COLOR][/B]', '', '', '', oOutputParameterHandler)
 
        cConfig().finishDialog(dialog)

    oGui.setEndOfDirectory()
        
    
def showMovies(sSearch = ''):
    oGui = cGui()
    
    if sSearch:
        
        #query_args = { 's': str(sSearch) }
        #data = urllib.urlencode(query_args)
        #headers = {'User-Agent' : 'Mozilla 5.10', 'Referer' : 'http://www.mangacity.org'}
        #url = 'http://www.mangacity.org/result.php'
        #request = urllib2.Request(url,data,headers)
        #reponse = urllib2.urlopen(request)
        
        sSearch = urllib2.unquote(sSearch)
        sSearch = urllib.quote_plus(sSearch)

        url = 'http://www.mangacity.org/resultat.php?string=' + sSearch
        headers = {'User-Agent' : 'Mozilla 5.10', 'Referer' : 'http://www.mangacity.org'}
        request = urllib2.Request(url,None,headers)
        reponse = urllib2.urlopen(request)
        
        sHtmlContent = reponse.read()
        
        reponse.close()
        
    else:
        oInputParameterHandler = cInputParameterHandler()
        sUrl = oInputParameterHandler.getValue('siteUrl')
    
        oRequestHandler = cRequestHandler(sUrl)
        sHtmlContent = oRequestHandler.request()
    
    #print sUrl
    
    #En cas de bug, partie a reactiver
    #fh = open('c:\\test.txt', "w")
    #fh.write(sHtmlContent)
    #fh.close()
    #Elle va creer un fichier text.txt dans c:/ a me refaire passer merci

    sPattern = 'background: url\(\'([^\'].+?)\'\); background-size.+?alt="(.+?)" title.+?<a href=\'(.+?)\' class=\'button'
    
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)
    #aResult = re.findall(sPattern, sHtmlContent)
    #print aResult
    
    if (aResult[0] == True):
        total = len(aResult[1])
        dialog = cConfig().createDialog(SITE_NAME)
        
        for aEntry in aResult[1]:
            cConfig().updateDialog(dialog, total) #dialog
            if dialog.iscanceled():
                break
            
            sTitle = aEntry[1]
            #sTitle = unicode(sTitle, errors='replace')
            sTitle = unicode(sTitle,'iso-8859-1')
            sTitle = unicodedata.normalize('NFD', sTitle).encode('ascii', 'ignore')
            sTitle = sTitle.encode('ascii', 'ignore').decode('ascii')
            sTitle = sTitle.replace('[Streaming] - ','')
            sTitle = DecoTitle(sTitle)
            
            sPicture = aEntry[0]
            #sPicture = sPicture.encode('ascii', 'ignore').decode('ascii')
            #sPicture = sPicture.replace('[Streaming] - ','')
            sPicture = str(URL_MAIN) + str(sPicture)
            #print sPicture
            
            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', str(URL_MAIN) + str(aEntry[2]))
            oOutputParameterHandler.addParameter('sMovieTitle', str(sTitle))
            oOutputParameterHandler.addParameter('sThumbnail', sPicture)

            oGui.addMovie(SITE_IDENTIFIER, 'showEpisode', sTitle, sPicture, sPicture, '', oOutputParameterHandler)
 
        cConfig().finishDialog(dialog)
        
        if sSearch:
            sNextPage = False
        else:
            sNextPage = __checkForNextPage(sHtmlContent,sUrl)
        if (sNextPage != False):
            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', sNextPage)
            oGui.addDir(SITE_IDENTIFIER, 'showMovies', '[COLOR teal]Next >>>[/COLOR]', 'next.png', oOutputParameterHandler)
            #Ajoute une entrer pour le lien Next | pas de addMisc pas de poster et de description inutile donc

    if not sSearch:
        oGui.setEndOfDirectory() #ferme l'affichage
    
def __checkForNextPage(sHtmlContent,sUrl):
    #test si un lien est deja dans l'url
    oParser = cParser()
    
    sPattern ='class=.button red light. title=.Voir la page.+?<a href=.(.+?)(?:\'|") class=.button light.'
    aResult = oParser.parse(sHtmlContent, sPattern)
    
    if (aResult[0] == False):
        sPattern = "<.table><center><center><a href='(.+?)' class='button light' title='Voir la page 1'>"
        aResult = oParser.parse(sHtmlContent, sPattern)
    
    #fh = open('c:\\test.txt', "w")
    #fh.write(sHtmlContent)
    #fh.close()
    
    if (aResult[0] == True):
        return str(URL_MAIN) + str(aResult[1][0])

    return False

def showEpisode():
    oGui = cGui()
    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    sMovieTitle = oInputParameterHandler.getValue('sMovieTitle')
    sThumb = oInputParameterHandler.getValue('sThumbnail')
   
    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()
    
    oParser = cParser()
    
    #print sUrl
    
    #On fait 2 passage pr accelerer le parsing regex
    sPattern = '<div class="&#105;&#110;&#110;&#101;&#114;">(.+?)<footer id="footer">'
    aResult = oParser.parse(sHtmlContent, sPattern)
    sPattern = '<img src="(.+?).+? alt="&#101;&#112;&#105;&#115;&#111;&#100;&#101;&#115;".+?<a href="(.+?)" title="(.+?)"'
    aResult = oParser.parse(aResult[1][0], sPattern)
    
    if (aResult[0] == True):
        total = len(aResult[1])
        dialog = cConfig().createDialog(SITE_NAME)
        for aEntry in aResult[1]:
            cConfig().updateDialog(dialog, total)
            if dialog.iscanceled():
                break
                
        
            sTitle = unescape(aEntry[2])
            sTitle = DecoTitle(sTitle)
            sUrl2 = URL_MAIN + str(unescape(aEntry[1]))
            
            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', sUrl2)
            oOutputParameterHandler.addParameter('sMovieTitle', sTitle)
            oOutputParameterHandler.addParameter('sThumbnail', sThumb)
            oGui.addMovie(SITE_IDENTIFIER, 'showHosters', sTitle, sThumb, sThumb, '', oOutputParameterHandler)
        cConfig().finishDialog(dialog)


    oGui.setEndOfDirectory()
      
    
def showHosters():
    oGui = cGui()
    
    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    sMovieTitle = oInputParameterHandler.getValue('sMovieTitle')
    sThumbnail = oInputParameterHandler.getValue('sThumbnail')
    
    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()
    sHtmlContent = sHtmlContent.replace('<iframe src="http://www.promoliens.net','')
    sHtmlContent = sHtmlContent.replace("<iframe src='cache_vote.php",'')
    

    sPattern = '<iframe[^<>]+?src=[\'"]([^<>]+?)[\'"][^<]+?<\/iframe>|<script>eval\(unescape\((.+?)\); eval\(unescape\((.+?)\);<\/script>'
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)

    print aResult
    
    if (aResult[0] == True):
        total = len(aResult[1])
        dialog = cConfig().createDialog(SITE_NAME)
        for aEntry in aResult[1]:
            cConfig().updateDialog(dialog, total)
            if dialog.iscanceled():
                break
            
            
            if aEntry[0]:#adresse directe  
                if re.match(".+?&#[0-9]+;", aEntry[0]):#directe mais codé html
                    sHosterUrl = unescape(aEntry[0])
                else:#directe en clair
                    sHosterUrl = str(aEntry[0])
            else:#adresse cryptee
                print 'decryptage'
                sHosterUrl = DecryptMangacity(aEntry[2])
                sHosterUrl = sHosterUrl.replace('\\','')
                
                print sHosterUrl
                
                #Dans le cas ou l'adresse n'est pas directe
                if not (sHosterUrl[:4] == 'http'):
                    final = ''
                    
                    sPattern = '[src|SRC]=(?:\'|")(http:.+?)(?:\'|")'
                    aResult = re.findall(sPattern,sHosterUrl)
                    if aResult:
                        final = aResult[0]
                        
                    sPattern = 'encodeURI\("(.+?)"\)'
                    aResult = re.findall(sPattern,sHosterUrl)
                    if aResult:
                        final = aResult[0]
                        
                    sPattern = "'file': '(.+?)',"
                    aResult = oParser.parse(sHosterUrl, sPattern)
                    if aResult[0] == True:
                        final = URL_MAIN + aResult[1][0]
                        
                    sHosterUrl = final

            print 'Adresse :' + sHosterUrl

            #oHoster = __checkHoster(sHosterUrl)
            oHoster = cHosterGui().checkHoster(sHosterUrl)
            
            if (oHoster != False):
                oHoster.setDisplayName(sMovieTitle)
                oHoster.setFileName(sMovieTitle)
                cHosterGui().showHoster(oGui, oHoster, sHosterUrl, sThumbnail)

        cConfig().finishDialog(dialog) 

    oGui.setEndOfDirectory()
    
