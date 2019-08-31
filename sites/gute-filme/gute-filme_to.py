# -*- coding: utf-8 -*-
from resources.lib.gui.gui import cGui
from resources.lib.gui.guiElement import cGuiElement
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.parser import cParser
from resources.lib import logger
from resources.lib.handler.ParameterHandler import ParameterHandler
from resources.lib.util import cUtil

SITE_IDENTIFIER = 'gute-filme_to'
SITE_NAME = 'Gute Filme'
SITE_ICON = 'gutefilme.png'

URL_MAIN = 'http://www.gute-filme.to/'
URL_LIST = URL_MAIN + 'filmliste/grid/%s/4:6/title/ASC/'
URL_SEARCH = URL_MAIN + '?s=%s&searchsubmit=U'

def load():
    logger.info("Load %s" % SITE_NAME)

    oGui = cGui()
    params = ParameterHandler()

    params.setParam('sUrl', URL_LIST % "#")
    oGui.addFolder(cGuiElement("Alle Filme", SITE_IDENTIFIER, 'showEntriesFilmlist'), params)
    oGui.addFolder(cGuiElement('A-Z', SITE_IDENTIFIER, 'showFilmlist'))
    params.setParam('sTyp', "Genres")
    oGui.addFolder(cGuiElement('Genres', SITE_IDENTIFIER, 'showYearOrGenreList'),params)
    params.setParam('sTyp', "Jahr")
    oGui.addFolder(cGuiElement('Jahr', SITE_IDENTIFIER, 'showYearOrGenreList'),params)
    oGui.addFolder(cGuiElement('Suche', SITE_IDENTIFIER, 'showSearch'))
    oGui.setEndOfDirectory()

def showFilmlist():
    oGui = cGui()
    params = ParameterHandler()
    for number in range(0, 10): # numbers from 0-9
        params.setParam('sUrl', URL_LIST % str(number))
        oGui.addFolder(cGuiElement(str(number), SITE_IDENTIFIER, 'showEntriesFilmlist'), params)
    import string   
    for letter in string.uppercase[:26]: # letters from A-Z
        params.setParam('sUrl', URL_LIST % str(letter))
        oGui.addFolder(cGuiElement(letter, SITE_IDENTIFIER, 'showEntriesFilmlist'), params)
    oGui.setEndOfDirectory()

def showYearOrGenreList():
    oGui = cGui()
    sHtmlContent = cRequestHandler(URL_MAIN).request()
    pattern = "<a[^>]*href=['\"][^'\"]*['\"][^>]*>%s</a><ul class=['\"]sub-menu['\"]>(.*?)</ul>" % ParameterHandler().getValue('sTyp')
    aResult = cParser().parse(sHtmlContent, pattern)
    if aResult[0]: 
        aResult = cParser().parse(aResult[1][0], "<a[^>]*href=['\"]([^'\"]*)['\"][^>]*>(.*?)</a></li>")
        if not aResult[0]:
            return
        total = len (aResult[1])
        for sUrl, sTitle in aResult[1]:
            oOutParms = ParameterHandler()
            oOutParms.setParam('sUrl', sUrl)
            oGui.addFolder(cGuiElement(sTitle.strip(), SITE_IDENTIFIER, 'showEntries'), oOutParms, iTotal = total)
    oGui.setEndOfDirectory()

def showEntries(entryUrl = False, sGui = False):
    oGui = sGui if sGui else cGui()
    params = ParameterHandler()

    if not entryUrl: entryUrl = params.getValue('sUrl')

    sHtmlContent = cRequestHandler(entryUrl, ignoreErrors = (sGui is not False)).request()
    pattern = "<article[^>]*class=['\"].*? (movie|page) .*?['\"][^>]*>.*?" # link-typ
    pattern += "<a[^>]*href=['\"]([^'\"]*)['\"][^>]*>(.*?)</a>.*?" # url / title
    pattern += "(?:<img[^>]*src=['\"]([^'\"]*)\?fit.*?['\"][^>]*>.*?)?" # Thumbnail (opt)
    pattern += "(?:<div[^>]*class=['\"]post-entry-content['\"][^>]*><p>(.*?)<.*?)?" # description (opt) 
    pattern += "</article>" 
    aResult = cParser().parse(sHtmlContent, pattern)

    if not aResult[0] or not aResult[1][0]: 
        if not sGui: oGui.showInfo('xStream','Es wurde kein Eintrag gefunden')
        return

    for sLinkTyp ,sUrl, sName, sThumbnail, sDesc in aResult[1]:
        if sLinkTyp == "movie" : # only allow movies (ignore other typs)
            __addMovieEntry(oGui, sName, sUrl, sThumbnail, sDesc)

    __addNextPage(oGui,sHtmlContent,params,'showEntries')
    if not sGui: oGui.setEndOfDirectory()

def showEntriesFilmlist(entryUrl = False, sGui = False):
    oGui = sGui if sGui else cGui()
    params = ParameterHandler()

    if not entryUrl: entryUrl = params.getValue('sUrl')

    sHtmlContent = cRequestHandler(entryUrl).request()
    pattern = "<div[^>]*id=['\"]wpmoly-movie-\d*['\"][^>]*>\s*?"
    pattern += "<a[^>]*title=['\"]([^'\"]*)['\"][^>]*href=['\"]([^'\"]*)['\"][^>]*>\s?" # title / url
    pattern += "(?:<img[^>]*src=['\"]([^'\"]*)\?fit.*?['\"][^>]*>.*?)?" # Thumbnail (opt)
    aResult = cParser().parse(sHtmlContent, pattern)

    if not aResult[0] or not aResult[1][0]: 
        if not sGui: oGui.showInfo('xStream','Es wurde kein Eintrag gefunden')
        return

    for sName, sUrl, sThumbnail in aResult[1]:
        __addMovieEntry(oGui, sName, sUrl, sThumbnail)

    __addNextPage(oGui,sHtmlContent,params,'showEntriesFilmlist')
    if not sGui: oGui.setEndOfDirectory()

def __addMovieEntry(oGui, sName, sUrl, sThumbnail, sDesc = ""):
    oGuiElement = cGuiElement()
    oGuiElement.setSiteName(SITE_IDENTIFIER)
    oGuiElement.setFunction('showHosters')
    oGuiElement.setTitle(cUtil().unescape(sName.decode('utf-8')).encode('utf-8'))
    oGuiElement.setMediaType('movie')
    oGuiElement.setThumbnail(sThumbnail)
    oGuiElement.setDescription(cUtil().unescape(sDesc.decode('utf-8')).encode('utf-8').strip())
    oOutParms = ParameterHandler()
    oOutParms.setParam('entryUrl', sUrl)
    oGui.addFolder(oGuiElement, oOutParms, bIsFolder = False)

def __addNextPage(oGui, sHtmlContent, params, function):
    aResult = cParser().parse(sHtmlContent, "<span[^>]class=['\"]page-numbers current['\"].*?<a[^>]*href=['\"]([^'\"]*)['\"][^>]*>\d+</a>")
    if aResult[0] and aResult[1][0]:
        params.setParam('sUrl', aResult[1][0])
        oGui.addNextPage(SITE_IDENTIFIER, function, params)

def showHosters():
    sHtmlContent = cRequestHandler(ParameterHandler().getValue('entryUrl')).request()
    aResult = cParser().parse(sHtmlContent, "<p><iframe[^>]src=['\"]([^'\"]*)['\"][^>]*>")
    results = []
    if aResult[0]: 
        result = {}
        result['streamUrl'] = aResult[1][0]
        result['resolved'] = False
        results.append(result)
    return results

def showSearch():
    oGui = cGui()
    sSearchText = oGui.showKeyBoard()
    if not sSearchText: return
    _search(False, sSearchText)
    oGui.setEndOfDirectory()

def _search(oGui, sSearchText):
    if not sSearchText: return
    showEntries(URL_SEARCH % sSearchText.strip(), oGui)
