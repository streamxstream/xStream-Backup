# -*- coding: utf-8 -*-
from resources.lib import logger
from resources.lib.gui.gui import cGui
from resources.lib.gui.guiElement import cGuiElement
from resources.lib.handler.ParameterHandler import ParameterHandler
from resources.lib.handler.requestHandler2 import cRequestHandler
from resources.lib.parser import cParser

SITE_IDENTIFIER = 'topstreamfilm'
SITE_NAME = 'Topstreamfilm'
SITE_ICON = 'topstreamfilm.png'

URL_MAIN = 'https://topstreamfilm.com/'
URL_MOVIES = URL_MAIN + 'filme'
URL_SHOWS = URL_MAIN + 'serien'
URL_SEARCH = URL_MAIN + '?s=%s'


def load():
    logger.info("Load %s" % SITE_NAME)
    oGui = cGui()
    params = ParameterHandler()
    params.setParam('sUrl', URL_MOVIES)
    oGui.addFolder(cGuiElement('Filme', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', URL_SHOWS)
    oGui.addFolder(cGuiElement('Serien', SITE_IDENTIFIER, 'showEntries'), params)
    oGui.addFolder(cGuiElement('Genre', SITE_IDENTIFIER, 'showGenre'), params)
    oGui.addFolder(cGuiElement('Suche', SITE_IDENTIFIER, 'showSearch'))
    oGui.setEndOfDirectory()


def showGenre():
    oGui = cGui()
    params = ParameterHandler()
    sHtmlContent = cRequestHandler(URL_MAIN).request()
    pattern = 'Kategorien.*?</aside>'
    isMatch, sContainer = cParser.parseSingleResult(sHtmlContent, pattern)
    if  isMatch:
        pattern = 'href="([^"]+).*?>([^<]+)'
        isMatch, aResult = cParser.parse(sContainer, pattern)
    if not isMatch:
        oGui.showInfo('xStream', 'Es wurde kein Eintrag gefunden')
        return

    for sUrl, sName in aResult:
        params.setParam('sUrl', sUrl)
        oGui.addFolder(cGuiElement(sName, SITE_IDENTIFIER, 'showEntries'), params)
    oGui.setEndOfDirectory()


def showEntries(entryUrl=False, sGui=False, sSearchText=False):
    oGui = sGui if sGui else cGui()
    params = ParameterHandler()
    if not entryUrl: entryUrl = params.getValue('sUrl')
    oRequest = cRequestHandler(entryUrl)
    sHtmlContent = oRequest.request()
    pattern = 'TPost C">.*?href="([^"]+).*?img[^>]src="([^"]+)(.*?)Title">([^<]+)(.*?)Description">([^"]+)</p>'
    isMatch, aResult = cParser().parse(sHtmlContent, pattern)

    if not isMatch:
        if not sGui: oGui.showInfo('xStream', 'Es wurde kein Eintrag gefunden')
        return

    cf = cRequestHandler.createUrl(entryUrl, oRequest)
    total = len(aResult)
    for sUrl, sThumbnail, sType, sName, sDummy, sDesc in aResult:
        isDuration, sDuration = cParser.parseSingleResult(sDummy, 'time">([\d(h) \d]+)')
        isYear, sYear = cParser.parseSingleResult(sDummy, 'date_range">([\d]+)')
        sThumbnail = 'https:' + sThumbnail + cf
        if sSearchText and not cParser().search(sSearchText, sName):
            continue
        isTvshow = True if 'Season' in sType or 'TV' in sType else False
        oGuiElement = cGuiElement(sName, SITE_IDENTIFIER, 'showSeasons' if isTvshow else 'showHosters')
        oGuiElement.setThumbnail(sThumbnail)
        oGuiElement.setFanart(sThumbnail)
        oGuiElement.setMediaType('tvshow' if isTvshow else 'movie')
        if isDuration:
            sDuration = sDuration.replace('h ', '')
            oGuiElement.addItemValue('duration', int(sDuration) - 40)
        if isYear:
            oGuiElement.setYear(sYear)
        oGuiElement.setDescription(sDesc)
        params.setParam('entryUrl', sUrl)
        params.setParam('sThumbnail', sThumbnail)
        oGui.addFolder(oGuiElement, params, isTvshow, total)
    if not sGui:
        pattern = 'next page-numbers" href="([^"]+)'
        isMatchNextPage, sNextUrl = cParser.parseSingleResult(sHtmlContent, pattern)
        if isMatchNextPage:
            params.setParam('sUrl', sNextUrl)
            oGui.addNextPage(SITE_IDENTIFIER, 'showEntries', params)
        oGui.setView('tvshow' if 'Season' in sType or 'TV' in sType else 'movie')
        oGui.setEndOfDirectory()


def showSeasons():
    oGui = cGui()
    params = ParameterHandler()
    entryUrl = params.getValue('entryUrl')
    sHtmlContent = cRequestHandler(entryUrl).request()
    isMatch, aResult = cParser.parse(sHtmlContent, 'Season <span>([\d]+)')

    if not isMatch:
        oGui.showInfo('xStream', 'Es wurde kein Eintrag gefunden')
        return

    isDesc, sDesc = cParser.parseSingleResult(sHtmlContent, 'class="Description">(.*?)</p>')
    total = len(aResult)
    for sSeason, in aResult:
        oGuiElement = cGuiElement('Staffel ' + sSeason, SITE_IDENTIFIER, 'showEpisodes')
        oGuiElement.setMediaType('season')
        oGuiElement.setSeason(sSeason)
        oGuiElement.setThumbnail(params.getValue('sThumbnail'))
        oGuiElement.setFanart(params.getValue('sThumbnail'))
        if isDesc:
            oGuiElement.setDescription(sDesc)
        params.setParam('Season', sSeason)
        oGui.addFolder(oGuiElement, params, True, total)
    oGui.setView('seasons')
    oGui.setEndOfDirectory()


def showEpisodes():
    oGui = cGui()
    params = ParameterHandler()
    entryUrl = params.getValue('entryUrl')
    sSeason = params.getValue('Season')
    oRequest = cRequestHandler(entryUrl)
    sHtmlContent = oRequest.request()
    pattern = 'Season <span>%s.*?></tbody>' % sSeason
    isMatch, sContainer = cParser.parseSingleResult(sHtmlContent, pattern)
    if isMatch:
        pattern = 'Num">([\d]+).*?href="([^"]+)'
        isMatch, aResult = cParser.parse(sContainer, pattern)
    if not isMatch:
        oGui.showInfo('xStream', 'Es wurde kein Eintrag gefunden')
        return

    isDesc, sDesc = cParser.parseSingleResult(sHtmlContent, 'class="Description">(.*?)</p>')
    total = len(aResult)
    for sEpisode, sUrl in aResult:
        oGuiElement = cGuiElement('Folge ' + sEpisode, SITE_IDENTIFIER, 'showHosters')
        oGuiElement.setMediaType('season')
        oGuiElement.setSeason(sSeason)
        oGuiElement.setEpisode(sEpisode)
        oGuiElement.setMediaType('episode')
        oGuiElement.setThumbnail(params.getValue('sThumbnail'))
        if isDesc:
            oGuiElement.setDescription(sDesc)
        oGuiElement.setFanart(params.getValue('sThumbnail'))
        params.setParam('entryUrl', sUrl)
        oGui.addFolder(oGuiElement, params, False, total)
    oGui.setView('episodes')
    oGui.setEndOfDirectory()


def showHosters():
    hosters = []
    url = ParameterHandler().getValue('entryUrl')

    oRequest = cRequestHandler(url, ignoreErrors=False)
    sHtmlContent = oRequest.request()
    pattern = '" src="([^"]+)" f'
    isMatch, aResult = cParser().parse(sHtmlContent, pattern)

    oRequest = cRequestHandler(aResult[0], ignoreErrors=False)
    sHtmlContent = oRequest.request()

    pattern = '" src="([^"]+)" f'
    isMatch, aResult = cParser().parse(sHtmlContent, pattern)

    oRequest = cRequestHandler(aResult[0], caching=False)
    oRequest.addHeaderEntry('Referer', 'https://topstreamfilm.com/')
    oRequest.addHeaderEntry('X-Requested-With', 'XMLHttpRequest')
    oRequest.request()
    sUrl = oRequest.getRealUrl()

    oRequest = cRequestHandler(sUrl.replace('v', 'api/source'), ignoreErrors=False)
    oRequest.addHeaderEntry('Referer', sUrl)
    oRequest.addHeaderEntry('X-Requested-With', 'XMLHttpRequest')
    oRequest.addHeaderEntry('Host', 'feurl.com')
    oRequest.addHeaderEntry('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0')
    oRequest.addHeaderEntry('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8')
    oRequest.addHeaderEntry('Origin', 'https://feurl.com')
    oRequest.addHeaderEntry('Accept', '*/*')
    oRequest.addParameters('r', 'https://topstreamfilm.com/')
    oRequest.addParameters('d', 'feurl.com')
    oRequest.setRequestType(1)
    sHtmlContent = oRequest.request()

    pattern = 'file":"([^"]+)","label":"([^"]+)'
    isMatch, aResult = cParser().parse(sHtmlContent, pattern)

    if isMatch:
        for sUrl, sQ in aResult:
            hoster = {'link': sUrl, 'name': sQ}
            hosters.append(hoster)
    if hosters:
        hosters.append('getHosterUrl')
    return hosters


def getHosterUrl(sUrl=False):
    return [{'streamUrl': sUrl, 'resolved': True}]


def showSearch():
    oGui = cGui()
    sSearchText = oGui.showKeyBoard()
    if not sSearchText: return
    _search(False, sSearchText)
    oGui.setEndOfDirectory()


def _search(oGui, sSearchText):
    showEntries(URL_SEARCH % sSearchText, oGui, sSearchText)
