#-*- coding: utf-8 -*-
#
from resources.lib.config import cConfig
import re,os
import urllib2,urllib
import xbmc


def parseInt(chain):

    chain = chain.replace(' ','')
    chain = re.sub(r'!!\[\]','1',chain) # !![] = 1
    chain = re.sub(r'\(!\+\[\]','(1',chain)  #si le bloc commence par !+[] >> +1
    chain = re.sub(r'(\([^()]+)\+\[\]\)','(\\1)*10)',chain)  # si le bloc commence par !+[] et fini par +[] >> *10
    
    #bidouilles a optimiser non geree encore par regex
    chain = re.sub(r'\(\+\[\]\)','0',chain)
    if chain.startswith('!+[]'):
        chain = chain.replace('!+[]','1')
    
    #print chain
    return eval(chain)
    
    
class NoRedirection(urllib2.HTTPErrorProcessor):    
    def http_response(self, request, response):
        return response

class CloudflareBypass(object):

    def __init__(self):
        self.state = False
                       
    def DeleteCookie(self,Domain):
        PathCache = cConfig().getSettingCache()
        file = os.path.join(PathCache,'Cookie_'+ str(Domain) +'.txt')
        os.remove(os.path.join(PathCache,file))
        
    def SaveCookie(self,Domain,data):
        PathCache = cConfig().getSettingCache()
        Name = os.path.join(PathCache,'Cookie_'+ str(Domain) +'.txt')

        #save it
        file = open(Name,'w')
        file.write(data)

        file.close()
        
    def Readcookie(self,Domain):
        PathCache = cConfig().getSettingCache()
        Name = os.path.join(PathCache,'Cookie_'+ str(Domain) +'.txt')
        
        try:
            file = open(Name,'r')
            data = file.read()
            file.close()
        except:
            return False
        
        return data
            
  
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
        
        
    def Valid(self,url,htmlcontent,cookies):
        
        self.hostComplet = re.sub(r'(https*:\/\/[^/]+)(\/*.*)','\\1',url)
        self.host = re.sub(r'https*:\/\/','',self.hostComplet)
        self.cookies = cookies
        
        self.headers = [('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:39.0) Gecko/20100101 Firefox/39.0'),
                       ('Host' , self.host),
                       ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'),
                       ('Accept-Language','fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3'),
                       #('Accept-Encoding','gzip, deflate'),
                       ('Referer', url),
                       #('Cookie' , self.cookies),
                       ('Content-Type', 'text/html; charset=utf-8')]
                       
                       
        cookieMem = self.Readcookie(self.host.replace('.','_'))
        if not (cookieMem == False):
            cookies = cookieMem
            print 'cookies present'
        else:
        
            #1 er etape : On recharge la page, pas forcement necessaire mais evite les probleme de headers
            opener = urllib2.build_opener(NoRedirection)
            opener.addheaders = self.headers
            #opener.addheaders.append (('Cookie', self.cookies))

            response = opener.open(url)
            htmlcontent = response.read()
            response.close()
            
            #print htmlcontent
            
            #2 eme etape recuperation cookies
            hash = re.findall('<input type="hidden" name="jschl_vc" value="(.+?)"\/>',htmlcontent)[0]
            passe = re.findall('<input type="hidden" name="pass" value="(.+?)"\/>',htmlcontent)[0]

            #calcul de la reponse
            rep = self.GetResponse(htmlcontent)

            xbmc.sleep(5000)
            
            NewUrl = self.hostComplet + '/cdn-cgi/l/chk_jschl?jschl_vc='+ urllib.quote_plus(hash) +'&pass=' + urllib.quote_plus(passe) + '&jschl_answer=' + rep
            
            opener = urllib2.build_opener(NoRedirection)
            opener.addheaders = self.headers
            #opener.addheaders.append(('Cookie', self.cookies))
            
            response = opener.open(NewUrl)

            if 'Set-Cookie' in response.headers:
                cookies = str(response.headers.get('Set-Cookie'))
                c1 = re.findall('__cfduid=(.+?);',cookies)
                c2 = re.findall('cf_clearance=(.+?);',cookies)
                if not c1 or not c2:
                    return False
                cookies = '__cfduid=' + c1[0] + '; cf_clearance=' + c2[0]
                response.close()
            else:
                print "Cookies manquants"
                response.close()
                return False
                
            #Memorisation
            print cookies
            self.SaveCookie(self.host.replace('.','_'),cookies)


        #3 eme etape : on refait la requete mais avec les nouveaux cookies 
        opener = urllib2.build_opener(NoRedirection)
        opener.addheaders = self.headers
        
        #on rajoute les nouveaux coockies
        opener.addheaders.append (('Cookie', cookies))
        
        response = opener.open(url)
        htmlcontent = response.read()
        if self.check(htmlcontent):
            #probleme, cookies plus valide, on l'efface, sera remit a jour la prochaine fois
            print "Cookies Out of date"
            self.DeleteCookie(self.host.replace('.','_'))
            return False
            
        response.close()
            
        #print htmlcontent
        
        fh = open('c:\\test.txt', "w")
        fh.write(htmlcontent)
        fh.close()
        
        return htmlcontent
