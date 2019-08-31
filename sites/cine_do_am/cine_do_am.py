# -*- coding: utf-8 -*-
from resources.lib.gui.gui import cGui
from resources.lib.gui.guiElement import cGuiElement
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.parser import cParser
from resources.lib import logger
from resources.lib.handler.ParameterHandler import ParameterHandler
from resources.lib.handler.pluginHandler import cPluginHandler
from resources.lib.util import cUtil
import re

SITE_IDENTIFIER = 'cine_do_am'
SITE_NAME = 'CineDoam'
SITE_ICON = 'cine_do_am.png'

URL_MAIN = 'http://cine.do.am'
URL_CINEMA = URL_MAIN + '/load/deutsche_filme/alle_filme/2'

def load():
   logger.info("Load %s" % SITE_NAME)
   oGui = cGui()
   params = ParameterHandler()
   params.setParam('sUrl', URL_CINEMA)
   oGui.addFolder(cGuiElement('Deutsche Filme', SITE_IDENTIFIER, 'showEntries'), params)
   oGui.setEndOfDirectory()

def showEntries(entryUrl = False, sGui = False):
   oGui = cGui()
   params = ParameterHandler()
   if not entryUrl: entryUrl = params.getValue('sUrl')
   sHtmlContent = cRequestHandler(entryUrl).request()
   pattern ='<div[^>]class="eTitle"[^>]style=".*?<a[^>]href="([^"]+).*?">([^"]+)</a></div>.*?img alt=""[^>]src="([^"]+)'
   aResult = cParser().parse(sHtmlContent, pattern)

   if len(aResult) > 0:

       for result in aResult[1]:
           oGuiElement = cGuiElement(result[1], SITE_IDENTIFIER, 'showHosters')
           oGuiElement.setThumbnail(result[2])
           params.setParam('entryUrl', URL_MAIN + result[0])
           params.setParam('sName', result[1])
           params.setParam('sThumbnail', result[2])
           oGui.addFolder(oGuiElement, params, bIsFolder = False)
            
           pattern = '<span>4</span></a>  <a class="swchItem" href="([^" ]+)'
           aResult = cParser().parse(sHtmlContent, pattern)
   if aResult[0] and aResult[1][0]:
       params.setParam('sUrl', URL_MAIN + aResult[1][0])
       oGui.addNextPage(SITE_IDENTIFIER, 'showEntries', params)
            
            
            
       oGui.setEndOfDirectory()

       return
            
def showHosters():
   oParams = ParameterHandler()
   sUrl = oParams.getValue('entryUrl')
   sHtmlContent = cRequestHandler(sUrl).request()
   sPattern = 'STREAM[^>]MIT[^>]([^$)]+)"/></div>.*?<br[^>][^>]>[^>]<a[^>]class="link"[^>]href="([^"]+)' # hostername / url
   aResult = cParser().parse(sHtmlContent, sPattern)
   hosters = []
   if aResult[1]:
       for sName, sUrl in aResult[1]:
           hoster = {} 
           hoster['link'] = sUrl
           hoster['name'] = sName.replace('sharedsx', 'Shared.sx')
           hosters.append(hoster)
   if hosters:
       hosters.append('getHosterUrl')
   return hosters
    
def getHosterUrl(sUrl = False):
   if not sUrl: sUrl = ParameterHandler().getValue('url')
   results = []
   result = {}
   result['streamUrl'] = sUrl
   result['resolved'] = False
   results.append(result)
   return results