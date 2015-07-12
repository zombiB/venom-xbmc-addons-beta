#-*- coding: utf-8 -*-
#Venom.
from resources.lib.config import cConfig
#from resources.lib.gui.gui import cGui
#from resources.lib.gui.hoster import cHosterGui
from resources.lib.handler.inputParameterHandler import cInputParameterHandler
from resources.lib.handler.outputParameterHandler import cOutputParameterHandler
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.parser import cParser
import xbmc


SITE_IDENTIFIER = 'ePg'
SITE_NAME = 'epg'


url_index = 'http://television.telerama.fr/tele/chaine-tv/tf1,192.php'
channel = '<span class="logo-chaine">|alt=".+?" />|</li>'
id = '<span class="logo-chaine">|epgid=|".+?</li>'


class cePg:
    
    def get_epg(self):
        
        oRequestHandler = cRequestHandler(url_index)
        sHtmlContent = oRequestHandler.request();
        sHtmlContent = sHtmlContent.replace('<br>', '')
        text = ''
        sPattern = '<div class="tv10-chaine-item">.+?<div class="tv10-chaine-vignette">(.+?)<a.+?<h2 class="tv10-chaine-descri-tit">.*?<a href=".+?">(.+?)</a>'
        
        oParser = cParser()
        aResult = oParser.parse(sHtmlContent, sPattern)
        if (aResult[0] == True):
            for aEntry in aResult[1]:
                text += aEntry[0]+" -/- "+aEntry[1]+'\r\n'
                
            return text
        else:
            return ''
        
    def get_favorite(self):
    
        sql_select = "SELECT * FROM favorite"

        try:    
            self.dbcur.execute(sql_select)
            #matchedrow = self.dbcur.fetchone()
            matchedrow = self.dbcur.fetchall()
            return matchedrow        
        except Exception, e:
            cConfig().log('SQL ERROR EXECUTE') 
            return None
        self.dbcur.close()
        
    def get_countfavorite(self):
    
        sql_select = "SELECT COUNT(*) FROM favorite"

        try:    
            self.dbcur.execute(sql_select)
            #matchedrow = self.dbcur.fetchone() 
            matchedrow = self.dbcur.fetchone()
            return matchedrow[0]      
        except Exception, e:
            cConfig().log('SQL ERROR EXECUTE') 
            return None
        self.dbcur.close()

    def get_resume(self, meta):
        title = self.str_conv(meta['title'])
        site = urllib.quote_plus(meta['site'])

        sql_select = "SELECT * FROM resume WHERE hoster = '%s'" % (site)

        try:    
            self.dbcur.execute(sql_select)
            #matchedrow = self.dbcur.fetchone()
            matchedrow = self.dbcur.fetchall()
            return matchedrow        
        except Exception, e:
            cConfig().log('SQL ERROR EXECUTE') 
            return None
        self.dbcur.close()

    def get_watched(self, meta):        
        count = 0
        site = urllib.quote_plus(meta['site'])
        sql_select = "SELECT * FROM watched WHERE site = '%s'" % (site)

        try:    
            self.dbcur.execute(sql_select)
            #matchedrow = self.dbcur.fetchone()
            matchedrow = self.dbcur.fetchall()

            if matchedrow:
                count = 1
            else:
                count = 0    
            return count        
        except Exception, e:
            cConfig().log('SQL ERROR EXECUTE') 
            return None
        self.dbcur.close()          

    def del_history(self):

        sql_delete = "DELETE FROM history;"

        try:    
            self.dbcur.execute(sql_delete)
            self.db.commit()
            cConfig().showInfo('vStream', 'Historique supprime')
            cConfig().update()
            return False, False       
        except Exception, e:
            cConfig().log('SQL ERROR DELETE') 
            return False, False
        self.dbcur.close()  
       
    def del_watched(self, meta):
        site = urllib.quote_plus(meta['site'])
        sql_select = "DELETE FROM watched WHERE site = '%s'" % (site)

        try:    
            self.dbcur.execute(sql_select)
            self.db.commit()
            return False, False
        except Exception, e:
            cConfig().log('SQL ERROR EXECUTE') 
            return False, False
        self.dbcur.close() 
        
    def del_favorite(self, meta):
        siteUrl = urllib.quote_plus(meta['siteurl'])

        sql_select = "DELETE FROM favorite WHERE siteurl = '%s'" % (siteUrl)

        try:    
            self.dbcur.execute(sql_select)
            self.db.commit()
            cConfig().showInfo('vStream', 'Favoris supprimer')
            cConfig().update()
            return False, False
        except Exception, e:
            cConfig().log('SQL ERROR EXECUTE') 
            return False, False
        self.dbcur.close() 

    def getFav(self):
        oGui = cGui()
        fav_db = self.__sFile

        oInputParameterHandler = cInputParameterHandler()
        if (oInputParameterHandler.exist('sCat')):
            sCat = oInputParameterHandler.getValue('sCat')
        else:
            sCat = '5'

        if os.path.exists(fav_db): 
            watched = eval( open(fav_db).read() )

            items = []
            item = []
            for result in watched:

                sUrl = result
                sFunction =  watched[result][0]
                sId = watched[result][1]
                try:
                    sTitle = watched[result][2]
                except:
                    sTitle = sId+' - '+urllib.unquote_plus(sUrl)

                try:
                    sCategorie = watched[result][3]
                except:
                    sCategorie = '5'

                items.append([sId, sFunction, sUrl])
                item.append(result)
                oOutputParameterHandler = cOutputParameterHandler()
                oOutputParameterHandler.addParameter('siteUrl', sUrl)
                oOutputParameterHandler.addParameter('sMovieTitle', sTitle)
                oOutputParameterHandler.addParameter('sThumbnail', 'False')
                
                if (sFunction == 'play'):
                    oHoster = cHosterGui().checkHoster(sUrl)
                    oOutputParameterHandler.addParameter('sHosterIdentifier', oHoster.getPluginIdentifier())
                    oOutputParameterHandler.addParameter('sFileName', oHoster.getFileName())
                    oOutputParameterHandler.addParameter('sMediaUrl', sUrl)

                if (sCategorie == sCat):
                    oGui.addFav(sId, sFunction, sTitle, 'mark.png', sUrl, oOutputParameterHandler)
               
            
            oGui.setEndOfDirectory()
        else: return
        return items


    def writeFavourites(self):

        oInputParameterHandler = cInputParameterHandler()
        sTitle = oInputParameterHandler.getValue('sTitle')
        sId = oInputParameterHandler.getValue('sId')
        sUrl = oInputParameterHandler.getValue('siteUrl')
        sFav = oInputParameterHandler.getValue('sFav')

        if (oInputParameterHandler.exist('sCat')):
            sCat = oInputParameterHandler.getValue('sCat')
        else:
            sCat = '5'

        sUrl = urllib.quote_plus(sUrl)
        fav_db = self.__sFile
        watched = {}
        if not os.path.exists(fav_db):
            file(fav_db, "w").write("%r" % watched) 
            
        if os.path.exists(fav_db):
            watched = eval(open(fav_db).read() )
            watched[sUrl] = watched.get(sUrl) or []
            
            #add to watched
            if not watched[sUrl]:
                #list = [sFav, sUrl];
                watched[sUrl].append(sFav)
                watched[sUrl].append(sId)
                watched[sUrl].append(sTitle)
                watched[sUrl].append(sCat)
            else:
                watched[sUrl][0] = sFav
                watched[sUrl][1] = sId
                watched[sUrl][2] = sTitle
                watched[sUrl][3] = sCat

        file(fav_db, "w").write("%r" % watched)
        cConfig().showInfo('Marque-Page', sTitle)
        #fav_db.close()
