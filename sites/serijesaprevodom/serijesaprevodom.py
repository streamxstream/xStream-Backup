from resources.lib.gui.gui import cGui
from resources.lib.gui.guiElement import cGuiElement
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.parser import cParser
from resources.lib.handler.ParameterHandler import ParameterHandler
from resources.lib import logger
from resources.lib.util import cUtil

SITE_IDENTIFIER = 'serijesaprevodom'
SITE_NAME = 'SSP'

URL_MAIN = 'http://www.turske-serije.com'

def load():
    logger.info("Load %s" % SITE_NAME)
    oGui = cGui()
    params = ParameterHandler()

    oRequestHandler = cRequestHandler(URL_MAIN)
    sHtmlContent = oRequestHandler.request()
    pattern = '<ul[^>]*class="nav menu"[^>]*>(.*?)</ul>'
    aResult = cParser().parse(sHtmlContent, pattern)

    if not aResult[0]:
        return

    pattern = '<li[^>]*class="item-\d+.*?"[^>]*><a[^>]*href="([^"]*)"[^>]*>(.*?)</'
    aResult = cParser().parse(aResult[1][0], pattern)

    for sUrlPart,sName in aResult[1]:
        params.setParam('sUrl',URL_MAIN + sUrlPart)
        oGui.addFolder(cGuiElement(sName.strip() + " serije", SITE_IDENTIFIER, 'showContent'), params)
    
    oGui.setEndOfDirectory()

def showContent (sUrl = False, sGui = False): 
    oGui = sGui if sGui else cGui()
    params = ParameterHandler()
    isEpisode = params.getValue('showEpisodes')
    if not sUrl: sUrl = params.getValue('sUrl')
    sHtmlContent = cRequestHandler(sUrl).request()
    # parse movie entries
    pattern = '<div[^>]*itemtype="[^>]*BlogPosting"[^>]*>.*?' # container
    pattern += '<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>.*?' # name / link
    pattern += '<img[^>]*src="([^"]*)"[^>]*>' # img
    aResult = cParser().parse(sHtmlContent, pattern)

    if not aResult[0]:
        pattern = '<li><img[^>]*src="([^"]+)".*?<a href="([^"]+).*?>([^"]+)</a></li>' # img/link/name
        aResult = cParser().parse(sHtmlContent, pattern)

    if not aResult[0]:
        if not sGui: oGui.showInfo('xStream','Es wurde kein Eintrag gefunden')
        return

    total = len(aResult[1]) # Anzahl der Treffer
    for sLinkRegex, sNameRegex, sImgRegex in aResult[1]:
        sLink = sLinkRegex
        sName = sNameRegex
        sImg = sImgRegex
        if '/' in sName: # fallback
            sImg = sLinkRegex
            sLink = sNameRegex
            sName = sImgRegex

        guiElement = cGuiElement(cUtil().unescape(sName.decode('utf-8')).encode('utf-8').strip(), SITE_IDENTIFIER, 'getHosters' if isEpisode else 'showContent')
        guiElement.setThumbnail(URL_MAIN + sImg)
        guiElement.setMediaType('episode' if isEpisode else 'tvshow')
        params.setParam('sUrl', URL_MAIN + sLink)
        params.setParam('showEpisodes', True)
        oGui.addFolder(guiElement, params, (not isEpisode), total)

    pattern = '<li[^>]*pagination-next[^>]*><a[^>]*href="([^"]*)"[^>]*>'
    aResult = cParser().parse(sHtmlContent, pattern)

    if aResult[0] and aResult[1][0]:
        params.setParam('sUrl', URL_MAIN + aResult[1][0])
        oGui.addNextPage(SITE_IDENTIFIER, 'showContent', params)

    if not sGui:
        oGui.setView('episodes' if isEpisode else 'tvshows')
        oGui.setEndOfDirectory()

def getHosters():
    sUrl = ParameterHandler().getValue('sUrl')  # Weitergegebenen Urlteil aus den Parametern holen 
    sHtmlContent = cRequestHandler(sUrl).request()         # Seite abrufen

    hosters = []

    aResult = cParser().parse(sHtmlContent, '"item-page">(.*?)class="moduletable"')

    if not aResult[0]:
        return hosters

    aResult = cParser().parse(aResult[1][0], '<iframe[^>]*src="([^"]+)"')
    if aResult[0]:
        for sHosterUrl in aResult[1]:
            hoster = {} 
            hoster['link'] = sHosterUrl
            # extract domain name
            temp = sHosterUrl.split('//')
            temp = str(temp[-1]).split('/')
            temp = str(temp[0]).split('.')
            hName = temp[-2]
            Vname = hName.upper()
            hoster['name'] = (Vname)
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