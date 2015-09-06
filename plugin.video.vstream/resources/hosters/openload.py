from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.parser import cParser
from resources.lib.config import cConfig
from resources.hosters.hoster import iHoster
import re,urllib2
import xbmcgui

class cHoster(iHoster):

    def __init__(self):
        self.__sDisplayName = 'Openload'
        self.__sFileName = self.__sDisplayName
        self.__sHD = ''

    def getDisplayName(self):
        return  self.__sDisplayName

    def setDisplayName(self, sDisplayName):
        self.__sDisplayName = sDisplayName + ' [COLOR skyblue]'+self.__sDisplayName+'[/COLOR] [COLOR khaki]'+self.__sHD+'[/COLOR]'

    def setFileName(self, sFileName):
        self.__sFileName = sFileName

    def getFileName(self):
        return self.__sFileName

    def getPluginIdentifier(self):
        return 'openload'

    def setHD(self, sHD):
        self.__sHD = ''

    def getHD(self):
        return self.__sHD

    def isDownloadable(self):
        return True

    def isJDownloaderable(self):
        return True

    def getPattern(self):
        return '';
        
    def __getIdFromUrl(self, sUrl):
        return ''

    def setUrl(self, sUrl):
        self.__sUrl = str(sUrl)

    def checkUrl(self, sUrl):
        return True

    def __getUrl(self, media_id):
        return
        
    def getMediaLink(self):
        return self.__getMediaLinkForGuest()

    def __getMediaLinkForGuest(self):

        api_call =''
        
        oRequest = cRequestHandler(self.__sUrl)
        sHtmlContent = oRequest.request()
        
        #fh = open('c:\\test.txt', "w")
        #fh.write(sHtmlContent)
        #fh.close()
        
        # UA = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0'
        # headers = {'User-Agent': UA ,
                   # 'Host' : 'openload.co',
                   # 'Accept-Language':'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
                   # #'Referer': 'http://www.voirfilms.org/batman-unlimited-monstrueuse-pagaille.htm',
                   # 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                   # #'Content-Type': 'text/html; charset=utf-8'
                   # 'Accept-Encoding' : 'gzip, deflate'
                   # }
        
        
        # class NoRedirection(urllib2.HTTPErrorProcessor):
            # def http_response(self, request, response):
                # return response
            # https_response = http_response
        
        
        # req = urllib2.Request(url,None, headers)
        # try:
            # response = urllib2.urlopen(req)
        # except urllib2.URLError, e:
            # print e.read()
            # print e.reason
            
        # print response.geturl()
        
        # sHtmlContent = response.read()
        # response.close()       
        
        oParser = cParser()
        sPattern = 'urce type="video[^"<>]+?" src="([^<>"]+?)">'
        aResult = oParser.parse(sHtmlContent, sPattern)
        
        #1 er essais
        if (aResult[0] == True):
            api_call = aResult[1][0]
        else:
            #second essais
            sPattern = 'script>\$\("video source"\)\.attr\("src", "(.+?)"\);'
            aResult = oParser.parse(sHtmlContent, sPattern)
            if (aResult[0] == True):
                api_call = aResult[1][0]
            else:
                #3 eme essais
                sPattern = '<source src="([^<>"]+?)?mime=true" type='
                aResult = oParser.parse(sHtmlContent, sPattern)
                if (aResult[0] == True):
                    api_call = aResult[1][0]
        
        #print api_call
        
        if (api_call):
            return True, api_call
            
        return False, False
