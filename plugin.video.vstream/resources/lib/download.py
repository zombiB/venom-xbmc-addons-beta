#-*- coding: utf-8 -*-

from resources.lib.gui.hoster import cHosterGui
from resources.lib.config import cConfig
from resources.lib.handler.inputParameterHandler import cInputParameterHandler
from resources.lib.handler.outputParameterHandler import cOutputParameterHandler
from resources.lib.handler.hosterHandler import cHosterHandler
from resources.lib.handler.pluginHandler import cPluginHandler
from resources.lib.gui.gui import cGui
from resources.lib.gui.guiElement import cGuiElement
from resources.lib.db import cDb
#from traceback import print_exc
import urllib2,urllib
import xbmcplugin, xbmc
import xbmcgui
import xbmcvfs
import string
import re
import threading,os,sys
import weakref

SITE_IDENTIFIER = 'cDownload'

#http://kodi.wiki/view/Add-on:Common_plugin_cache
#https://pymotw.com/2/threading/
#https://code.google.com/p/navi-x/source/browse/trunk/Navi-X/src/CDownLoader.py?r=155

def _run_async(self, func, *args, **kwargs):
    from threading import Thread
    worker = Thread(name='VstreamDownloader' , target=func, args=args, kwargs=kwargs)
    #self.__workersByName[worker.getName()] = worker
    worker.start()
    return worker

    
def listthread():
    print 'list'

    for t in threading.enumerate():
        print t
        #print t.getName()
    return

class cDownloadProgressBar(threading.Thread):
    def __init__(self, *args, **kwargs):

        self.__sTitle = ''
        self.__sDBUrl = ''
        self.__fPath = ''
        self.__sDBUrl = ''
    
        if (kwargs):
            self.__sTitle = kwargs['title']
            self.__sUrl = kwargs['url']
            self.__fPath = kwargs['Dpath']
            self.__sDBUrl = kwargs['DBurl']
        
        threading.Thread.__init__(self)
        
        self.processIsCanceled = False
        self.iCount = 0
        self.oUrlHandler = None
        self.f = None
        
        self.__workersByName = {}
        
        try:
            import StorageServer
            self.Memorise = StorageServer.StorageServer("VstreamDownloader")
        except:
            print 'Le download ne marchera pas correctement'
            
        #queue = self.Memorise.get("SimpleDownloaderQueue")
        #if self.Memorise.lock("SimpleDownloaderQueueLock"):
        #self.Memorise.set("SimpleDownloaderQueue", repr(items))
        
        
    def createProcessDialog(self):
        self.__oDialog = xbmcgui.DialogProgressBG()
        self.__oDialog.create('Download')            
        #xbmc.sleep(1000)
        return self.__oDialog
        
        
    def _StartDownload(self):

        print 'Thread'
        print threading.current_thread().getName()
        
        diag = self.createProcessDialog()
        #diag.isFinished()
        
        #self.Memorise.set("VstreamDownloaderClass", self)
        #self.Memorise.set("VstreamDownloaderClass", repr(self))
        
        self.Memorise.set("VstreamDownloaderWorking", "1")
        
        self.iCount = 0
        
        headers = self.oUrlHandler.info()
        
        iTotalSize = -1
        if "content-length" in headers:
            iTotalSize = int(headers["Content-Length"])
        
        chunk = 16 * 1024
        
        TotDown = 0
        
        while not (self.processIsCanceled or diag.isFinished()):
            
            self.iCount = self.iCount + 1
            data = self.oUrlHandler.read(chunk)
            if not data: break
            self.file.write(data)
            TotDown = TotDown + data.__len__()
            self.__updatedb(TotDown,iTotalSize) 
            
            self.__stateCallBackFunction(self.iCount, chunk, iTotalSize)
            if self.Memorise.get("VstreamDownloaderWorking") == "0":
                self.processIsCanceled = True
                
            #petite pause, ca ralentit le download mais evite de bouffer 100/100 ressources
            xbmc.sleep(200)
        
        self.oUrlHandler.close()
        self.f.close()
        self.__oDialog.close()
        
        self.StopAll()
        
        #if download finish
        if TotDown == iTotalSize:
            print 'Fin de telechargement'
            test = cDownload()
            test.delDownload(self.__sDBUrl)


    def __updatedb(self, TotDown, iTotalSize):
        #percent 3 chiffre
        percent = '{0:.2f}'.format(min(100 * float(TotDown) / float(iTotalSize), 100))
        if percent in ['2.00','10.00','20.00','30.00','40.00','50.00','60.00','70.00','80.00','90.00']:
            meta = {}      
            meta['path'] = self.__fPath
            meta['size'] = TotDown
            meta['totalsize'] = iTotalSize
            meta['status'] = 1
            
            try:
                cDb().update_download(meta)
            except:
                pass
        
        
    def __stateCallBackFunction(self, iCount, iBlocksize, iTotalSize):
        
        if self.__oDialog.isFinished():
            self.createProcessDialog()

        iPercent = int(float(iCount * iBlocksize * 100) / iTotalSize)
        self.__oDialog.update(iPercent, self.__sTitle, self.__formatFileSize(float(iCount * iBlocksize))+'/'+self.__formatFileSize(iTotalSize))
        
        if (self.__oDialog.isFinished()) and not (self.__processIsCanceled):
            self.__processIsCanceled = True
            self.__oDialog.close()

    def run(self):
        
        if not self.Memorise.lock("VstreamDownloaderLock"):
            cConfig().showInfo('Telechargements deja demarrés', self.__sTitle)
            return
        
        #self.Memorise.set("VstreamDownloaderInstance", repr(self))
        self.oUrlHandler = urllib2.urlopen(self.__sUrl)
        
        self.__instance = repr(self)
        
        self.file = xbmcvfs.File(self.__fPath, 'w')
        
        #self._run_async(self._StartDownload,'','')
        self._StartDownload()
        
    def __formatFileSize(self, iBytes):
        iBytes = int(iBytes)
        if (iBytes == 0):
            return '%.*f %s' % (2, 0, 'MB')
        
        return '%.*f %s' % (2, iBytes/(1024*1024.0) , 'MB')
        
    def StopAll(self):
        
        self.processIsCanceled = True
        self.Memorise.unlock("VstreamDownloaderLock")       
        self.Memorise.set("VstreamDownloaderWorking", "0")
                
        return
     
        
class cDownload:  
    def __init__(self):
        self.PBTread = ''

    def __createDownloadFilename(self, sTitle):
        sTitle = re.sub(' +',' ',sTitle) #Vire double espace
        valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
        filename = ''.join(c for c in sTitle if c in valid_chars)
        filename = filename.replace(' .','.')
        #filename = filename.replace(' ','_') #pas besoin de ca, enfin pr moi en tout cas
        return filename
        
    def __formatFileSize(self, iBytes):
        iBytes = int(iBytes)
        if (iBytes == 0):
            return '%.*f %s' % (2, 0, 'MB')
        
        return '%.*f %s' % (2, iBytes/(1024*1024.0) , 'MB')
        
    def CheckDownloadActive(self):
        for t in threading.enumerate():
            print t
            print t.getName()
        return False
   
    def download(self, sDBUrl, sTitle,sDownloadPath):

        __processIsCanceled = False
        self.__sTitle = sTitle
        
        #oGui = cConfig()
        
        #resolve url
        oHoster = cHosterGui().checkHoster(sDBUrl)
        oHoster.setUrl(sDBUrl)
        aLink = oHoster.getMediaLink()

        #aLink = (True,'https://github.com/LordVenom/venom-xbmc-addons-beta/blob/master/plugin.video.vstream/Thumbs.db?raw=true')

        if (aLink[0] == True):
            sUrl = aLink[1]
        else:
            cConfig().showInfo('Lien non resolvable', sTitle)
            return
            
            
        
        try:
            cConfig().log("Telechargement " + str(sUrl))
            
            #background download task
            self.PBTread = cDownloadProgressBar(title = self.__sTitle , url = sUrl , Dpath = sDownloadPath , DBurl = sDBUrl)
            self.PBTread.start()

            cConfig().log("Telechargement ok")

        except:
            #print_exc()
            cConfig().showInfo('Telechargement impossible', sTitle)
            cConfig().log("Telechargement impossible")
            pass
            
        #self.__oDialog.close()
            

    def __createTitle(self, sUrl, sTitle):
        sTitle = re.sub('[\(\[].+?[\)\]]',' ', sTitle)
        
        
        aTitle = sTitle.rsplit('.')
        #Si deja extension
        if (len(aTitle) > 1):
            return sTitle
        
        #recherche d'une extension
        print sUrl
        sUrl = sUrl.lower()
        m = re.search('(flv|avi|mp4|mpg|mpeg)', sUrl)
        if m:
            sTitle = sTitle + '.' + m.group(0)
        else:
            sTitle = sTitle + '.flv' #Si quedale on en prend une au pif
            
        #aUrl = sUrl.rsplit('.')
        #if (len(aUrl) > 1):
        #    sSuffix = aUrl[-1]
        #    sTitle = sTitle + '.' + sSuffix
            
        return sTitle
            
    


        
    def getDownload(self):
        
        oGui = cGui()
        #test
        sPluginHandle = cPluginHandler().getPluginHandle();
        sPluginPath = cPluginHandler().getPluginPath();
        sItemUrl = '%s?site=%s&function=%s&title=%s' % (sPluginPath, SITE_IDENTIFIER, 'StartDownloadList', 'tittle')
        meta = {'title': 'Demarrer la liste complete'}
        
        item = xbmcgui.ListItem('demarer1')
        item.setInfo(type="Video", infoLabels = meta)
        item.setProperty("Video", "true")
        #IMPORTANT
        item.setProperty("IsPlayable", "false")
        # ##
        xbmcplugin.addDirectoryItem(sPluginHandle,sItemUrl,item,isFolder=False)
        #xbmcplugin.setContent(sPluginHandle, 'episodes')
        #xbmcplugin.endOfDirectory(sPluginHandle, cacheToDisc=False)
        
        oOutputParameterHandler = cOutputParameterHandler()
        oGui.addDir(SITE_IDENTIFIER, 'StopDownloadList', 'Arreter', 'mark.png', oOutputParameterHandler)

        oOutputParameterHandler = cOutputParameterHandler()
        oGui.addDir(SITE_IDENTIFIER, 'getDownloadList', 'Liste de Telechargement', 'mark.png', oOutputParameterHandler)
        
        sPluginHandle = cPluginHandler().getPluginHandle();
        sPluginPath = cPluginHandler().getPluginPath();
        sItemUrl = '%s?site=%s&function=%s&title=%s' % (sPluginPath, SITE_IDENTIFIER, 'dummy1', 'tittle')
        meta = {'title': 'Debug1'}     
        item = xbmcgui.ListItem('demarer1')
        item.setInfo(type="Video", infoLabels = meta)
        item.setProperty("Video", "true")
        #IMPORTANT
        item.setProperty("IsPlayable", "false")
        # ##
        xbmcplugin.addDirectoryItem(sPluginHandle,sItemUrl,item,isFolder=False)
        
        oOutputParameterHandler = cOutputParameterHandler()
        oGui.addDir(SITE_IDENTIFIER, 'dummy', 'Debug2', 'mark.png', oOutputParameterHandler)
        
        oOutputParameterHandler = cOutputParameterHandler()
        oGui.addDir(SITE_IDENTIFIER, 'debug', 'Debug3 inf', 'mark.png', oOutputParameterHandler)      
   
        oGui.setEndOfDirectory()
    
    def worker(self):
        """thread worker function"""
        t = threading.currentThread()
        xbmc.sleep(5000)
        print t
        print 'fin'
        return
    
    def debug(self):
        
        print 'debug'
        listthread()
        #print globals()
        
        pass      
    
    
    def dummy1(self):

        print 'start'

        for i in range(3):
            t = threading.Thread(target=self.worker)
            t.start()
        
        listthread()
        
        pass   
    
    def dummy(self):
        listthread()
    
    def StartDownloadOneFile(self):
        self.StartDownloadList(True)
    
    def StartDownloadList(self, one = False):

        if (one):
            oInputParameterHandler = cInputParameterHandler()
            url = oInputParameterHandler.getValue('sUrl')

            meta = {}      
            meta['url'] = url
        
            row = cDb().get_Download(meta)
        else:
            row = cDb().get_Download()
        
        for data in row:

            title = data[1]
            url = urllib.unquote_plus(data[2])
            path = data[3]
            thumbnail = data[4]
            
            print 'telechargement de : ' + title
            break
                
        self.download(url,title,path)

    def StopDownloadList(self):
        self.dummy()
        self.PBTread = cDownloadProgressBar()
        self.PBTread.StopAll()

        return

    def getDownloadList(self):
        oGui = cGui()

        oInputParameterHandler = cInputParameterHandler()

        #try:
        if (1 == 1):
            row = cDb().get_Download()
            print row
            
            for data in row:

                title = data[1]
                url = urllib.unquote_plus(data[2])
                function = data[3]
                cat = data[4]
                thumbnail = data[5]
                size = data[6]
                totalsize = data[7]
                status = data[8]

                oOutputParameterHandler = cOutputParameterHandler()
                oOutputParameterHandler.addParameter('sUrl', url)
                oOutputParameterHandler.addParameter('sMovieTitle', title)
                oOutputParameterHandler.addParameter('sThumbnail', 'False')
                
                # if (function == 'play'):
                    # oHoster = cHosterGui().checkHoster(siteurl)
                    # oOutputParameterHandler.addParameter('sHosterIdentifier', oHoster.getPluginIdentifier())
                    # oOutputParameterHandler.addParameter('sFileName', oHoster.getFileName())
                    # oOutputParameterHandler.addParameter('sMediaUrl', siteurl)


                if status == '0':
                    status = '[COLOR=red]stop[/COLOR]'
                elif status == '1':
                    status='[COLOR=green]encours[/COLOR]'
                                   
                if size:
                    sTitle = title+' - '+status+' - [COLOR=green]'+self.__formatFileSize(size)+'/'+self.__formatFileSize(totalsize)+'[/COLOR]'
                else:
                    sTitle= title+' - '+status
                oGuiElement = cGuiElement()

                #oGuiElement.setSiteName(site)
                oGuiElement.setFunction(function)
                oGuiElement.setTitle(sTitle)
                oGuiElement.setIcon("mark.png")
                oGuiElement.setMeta(0)
                oGuiElement.setThumbnail(thumbnail)
                
                oGui.createContexMenuDownload(oGuiElement, oOutputParameterHandler)
                
                oGui.addFolder(oGuiElement, oOutputParameterHandler, False)
                #oGui.addMovie(SITE_IDENTIFIER, 'showHosters', title, 'films.png', '', '', oOutputParameterHandler)

            oGui.setEndOfDirectory()
        #except: pass
        
        return
        
    def delDownload(self,url =''):
        
        if not url:
            oInputParameterHandler = cInputParameterHandler()
            url = oInputParameterHandler.getValue('sUrl')

        meta = {}      
        meta['url'] = url
        
        try:
            cDb().del_download(meta)
        except:
            pass

        return
        
    def AddDownload(self,meta):
        
        self.__processIsCanceled = False
        
        sTitle = meta['title']
        sUrl = meta['url']
        
        sTitle = self.__createTitle(sUrl, sTitle)
        sTitle = self.__createDownloadFilename(sTitle)
        
        oGui = cConfig()
        sTitle = oGui.showKeyBoard(sTitle)
        if (sTitle != False and len(sTitle) > 0):

            #chemin de sauvegarde
            sPath2 = cConfig().getSetting('Download_Folder')

            dialog = xbmcgui.Dialog()
            sPath = dialog.browse(3, 'Downloadfolder', 'files', '', False, False , sPath2)
            
            if (sPath != ''):
                cConfig().setSetting('Download_Folder',sPath)
                
                sDownloadPath = xbmc.translatePath(sPath +  '%s' % (sTitle, ))

                try:
                    cConfig().log("Rajout en liste de telechargement " + str(sUrl))
                    meta['title'] = sTitle
                    meta['path'] = sDownloadPath
                    cDb().insert_download(meta)
                    
                except:
                    #print_exc()
                    cConfig().showInfo('Telechargement impossible', sTitle)
                    cConfig().log("Telechargement impossible")
                    pass
  
  
    def AddtoDownloadList(self):

        oInputParameterHandler = cInputParameterHandler()
        
        sHosterIdentifier = oInputParameterHandler.getValue('sHosterIdentifier')
        sMediaUrl = oInputParameterHandler.getValue('sMediaUrl')
        #bGetRedirectUrl = oInputParameterHandler.getValue('bGetRedirectUrl')
        sFileName = oInputParameterHandler.getValue('sFileName')

        #if (bGetRedirectUrl == 'True'):
        #    sMediaUrl = self.__getRedirectUrl(sMediaUrl)

        cConfig().log("Telechargement " + sMediaUrl)

        #oHoster = cHosterHandler().getHoster(sHosterIdentifier)
        #oHoster.setFileName(sFileName)

        #oHoster.setUrl(sMediaUrl)
        #aLink = oHoster.getMediaLink()

        meta = {}
        meta['url'] = sMediaUrl
        meta['cat'] = oInputParameterHandler.getValue('sCat')
        meta['title'] = sFileName
        meta['icon'] = xbmc.getInfoLabel('ListItem.Art(thumb)')
    
        self.AddDownload(meta)
            
        return   
