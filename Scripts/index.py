import Constellation
from datetime import datetime
import time
import threading

# VARIABLES GLOBALES ET DEFINITIONS ####################################################################################

# Packets
MUSIC_PACKAGE   = "ConstellationSpotify"
DISPLAY_PACKAGE = "ConstellationAffichageLED"
ALARM_PACKAGE   = "AlarmClock"
SYSTEM_PACKAGE  = "ConstellationRPiSystem"

# Variables globales
global weatherForecastIO
global displays
global currentDisplay 
global twitterSO
global musicSO
global alarmName 
alarmName = None    

# FONCTIONS D'AFFICHAGE ################################################################################################

""" FONCTION displayHome
    ====================
    Permet d'afficher la page "HOME" du reveil correspondant à l'affichage de l'heure
    Se met à jour toutes les dix secondes avec un Thread
"""
def displayHome():
    # Si l'on se trouve sur l'écran du module, on update en live:
    if(displays[currentDisplay] == displayHome):
        Constellation.WriteWarn("DISPLAY HOME !")
        threading.Timer(10.0, displayHome).start()
        Constellation.SendMessage(DISPLAY_PACKAGE, "DisplayContent", {"icon":"horloge", "text":datetime.now().strftime('%H:%M'),"time":None,"matrix":None})

""" FONCTIONS displayWeather
    ========================
    Permet d'afficher la page "METEO" du reveil
"""
def displayWeather():
    Constellation.WriteWarn("DISPLAY FORECAST")
    Constellation.SendMessage(DISPLAY_PACKAGE, "DisplayContent", {"icon":"cloudy", "text":str(int(round(weatherForecastIO.temperature,0))) + 'C',"time":None,"matrix":None})

""" FONCTIONS displayTwitter
    ========================
    Permet d'afficher la page "TWITTER" du réveil
"""
def displayTwitter():
    Constellation.WriteWarn("DISPLAY TWITTER")
    Constellation.SendMessage(DISPLAY_PACKAGE, "DisplayContent", {"icon":"twitter_oiseau", "text":twitterSO.followers_count,"time":None,"matrix":None})
    
""" FONCTION displayMusic
    =====================
    Permet d'afficher la musique en cours de lecture

"""
def displayMusic():
    Constellation.WriteWarn("DISPLAY MUSIQUE")
    Constellation.SendMessage(DISPLAY_PACKAGE, "DisplayContent", {"icon":"musique", "text":"Musique !","time":None,"matrix":None})   


# VALEURS PAR DEFAUT DES VARIABLES GLOBALES ###########################################################################

displays = [displayHome, displayWeather, displayTwitter, displayMusic]
currentDisplay = 0

""" FONCTION snooze
    ===============
    Snooze alarm
"""
def snooze():
    global alarmName
    Constellation.SendMessage(ALARM_PACKAGE, "SnoozeAlarm", alarmName)
    Constellation.WriteInfo("Snooze de l'alarme %s" % alarmName)
    Constellation.SendMessage(MUSIC_PACKAGE, "MusicControl", {"instruction":"PLAY_PAUSE"})

# MESSAGE CALLBACK DES APPELS BOUTONS ##################################################################################

@Constellation.MessageCallback()
def ButtonAction(data):
    "Action et description d'un bouton poussoir branché sur un port GPIO du RPi poussé par packet ButtonRPi"
    Constellation.WriteInfo('Packet ReveilISEN / Callback ButtonAction ; pin = ' + str(data.pin) + ' / event = ' + str(data.event))
    global currentDisplay

    # POSITION BOUTONS
    # [13]_____[16][19][20]_____[26]
    BUTTON_FARLEFT  = 13
    BUTTON_LEFT     = 16
    BUTTON_HOME     = 19
    BUTTON_RIGHT    = 20
    BUTTON_FARRIGHT = 26

    # Clics simples
    if data.event == "clicked":
        if data.pin == BUTTON_FARLEFT:      # Interface précédente
            currentDisplay = previousDisplay(currentDisplay)
            toDisplay(currentDisplay)
        if data.pin == BUTTON_LEFT:         # Volume moins
            Constellation.SendMessage(MUSIC_PACKAGE, "MusicControl", {"instruction":"TURNDOWN_VOLUME"})
        if data.pin == BUTTON_HOME:         # Lecture / pause
            Constellation.SendMessage(MUSIC_PACKAGE, "MusicControl", {"instruction":"PLAY_PAUSE"})
            Constellation.SendMessage(ALARM_PACKAGE, "StopRinging", alarmName)
            Constellation.WriteInfo("Stop la dernière alarme '%s' " % alarmName)
        if data.pin == BUTTON_RIGHT:        # Volume plus
            Constellation.SendMessage(MUSIC_PACKAGE, "MusicControl", {"instruction":"TURNUP_VOLUME"})
        if data.pin == BUTTON_FARRIGHT:     # Interface suivante
            currentDisplay = nextDisplay(currentDisplay)
            toDisplay(currentDisplay)
    # Clics doubles
    elif data.event == "doubleclicked":
        if data.pin == BUTTON_FARLEFT:      # Interface précédente
            currentDisplay = previousDisplay(currentDisplay)
            toDisplay(currentDisplay)
        if data.pin == BUTTON_LEFT:         # Volume moins
            Constellation.SendMessage(MUSIC_PACKAGE, "MusicControl", {"instruction":"TURNDOWN_VOLUME"})
        if data.pin == BUTTON_HOME:         # Lecture / pause
            Constellation.SendMessage(MUSIC_PACKAGE, "MusicControl", {"instruction":"PLAY_PAUSE"})
            Constellation.SendMessage(ALARM_PACKAGE, "StopRinging", alarmName)
            Constellation.WriteInfo("Stop la dernière alarme '%s' " % alarmName)
        if data.pin == BUTTON_RIGHT:        # Volume plus
            Constellation.SendMessage(MUSIC_PACKAGE, "MusicControl", {"instruction":"TURNUP_VOLUME"})
        if data.pin == BUTTON_FARRIGHT:     # Interface suivante
            currentDisplay = nextDisplay(currentDisplay)
            toDisplay(currentDisplay)
    # Clics longs 
    elif data.event == "longpressed":
        if data.pin == BUTTON_FARLEFT:      # Snooze
            snooze()
        if data.pin == BUTTON_LEFT:         # Titre précédent
            Constellation.SendMessage(MUSIC_PACKAGE, "MusicControl", {"instruction":"PREVIOUS_SONG"})
        if data.pin == BUTTON_HOME:         # Home
            currentDisplay = 0
            toDisplay(currentDisplay)
        if data.pin == BUTTON_RIGHT:        # Titre suivant
            Constellation.SendMessage(MUSIC_PACKAGE, "MusicControl", {"instruction":"NEXT_SONG"})
        if data.pin == BUTTON_FARRIGHT:     # Snooze
            snooze()

# UPDATE DES STATESOBJECTS #############################################################################################

""" FONCTION WeatherUpdated
    =======================
    Récupère le stateObject de ForecastIO pour la météo, met à jour la variable globale weatherForecastIO
"""
@Constellation.StateObjectLink(package = "ForecastIO", name = "Lille")
def WeatherUpdated(stateobject):
    global weatherForecastIO
    weatherForecastIO = stateobject.Value.currently

    # Si l'on se trouve sur l'écran du module, on update en live:
    if(displays[currentDisplay] == displayWeather):
        toDisplay(currentDisplay)
    
    Constellation.WriteInfo("Affichage température %s : %f°C (icone : %s)" % (stateobject.Name, stateobject.Value.currently.temperature, stateobject.Value.currently.icon))
 
""" FONCTION Twitter
    =======================
    Récupère le stateObject de ForecastIO pour la météo, met à jour la variable globale weatherForecastIO
"""
@Constellation.StateObjectLink(package = "Twitter", name = "ShiningParadox")
def TwitterUpdated(stateobject):
    global twitterSO
    twitterSO   = stateobject.Value
    
    # Si l'on se trouve sur l'écran du module, on update en live:
    if(displays[currentDisplay] == displayTwitter):
        toDisplay(currentDisplay)

    Constellation.WriteInfo("Affichage de Twitter @%s : %i" % (stateobject.Name, stateobject.Value.followers_count))

""" FONCTION Musique
    =======================
    Récupère le stateObject de ForecastIO pour la météo, met à jour la variable globale weatherForecastIO
"""
@Constellation.StateObjectLink(package = "ConstellationSpotify", name = "track_Title")
def MusicUpdated(stateobject):
    global musicSO
    musicSO   = stateobject.Value
    
    # Si l'on se trouve sur l'écran du module, on update en live:
    if(displays[currentDisplay] == displayMusic):
        toDisplay(currentDisplay)

    Constellation.WriteInfo("Affichage du titre de la musique %s" % (stateobject.Value))

# STATEBOJECT DU REVEIL ################################################################################################

""" FONCTION Alarme
    =======================
    Récupère le stateObject de ForecastIO pour la météo, met à jour la variable globale weatherForecastIO
"""
@Constellation.StateObjectLink(package = "AlarmClock", name = "*")
def ClockUpdated(stateobject):
    global alarmName
    
    Constellation.WriteInfo("Check reveil %s" % stateobject.Name)
    if stateobject.Value.IsRinging == True:
        Constellation.WriteWarn("REVEIL '%s' en action !" % stateobject.Name)
        Constellation.SendMessage(MUSIC_PACKAGE, "MusicControl", {"instruction":"PLAY_PLAYLIST", "uri":"spotify:user:officiallifeisstrange:playlist:1f5ZzLDTXHTDR8CYIEddpW"})
        #time.sleep(10)
        #Constellation.SendMessage(MUSIC_PACKAGE, "MusicControl", {"instruction":"PLAY_PAUSE"})
        Constellation.SendMessage(DISPLAY_PACKAGE, "DisplayContent", {"icon":"musique", "text":stateobject.Name,"time":None,"matrix":None})
        alarmName = stateobject.Value.ClockName

# FONCTIONS DE CHANGEMENT D'INTERFACE ##################################################################################
 
""" FONCTIONS

"""
def nextDisplay(currentDisplay):
    if currentDisplay >= len(displays)-1:
        next = 0
        Constellation.WriteInfo("Next display (1) : " + str(next))
        return 0
    else:
        next = currentDisplay + 1
        Constellation.WriteInfo("Next display (2) : " + str(next))
        return currentDisplay + 1
        
def previousDisplay(currentDisplay):
    if currentDisplay <= 0:
        next = currentDisplay + 1
        Constellation.WriteInfo("Next display (3) : " + str(next))
        return len(displays) - 1
    else:
        next = currentDisplay + 1
        Constellation.WriteInfo("Next display (4) : " + str(next))
        return currentDisplay - 1
    
def toDisplay(toDisplay):
    displays[toDisplay]()

# FONCTIONS PAR DEFAUT #################################################################################################

def OnStart():

    Constellation.WriteInfo("Démarrage du packet Reveil ISEN...")

    toDisplay(currentDisplay)
    
    pass

Constellation.Start(OnStart);