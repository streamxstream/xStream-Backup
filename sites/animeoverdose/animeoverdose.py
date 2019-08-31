from resources.lib.gui.gui import cGui
from resources.lib.gui.guiElement import cGuiElement
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.parser import cParser
from resources.lib.handler.ParameterHandler import ParameterHandler

SITE_IDENTIFIER = 'animeoverdose'
SITE_NAME = 'AnimeOverdose'
SITE_ICON = 'animeoverdose.png'

URL_MAIN = 'http://www.anime-overdose.com/'
URL_MOVIES = 'http://www.anime-overdose.com/streaming/filmovi?stranica=1'
URL_SERIES = 'http://www.anime-overdose.com/streaming'

def load():
  
    oGui = cGui()
   
    oGui.addFolder(cGuiElement('Serije', SITE_IDENTIFIER, 'showSeries'))
    oGui.addFolder(cGuiElement('Filmovi', SITE_IDENTIFIER, 'showMovies'))
    oGui.addFolder(cGuiElement('Pretrazi', SITE_IDENTIFIER, 'showSearch'))
    oGui.setEndOfDirectory()
   

def showMovies(): 
    oGui = cGui() 
    params = ParameterHandler()    
    oRequestHandler = cRequestHandler(URL_MOVIES)
    sHtmlContent = oRequestHandler.request()
    # parse movie entries
    pattern = 'class="download-button".*?<a href="([^"]+)".*?<dd class="name"><h2>([^"]+)</h2>'
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, pattern)
    if not aResult[0]:
        return  
    total = len(aResult[1]) # Anzahl der Treffer
    for link, title in aResult[1]:
        movieTitle = title # Titel von Jahr trennen
        
          
        guiElement = cGuiElement(movieTitle, SITE_IDENTIFIER, 'getHosters')
           
        guiElement.setMediaType('movie')
        params.setParam('siteUrl',link)  
        oGui.addFolder(guiElement, params, bIsFolder = False, iTotal = total)
	pattern = 'class="selected".*?<a href="([^"]+)"'
    aResult = cParser().parse(sHtmlContent, pattern)
    if aResult[0] and aResult[1][0]:
        params.setParam('sUrl', aResult[1][0])
        oGui.addNextPage(SITE_IDENTIFIER, 'showMovies', params)
    if not cGui:
        oGui.setView(contentType)	
        	
        
    oGui.setEndOfDirectory()
	
def showSeries(): 
    oGui = cGui() 
    params = ParameterHandler()    
    oRequestHandler = cRequestHandler(URL_SERIES)
    sHtmlContent = oRequestHandler.request()
    # parse movie entries
    pattern = 'class="completed".*?<a href="([^"]+)".*?>([^"]+)</a>'
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, pattern)
    if not aResult[0]:
        return  
    total = len(aResult[1]) # Anzahl der Treffer
    for link, title in aResult[1]:
        seriesTitle = title # Titel von Jahr trennen
           
        guiElement = cGuiElement(seriesTitle, SITE_IDENTIFIER, 'getEpisodes')
           
        guiElement.setMediaType('tvshow')
        params.setParam('siteUrl',link)
        oGui.addFolder(guiElement, params, bIsFolder = False, iTotal = total)
    oGui.setEndOfDirectory()		
	
def getEpisodes ():
    oGui = cGui() 
    params = ParameterHandler()
    sUrl2 = params.getValue('siteUrl')
    oRequestHandler = cRequestHandler(sUrl2)
    sHtmlContent = oRequestHandler.request()
    # parse movie entries
    pattern = 'class="download-button".*?<a href="([^"]+)".*?<dd class="name"><h2>([^"]+)</h2>'
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, pattern)
    if not aResult[0]:
        return  
    total = len(aResult[1]) # Anzahl der Treffer
    for link, title in aResult[1]:
        episodeTitle = title # Titel von Jahr trennen
          
        guiElement = cGuiElement(episodeTitle, SITE_IDENTIFIER, 'getHosters')
           
        guiElement.setMediaType('episodes')
        params.setParam('siteUrl',link)  
        oGui.addFolder(guiElement, params, bIsFolder = False, iTotal = total)
	
    if not cGui:
        oGui.setView(contentType)	
        	    
    oGui.setEndOfDirectory()
	
def getHosters():
    oParams = ParameterHandler() #Parameter laden
    sUrl = oParams.getValue('siteUrl')  # Weitergegebenen Urlteil aus den Parametern holen 
   
    oRequestHandler = cRequestHandler(sUrl) # gesamte Url zusammesetzen
    sHtmlContent = oRequestHandler.request()         # Seite abrufen

    sPattern = 'class="video-link".*? href="([^"]+)".*?data-type="([^"]+)"'
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)
    hosters = []                                     # hosterliste initialisieren
    sFunction='getHosterUrl'                         # folgeFunktion festlegen 
    if aResult[0]:
        for aEntry, name in aResult[1]:
            hoster = {} 
            hoster['link'] = aEntry
            # extract domain name
            hoster['name'] = name
            hosters.append(hoster)
        hosters.append(sFunction)
    return hosters
   
def getHosterUrl(sStreamUrl = False):

    if not sStreamUrl:
        params = ParameterHandler()
        sStreamUrl = oParams.getValue('url')
    results = []
    result = {}
    result['streamUrl'] = sStreamUrl
    result['resolved'] = False
    results.append(result)
    return results