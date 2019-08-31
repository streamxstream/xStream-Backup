from resources.lib.gui.gui import cGui
from resources.lib.gui.guiElement import cGuiElement
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.parser import cParser
from resources.lib.handler.ParameterHandler import ParameterHandler

#Membervariables
SITE_IDENTIFIER = 'watchseries_ag'
SITE_NAME = 'Watch Series'
SITE_ICON = 'watchseries_ag.png'

URL_MAIN = 'http://watchseries.ag/'

#Mainmenu
def load():
oGui = cGui();

oGui.addFolder(cGuiElement('A-Z', SITE_IDENTIFIER, 'showAlphabet'))
oGui.addFolder(cGuiElement('Suche', SITE_IDENTIFIER, 'showSearch'))
oGui.setEndOfDirectory()
###Mainmenu

def showAlphabet():
    myList = ['09','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
    oGui = cGui()
    params = ParameterHandler()
    total = len(myList)

    for l in myList:
        #setze link als Parameter
        params.setParam('localUrl', 'letters/' + l)
        #setze title als Titel
        guiElement = cGuiElement(l, SITE_IDENTIFIER, 'showAlphabetical')
        oGui.addFolder(guiElement, params, iTotal = total)
    oGui.setEndOfDirectory()


#Show list of tvShows
def showAlphabetical():
    oGui = cGui()
    oParams = ParameterHandler() #Parameter laden
    strUrl = oParams.getValue('localUrl') #Url aus Parametern holen
    oRequestHandler = cRequestHandler(URL_MAIN + strUrl)
    sHtmlContent = oRequestHandler.request()

    pattern = '<li><a title="([^"]+)" href="([^"]+)"' #tvshow title,link to series

    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, pattern)
    if not aResult[0]:
        return

    total = len(aResult[1]) # Anzahl der Treffer
    for title, link in aResult[1]:
        #setze title als Titel
        guiElement = cGuiElement(title, SITE_IDENTIFIER, 'showSeries')
        guiElement.setMediaType('tvshow')
        oParams.setParam('localUrl', link)
        oParams.setParam('tvshow', ''+ title + '')
        oGui.addFolder(guiElement, oParams, iTotal = total)
    oGui.setEndOfDirectory()

#Show list of seasons
def showSeries():
    oGui = cGui()
    oParams = ParameterHandler() #Parameter laden
    strUrl = oParams.getValue('localUrl') #Url aus Parametern holen
    strTvShow = oParams.getValue('tvshow')
    oRequestHandler = cRequestHandler(URL_MAIN + strUrl)
    sHtmlContent = oRequestHandler.request()

    pattern = '<a class="null" href="([^"]+)">([^<]+)</a>' #tvshow title,link to series

    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, pattern)
    if not aResult[0]:
        guiElement = cGuiElement(strUrl, SITE_IDENTIFIER, 'dummy')  #debug
        oGui.addFolder(guiElement) #debug
        oGui.setEndOfDirectory() #debug
        return

    total = len(aResult[1]) # Anzahl der Treffer
    for link, title in aResult[1]:
        #setze title als Titel
        guiElement = cGuiElement(title, SITE_IDENTIFIER, 'showSeason')
        guiElement.setMediaType('season')
        oParams.setParam('localUrl', link)
        oParams.setParam('season', title)
        oParams.setParam('tvshow', strTvShow)
        oGui.addFolder(guiElement, oParams, iTotal = total)
    oGui.setEndOfDirectory()

    #Show list of episodes
def showSeason():
    oGui = cGui()
    oParams = ParameterHandler() #Parameter laden
    strUrl = oParams.getValue('localUrl') #Url aus Parametern holen
    strSeason = oParams.getValue('season')
    strTvShow = oParams.getValue('tvshow')
    oRequestHandler = cRequestHandler(URL_MAIN + strUrl)
    sHtmlContent = oRequestHandler.request()

    pattern = '<a class="watchEpisodeLink p1" title="([^"]+)" href="([^"]+)">' #tvshow_season_episode_title, link to episode

    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, pattern)
    if not aResult[0]:
        guiElement = cGuiElement(pattern, SITE_IDENTIFIER, 'dummy')  #debug
        oGui.addFolder(guiElement) #debug
        oGui.setEndOfDirectory() #debug
        return

    total = len(aResult[1]) # Anzahl der Treffer
    for tvshow_season_episode_title, link in aResult[1]:
        saEpisode = tvshow_season_episode_title.split(strSeason)
        sbEpisode = saEpisode[1].split(' - ')
        sEpisode = sbEpisode[1]
        sTitle = ""
        if len(sbEpisode)>2:
            if len(sbEpisode[2])>0:
                sTitle = sbEpisode[2]

        #setze episode und title als Titel
        if len(sTitle)>0:
            text = sEpisode+': '+sTitle
        else:
            text = sEpisode
        guiElement = cGuiElement(text, SITE_IDENTIFIER, 'showEpisodeLanguages')
        guiElement.setMediaType('episode')
        intSeason = strSeason.split(' ')
        if intSeason[1].isdigit():
            guiElement.setSeason(intSeason[1])
        intEpisode = sEpisode.split(' ')
        if intEpisode[1].isdigit():
            guiElement.setEpisode(intEpisode[1])
        guiElement.setTVShowTitle(strTvShow)
        oParams.setParam('localUrl', link)
        oGui.addFolder(guiElement, oParams, iTotal = total)
    oGui.setEndOfDirectory()

def showEpisodeLanguages():
    oGui = cGui()
    oParams = ParameterHandler()
    strUrl = oParams.getValue('localUrl')
    oRequestHandler = cRequestHandler(URL_MAIN + strUrl)
    sHtmlContent = oRequestHandler.request()

    pattern = '<h2 style="padding-top: 20px;" class="channel-title">([^<]+)<'

    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, pattern)

    if not aResult[0]:
        return

    total = len(aResult[1])
    tab_lang_nr = 1

    for language in aResult[1]:
        guiElement = cGuiElement(language.strip(), SITE_IDENTIFIER, 'getHosters')
        guiElement.setMediaType('episode')
        oParams.setParam('localUrl', strUrl)
        oParams.setParam('tabLangNr', tab_lang_nr)
        oGui.addFolder(guiElement, oParams, iTotal = total)
    oGui.setView('episodes') #diese Liste unterliegt den automatisch ViewSettings fuer Episoden
    oGui.setEndOfDirectory()

def getHosters():
    oParams = ParameterHandler()#Parameter laden
    strUrl = oParams.getValue('localUrl') #Urlteil
    strTabLangNr = oParams.getValue('tabLangNr') #Nummer des Quellcodeteils der gewaehlten Sprache

    oRequestHandler = cRequestHandler(URL_MAIN + strUrl)
    sHtmlContent = oRequestHandler.request()

    sHtmlContent = sHtmlContent.split('<h2 style="padding-top: 20px;" class="channel-title">') #splitte quellcode in die versch. Sprachen

    pattern = '<tr><td style="vertical-align: middle; line-height: 20px; "><span style="line-height:20px; vertical-align: middle;">([^<]+)</span></td><td > <a target="_blank" href="/([^"]+)"' #hostername, link
    
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent[int(strTabLangNr)], pattern)

    if not aResult[0]:
        return

    hosters = []            # hosterliste initialisieren
    sFunction='getHosterUrl'    # folgeFunktion festlegen 

    for hostername, localLink in aResult[1]:
        hoster = {}
        oRequestHandler = cRequestHandler(URL_MAIN + localLink)
        slocalLinkHtmlContent = oRequestHandler.request()
        streamPattern = '<a class="myButton.*href="([^"]+)"'
        streamResult = oParser.parse(slocalLinkHtmlContent, streamPattern)
        print streamResult[1][0]
        hoster['link'] = streamResult[1][0]
        hoster['name'] = hostername
        hoster['displayedName'] = hostername
        hosters.append(hoster)
    hosters.append('getHosterUrl')
    return hosters

def getHosterUrl(sUrl = False):
    results = []
    oParams = ParameterHandler()
    if not sUrl: sUrl = oParams.getValue('url')
    results = []
    result = {}
    result['streamUrl'] = sUrl
    result['resolved'] = False
    results.append(result)
    return results