# -*- coding: utf-8 -*-
from resources.lib import logger
from resources.lib.gui.gui import cGui
from resources.lib.gui.guiElement import cGuiElement
from resources.lib.handler.ParameterHandler import ParameterHandler
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.parser import cParser
from resources.lib.util import cUtil

SITE_IDENTIFIER = 'view4u_co'
SITE_NAME = 'View4U'
SITE_ICON = 'view4u.png'

URL_MAIN = 'http://view4u.co'
URL_Kinofilme = URL_MAIN + '/load/25'
URL_FILME_HD = URL_MAIN + '/load/32'
URL_BELIEBT = URL_MAIN + '/index/beliebte_filme/0-10'
URL_SEARCH = URL_MAIN + '/search/?q=%s'


def load():
    logger.info("Load %s" % SITE_NAME)
    oGui = cGui()
    params = ParameterHandler()
    params.setParam('sUrl', URL_MAIN)
    oGui.addFolder(cGuiElement('Letzte Updates', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', URL_Kinofilme)
    oGui.addFolder(cGuiElement('Kinofilme', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', URL_BELIEBT)
    oGui.addFolder(cGuiElement('Beliebte Filme ', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', URL_FILME_HD)
    oGui.addFolder(cGuiElement('Filme in HD', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', URL_Kinofilme)
    oGui.addFolder(cGuiElement('Genre', SITE_IDENTIFIER, 'showGenre'))
    oGui.addFolder(cGuiElement('Suche', SITE_IDENTIFIER, 'showSearch'))
    oGui.setEndOfDirectory()


def showGenre():
    oGui = cGui()
    params = ParameterHandler()
    sHtmlContent = cRequestHandler(URL_Kinofilme).request()
    pattern = '<ul[^>]*class="vert_nav">.*?</a></li>[^>]*</ul>'
    isMatch, sContainer = cParser.parseSingleResult(sHtmlContent, pattern)

    if isMatch:
        pattern = '<a[^>]*href="([^"]+)"[^>]*>([^<]*)</a>'
        isMatch, aResult = cParser.parse(sContainer, pattern)

    if not isMatch:
        oGui.showInfo('xStream', 'Es wurde kein Eintrag gefunden')
        return

    for sUrl, sName in aResult:
        params.setParam('sUrl', URL_MAIN + sUrl)
        oGui.addFolder(cGuiElement(sName, SITE_IDENTIFIER, 'showEntries'), params)
    oGui.setEndOfDirectory()


def showEntries(entryUrl=False, sGui=False, sSearchText=False):
    oGui = sGui if sGui else cGui()
    params = ParameterHandler()
    if not entryUrl: entryUrl = params.getValue('sUrl')
    sHtmlContent = cRequestHandler(entryUrl, ignoreErrors=(sGui is not False)).request()
    pattern = 'poster.*?<img src="([^"]+).*?href="([^"]+)">([^"]+)</a>.*?body">(.*?)div.*?bottom">([^<]+)'
    isMatch, aResult = cParser.parse(sHtmlContent, pattern)

    if not isMatch:
        if not sGui: oGui.showInfo('xStream', 'Es wurde kein Eintrag gefunden')
        return

    total = len(aResult)
    for sThumbnail, sUrl, sName, sDummy, sDesc in aResult:
        if sSearchText and not cParser().search(sSearchText, cUtil.cleanse_text(sName)):
            continue
        oGuiElement = cGuiElement(sName, SITE_IDENTIFIER, 'showHosters')
        oGuiElement.setThumbnail(URL_MAIN + sThumbnail)
        oGuiElement.setFanart(URL_MAIN + sThumbnail)
        oGuiElement.setDescription(sDesc)
        isYear, sYear = cParser.parse(sDummy, '>([\d]+)<')
        if isYear:
            oGuiElement.setYear(sYear[0])
        oGuiElement.setMediaType('movie')
        if sUrl.startswith('http'):
            params.setParam('entryUrl', sUrl)
        else:
            params.setParam('entryUrl', URL_MAIN + sUrl)
        oGui.addFolder(oGuiElement, params, False, total)
    if not sGui:
        pattern = 'class="swchItemA1"[^>]*>.*?</b>\s*<a[^>]*href="([^"]+)"'
        isMatchNextPage, sNextUrl = cParser.parseSingleResult(sHtmlContent, pattern)
        if isMatchNextPage:
            params.setParam('sUrl', URL_MAIN + sNextUrl)
            oGui.addNextPage(SITE_IDENTIFIER, 'showEntries', params)
        oGui.setView('movies')
        oGui.setEndOfDirectory()


def showHosters():
    params = ParameterHandler()
    sUrl = params.getValue('entryUrl')
    sHtmlContent = cRequestHandler(sUrl).request()
    pattern = '>[^>]<img.*?href="([^"]+)'
    isMatch, aResult = cParser.parse(sHtmlContent, pattern)

    if not isMatch:
        return []

    hosters = []
    for sUrl in aResult:
        hoster = {}
        if not 'nurhd' in sUrl:
            isMatch, sName = cParser.parseSingleResult(sUrl, '^(?:https?:\/\/)?(?:[^@\n]+@)?([^:\/\n]+)')
            hoster = {'link': sUrl, 'name': sName}
            hosters.append(hoster)
    if hosters:
        hosters.append('getHosterUrl')
    return hosters


def getHosterUrl(sUrl=False):
    return [{'streamUrl': sUrl, 'resolved': False}]


def showSearch():
    oGui = cGui()
    sSearchText = oGui.showKeyBoard()
    if not sSearchText: return
    _search(False, sSearchText)
    oGui.setEndOfDirectory()


def _search(oGui, sSearchText):
    showEntries(URL_SEARCH % sSearchText, oGui, sSearchText)
