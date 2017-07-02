# Constellation-Réveil-ISEN
Ce package pour Constellation est l'intelligence du réveil et permet de faire fonctionner ensemble tous les autres packages du réveil. C'est lui qu'il faut éditer pour rajouter des interfaces et des fonctionnalités au reveil.

## Installation
Le package ne demande aucune bibliothèque python particulière mais a cependant besoin de tous les autres packages tel que décrit dans le [fichier suivant](https://github.com/CeriseGoutPelican/Reveil-ISEN/blob/master/README.md) : 

 - Réveil ISEN (CERVEAU) : [voir le Github](https://github.com/CeriseGoutPelican/Constellation-Reveil-ISEN)
 - Serveur Spotify : [voir le Github](https://github.com/nicolasroi/Constellation-Spotify)
 - Package Twitter pour Constellation : [voir le Github](https://github.com/CeriseGoutPelican/Package-Twitter-pour-Constellation)
 - Package bouton GPIO pour Raspberry Pi pour Constellation : [voir le Github](https://github.com/CeriseGoutPelican/Package-boutons-GPIO-pour-Constellation)
 - Package affichage RGB LED (8x32) pour Constellation : [voir le Github](https://github.com/CeriseGoutPelican/Package-Affichage-LED-pour-Constellation)
 - Package Alarme pour Constellation : [voir le Github](https://github.com/MrOwlTA2/AlarmClock-Constellation)
 - Package Forecast IO pour Constellation : [voir le Github](https://github.com/myconstellation/constellation-packages/tree/master/ForecastIO)
 
 ## Utilisation : ajout d'une interface
L'ajout d'une interface doit, pour le moment, passer par l'édition du package REVEIL ISEN. Habituellement l'ajout d'une nouvelle interface se fait en trois étapes :
1. Créer une nouvelle fonction pour l'affichage : `displayMonInterface()` contenant les informations requise :
```python
def display():
    Constellation.SendMessage(DISPLAY_PACKAGE, "DisplayContent", {"icon":"monIcone", "text":"monTexte","time":None,"matrix":None}) 
```
2. Ajouter la fonction à la liste des affichages à l'emplacement souhaité :
```python
displays = [displayHome, displayWeather, displayTwitter, displayMusic, displayMonInterface]
```
3. Enfin il faut mettre à jour votre affichage en écoutant par exemple un `stateObject`:
```python
@Constellation.StateObjectLink(package = "monPackage", name = "monSOName")
def monPackageUpdated(stateobject):
    # Mise à jour de la variable globale contenant votre contenu
    global monPackageSO
    monPackageSO = stateobject.Value
    
    # Update en live si l'interface est correcte :
    if(displays[currentDisplay] == displayMonInterface):
        toDisplay(currentDisplay)
