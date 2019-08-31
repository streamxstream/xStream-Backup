# -*- coding: utf-8 -*-
from resources.lib.gui.gui import cGui
from resources.lib.gui.guiElement import cGuiElement
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.parser import cParser
from resources.lib import logger
from resources.lib.handler.ParameterHandler import ParameterHandler
from resources.lib.config import cConfig
from resources.lib.util import cUtil
import threading

SITE_IDENTIFIER = 'movie2z_to'
SITE_NAME = 'Movie2z'
SITE_ICON = 'movie2z.png'

URL_MAIN = 'https://www.movie2z.to/de/'
URL_GENERIC_URL = URL_MAIN + '%s%s/%s'
URL_SEARCH = URL_MAIN + 'search.html'


def load():
    logger.info("Load %s" % SITE_NAME)
    oGui = cGui()
    params = ParameterHandler()
    params.setParam('sType', 'movies')
    oGui.addFolder(cGuiElement('Filme', SITE_IDENTIFIER, 'showContentMenu'), params)
    params.setParam('sType', 'series')
    oGui.addFolder(cGuiElement('Serien', SITE_IDENTIFIER, 'showContentMenu'), params)
    if showAdult():
        params.setParam('sType', 'xxx')
        oGui.addFolder(cGuiElement('XXX', SITE_IDENTIFIER, 'showContentMenu'), params)
    oGui.addFolder(cGuiElement('Suche', SITE_IDENTIFIER, 'showSearch'))
    oGui.setEndOfDirectory()


def showContentMenu():
    oGui = cGui()
    params = ParameterHandler()
    sType = params.getValue('sType')

    if sType == 'movies':
        params.setParam('sUrl', URL_GENERIC_URL % (sType, '-100newest', ''))
        oGui.addFolder(cGuiElement('100 Neusten', SITE_IDENTIFIER, 'showEntries'), params)

    params.setParam('sUrl', URL_GENERIC_URL % (sType, '', 'alle/'))
    oGui.addFolder(cGuiElement('Alle', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', URL_GENERIC_URL % (sType, '', ''))
    oGui.addFolder(cGuiElement('A-Z', SITE_IDENTIFIER, 'showCharacters'), params)
    params.setParam('sUrl', URL_GENERIC_URL % (sType, '-mostview', ''))
    oGui.addFolder(cGuiElement('Meistgesehen', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', URL_GENERIC_URL % (sType, '', ''))
    oGui.addFolder(cGuiElement('Genre', SITE_IDENTIFIER, 'showGenre'), params)
    oGui.setEndOfDirectory()


def showCharacters():
    oGui = cGui()
    params = ParameterHandler()
    sUrl = params.getValue('sUrl')

    sHtmlContent = cRequestHandler(sUrl).request()
    sPattern = '<div[^>]*class="mtop20[^"]+"[^>]*>(.*?)</div>'
    isMatch, sHtmlContainer = cParser.parseSingleResult(sHtmlContent, sPattern)

    if not isMatch:
        oGui.showInfo('xStream', 'Es wurde kein Eintrag gefunden')
        return

    pattern = '<a[^>]*href="([^"]+)"[^>]*>(.)</a>'
    isMatch, aResult = cParser.parse(sHtmlContainer, pattern)

    if not isMatch:
        oGui.showInfo('xStream', 'Es wurde kein Eintrag gefunden')
        return

    for sUrl, sName in aResult:
        params.setParam('sUrl', sUrl)
        oGui.addFolder(cGuiElement(sName, SITE_IDENTIFIER, 'showEntries'), params)
    oGui.setEndOfDirectory()


def showGenre():
    oGui = cGui()
    params = ParameterHandler()
    sUrl = params.getValue('sUrl')
    sHtmlContent = cRequestHandler(sUrl).request()
    sPattern = '<option value="([^"]+)">([^<]+)'
    isMatch, aResult = cParser.parse(sHtmlContent, sPattern)

    if not isMatch:
        oGui.showInfo('xStream', 'Es wurde kein Eintrag gefunden')
        return

    for sUrl, sName in aResult:
        params.setParam('sUrl', sUrl)
        oGui.addFolder(cGuiElement(sName, SITE_IDENTIFIER, 'showEntries'), params)
    oGui.setEndOfDirectory()


def _getPrefLanguage():
    sLanguage = cConfig().getSetting('prefLanguage')
    sLanguage = sLanguage if sLanguage != '' else '2'
    return sLanguage


def _setPrefLanguage(oRequest):
    sLanguage = _getPrefLanguage()
    oRequest.addParameters('movlang', '')

    if sLanguage == '0':
        oRequest.addParameters('movlang_de', '1')
    elif sLanguage == '1':
        oRequest.addParameters('movlang_en', '1')
    elif sLanguage == '2':
        sHtmlContent = cRequestHandler(URL_MAIN, ignoreErrors=True).request()
        sPattern = '<input[^>]*type="checkbox"[^>]*name="(movlang_\w+)"[^>]*>'
        isMatch, aResult = cParser.parse(sHtmlContent, sPattern)

        if not isMatch:
            return

        for sName in aResult:
            oRequest.addParameters(sName, '1')


def showEntries(entryUrl=False, sGui=False, sSearchText=None):
    oGui = sGui if sGui else cGui()
    params = ParameterHandler()
    if not entryUrl: entryUrl = params.getValue('sUrl')

    oRequest = cRequestHandler(entryUrl, ignoreErrors=(sGui is not False))
    _setPrefLanguage(oRequest)
    if sSearchText:
        oRequest.addParameters('searchword', sSearchText)
    oRequest.setRequestType(1)
    sHtmlContent = oRequest.request()

    sPattern = '<tr>.*?'  # container start
    sPattern += '<td><a[^>]*href="([^"]+)"[^>]*rel="([^"]+)"[^>]*>([^<]+)</a></td>.*?'  # url / thumbnail / Name
    sPattern += '(?:<td[^>]*>(\d+)[^<]+</td>.*?)?'  # duration
    sPattern += '(?:<td[^>]*>([\d|\.]+).*?)?'  # rating
    sPattern += '(?:<img[^>]*src="[^"]+flaggs[^"]+"[^>]*alt="(\w+)"[^>]*>.*?)?'  # language
    sPattern += '</tr>'  # container end
    isMatch, aResult = cParser.parse(sHtmlContent, sPattern)

    if not isMatch:
        sPattern = '<div[^>]*class="[^"]*mtop20[^"]*text-center[^"]*">'  # container start
        sPattern += '<a[^>]*href="([^"]+)"[^>]*>\s*<img[^>]*src="([^"]*)"[^>]*>\s*'  # url / thumbnail
        sPattern += '(?:<div[^>]*class="[^"]*flag_(\w+)[^"]*"></div>.*?)?'  # language
        sPattern += '<a[^>]*class="lnk-white bold"[^>]*>([^<]+)</a>'  # name
        isMatch, aResultPoster = cParser.parse(sHtmlContent, sPattern)

        aResult = []
        for sUrl, sThumbnail, sLang, sName in aResultPoster:
            aResult.append((sUrl, sThumbnail, sName, False, False, sLang))

    if not isMatch:
        if not sGui: oGui.showInfo('xStream', 'Es wurde kein Eintrag gefunden')
        return

    isShowAdult = showAdult()

    total = len(aResult)
    for sUrl, sThumbnail, sName, sDuration, sRating, sLang in aResult:
        isTvshow = True if "serie" in sUrl else False
        if not isShowAdult and '/xxx-details/' in sUrl.lower():
            continue
        try:
            sName = cUtil.unescape(sName.decode('utf-8')).encode('utf-8')
        except UnicodeDecodeError:
            pass
        if 'error_poster' in sThumbnail: sThumbnail = ''  # remove the ugly poster

        oGuiElement = cGuiElement(sName, SITE_IDENTIFIER, 'showSeasons' if isTvshow else 'showHosters')
        oGuiElement.setThumbnail(sThumbnail)
        oGuiElement.setMediaType('tvshow' if isTvshow else 'movie')
        oGuiElement.setLanguage(sLang)
        oGuiElement.addItemValue('rating', sRating)
        if sDuration:
            oGuiElement.addItemValue('duration', int(sDuration) * 60)
        params.setParam('entryUrl', sUrl)
        params.setParam('isTvshow', isTvshow)
        params.setParam('sThumbnail', sThumbnail)
        params.setParam('sName', sName)
        oGui.addFolder(oGuiElement, params, isTvshow, total)

    if not sGui:
        sPattern = "pagination\(.*items:\s*(\d+).*?"  # item-count
        sPattern += "itemsOnPage:\s*(\d+).*?"  # itemsOnPage
        sPattern += "currentPage:\s*(\d+).*?"  # currentPage
        sPattern += "hrefTextPrefix:\s*'([^']+)'.*?"  # hrefTextPrefix
        sPattern += "hrefTextSuffix:\s*'([^']+)'.*?"  # hrefTextSuffix
        isMatch, aResult = cParser.parse(sHtmlContent, sPattern)

        if isMatch:
            items = int(aResult[0][0])
            per_page = int(aResult[0][1])
            cur_page = int(aResult[0][2])
            max_page = int(round(float(float(items) / float(per_page))))  # ty python 2.x

            if cur_page < max_page:
                params.setParam('sUrl', aResult[0][3] + str(cur_page + 1) + aResult[0][4])
                oGui.addNextPage(SITE_IDENTIFIER, 'showEntries', params)

        oGui.setView('tvshows' if 'serie' in entryUrl else 'movies')
        oGui.setEndOfDirectory()


def showSeasons():
    oGui = cGui()
    params = ParameterHandler()
    entryUrl = params.getValue('entryUrl')
    sThumbnail = params.getValue('sThumbnail')
    sTVShowTitle = params.getValue('sName')

    sHtmlContent = cRequestHandler(entryUrl).request()
    sPattern = '<select[^>]*id="seasonselector"[^>]*>(.*?)</select>'
    isMatch, sHtmlContainer = cParser.parseSingleResult(sHtmlContent, sPattern)

    if not isMatch:
        oGui.showInfo('xStream', 'Es wurde kein Eintrag gefunden')
        return

    pattern = '<option[^>]*value="(\d+)"[^>]*>'
    isMatch, aResult = cParser.parse(sHtmlContainer, pattern)

    if not isMatch:
        oGui.showInfo('xStream', 'Es wurde kein Eintrag gefunden')
        return

    total = len(aResult)
    for sSeasonNr in aResult:
        if int(sSeasonNr) < 1:
            continue
        oGuiElement = cGuiElement('Staffel ' + sSeasonNr, SITE_IDENTIFIER, 'showEpisodes')
        oGuiElement.setMediaType('season')
        oGuiElement.setThumbnail(sThumbnail)
        oGuiElement.setSeason(sSeasonNr)
        oGuiElement.setTVShowTitle(sTVShowTitle)
        params.setParam('entryUrl', entryUrl + ('/' if not entryUrl.endswith('/') else '') + sSeasonNr + '/')
        params.setParam('sSeasonNr', sSeasonNr)
        oGui.addFolder(oGuiElement, params, True, total)

    oGui.setView('seasons')
    oGui.setEndOfDirectory()


def showEpisodes():
    oGui = cGui()
    params = ParameterHandler()
    entryUrl = params.getValue('entryUrl')
    sThumbnail = params.getValue('sThumbnail')
    sTVShowTitle = params.getValue('sName')
    sSeasonNr = params.getValue('sSeasonNr')

    sHtmlContent = cRequestHandler(entryUrl).request()
    sPattern = '<select[^>]*id="partselector"[^>]*>(.*?)</select>'
    isMatch, sHtmlContainer = cParser.parseSingleResult(sHtmlContent, sPattern)

    if not isMatch:
        oGui.showInfo('xStream', 'Es wurde kein Eintrag gefunden')
        return

    pattern = '<option[^>]*value="(\d+)"[^>]*>'
    isMatch, aResult = cParser.parse(sHtmlContainer, pattern)

    if not isMatch:
        oGui.showInfo('xStream', 'Es wurde kein Eintrag gefunden')
        return

    total = len(aResult)
    for sEpisodeNr in aResult:
        if int(sEpisodeNr) < 1:
            continue
        oGuiElement = cGuiElement('Folge ' + sEpisodeNr, SITE_IDENTIFIER, 'showHosters')
        oGuiElement.setTVShowTitle(sTVShowTitle)
        oGuiElement.setSeason(sSeasonNr)
        oGuiElement.setEpisode(sEpisodeNr)
        oGuiElement.setThumbnail(sThumbnail)
        oGuiElement.setMediaType('episode')
        params.setParam('entryUrl', entryUrl + ('/' if not entryUrl.endswith('/') else '') + sEpisodeNr + '/')
        oGui.addFolder(oGuiElement, params, False, total)
    oGui.setView('episodes')
    oGui.setEndOfDirectory()


def showHosters():
    params = ParameterHandler()
    sUrl = params.getValue('entryUrl')
    sHtmlContent = cRequestHandler(sUrl).request()
    sPattern = '<li><a[^>]*href="([^"]+)"[^>]*class="text-white">'
    isMatch, aResult = cParser.parse(sHtmlContent, sPattern)

    if not isMatch:
        return []

    hosters = []
    threads = []
    for sUrl in aResult:
        t = threading.Thread(target=_addHosterThread, args=(hosters, sUrl))
        threads += [t]
        t.start()

    for count, t in enumerate(threads):
        t.join()

    if hosters:
        hosters.append('getHosterUrl')
        return hosters

def _addHosterThread(hosters, sUrl):
    sHtmlContent = cRequestHandler(sUrl).request()
    sPattern = '<select[^>]*id="selecthost"[^>]*>(.*?)</select>'
    isMatch, sHtmlContainer = cParser.parseSingleResult(sHtmlContent, sPattern)

    if not isMatch:
        return

    sPattern = '<option[^>]*value="([^"]+)">([^\d]+)(\d+)[^>]*(?:(\d+))?</option>'
    isMatch, aResult = cParser.parse(sHtmlContainer, sPattern)

    if not isMatch:
        return

    for sUrl, sHoster, sMirror, sQualy in aResult:
        sHoster = sHoster.strip()
        hoster = {}
        hoster['name'] = sHoster
        hoster['link'] = cUtil.unescape(sUrl)
        hoster['displayedName'] = sHoster + ' #' + sMirror
        if sQualy:
            hoster['displayedName'] = hoster['displayedName'] + ' - Quality: ' + sQualy
            hoster['quality'] = sQualy
        hosters.append(hoster)


def getHosterUrl(sUrl=False):
    if not sUrl: sUrl = ParameterHandler().getValue('sUrl')

    refUrl = ParameterHandler().getValue('entryUrl')
    oRequest = cRequestHandler(sUrl, caching=False)
    oRequest.addHeaderEntry("Referer", refUrl)
    oRequest.request()

    return {'streamUrl': oRequest.getRealUrl(), 'resolved': False}


def showAdult():
    oConfig = cConfig()
    if oConfig.getSetting('showAdult') == 'true':
        return True
    return False


def showSearch():
    oGui = cGui()
    sSearchText = oGui.showKeyBoard()
    if not sSearchText: return
    _search(False, sSearchText)
    oGui.setEndOfDirectory()


def _search(oGui, sSearchText):
    if not sSearchText: return
    showEntries(URL_SEARCH, oGui, sSearchText)
