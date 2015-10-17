#-*- coding: utf-8 -*-
#
import re
import urllib2,urllib
import xbmc


def parseInt(chain):

    chain = chain.replace(' ','')
    chain = re.sub(r'!!\[\]','1',chain) # !![] = 1
    chain = re.sub(r'\(!\+\[\]','(1',chain)  #si le bloc commence par !+[] >> +1
    chain = re.sub(r'(\([^()]+)\+\[\]\)','(\\1)*10)',chain)  # si le bloc commence par !+[] et fini par +[] >> *10
    
    #bidouille a optimiser
    chain = re.sub(r'\(\+\[\]\)','0',chain)
    
    #print chain

    return eval(chain)

class CloudflareBypass(object):

    def __init__(self):
        self.state = False
            
    def check(self,htmlcontent):
        if 'Checking your browser before accessing' in htmlcontent:
            self.state = True
            return True
        return False
        
    def GetResponse(self,htmlcontent):
        line1 = re.findall('var t,r,a,f, (.+?)={"(.+?)":\+*(.+?)};',htmlcontent)

        varname = line1[0][0] + '.' + line1[0][1]
        calcul = int(parseInt(line1[0][2]))
        
        AllLines = re.findall(';' + varname + '([*\-+])=\+([^;]+)',htmlcontent)
        
        for aEntry in AllLines:
            calcul = eval( str(calcul) + str(aEntry[0]) + str(parseInt(aEntry[1])))
            
        rep = calcul + len(self.host)
        
        return str(rep)
        
    def Valid(self,url,htmlcontent):
        
        #test part
        #url ='http://www.series-en-streaming.tv/saison/250487/1/american-horror-story/'
        #fh = open('c:\\test.txt', "r")
        #htmlcontent = fh.read()
        #fh.close()
        
        
        host1  = re.sub(r'(https*:\/\/[^/]+)(\/*.*)','\\1',url)
        self.host = re.sub(r'https*:\/\/','',host1)
        
        #fh = open('c:\\test.txt', "w")
        #fh.write(htmlcontent)
        #fh.close()
        
        hash = re.findall('<input type="hidden" name="jschl_vc" value="(.+?)"\/>',htmlcontent)[0]
        passe = re.findall('<input type="hidden" name="pass" value="(.+?)"\/>',htmlcontent)[0]
        
        #calcul de la reponse
        rep = self.GetResponse(htmlcontent)

        #xbmc.sleep(5000)
        
        NewUrl = host1 + '/cdn-cgi/l/chk_jschl?jschl_vc='+ urllib.quote_plus(hash) +'&pass=' + urllib.quote_plus(passe) + '&jschl_answer=' + rep
        
        print NewUrl
        print self.host
        print url
        
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:39.0) Gecko/20100101 Firefox/39.0',
                   'Host' : self.host,
                   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                   'Referer': url,
                   'Content-Type': 'text/html; charset=utf-8'}
                   
        req = urllib2.Request(NewUrl,None,headers)
        try:
            response = urllib2.urlopen(req)
        except urllib2.URLError, e:
            if e.code == 503:
            #print e.code
                #On recupere les fameaux cookies
                cookies = e.headers['Set-Cookie']
                cookies = cookies.split(';')[0]
                #print cookies

        #on refait la requete mais avec les cookies
        headers.update({'Cookie': cookies})
        
        print headers
        
        req = urllib2.Request(url,None,headers)
        try:
            response = urllib2.urlopen(req)
            sHtmlContent = response.read()
            
            response.close()
        except urllib2.URLError, e:
            print "CloudFlare bypass failed with cookies"
            print e.code
            #print e.read()
        
            return

        fh = open('c:\\test.txt', "w")
        fh.write(sHtmlContent)
        fh.close()
