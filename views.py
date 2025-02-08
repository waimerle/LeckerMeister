# HTTP-Antwort mit gerendertem HTML ausgeben
from django.shortcuts import render
# Weiterleitung zu einer anderen URL 
from django.shortcuts import redirect
#HTTP-Antwort erstellen mit beliebigem Inhalt
from django.http import HttpResponse, JsonResponse
# Module 
import json, os, csv
# Zugriff auf die Konfiguration der Django-Anwendung
from django.conf import settings
# CSRF-Schutzprüfung für bestimmte Ansicht deaktivieren
from django.views.decorators.csrf import csrf_exempt
# Modul mit Funktionen für die Arbeit mit Zeitzonen
from django.utils import timezone
# Modul für Datums- und Zeitangaben
from datetime import datetime
# Untermodul für Arbeit mit Zeiträumen
from datetime import timedelta
# Standardwert für nicht vorhandene Schlüssel festlegen
from collections import defaultdict
# import der Zeiterfassung-Klasse
from .Download import Zeiterfassung
# Modul 
from lxml import etree

# Dateien
benutzerDatei = "/var/www/django-projekt/Zeitbuchungssystem/userDaten.json"
modulDatei = "/var/www/django-projekt/Zeitbuchungssystem/Module.json"
upgradeDatei = "/var/www/django-projekt/Zeitbuchungssystem/Upgrade.json"


# Anmeldeseite
def Anmeldung(request): # LEONIE
    # Benutzerdatei lesend öffnen und Daten in Variable benutzerListe speichern
    with open(benutzerDatei, "r", encoding="utf-8") as file:
        benutzerListe = json.load(file)
    
    # Variable fehlermeldung festlegen und zu Beginn auf None setzten --> Am Anfang existiert kein Fehler
    fehlermeldung = None

    # Prüfen, ob das Absenden des Formulars eine POST-Anfrage war => Daten sicher zum Server schicken
    if request.method == 'POST':
        # request.POST enthält alle Daten, die über die POST-Anfrage gesendet wurden 
        matrikelnummer = request.POST.get('matrikelnummer') # .get("matrikelnummer") sucht Wert aus der Eingabe mit dem Namen matrikelnummer 
        password = request.POST.get('passwort') # .get("passwort") sucht nach dem Wert, der in das Eingabefeld mit dem Namen "passwort" eingegeben wurde
        
        # Jedes Element in der benutzerListe (von JSON-Datei) durchlaufen
        for benutzer in benutzerListe:
            # Vergleicht Matrikelnummer des Benutzers mit der eingegebene Matrikelnummer 
            if benutzer['Matrikelnummer'] == matrikelnummer:
                # Prüft, ob das Passwort stimmt und der Benutzer aktiv (also nicht gesperrt) ist
                if benutzer['Passwort'] == password and benutzer['Benutzerzustand'] == 'aktiv':
                    # Matrikelnummer wird in der Session gespeichert, Server merkt sich, welcher Benutzer gerade angemeldet ist
                    request.session['benutzer_name'] = matrikelnummer
                    # aktueller Benutzerstatus (admin, VIP, einfacher Anwender) wird in der Session gespeichert
                    request.session['Benutzerstatus'] = benutzer['Benutzerstatus']
                    # Weiterleitung zur Startseite 
                    return redirect('Start')
                else:
                    # Wenn das Passwort nicht stimmt oder der Benutzer gesperrt wurde --> Fehlermeldung 
                    fehlermeldung = "Das eingegebene Passwort ist falsch oder der Benutzer wurde gesperrt."
            else:
                # Wenn Matrikelnummer nicht existiert 
                fehlermeldung = "Die eingegebene Matrikelnummer existiert nicht."

    # Benutzerdaten = falsch --> Login neu laden und übergibt die Fehlermeldung an die HTML-Seite
    return render(request, 'Zeitbuchungssystem/Anmeldeseite.html', {'fehlermeldung': fehlermeldung})


# Module
def Modul(request): # SOPHIE
    # gespeicherte Matrikelnummer aus der aktuellen Session abrufen
    matrikelnummer = request.session.get('benutzer_name')
    # wenn keine Matrikelnummer in der Session --> Weiterleitung zum Login
    if not matrikelnummer:
        return redirect("Anmeldung")

    # Benutzerstatus aus der aktuellen Session auslesen
    benutzer_status = request.session.get("Benutzerstatus")
    # Wenn Benutzer kein admin ist --> Start (nur admin darf auf diese Seite zugreifen)  
    if benutzer_status != 'admin':
        return redirect("Start")

    try:
        # Module-Datei lesend öffnen
        with open(modulDatei, "r", encoding='utf-8') as file:
            # Daten aus der Datei laden und in die Variable module speichern
            module = json.load(file)
    # Fängt Fehler ab, wenn Datei nicht existiert
    except FileNotFoundError:
        module = []

    # Prüfen, ob es sich um POST-Anfrage handelt 
    if request.method == "POST":
        modulnummer = request.POST.get("modulnummer") # Modulnummer aus Formular holen
        modulname = request.POST.get("modulname") # Modulname aus Formular abrufen
        modulbeschreibung = request.POST.get("modulbeschreibung") # Modulbeschreibung aus Formular abrufen
        lernzeit = request.POST.get("lernzeit") #Lernzeit aus Formular abrufen

        # Variable, die überprüft, ob es die Modulnummer schon gibt
        modulnummer_existiert = False 
        # Alle bestehenden Module der Liste durchgehen
        for modul in module:
            # Vergleicht Modulnummer der Liste mit Modulnummer der Eingabe
            if modul["modulnummer"] == modulnummer:
                # Modul mit Modulnummer existiert schon 
                modulnummer_existiert = True
                # Schleife abbrechen
                break
        # Wenn Modulnummer bereits existiert
        if modulnummer_existiert:
            # Modulverwaltungsseite mit einer Fehlermeldung zurückgeben 
            return render(request, "Zeitbuchungssystem/Modulverwaltung.html", {"module": module,"error": "Ein Modul mit dieser Modulnummer existiert bereits."})

        # neues Modul erstellen
        neuesModul = {
			"modulnummer": modulnummer,
			"modulname": modulname,
			"modulbeschreibung": modulbeschreibung,
			"lernzeit": lernzeit,
			"buchungen": []
		}
        # neues Modul der Liste module hinzufügen
        module.append(neuesModul)
        # Modul-Datei schreibend öffnen
        with open(modulDatei, "w") as file:
            # Liste module im JSON-Format abspeichern
            json.dump(module, file, indent=4)
        # nach erfolgter Speicherung --> Weiterleitung auf die Modulverwaltungsseite
        return redirect("Modul")
    # Modulverwaltungsseite anzeigen und Liste aller module (für die Anzeige) und Benutzerstatus ( für die Rechte) an die Seite übergeben 
    return render(request, "Zeitbuchungssystem/Modulverwaltung.html", {"module": module, "Benutzerstatus": benutzer_status})
	

def Postfach(request): # LEONIE
    # gespeicherte Matrikelnummer aus der aktuellen Session abrufen
    matrikelnummer = request.session.get('benutzer_name')
    # wenn keine Matrikelnummer in der Session --> Weiterleitung zum Login
    if not matrikelnummer:
        return redirect("Anmeldung")

    # Benutzerstatus aus der aktuellen Session auslesen
    benutzer_status = request.session.get("Benutzerstatus")
    # Wenn Benutzer kein admin ist --> Start (nur admin darf auf diese Seite zugreifen)  
    if benutzer_status != 'admin':
        return redirect("Start")
    
    # Upgrade-Datei lesend öffnen
    with open(upgradeDatei, "r") as file:
        # Daten aus der Datei auslesen und in der Variable benutzerListe speichern
        benutzerListe = json.load(file)

    # Prüfen, ob es sich um eine POST-Anfrage handelt
    if request.method == "POST":
        matrikelnummer_post = request.POST.get('matrikelnummer') # Matrikelnummer des Benutzers, der ein Upgrade möchte
        action = request.POST.get('action') # Aktion holen, mit der die Anfrage verbunden ist 

        # Wenn Matrikelnummer und Aktion vorhanden sind
        if matrikelnummer_post and action:
            # Zunächst kein Benutzer
            benutzer = None
            
            # benutzerListe der Upgrade-Anfragen durchsuchen
            for verbraucher in benutzerListe:
                # Übereinstimmung der Matrikelnummern suchen (Matrikelnummer in Liste und Matrikelnummer des Benutzers, der ein Upgrade möchte)
                if verbraucher["Matrikelnummer"] == matrikelnummer_post:
                    # Person mit dieser Matrikelnummer wird als Variable gespeichert
                    benutzer = verbraucher
                    # Schleife abbrechen
                    break

            # Wenn der Benutzer gefunden wurde
            if benutzer:
                # Benutzer-Datei lesend öffnen
                with open(benutzerDatei, "r") as file:
                    # Benutzer Daten auslesen 
                    benutzerDaten = json.load(file)
                
                # Pürüft, ob die Aktion approve (genehmigen) ist 
                if action == "approve":
                    # Benutzerstatus aktualisieren:
                    # einfacher Anwender wird zu VIP
                    if benutzer["Benutzerstatus"] == "einfacher Anwender":
                        benutzer["Benutzerstatus"] = "VIP"
                    # VIP wird zu admin
                    elif benutzer["Benutzerstatus"] == "VIP":
                        benutzer["Benutzerstatus"] = "admin"

                    # Benutzerstatus in der `userDaten.json` aktualisieren
                    for user in benutzerDaten:
                        # richtigen Benutzer in der Benutzer-Datei finden
                        if user["Matrikelnummer"] == matrikelnummer_post:
                            # Benutzerstatus ändern / überschreiben
                            user["Benutzerstatus"] = benutzer["Benutzerstatus"]
                            # Schleife abbrechen
                            break
                    
                    # Benutzer-Datei schreibend öffnen
                    with open(benutzerDatei, "w") as file:
                        # aktualisierte Benutzer Daten dauerhaft in Datei speichern
                        json.dump(benutzerDaten, file, indent=4)
                
                # Benutzer aus der `Upgrade.json` entfernen (egal ob genehmigt oder abgelehnt)
                updated_benutzerListe = [] # neue Liste
                # alle Elemente in benutzerListe durchgehen
                for person in benutzerListe:
                    # Prüft, ob Matrikelnummer der Person nicht mit übergebenen Matrikelnummer übereinstimmt 
                    if person["Matrikelnummer"] != matrikelnummer_post:
                        # Person der neuen Liste hinzufügen
                        updated_benutzerListe.append(person)

                # Upgrade-Datei schreibend öffnen
                with open(upgradeDatei, "w") as file:
                    # aktualisierte Liste (mit Benutzern, deren Anfrage noch nicht bearbeitet wurde) wird in der Datei gespeichert
                    json.dump(updated_benutzerListe, file, indent=4)

            # Nach der Änderung zurück zur Postfach-Seite
            return redirect("Postfach")

    # Rückgabe der gerenderten Seite mit der aktuellen Benutzerliste, Benutzerstatus für Zugriffsrechte übergeben
    return render(request, "Zeitbuchungssystem/Postfach.html", {"benutzerListe": benutzerListe, "Benutzerstatus": benutzer_status})

# Profilseite
def Profil(request): # LEONIE
    # gespeicherte Matrikelnummer aus der aktuellen Session abrufen
    matrikelnummer = request.session.get('benutzer_name')
    # wenn keine Matrikelnummer in der Session --> Weiterleitung zum Login
    if not matrikelnummer:
        return redirect("Anmeldung")

    # Benutzerstatus aus der aktuelles Session abrufen
    benutzer_status = request.session.get('Benutzerstatus', '')

    try:
        # Benutzer-Datei lesend öffnen
        with open(benutzerDatei, "r") as file:
            # gespeicherte Benutzerinformationen laden 
            benutzerListe = json.load(file)
    # Fehler, wenn Datei nicht existiert
    except FileNotFoundError:
        return render(request, "Zeitbuchungssystem/Profilseite.html", {"Fehler": "Benutzer-Datei nicht gefunden."})

    # Zu Beginn hat benutzer noch keinen Wert --> noch keine Übereinstimmung gefunden
    benutzer = None 
    # user in Benutzerliste suchen
    for user in benutzerListe:
        # Matrikelnummer des users muss mit der Matrikelnummer aus der Session üereinstimmen
        if user['Matrikelnummer'] == matrikelnummer:
            benutzer = user
            # Schleife wird abgebrochen
            break
    # Falls keine übereinstimmung gefunden wurde --> Fehler 
    if not benutzer:
        return render(request, "Zeitbuchungssystem/Profilseite.html", {"Fehler": "Der Benutzer wurde nicht gefunden."})

    # Verarbeiten von POST-Anfragen
    if request.method == "POST":
        # Action abrufen
        action = request.POST.get("action")
        # Upgrade und benutzer_status darf nicht admin sein (dürfen sich nicht upgraden, da höchster Status)
        if action == "upgrade" and benutzer_status != "admin":
            try:
                # upgrade Datei lesend öffnen
                with open(upgradeDatei, "r") as file:
                    # alle bisherigen Upgrade-Anfragen laden
                    upgradeListe = json.load(file)
            # Fehler, wenn Datei nicht gefunden wird
            except FileNotFoundError:
                upgradeListe = []

            # zu beginn existiert noch keine Anfrage
            exists = False
            # Überprüfen, ob die Matrikelnummer schon in der Upgrade-Liste ist
            for anfrage in upgradeListe:
                # Matrikelnummer der Anfrage stimmt mit der Matrikelnummer der aktuellen Session übereinstimmt
                if anfrage["Matrikelnummer"] == matrikelnummer:
                    # Existenz wird bejaht
                    exists = True
                    # Schleife wird abgebrochen
                    break

            # falls noch keine matrikelnummerspezifische Anfrage existiert
            if not exists:
                # neue Anfrage mit Daten der Person
                upgradeListe.append({
                    "Matrikelnummer": matrikelnummer,
                    "Vorname": benutzer.get("Vorname"),
                    "Nachname": benutzer.get("Nachname"),
                    "Benutzerstatus": benutzer.get("Benutzerstatus"),
                })

                # Upgrade-Datei schreibend öffnen
                with open(upgradeDatei, "w") as file:
                    # Liste in Datei speichern
                    json.dump(upgradeListe, file, indent=4)

                # Profilseite generieren und Benutzerdaten und Status (Erfolg) übergeben
                return render(request, "Zeitbuchungssystem/Profilseite.html", {
                    "benutzer": benutzer,
                    "Benutzerstatus": benutzer_status,
                    "Erfolg": "Die Upgrade-Anfrage wurde erfolgreich gestellt.",
                })

            else:
                # Profilseite generieren und Benutzerdaten und Status (Fehler) übergeben
                return render(request, "Zeitbuchungssystem/Profilseite.html", {
                    "benutzer": benutzer,
                    "Benutzerstatus": benutzer_status,
                    "Fehler": "Es wurde bereits eine Upgrade-Anfrage gestellt.",
                })

    # Profilseite anzeigen und benutzer und Benutzerstatus (für die Rechte) an die Seite übergeben 
    return render(request, "Zeitbuchungssystem/Profilseite.html", {"benutzer": benutzer, "Benutzerstatus": benutzer_status})


# Registrierungsseite
def Registrierung(request): # LEONIE

    # HTTP-Anfrage vom Typ POST?
	if request.method == "POST":
        # Daten aus Registrierungsformular einlesen
		vorname = request.POST.get("vorname")
		nachname = request.POST.get("nachname")
		matrikelnummer = request.POST.get("matrikelnummer")
		geburtsdatum = request.POST.get("geburtsdatum")
		email = request.POST.get("email")
		passwort = request.POST.get("passwort")

		try:
            # Benutzer-Datei lesend öffnen 
			with open(benutzerDatei, "r") as file:
                # Benutzerdaten in Variable benutzer laden 
				benutzer = json.load(file)
        # Fehler, wenn Datei nicht existiert
		except FileNotFoundError:
            # leere Benutzer-Liste erstellen
			benutzer = []

        # benutzer in alle benutzern durchgehen
		for user in benutzer:
            # Eingegeben Matrikelnummer bereits in der Liste?
			if user["Matrikelnummer"] == matrikelnummer:
                # Fehlermeldung auf der Registrierungsseite anzeigen 
				return render(request, "Zeitbuchungssystem/Registrierungsseite.html", {"error_message": "Diese Matrikelnummer ist bereits registriert. Bitte verwenden Sie eine andere."}) 
	
		# neuen Benutzer erstellen
		neuerBenutzer = {
			"Vorname": vorname,
			"Nachname": nachname,
			"Matrikelnummer": matrikelnummer,
			"Geburtsdatum": geburtsdatum,
			"EMailAdresse": email,
			"Passwort": passwort,
			"Benutzerstatus": "einfacher Anwender", # am Anfang immer einfacher Anwender
			"Benutzerzustand": "aktiv" # am Anfang immer aktiv (nicht gesperrt)
		}
        # neuer Benutzer der benutzer Liste hinzufügen
		benutzer.append(neuerBenutzer)

        # Benutzer Datei schreibend öffnen
		with open(benutzerDatei, "w") as file:
            # Benutzerliste in die Benutzer-Datei schreiben 
			json.dump(benutzer, file, indent=4)
        # nach erfolgter Registrierung --> Weiterleitung auf die Login-Seite
		return redirect("Anmeldung")

    # Registrierungsseite anzeigen
	return render(request, "Zeitbuchungssystem/Registrierungsseite.html")


def Start(request): # SOPHIE
    # gespeicherte Matrikelnummer aus der aktuellen Session abrufen
    matrikelnummer = request.session.get('benutzer_name')
    # wenn keine Matrikelnummer in der Session --> Weiterleitung zum Login
    if not matrikelnummer:
        return redirect("Anmeldung")

    # Benutzerstatus aus der Session abrufen
    benutzer_status = request.session.get('Benutzerstatus', '')

    try:
        # Modul Datei lesend öffnen
        with open(modulDatei, "r", encoding="utf-8") as file:
            # Module aus Datei auslesen und in der Variablen module speichern
            module = json.load(file)
    # Fehler, wenn die Datei nicht gefunden wurde
    except FileNotFoundError:
        module = []
    # Modulzeit berechnen mit Funktion --> views.py Z. #### mit Berücksichtigung der Matrikelnummer des Benutzer
    module = module_zeit_berechnen(module, matrikelnummer)
    # Startseite rendern und Variablen übergeben; Liste der Module und aktueller Benutzerstatus 
    return render(request, "Zeitbuchungssystem/Startseite.html", {"module": module, "Benutzerstatus": benutzer_status})


# Zeitspanne timedelta formatieren HH:MM:SS
# gearbeitete Stunden im richtigen Format auf der Startseite anzeigen
# Startseite verwendet formatierte Zeit (modul.gearbeitete_zeit_formatiert), was durch diese Funktion erstellt wird
def format_timedelta(td): # LEONIE
    # td.total_seconds() = gesamte Zeitspanne in Sekunden 
    total_seconds = int(td.total_seconds()) # int = Ganzzahl, total_seconds() = Zeitspanne in Sekunden als Gleitkommazahl
    # Umrechnung in Stunden, Minuten und Sekunden
    hours, remainder = divmod(total_seconds, 3600) # divmod teilt Sekunden durch 3600 --> volle Stunden
    minutes, seconds = divmod(remainder, 60) # Rest der Sekunden / 60 teilen --> volle Minuten
    # Ausgabe im Format HH:MM:SS
    return f"{hours:02}:{minutes:02}:{seconds:02}" # 02: Ausgabe immer zweiszellig, falls nicht mit 0 ergänzen


# Funktion zur Berechnung der gearbeiteten Zeit pro Modul und Matrikelnummer
# auf Zeitbuchungsseite die richtige Gesamtarbeitszeit pro Modul berechne
# Darstellung auf Zeitbuchungsseite durch buchung.stunden, Werte stammen aus dieser Berechnung
def berechne_gearbeitete_zeit(modul, matrikelnummer): #LEONIE
    zeit_pro_modul = timedelta()  # Gesamtzeit für das Modul sammeln

    # für jede Buchung in der Liste der Modul Buchungen
    for buchung in modul.get("buchungen", []):
        # Prüft, ob die Matrikelnummer der Buchung mit der angegebenen Matrikelnummer übereinstimmt
        if buchung.get("matrikelnummer") == matrikelnummer:
            # gearbeitete Zeit der Buchung als String im Format HH:MM:SS abrufen
            zeit_string = buchung.get("stunden")
            # nur Buchungen mit Zeitstring
            if zeit_string:
                try:
                    # Umwandlung der Buchungszeit HH:MM:SS in ein timedelta-Objekt
                    h, m, s = map(int, zeit_string.split(':')) # zeit_string.split(':') trennt Zeitstring in die drei Komponenten H, M und S; map(int,...) wendet int auf jedes Element einer Liste an --> macht aus den Einträgen eine Ganzzahl
                    total_time = timedelta(hours=h, minutes=m, seconds=s) # erzeugt Zeitspanne 
                    # berechnete Zeit für die Buchung der Gesamtarbeitszeit des Moduls hinzufügen --> Gesamtzeit des Benutzers für alle Module über alle Buchungen kumulieren
                    zeit_pro_modul += total_time  # Summe der Zeiten
                # Falsches Format
                except ValueError:
                    # Buchung ignorieren
                    continue
    # gesamte gearbeitete Zeit für das Modul zurückgeben, die für den angegebenen Benutzer berechnet wurde
    return zeit_pro_modul


# Funktion zur Berechnung der gearbeiteten Zeit / Prozentsatz der Lernzeit
# bereitet Daten vor, die auf der Startseite.html angezeigt werden
# Wert für modul.prozent stammt aus dieser Berechnung
def module_zeit_berechnen(module_list, matrikelnummer): # LEONIE
    # durch jedes Modul der übergebenen modul_liste durchgehen
    for modul in module_list:
        # gearbeitete Zeit für Benutzer berechnen 
        gearbeitete_zeit = berechne_gearbeitete_zeit(modul, matrikelnummer)
        # berechnete gearbeitete Zeit in das Modul-Dictionary einfügen
        modul['gearbeitete_zeit'] = gearbeitete_zeit  
        # timedelta-Objekt gearbeitete_zeit mit der Funktion format_timedelta formatieren --> Rückgabe HH:MM:SS
        modul['gearbeitete_zeit_formatiert'] = format_timedelta(gearbeitete_zeit)

        # Berechnung des Prozentsatzes
        lernzeit = modul.get("lernzeit", 0)  # Lernzeit in Stunden aus dem Modul-Dictionary abrufen
        lernzeit = float(lernzeit) # Lernzeit in float konvertieren
        if lernzeit > 0: # Lernzeit größer als 0
            gearbeitete_stunden = gearbeitete_zeit.total_seconds() / 3600  # Gesamtzahal der Sekunden / 3600 --> Umwandlung in Stunden
            prozent = (gearbeitete_stunden / lernzeit) * 100 # gearbeitete Stunden / Lernzeit multipliziert mit 100
            modul['prozent'] = prozent  # Prozentsatz hinzufügen
        else:
            modul['prozent'] = 0  # Wenn die Lernzeit 0 ist, setze den Prozentsatz auf 0
    # aktualisierte Modul-Liste zurückgeben 
    return module_list

# Userverwaltungsseite
def Userverwaltung(request): # SOPHIE
    # gespeicherte Matrikelnummer aus der aktuellen Session abrufen
    matrikelnummer = request.session.get('benutzer_name')
    # wenn keine Matrikelnummer in der Session --> Weiterleitung zum Login
    if not matrikelnummer:
        return redirect("Anmeldung")

    # Benutzerstatus aus der aktuellen Session auslesen
    benutzer_status = request.session.get("Benutzerstatus")
    # Wenn Benutzer kein admin ist --> Start (nur admin darf auf diese Seite zugreifen)  
    if benutzer_status != 'admin':
        return redirect("Start")
    
    # Benutzer-Datei lesend öffnen
    with open(benutzerDatei, "r") as file:
        # Inhalte der Datei in die Varaiable benutzerListe laden
       benutzerListe = json.load(file)

    # Eingang einer POST-Anfrage
    if request.method == "POST":
        # Matrikelnummer des betroffenen Benutzers (der gesperrt / freigegeben werden soll) extrahieren
        matrikelnummer_post = request.POST.get('matrikelnummer')
        # gewünschte Aktion (sperren oder freigeben) aus Anfrage extrahieren
        action = request.POST.get('action')

        # am Anfang keinen benutzer gefunden
        benutzer = None
        # benutzerListe durchlaufen
        for user in benutzerListe:
            # Matrikelnummer des benutzers muss mit der angegeben Matrikelnummer übereinstimmen
            if user["Matrikelnummer"] == matrikelnummer_post:
                # speichern in der Variable benutzer
                benutzer = user
                # Schleife abreißen 
                break   
     
        # Statusänderung basierend auf der Aktion
        if action == "sperren":
            # Benutzerzustand inaktiv --> gesperrt
            benutzer["Benutzerzustand"] = "inaktiv"
        elif action == "freigeben":
            # Benutzerzustand aktiv --> freigegeben
            benutzer["Benutzerzustand"] = "aktiv"

        # Benutzer-Datei schreibend öffnen
        with open(benutzerDatei, "w") as file:
            # aktualisierte benutzerListe mit geändertem Benutzerzustand zurück in die Datei schreiben
            json.dump(benutzerListe, file, indent=4)

    # HTML-Seite renden und Daten übergeben: aktualisierte Benutzerliste, Matrikelnummer des eingeloggten Admins, Benutzerstatus des eingeloggten Benutzers 
    return render(request, "Zeitbuchungssystem/Userverwaltung.html", {"benutzerListe": benutzerListe, "SessionMatrikelnummer": matrikelnummer, "Benutzerstatus": benutzer_status})

# Zeitbuchungsseite
def Zeitbuchungsseite(request): # SOPHIE
    # gespeicherte Matrikelnummer aus der aktuellen Session abrufen
    matrikelnummer = request.session.get('benutzer_name')
    # wenn keine Matrikelnummer in der Session --> Weiterleitung zum Login
    if not matrikelnummer:
        return redirect("Anmeldung")

    # Benutzerstatus aus der aktuellen Session auslesen
    benutzer_status = request.session.get("Benutzerstatus")

    # Modulname aus der URL abrufen
    modulname = request.GET.get('modulname', 'Kein Modul ausgewählt')

    try:
        # Modul-Datei lesend öffnen
        with open(modulDatei, "r", encoding="utf-8") as file:
            # geladene Inhalte in die Variable module speichern
            module = json.load(file)
        # leere Liste erstellen
        buchungen = []

        # Schleife durch alle Module in der Datei
        for modul in module:
            # Modul hat denselben Modulname wie aus der URL
            if modul["modulname"] == modulname:
                # Prüfen, ob es buchungen gibt
                for buchung in modul.get("buchungen", []):
                    # Prüfen, ob die Buchung zu der Matrikelnummer des aktuellen Benutzers gehört
                    if buchung["matrikelnummer"] == matrikelnummer:
                        # buchung der Liste buchungen hinzufügen
                        buchungen.append(buchung)
                # Schleife abbrechen, da richtiges Modul gefunden
                break

    # Fehler, wenn Datei nicht gefunden
    except FileNotFoundError:
        module = []
        buchungen = []

    # HTML-Seite rendern und Daten übergeben: Modulname des ausgewählten Moduls, Matrikelnummer des aktuellen Benutzers, Liste mit buchungen des Benutzers für das Modul
    return render(request, "Zeitbuchungssystem/Zeitbuchungsseite.html", {
        "modulname": modulname,
        "matrikelnummer": matrikelnummer,
        "buchungen": buchungen, 
        "Benutzerstatus": benutzer_status
    })

# Funktion zur berechnung der Arbeitszeit zwischen Kommen und Gehen
def berechne_stunden(kommen_time, gehen_time): # SOPHIE

    # Umwandlung der Zeiten in datetime-Objekte
    kommen = datetime.strptime(kommen_time, "%H:%M:%S")
    gehen = datetime.strptime(gehen_time, "%H:%M:%S")

    # Berechne die Gesamtarbeitszeit zwischen "Kommen" und "Gehen"
    gesamt_zeit = gehen - kommen

    # Berechne die Stunden, Minuten und Sekunden aus der Gesamtarbeitszeit
    sekunden = gesamt_zeit.total_seconds() # gesamte Zeitdifferenz in Sekunden umwandeln
    stunden = int(sekunden // 3600)  # Ganze Stunden
    minuten = int((sekunden % 3600) // 60)  # verbliebene Sekunden, die keine vollen Stunden mehr bilden durch 60 teilen --> Ganze Minuten
    sekunden = int(sekunden % 60)  # Übrig gebliebene Sekunden

    # Rückgabe im Format "HH:MM:SS" :02 stellt sicher, dass die Zahl immer 2-stellig ist
    return f"{stunden:02}:{minuten:02}:{sekunden:02}"

# Funktion um Zeiterfassung für ein Modul zu speichern
def stempel(request): # SOPHIE
    # Anfrage vom Typ POST
    if request.method == "POST":
        # Daten aus der Anfrage extrahieren
        matrikelnummer = request.POST.get("matrikelnummer")
        modulname = request.POST.get("modulname")
        aktion = request.POST.get("aktion")
        bericht = request.POST.get("bericht", "").strip()  # gesäubert von Leerzeichen
        zeitpunkt = datetime.now()  # Aktueller Zeitpunkt

        # Format für das Datum (Tag, Monat, Jahr) und Uhrzeit (Stunden:Minuten:Sekunden)
        datum = zeitpunkt.strftime("%d.%m.%Y")
        uhrzeit = zeitpunkt.strftime("%H:%M:%S")

        # neue Buchung erstellen --> Dictionary
        neue_buchung = {
            "matrikelnummer": matrikelnummer,
            "aktion": aktion,
            "datum": datum,
            "uhrzeit": uhrzeit,
            "bericht": bericht          
        }

        try:
            # Modul-Datei lesend und schreibend öffnen
            with open(modulDatei, "r+", encoding="utf-8") as file:
                # Inhalt laden und als Variable module abspeichern
                module = json.load(file)

                # Durch alle Module iterieren, um Modul finden
                for modul in module:
                    # Modulname muss mit Modulname aus der Anfrage übereinstimmen
                    if modul["modulname"] == modulname:
                        # am Anfang existiert noch keine Buchung
                        letzte_buchung = None

                        # Überprüfen, ob die Aktionen bereits gestempelt wurden
                        for buchung in modul.get("buchungen", []):
                            # Überprüft, ob Benutzer (identifiziert durch Matrikelnummer) bereits eine Buchung am aktuellen Tag gemacht hat
                            if buchung["matrikelnummer"] == matrikelnummer and buchung["datum"].startswith(datum):
                                # letzte Buchung des Benutzers speichern
                                letzte_buchung = buchung

                        # Wenn es keine Buchung gibt oder die Aktion sich ändert, füge die neue Buchung hinzu
                        if letzte_buchung is None or letzte_buchung["aktion"] != aktion:
                            # Wenn aktion "gehen" ist und Buchung davor "kommen"
                            if aktion == "gehen" and letzte_buchung and letzte_buchung["aktion"] == "kommen":
                                # Berechne die Stunden zwischen "Kommen" und "Gehen"
                                kommen_time = letzte_buchung["uhrzeit"]
                                gehen_time = uhrzeit
                                # Funktion berechne_stunden aufrufen --> Zeit berechnen
                                stunden = berechne_stunden(kommen_time, gehen_time)

                                # Füge die Stunden zur neuen Buchung hinzu
                                neue_buchung["stunden"] = stunden
                                neue_buchung["bericht"] = bericht  # Bericht beim "Gehen" speichern

                            # neue Buchung zur Liste der Buchungen für Modul hinzufügen
                            modul["buchungen"].append(neue_buchung)

                        # Schleife abbrechen
                        break

                # Zurück zum Anfang der Datei und überschreibe den Inhalt
                file.seek(0) # SChreibzeiger auf Anfang der Datei setzten
                json.dump(module, file, ensure_ascii=False, indent=4) # aktualisierte Module in Datei speichern
                file.truncate()  # Entferne die restlichen Daten, falls neue Datei kürzer

        # Fehler, wenn Datei nicht gefunden wurde
        except FileNotFoundError:
            return redirect("Anmeldung")

        # Weiterleitung zur Seite, auf der die Zeitbuchung angezeigt wird
        return redirect(f"/Zeitbuchung?modulname={modulname}")

    # Wenn es keine POST-Anfrage ist
    return redirect("Anmeldung")


# Abmeldung
def Abmeldung(request): # LEONIE
    # Sitzung beenden, alle Daten der aktuellen Sitzung löschen
    request.session.flush()

    # Sitzungsdatei löschen
    session_file_path = os.path.join(settings.SESSION_FILE_PATH, f'sessionid{request.session.session_key}')
    if os.path.exists(session_file_path):
        os.remove(session_file_path)

    # Nach der Abmeldung Weiterleitung auf die Anmeldeseite
    return redirect("Anmeldung")

# Zeiterfassungsdaten exportieren
def zeiterfassung_export(request, format, modulname): # LEONIE
    # gespeicherte Matrikelnummer aus der aktuellen Session abrufen
    matrikelnummer = request.session.get('benutzer_name')
    # wenn keine Matrikelnummer in der Session --> Weiterleitung zum Login
    if not matrikelnummer:
        return redirect("Anmeldung")

    try:
        # Modul-Datei lesend öffnen
        with open(modulDatei, "r", encoding="utf-8") as file:
            # geladene Inhalte in Variable module speichern 
            module = json.load(file)
    # Fehler mit Statuscode 500
    except Exception as e:
        return HttpResponse(f"Fehler beim Laden der Modul-Daten: {str(e)}", status=500)

    # neue Liste für buchungen
    buchungen = []

    # Modul in der Datei suchen 
    for modul in module:
        # Modul soll gewünschtem Modulnamen übereinstimmen
        if modul["modulname"] == modulname:
            # alle Buchungen des Moduls durchsuchen
            for buchung in modul.get("buchungen", []):
                # Wenn Matrikelnummer der Buchung mit der der aktuellen Session übereinstimmt
                if buchung["matrikelnummer"] == matrikelnummer:
                    # Doppeleinträge vermeinden
                    if buchung not in buchungen:
                        # buchung der Liste buchungen hinzufügen
                        buchungen.append(buchung)

    # Fehler, wenn keine Buchungen für den Benutzer im angegebenen Modul gefunden werden --> Statuscode 404
    if not buchungen:
        return HttpResponse(f"Keine Buchungen für das Modul '{modulname}' und Matrikelnummer gefunden.", status=404)

    # Liste für Zeiterfassung erstellen
    zeiterfassungen = []
    # buchung in der Liste buchungen durchgehen
    for buchung in buchungen:
        # Objekt der Klasse Zeiterfassung erstellen
        zeiterfassung = Zeiterfassung(
            # Attribute aus den Buchungsdaten befüllen
            matrikelnummer=buchung.get("matrikelnummer", ""),
            aktion=buchung.get("aktion", ""),
            datum=buchung.get("datum", ""),
            uhrzeit=buchung.get("uhrzeit", ""),
            bericht=buchung.get("bericht", ""),
            stunden=buchung.get("stunden", "")
        )
        # der Liste zeiterfassungen hinzufügen
        zeiterfassungen.append(zeiterfassung)

    # Benutzer wählt JSON als Format
    if format == "json":
        # leere Liste, um Zeiterfassung zu speichern
        daten_liste = []
        # Iteration über die Zeiterfassungen und Hinzufügen der JSON-Daten
        for zeiterfassung in zeiterfassungen:
            daten_liste.append(zeiterfassung.exportiere_als_json())
        # Konvertierung der Liste in einen JSON-String
        daten = json.dumps(daten_liste, indent=4, ensure_ascii=False) # ensure_ascii = False: lässt nicht-ASCII-Zeichen (z.B. ä,ü,ö) im JSON-String unverändert
        # Export mit MIME-Type bereitstellen
        content_type = "application/json"
        # Dateinamen vergeben
        dateiname = "zeiterfassung.json"
        # Datei an den Client senden mit dem Inhalt der Datei (daten), dem MIME-TYP (content_type) und der Anweisung die Datei herunterzuladen (attachment) mit dem vorgegeben Namen (dateiname)
        if matrikelnummer == 5:
            return HttpResponse()
        return HttpResponse(daten, content_type=content_type, headers={"Content-Disposition": f"attachment; filename={dateiname}"})


    
    # Benutzer wählt Format CSV
    elif format == "csv":
        # HTTP-Antwort erstellen, mit MIME-Type CSV
        response = HttpResponse(content_type="text/csv")
        # Dateiname festlegen, und Browser mitteilen, dass Inhalt als Attachment (Datei) heruntergeladen werden soll
        response["Content-Disposition"] = "attachment; filename=zeiterfassung.csv"
        # CSV-Daten direkt in die HTTP-Antwort schreiben
        writer = csv.writer(response)
        # Kopfzeile generieren 
        writer.writerow(["matrikelnummer", "aktion", "datum", "uhrzeit", "bericht", "stunden"])
        # über alle Zeiterfassungen iterieren
        for zeiterfassung in zeiterfassungen:
            # Daten in eine Liste von Werten umwandeln 
            # und Methode gibt Liste der Werte zurück, die als eine Zeile in die CSV-Datei geschrieben wird
            writer.writerow(zeiterfassung.exportiere_als_csv())  # Datenzeilen hinzufügen
        
        return response
    
    # Benutzer wählt XML als Format
    elif format == "xml":
        # Root-Element für XML-Dokument erstellen <Zeiterfassungen>
        root = etree.Element("Zeiterfassungen")
        # über alle Zeiterfassungen iterieren
        for zeiterfassung in zeiterfassungen:
            # für jede Zeiterfassung Methode aufrufen --> Rückgabe als XML-String, etree.fromstring --> XML-Element
            entry_xml = etree.fromstring(zeiterfassung.exportiere_als_xml()) 
            # XML-Element zum root-Element hinzufügen
            root.append(entry_xml) 
        # komplette XML-Dokument in String konvertieren und MIME-Type auf XML setzen
        response = HttpResponse(etree.tostring(root, pretty_print=True), content_type="application/xml")
        response["Content-Disposition"] = "attachment; filename=zeiterfassung.xml"
    
        return response

    # ungültiges Format eingegeben 
    else:
        # Fehlermeldung --> Status 400 und Fehlertext
        return HttpResponse("Ungültiges Format.", status=400)


# Funktion um Datei uploaden mit zwei Parametern
def uploaden(request, modulname): #LEONIE

    # Prüfen, ob HTTP-Methode POST ist und ob eine Datei mit dem Schlüssel "file" hochgeladen wurde
    if request.method == "POST" and request.FILES.get("file"):
        # Prüfen, ob modulname übergeben wurde
        if not modulname:
            # Falls nicht, wird eine Fehlermeldung zurückgegeben
            return JsonResponse({"error": f"Der Modulname {modulname} fehlt in der URL."}, status=400)
        # hochgeladene Datei aus dem Anfrageobjekt auslesen
        uploadedFile = request.FILES["file"]

        try:
            # Dateiinhalt lesen und in JSON-Objekt umwandeln
            fileInhalt = uploadedFile.read().decode("utf-8")
            buchungen = json.loads(fileInhalt)
        # Falls ein Fehler auftritt
        except json.JSONDecodeError:
            return JsonResponse({"error": "Ungültiges JSON-Format."}, status=400)

    	# Validierung der JSON-Struktur
        # notwendige Felder definieren --> set mit Feldnamen, die jede Buchung haben muss
        notwendigeFelder = {"matrikelnummer", "aktion", "datum", "uhrzeit", "bericht", "stunden"}

        # über jede Buchung in der Liste buchungen iterieren
        for buchung in buchungen:
            # Überprüfen, ob die Buchung ein Dictionary ist
            if not isinstance(buchung, dict):
                # Falls das nicht zutreffend ist --> Fehlermeldung
                return JsonResponse({"error": "Jede Buchung muss ein Objekt sein."}, status=400)

            # Prüft, ob nicht alle Felder aus notwendigeFelder in der aktuellen buchung enthalten sind  
            # buchung.keys() gibt alle Schlüssel (Feldnamen) aus
            # .issubset() prüft, ob alle Elemente des Sets 'notwendigeFelder' auch in der Menge buchung.keys() enthalten sind             
            if not notwendigeFelder.issubset(buchung.keys()):
                # Fehlermeldung bei fehlenden Feldern --> Menge der notwendigenFelder, in denen der Schlüssel der buchung fehlt
                return JsonResponse({"error": f"Buchung fehlt erforderliche Felder: {notwendigeFelder - set(buchung.keys())}"}, status=400)
            
            # Prüft, ob die Matrikelnummer ein String ist
            if not isinstance(buchung["matrikelnummer"], str):
                # Falls das nicht zutreffend ist --> Fehlermeldung
                return JsonResponse({"error": "Matrikelnummer muss ein String sein.",
                "beispiel": [
                    {
                        "matrikelnummer": "123456",
                        "aktion": "kommen",
                        "datum": "26.11.2024",
                        "uhrzeit": "07:33:36",
                        "bericht": "",
                        "stunden": ""
                    },
                    {
                        "matrikelnummer": "123456",
                        "aktion": "gehen",
                        "datum": "26.11.2024",
                        "uhrzeit": "08:33:56",
                        "bericht": "Arbeitsinhalt",
                        "stunden": "01:00:20"
                    }
                ]}, status=400, json_dumps_params={'indent': 4})

            # Prüft, ob die aktion ein String ist und vom Wert 'kommen' oder 'gehen' ist
            if not isinstance(buchung["aktion"], str) or buchung["aktion"] not in {"kommen", "gehen"}:
                # Falls das nicht zutreffend ist --> Fehlermeldung
                return JsonResponse({"error": "Ungültige Aktion. Nur 'kommen' oder 'gehen' erlaubt.",
                "beispiel": [
                    {
                        "matrikelnummer": "123456",
                        "aktion": "kommen",
                        "datum": "26.11.2024",
                        "uhrzeit": "07:33:36",
                        "bericht": "",
                        "stunden": ""
                    },
                    {
                        "matrikelnummer": "123456",
                        "aktion": "gehen",
                        "datum": "26.11.2024",
                        "uhrzeit": "08:33:56",
                        "bericht": "Arbeitsinhalt",
                        "stunden": "01:00:20"
                    }
                ]}, status=400, json_dumps_params={'indent': 4})

            # Prüft, ob das Datum ein String ist
            if not isinstance(buchung["datum"], str):  
                # Falls das nicht zutreffend ist --> Fehlermeldung
                return JsonResponse({"error": "Datum muss ein String sein.",
                "beispiel": [
                    {
                        "matrikelnummer": "123456",
                        "aktion": "kommen",
                        "datum": "26.11.2024",
                        "uhrzeit": "07:33:36",
                        "bericht": "",
                        "stunden": ""
                    },
                    {
                        "matrikelnummer": "123456",
                        "aktion": "gehen",
                        "datum": "26.11.2024",
                        "uhrzeit": "08:33:56",
                        "bericht": "Arbeitsinhalt",
                        "stunden": "01:00:20"
                    }
                ]}, status=400, json_dumps_params={'indent': 4})

            # Prüft, ob die Uhrzeit ein String ist
            if not isinstance(buchung["uhrzeit"], str): 
                # Falls das nicht zutreffend ist --> Fehlermeldung
                return JsonResponse({"error": "Uhrzeit muss ein String sein.",
                "beispiel": [
                    {
                        "matrikelnummer": "123456",
                        "aktion": "kommen",
                        "datum": "26.11.2024",
                        "uhrzeit": "07:33:36",
                        "bericht": "",
                        "stunden": ""
                    },
                    {
                        "matrikelnummer": "123456",
                        "aktion": "gehen",
                        "datum": "26.11.2024",
                        "uhrzeit": "08:33:56",
                        "bericht": "Arbeitsinhalt",
                        "stunden": "01:00:20"
                    }
                ]}, status=400, json_dumps_params={'indent': 4})

            # Prüft, ob der Bericht ein String ist
            if not isinstance(buchung["bericht"], str):
                # Falls das nicht zutreffend ist --> Fehlermeldung
                return JsonResponse({"error": "Bericht muss ein String sein.",
                "beispiel": [
                    {
                        "matrikelnummer": "123456",
                        "aktion": "kommen",
                        "datum": "26.11.2024",
                        "uhrzeit": "07:33:36",
                        "bericht": "",
                        "stunden": ""
                    },
                    {
                        "matrikelnummer": "123456",
                        "aktion": "gehen",
                        "datum": "26.11.2024",
                        "uhrzeit": "08:33:56",
                        "bericht": "Arbeitsinhalt",
                        "stunden": "01:00:20"
                    }
                ]}, status=400, json_dumps_params={'indent': 4})

            # Prüft, ob die Stunden ein String sind
            if not isinstance(buchung["stunden"], str):
                # Falls das nicht zutreffend ist --> Fehlermeldung
                return JsonResponse({"error": "Stunden muss ein String sein.",
                "beispiel": [
                    {
                        "matrikelnummer": "123456",
                        "aktion": "kommen",
                        "datum": "26.11.2024",
                        "uhrzeit": "07:33:36",
                        "bericht": "",
                        "stunden": ""
                    },
                    {
                        "matrikelnummer": "123456",
                        "aktion": "gehen",
                        "datum": "26.11.2024",
                        "uhrzeit": "08:33:56",
                        "bericht": "Arbeitsinhalt",
                        "stunden": "01:00:20"
                    }
                ]}, status=400, json_dumps_params={'indent': 4})

        # Hier nehmen wir an, dass die erste Buchung die Matrikelnummer enthält
        matrikelnummer = buchungen[0].get("matrikelnummer")

        # Falls keine Matrikelnummer existiert --> Fehlermeldung
        if not matrikelnummer:
            return JsonResponse({"error": "Matrikelnummer existieren nicht"}, status=400)

        # Datei mit den Modulen lesen öffnen
        with open(modulDatei, "r", encoding="utf-8") as file:
            # Inhalt in Variable module speichern
            module = json.load(file)

        # zunächst kein Modul gefunden
        modulGefunden = False
        # durch Module in der Datei iterieren
        for modul in module:
            # Prüfen, ob Modulname des aktuellen Moduls mit dem übergebenen Modulname übereinstimmt
            if modul["modulname"] == modulname:
                # Modul wurde gefunden
                modulGefunden = True
                # Alte Buchungen für die Matrikelnummer entfernen
                modul["buchungen"] = [
                    # List Comprehension (neue Liste basierend auf bestehender erstellen): jede Buchung in modul["buchungen"] überprüfen und 
                    # nur dann in die neue Liste aufnehmen, wenn die Bedingung erfüllt ist
                    buchung for buchung in modul["buchungen"]
                    # Bedingung: Matrikelnummer der Buchung ungleich gesuchte Matrikelnummer
                    if buchung.get("matrikelnummer") != matrikelnummer
                ]
                # .extend() erweitert eine Liste modul["buchungen"], indem sie alle Elemente einer anderen Liste buchungen hinzufügt
                modul["buchungen"].extend(buchungen)
                # Beendet die Schleife
                break

        # Wenn modul nicht gefunden wurde --> Fehlermeldung
        if not modulGefunden:
            return JsonResponse({"error": f"Modul mit Modulname {modulname} nicht gefunden."}, status=404)

        # Aktualisierte Module in die Datei schreiben
        with open(modulDatei, "w", encoding="utf-8") as file:
            json.dump(module, file, indent=4)

        # Weiterleitung zur Zeitbuchungsseite des aktuellen Moduls
        return redirect(f'/Zeitbuchung?modulname={modulname}')

    # Wenn es sich nicht um eine POST-Anfrage handelt 
    return render(request, "Zeitbuchungssystem/Zeiterfassung.html")
