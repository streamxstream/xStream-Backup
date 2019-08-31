# -*- coding: utf-8 -*-
from resources.lib.gui.gui import cGui
from resources.lib.gui.guiElement import cGuiElement
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.parser import cParser
from resources.lib import logger
from resources.lib.handler.ParameterHandler import ParameterHandler
from resources.lib.util import cUtil
import re

SITE_IDENTIFIER = 'diefilme_net'
SITE_NAME = 'Die Filme'
SITE_ICON = 'diefilme_net.png'

URL_MAIN = 'http://diefilme.net'
URL_SEARCH =  URL_MAIN + '/search?q=%s' 

QUALITY_ENUM = {'CAM':0, 'TS':1, 'TV':2, 'DVD':3, 'HD':4, '3D':4}

def load():
    logger.info("Load %s" % SITE_NAME)

    params = ParameterHandler()
    oGui = cGui()

    sHtmlContent = cRequestHandler(URL_MAIN).request()
    pattern = '<li[^>]*><a[^>]*href="([^"]*)"[^>]*>(.*?)</a></li>' # url / title
    aResult = cParser().parse(sHtmlContent, pattern)

    for sUrl, sTitle in aResult[1]:
        params.setParam('sUrl', URL_MAIN + sUrl)
        oGui.addFolder(cGuiElement(sTitle.strip(), SITE_IDENTIFIER, 'showContentMenu'), params)

    oGui.addFolder(cGuiElement('Suche', SITE_IDENTIFIER, 'showSearch'))
    oGui.setEndOfDirectory()

def showContentMenu():
    oGui = cGui()
    params = ParameterHandler()

    sHtmlContent = cRequestHandler(params.getValue('sUrl')).request()
    pattern = '<li[^>]*role="presentation"[^>]*>\s+<a[^>]*href="([^"]*)"[^>]*>([^"]*)</a>\s+</li>' # url / title
    aResult = cParser().parse(sHtmlContent, pattern)

    if not aResult[0]:
        return

    for sUrl, sTitle in aResult[1]:
        params.setParam('sUrl', URL_MAIN + sUrl)
        oGui.addFolder(cGuiElement(sTitle.strip(), SITE_IDENTIFIER, 'showEntries'), params)

    oGui.setEndOfDirectory()

def showEntries(entryUrl = False, sGui = False):
    oGui = sGui if sGui else cGui()
    params = ParameterHandler()
    parser = cParser()

    if not entryUrl: entryUrl = params.getValue('sUrl')

    sHtmlContent = cRequestHandler(entryUrl, ignoreErrors = (sGui is not False)).request()
    pattern = "<div[^>]id=['\"]\w+-\d+['\"].*?" # entry-typ
    pattern += '(?:<div[^>]*class="movieTV"[^>]*>([^"]*)</div>.*?)?' # season / episodes
    pattern += '<img[^>]*src="([^"]*)"[^>]*>.*?' # Thumbnail
    pattern += '<h\d[^>]*><a[^>]*href="([^"]*)"[^>]*>(.*?)</a>.*?' # url / title
    aResult = parser.parse(sHtmlContent, pattern)

    if not aResult[0] or not aResult[1][0]: 
        if not sGui: oGui.showInfo('xStream','Es wurde kein Eintrag gefunden')
        return

    total = len (aResult[1])
    for sEpisodeStr, sThumbnail, sUrl, sName in aResult[1]:       
        isMovie = True if not sEpisodeStr else False
        oGuiElement = cGuiElement()
        oGuiElement.setSiteName(SITE_IDENTIFIER)
        oGuiElement.setFunction('showHosters' if isMovie else 'showSeasons')
        oGuiElement.setTitle(cUtil().unescape(sName.decode('utf-8')).encode('utf-8'))
        oGuiElement.setMediaType('movie' if isMovie else 'tvshow')
        oGuiElement.setThumbnail(sThumbnail)
        if not isMovie: 
            oGuiElement.setTVShowTitle(sName)
        oOutParms = ParameterHandler()
        oOutParms.setParam('sThumbnail', sThumbnail)
        oOutParms.setParam('entryUrl', URL_MAIN + sUrl)
        oGui.addFolder(oGuiElement, oOutParms, (not isMovie), total)

    aResult = parser.parse(sHtmlContent, "<span[^>]class=['\"]currentStep['\"].*?<a[^>]*href=['\"]([^'\"]*)['\"][^>]*>\d+</a>")
    if aResult[0] and aResult[1][0]:
        params.setParam('sUrl', URL_MAIN + aResult[1][0])
        oGui.addNextPage(SITE_IDENTIFIER, 'showEntries', params)

    if not sGui:
        oGui.setView('tvshows' if 'serien' in entryUrl else 'movies')
        oGui.setEndOfDirectory()

def showSeasons():
    oGui = cGui()
    params = ParameterHandler()
    
    entryUrl = params.getValue('entryUrl')
    sTVShowTitle = params.getValue('TVShowTitle')
    sThumbnail = params.getValue('sThumbnail')

    sHtmlContent = cRequestHandler(entryUrl).request()
    pattern = '<a[^>]*href="#tabs-(\d+)"[^>]*>'
    aResult = cParser().parse(sHtmlContent, pattern)

    total = len (aResult)
    for sSeason in aResult[1]:
        oGuiElement = cGuiElement(sTVShowTitle + " - Staffel " + sSeason, SITE_IDENTIFIER, 'showEpisodes')
        oGuiElement.setMediaType('season')
        oGuiElement.setTVShowTitle(sTVShowTitle)
        oGuiElement.setSeason(sSeason)
        oGuiElement.setThumbnail(sThumbnail)
        oGui.addFolder(oGuiElement, params, True, total)

    oGui.setView('seasons')
    oGui.setEndOfDirectory()

def showEpisodes():
    oGui = cGui()
    params = ParameterHandler()

    entryUrl = params.getValue('entryUrl')
    sTVShowTitle = params.getValue('TVShowTitle')
    sThumbnail = params.getValue('sThumbnail')
    sSeason = params.getValue('season')

    sHtmlContent = cRequestHandler(entryUrl).request()
    pattern = '<h\d+>[^"]*Staffel %s Episode (\d+)[^"]*</h\d+>' % sSeason
    aResult = cParser().parse(sHtmlContent, pattern)

    total = len (aResult)
    for sEpisode in sorted(aResult[1], key=lambda k: k) :
        oGuiElement = cGuiElement(sTVShowTitle + " - Folge " + sEpisode, SITE_IDENTIFIER, 'showHosters')
        oGuiElement.setMediaType('episode')
        oGuiElement.setTVShowTitle(sTVShowTitle)
        oGuiElement.setSeason(sSeason)
        oGuiElement.setEpisode(sEpisode)
        oGuiElement.setThumbnail(sThumbnail)
        oGui.addFolder(oGuiElement, params, False, total)

    oGui.setView('episodes')
    oGui.setEndOfDirectory()

def showHosters():
    params = ParameterHandler()
    parser = cParser()

    sSeason = params.getValue('season')
    sEpisode = params.getValue('episode')

    sHtmlContent = cRequestHandler(params.getValue('entryUrl')).request()

    if sSeason and sEpisode: # cut of the html for the extact episode
        pattern = '<div[^>]*id="season%s"[^>]*>(.*?)\s(?:\s+</div>){4}' % sSeason 
        aResult = parser.parse(sHtmlContent, pattern)
        if aResult[0] and aResult[1][0]:
            pattern = '<h\d+>[^"]*Staffel %s Episode %s[^"]*</h\d+>(.*?)/>(?:\s+</div>){3}' % (sSeason, sEpisode) 
            aResult = parser.parse(aResult[1][0], pattern)
            if aResult[0] and aResult[1][0]:
                sHtmlContent = aResult[1][0]
            else:
                return False
        else:
                return False

    pattern = '(?:<div[^>]*class="linkQuality[^>]*"[^>]*>([^"<]*)</div>.*?)' # quality
    pattern += '(?:<div[^>]*class="linkAdded"[^>]*>.*?;([^"]*)</div>.*?)' # add by
    pattern += '<div[^>]*class="[^"]*linkHiddenUrl[^"]*"[^>]*>([^"]*)</div>\s+' # url
    pattern += '<div[^>]*class="[^"]*linkHiddenContact[^"]*"[^"]*><a[^>]*href="[^"]*"[^>]*>([^"]*)</a></div>' # hostername
    aResult = parser.parse(sHtmlContent, pattern)

    if not aResult[0] or not aResult[1][0]: 
        return False

    hosters = []
    for sQuality, sDate, sUrl, sName in aResult[1]:
        hoster = dict()
        if sDate:
            hoster['displayedName'] = '%s - %s - Quality: %s' % (sDate.strip(), sName, sQuality)
        if sQuality.upper() in QUALITY_ENUM:
            hoster['quality'] = QUALITY_ENUM[sQuality.upper()]
        hoster['link'] = sUrl
        hoster['name'] = sName
        hosters.append(hoster)

    if hosters:
        hosters.append('play')
    return hosters

def play(sUrl = False):
    if not sUrl: sUrl = oParams.getValue('url')
    results = []
    result = {}
    result['streamUrl'] = sUrl
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
