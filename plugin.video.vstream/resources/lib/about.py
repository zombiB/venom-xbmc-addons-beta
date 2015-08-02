#-*- coding: utf-8 -*-
#Venom.
from config import cConfig
#from resources.lib.handler.pluginHandler import cPluginHandler       
import urllib, urllib2
import xbmc, xbmcgui, xbmcaddon
import xbmcvfs
import sys, time, os
import hashlib, md5

SITE_IDENTIFIER = 'about'
SITE_NAME = 'About'

class cAbout:

    def __init__(self):
        self.main(sys.argv[1])
        #self.__sFunctionName = ''

    def get_remote_md5_sum(self, url, max_file_size=100*1024*1024):
        try:
            remote = urllib2.urlopen(url)
            hash = hashlib.md5()
         
            total_read = 0
            while True:
                data = remote.read(4096)
                total_read += 4096
         
                if not data or total_read > max_file_size:
                    break
         
                hash.update(data)
         
            return hash.hexdigest()
        except:            
            cConfig().error("%s,%s" % (cConfig().getlanguage(30205), url))
            return False
            
    def get_root_md5_sum(self, root, max_file_size=100*1024*1024):
        try:
            remote = open(root,'r')
            hash = hashlib.md5()
         
            total_read = 0
            while True:
                data = remote.read(4096)
                total_read += 4096
         
                if not data or total_read > max_file_size:
                    break
         
                hash.update(data)
         
            return hash.hexdigest()
        except:            
            cConfig().error("%s,%s" % (cConfig().getlanguage(30205), url))
            return False
     
    def __getFileNamesFromFolder(self, sFolder):
        aNameList = []
        items = os.listdir(sFolder)
        for sItemName in items:
            sFilePath = os.path.join(sFolder, sItemName)
            # xbox hack
            sFilePath = sFilePath.replace('\\', '/')
            sUrlPath = "https://raw.githubusercontent.com/LordVenom/venom-xbmc-addons/master/plugin.video.vstream/resources/sites/"+sItemName
            
            if (os.path.isdir(sFilePath) == False):
                if (str(sFilePath.lower()).endswith('py')):   
                    aNameList.append([sFilePath,sUrlPath,sItemName])
        return aNameList
        
    def getPlugins(self):
        oConfig = cConfig()

        sFolder = cConfig().getAddonPath()
        sFolder = os.path.join(sFolder, 'resources/sites')

        # xbox hack        
        sFolder = sFolder.replace('\\', '/')
        
        aFileNames = self.__getFileNamesFromFolder(sFolder)
        return aFileNames
      

    def main(self, env):
    
        sUrl = 'https://raw.githubusercontent.com/LordVenom/venom-xbmc-addons/master/plugin.video.vstream/changelog.txt'
        

        if (env == 'changelog'):
            try:
                oRequest =  urllib2.Request(sUrl)
                oResponse = urllib2.urlopen(oRequest)
                sContent = oResponse.read()
                self.TextBoxes('vStream Changelog', sContent)
            except:            
                cConfig().error("%s,%s" % (cConfig().getlanguage(30205), sUrl))
            return

        if (env == 'update'):
            aPlugins = self.getPlugins()
            cConfig().showInfo('vStream', 'Patientez svp')
            sContent = ""
            sdown = 0

            for aPlugin in aPlugins:
                RootUrl = aPlugin[0]
                WebUrl = aPlugin[1]
                ItemName = aPlugin[2]
                PlugWeb = self.get_remote_md5_sum(WebUrl)
                PlugRoot = self.get_root_md5_sum(RootUrl)
                if (PlugWeb != PlugRoot):
                    try:
                        self.__download(WebUrl, RootUrl)
                        sContent += "[COLOR green]"+ItemName+"[/COLOR] OK \n"
                    except:
                        sContent += "[COLOR red]"+ItemName+"[/COLOR] Erreur \n"
                        
                else:
                    sdown = sdown+1
                    
                
            sContent += "Fichier à jour %s" %  (sdown)
            #self.TextBoxes('vStream mise à Jour', sContent)
            cConfig().createDialogOK(sContent)
            return

        else :

            stats_in = self.get_remote_md5_sum(sUrl) 

            stats_out = cConfig().getSetting('date_update')


            if (stats_out != stats_in):
                try:
                    oRequest =  urllib2.Request(sUrl)
                    oResponse = urllib2.urlopen(oRequest)
                    sContent = oResponse.read()
                    self.TextBoxes('Changelog', sContent)
                    cConfig().setSetting('date_update', str(stats_in))
                except:            
                    cConfig().error("%s,%s" % (cConfig().getlanguage(30205), sUrl))
                return
        return
        
    def __download(self, WebUrl, RootUrl):
            inf = urllib.urlopen(WebUrl)
            
            f = xbmcvfs.File(RootUrl, 'w')
            #if (xbmcvfs.exists(RootUrl)):
                #xbmcvfs.delete()
            #save it
            line = inf.read()         
            f.write(line)
            
            inf.close()
            f.close()
            
        
    def TextBoxes(self, heading, anounce):
        class TextBox():
            # constants
            WINDOW = 10147
            CONTROL_LABEL = 1
            CONTROL_TEXTBOX = 5

            def __init__( self, *args, **kwargs):
                # activate the text viewer window
                xbmc.executebuiltin( "ActivateWindow(%d)" % ( self.WINDOW, ) )
                # get window
                self.win = xbmcgui.Window( self.WINDOW )
                # give window time to initialize
                xbmc.sleep( 500 )
                self.setControls()

            def setControls( self ):
                # set heading
                self.win.getControl( self.CONTROL_LABEL ).setLabel(heading)
                try:
                    f = open(anounce)
                    text = f.read()
                except: text=anounce
                self.win.getControl( self.CONTROL_TEXTBOX ).setText(text)
                return
        TextBox()

cAbout()