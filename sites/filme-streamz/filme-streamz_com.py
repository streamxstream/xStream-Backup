# -*- coding: utf-8 -*-
from resources.lib.gui.gui import cGui
from resources.lib.gui.guiElement import cGuiElement
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.parser import cParser
from resources.lib.handler.ParameterHandler import ParameterHandler

SITE_IDENTIFIER = 'filme-streamz_com'
SITE_NAME = 'Filme-Streamz'
SITE_ICON = 'filme-streamz.png'

URL_MAIN = 'http://filme-streamz.com'

def load():
   oGui = cGui()
     
   oGui.addFolder(cGuiElement('Neuste Filme', SITE_IDENTIFIER, 'showNewMovies'))
   oGui.setEndOfDirectory()
 
def showNewMovies():
   oGui = cGui()
   params = ParameterHandler()
   oRequestHandler = cRequestHandler(URL_MAIN)
   sHtmlContent = oRequestHandler.request()
   # parse movie entries
   pattern = '<li[^>]*class="imgborder".*?<a[^>]*href="([^"]*)"[^>]*title="([^"]*)"[^>]*>.*?</a[>].*?<img[^>]*src="([^"]*)"[^>]*class="scale-with-grid"[^>]*>.*?'
   oParser = cParser()
   aResult = oParser.parse(sHtmlContent, pattern)

   if not aResult[0]:
      return

   total = len(aResult[1])

   for link, title, img in aResult[1]:
       titleParse = title.split('(')
       movieTitle = titleParse[0].strip().decode('iso-8859-1').encode('utf-8')
       guiElement = cGuiElement(movieTitle, SITE_IDENTIFIER, 'getHoster')
       guiElement.setThumbnail(img)
       #guiElement.setDescription(plot.decode('iso-8859-1'))
       if len(titleParse)>1:
           tag = titleParse[-1].replace(')','')
           if tag.isdigit() and len(tag)==4:
               guiElement.setYear(tag)
       guiElement.setMediaType('movie')
       #if '720' in qual:
       #    guiElement._sQuality = 720
       #elif '1080p' in qual:
       #    guiElement._sQuality = 1080

       params.setParam('siteUrl',link)
       oGui.addFolder(guiElement, params, bIsFolder = False, iTotal =total)
   oGui.setView('movies')
   oGui.setEndOfDirectory()