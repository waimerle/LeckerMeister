from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
import json, os
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

# Anmeldeseite
def Anmeldung(request):
    user_filename = "/var/www/django-projekt/LeckerMeister/user_Data.json" # JSON-Datei mit Profildaten 

    with open(user_filename, "r", encoding="utf-8") as file:
        user_list = json.load(file)

    # Abrufen der Benutzerdaten: Benutzername und Paswort 
    if request.method == 'POST':
        benutzer_name = request.POST.get('benutzer_name') 
        password = request.POST.get('Passwort')
        
        # Durchlaufen der user_liste um zu überprüfen, ob ein Benutzer mit dem
        # angegeben Passwort und Benutzernamen existiert
        # wenn ja: Speichern des Benutzernamens in der Session --> Weiterleitung zur Homeseite 
        for user in user_list:
            if user['name'] == benutzer_name and user['Passwort'] == password:
                request.session['benutzer_name'] = benutzer_name
                return redirect('Homeseite.html')

    # Wenn die Benutzerdaten nicht stimmen, wir die Anmeldeseite gerendert 
    return render(request, 'LeckerMeister/Anmeldung.html')




# Registrierung 
def Registrierung(request):

    if request.method == 'POST':
        # Formulardaten abrufen
        benutzer_name = request.POST.get('benutzer_name')
        profil_bild = request.FILES.get('profil_bild')
        email = request.POST.get('email')
        Wohnort = request.POST.get('Wohnort')
        Biografie = request.POST.get('Biografie') 
        Passwort = request.POST.get('Passwort')

        # Wenn Bild hochgeladen, wird Name des Bildes gespeichert, ansonsten None
        profil_bild_name = profil_bild.name if profil_bild else None

        # Neuer Benutzer erstellen
        neuer_Benutzer = {
            "Profilbild": profil_bild_name, 
            "name": benutzer_name, 
            "email": email,
            "Wohnort": Wohnort,
            "Passwort": Passwort,
            "bio": Biografie
        }

        user_filename = "/var/www/django-projekt/LeckerMeister/user_Data.json" #JSON-Datei mit Benutzerdaten
        #Versuchen, besetehende Benutzerdaten-Datei zu öffnen
        try:
            with open(user_filename, 'r') as file:
                benutzer = json.load(file)
        # Falls sie nicht existiert --> leere Liste
        except FileNotFoundError:
            benutzer = []

        # Neuer Benutzer wird zur Liste der bestehenden Benutzer hinzugefügt 
        benutzer.append(neuer_Benutzer)

        # aktualisierte Benutzerliste in JSON-Datei schreiben
        with open(user_filename, 'w') as file:
            json.dump(benutzer, file, indent=4)

        # Profilbild wird in static/users Order gelsichert
        if profil_bild:
            with open(f'/var/www/static/users/{profil_bild.name}', 'wb+') as destination:
                # Bild wird in kleinen Blöchen gelesen und geschrieben --> Optimierung der Speicherverwendung
                for chunk in profil_bild.chunks():
                    destination.write(chunk)

        return redirect("Anmeldung.html")

    return render(request, 'LeckerMeister/Registrierung.html')




# Homeseite --> Rezepte wie ein Feed anzeigen
def Homeseite(request):

    # Benutzername aus der Session abrufen
    benutzer_name = request.session.get("benutzer_name")

    # Falls kein Benutzer angemeldet ist --> Anmeldeseite
    if not benutzer_name:
        return redirect("Anmeldung.html")

    user_data_file = "/var/www/django-projekt/LeckerMeister/user_Data.json"
    rezept_file = "/var/www/django-projekt/LeckerMeister/Rezepte.json"

    try:
        # Laden der Benutzerdaten aus der JSON-Datei
        with open(user_data_file, "r") as file:
            user_data = json.load(file)

        # Laden der Rezepte aus der JSON-Datei
        with open(rezept_file, "r") as file: 
            rezept_list = json.load(file)

    except FileNotFoundError:
        # Behandlung, falls eine Datei nicht gefunden wird
        rezept_list = []

    # Vorbereitung der Rezepte für die Darstellung in der Vorlage
    rezepte = []
    for rezept in rezept_list:
        ersteller_name = rezept.get("Ersteller", "")
        # Abrufen des Erstellernamens für jedes Rezept 
        ersteller_data = next((user for user in user_data if user["name"] == ersteller_name), None)
        
        if ersteller_data:
            rezepte.append({
		        "id": rezept.get("id", ""),
                "Ersteller": ersteller_name,
                "Profilbild": ersteller_data.get("Profilbild", ""), 
                "Rezeptbild": rezept.get("Rezeptbild", ""),
                "name": rezept.get("name", ""),
                "Zutaten": rezept.get("Zutaten", ""),
                "Zubereitung": rezept.get("Zubereitung", ""),
                "Zubereitungszeit": rezept.get("Zubereitungszeit", ""),
                "Kategorie": rezept.get("Kategorie", ""),
		        "likes": rezept.get("likes", ""),
            })

    # Rendern der HTML-Seite mit den Rezepten als Kontext
    return render(request, "LeckerMeister/Homeseite.html", {"rezepte": rezepte})




# Suchseite --> Suche nach Wort und Kategorie
def Suchseite(request):

    # Benutzername aus der Session abrufen
    benutzer_name = request.session.get("benutzer_name")

    # Falls kein Benutzer angemeldet ist --> Anmeldeseite
    if not benutzer_name:
        return redirect("Anmeldung.html")

    Rezept_Filename = "/var/www/django-projekt/LeckerMeister/Rezepte.json"
    user_data_filename = "/var/www/django-projekt/LeckerMeister/user_Data.json"

    # Laden der Rezepte aus der JSON-Datei
    with open(Rezept_Filename, "r") as file:
        Rezept_list = json.loads(file.read())

    # Laden der Benutzerdaten aus der JSON-Datei
    with open(user_data_filename, "r") as file:
        user_data_list = json.load(file)

    # Abrufen der Suchparameter
    query = request.GET.get('query')
    category = request.GET.get('category')

    rezepte = Rezept_list

    # Suche nach Rezeptname
    if query:
        rezepte = [rezept for rezept in rezepte if query.lower() in rezept.get('name', '').lower()]

    # Suche nach Rezeptkategorie
    if category:
        rezepte = [rezept for rezept in rezepte if rezept.get('Kategorie') == category]

    # Vorbereitung der Rezepte für die Darstellung in der Vorlage
    rezepte_formatted = []
    for rezept in rezepte:
        ersteller_name = rezept.get("Ersteller", "")
        # Abrufen des Erstellernamens für jedes Rezept
        ersteller_data = next((user for user in user_data_list if user["name"] == ersteller_name), None)

        if ersteller_data:
            rezepte_formatted.append({
                "Ersteller": ersteller_name,
                "Profilbild": ersteller_data.get("Profilbild", ""),
                "Rezeptbild": rezept.get("Rezeptbild", ""),
                "name": rezept.get("name", ""),
                "Zutaten": rezept.get("Zutaten", ""),
                "Zubereitung": rezept.get("Zubereitung", ""),
                "Zubereitungszeit": rezept.get("Zubereitungszeit", ""),
                "Kategorie": rezept.get("Kategorie", ""),
            })

    return render(request, "LeckerMeister/Suchseite.html", {"rezepte": rezepte_formatted})





# Upload eines neuen Rezeptes
def Upload(request):

    # Benutzername aus der Session abrufen
    benutzer_name = request.session.get("benutzer_name")

    # Falls kein Benutzer angemeldet ist --> Anmeldeseite
    if not benutzer_name:
        return redirect("Anmeldung.html")

    if request.method == 'POST':
        # Formulardaten abrufen
        rezept_name = request.POST.get('recipeName')
        rezept_bild = request.FILES.get('recipeImage')
        zutaten_str = request.POST.get('ingredients')  # Zutaten als Zeichenkette abrufen
        zutaten = [z.strip() for z in zutaten_str.split(',')]  # Zutaten aufteilen und Leerzeichen entfernen
        zubereitung_str = request.POST.get('instructions')  # Zubereitung als Zeichenkette abrufen
        zubereitung = [step.strip() for step in zubereitung_str.split(',')]  # Zubereitung aufteilen und Leerzeichen entfernen
        zubereitungszeit = request.POST.get('preparationTime')
        kategorie = request.POST.get('category')
	    
        rezept_filename = "/var/www/django-projekt/LeckerMeister/Rezepte.json"
        # Laden der Rezepte aus der JSON-Datei
        try:
            with open(rezept_filename, 'r') as file:
                rezepte = json.load(file)
        except FileNotFoundError:
            rezepte = []

        # ID für das neue Rezept bestimmen
        if rezepte:
            neue_id = max(rezept.get("id", 0) for rezept in rezepte) + 1 # höchste id finden und +1 addieren
        else:
            neue_id = 1 # falls keine Rezepte, start mit 1

        # neues Rezept erstellen
        neues_rezept = {
            "id": neue_id,
            "Ersteller": benutzer_name,
            "Rezeptbild": rezept_bild.name,  
            "name": rezept_name,
            "Zutaten": zutaten,
            "Zubereitung": zubereitung,
            "Zubereitungszeit": zubereitungszeit,
            "Kategorie": kategorie
        }

        # Rezept wird zur Liste an 1. Stelle hinzugefügt 
        rezepte.insert(0, neues_rezept)
        # aktualisierte Rezeptdaten in die JSON-Datei
        with open(rezept_filename, 'w') as file:
            json.dump(rezepte, file, indent=4)

        # Rezeptbild in /static/uploads Ordner speichern
        with open(f'/var/www/static/uploads/{rezept_bild.name}', 'wb+') as destination:
            # Daten des Bildes in kleine Stücke 
            for chunk in rezept_bild.chunks():
                destination.write(chunk)

        return redirect("Homeseite.html")

    return render(request, 'LeckerMeister/Upload.html')



# Kochbuch = Speicherort für interessante Rezepte 
def Kochbuch(request):

    # Benutzername aus der Session abrufen
    benutzer_name = request.session.get("benutzer_name")

    # Falls kein Benutzer angemeldet ist --> Anmeldeseite
    if not benutzer_name:
        return redirect("Anmeldung.html")

    # Pfade zu den Dateien
    user_data_filename = "/var/www/django-projekt/LeckerMeister/user_Data.json"
    rezept_filename = "/var/www/django-projekt/LeckerMeister/Rezepte.json"

    # Lade Benutzerdaten aus der JSON-Datei
    with open(user_data_filename, "r", encoding="utf-8") as file:
        user_data_list = json.load(file)


    # Suche nach dem Benutzer in der Liste
    user_data = None
    for data in user_data_list:
        if data["name"] == benutzer_name:
            user_data = data
            break

    if user_data is None:
        return HttpResponse(f"Der Benutzer mit dem Benutzernamen {benutzer_name} wurde nicht gefunden.")

    # Lade gespeicherte Rezepte des Benutzers
    saved_recipe_ids = user_data.get("gespeicherte_Rezepte", [])  # Annahme: gespeicherte_Rezepte ist eine Liste von Rezept-IDs

    # Lade Rezepte aus der JSON-Datei
    with open(rezept_filename, "r") as file:
        rezepte_list = json.loads(file.read())

    # Filtere die Rezepte, die der Benutzer gespeichert hat
    gespeicherte_rezepte = [rezept for rezept in rezepte_list if rezept.get("id") in saved_recipe_ids]

    return render(request, 'LeckerMeister/Kochbuch.html', {'gespeicherte_rezepte': gespeicherte_rezepte})



# Profilseite: Anzeige für persönliche Daten und einene Rezepten
def Profil(request):

    # Benutzername aus der Session abrufen
    benutzer_name = request.session.get("benutzer_name")

    # Falls kein Benutzer angemeldet ist --> Anmeldeseite
    if not benutzer_name:
        return redirect("Anmeldung.html")

    user_data_filename = "/var/www/django-projekt/LeckerMeister/user_Data.json"
    rezept_filename = "/var/www/django-projekt/LeckerMeister/Rezepte.json"

    # Benutzerdaten aus JSON-Datei laden
    if not os.path.isfile(user_data_filename):
        return HttpResponse(f"Die Datei {user_data_filename} existiert nicht oder ist nicht zugaenglich.")

    with open(user_data_filename, "r", encoding="utf-8") as file: 
        user_data_list = json.load(file)

    # Benutzer in der Liste suchen 
    user_data = next((data for data in user_data_list if data["name"] == benutzer_name), None)
    if user_data is None:
        return HttpResponse(f"Der Benutzer mit dem Benutzernamen {benutzer_name} wurde nicht gefunden.")

    # Rezepte des Benutzers laden
    if not os.path.isfile(rezept_filename):
        return HttpResponse(f"Die Datei {rezept_filename} existiert nicht oder ist nicht zugänglich.")

    with open(rezept_filename, "r", encoding="utf-8") as file:
        rezepte_list = json.load(file)

    # Filtern der Eignenen Rezepte des Benutzers mit Abgleich Ersteller und Benutzername
    eigene_rezepte = [rezept for rezept in rezepte_list if rezept.get("Ersteller") == benutzer_name]

    # Variablen für Rezeptdarstellung
    img_path = user_data.get("Profilbild", "")

    vars = {
        "Profilbild": img_path,
        "Name": user_data.get("name", ""),
        "EMail": user_data.get("email", ""),
        "Wohnort": user_data.get("Wohnort", ""),
        "Bio": user_data.get("bio", ""),
        "Passwort": user_data.get("Passwort", ""),
        "eigene_rezepte": eigene_rezepte  
    }

    return render(request, "LeckerMeister/Profil.html", vars)


# Datenschutz
def Datenschutz(request):

    # Benutzername aus der Session abrufen
    benutzer_name = request.session.get("benutzer_name")

    # Falls kein Benutzer angemeldet ist --> Anmeldeseite
    if not benutzer_name:
        return HttpResponse("Benutzer nicht angemeldet oder Session abgelaufen.")

    return render(request, "LeckerMeister/Datenschutz.html")



# Impressum
def Impressum(request):

    # Benutzername aus der Session abrufen
    benutzer_name = request.session.get("benutzer_name")

    # Falls kein Benutzer angemeldet ist --> Anmeldeseite
    if not benutzer_name:
        return HttpResponse("Benutzer nicht angemeldet oder Session abgelaufen.")

    return render(request, "LeckerMeister/Impressum.html")



# AGB
def AGB(request):

    # Benutzername aus der Session abrufen
    benutzer_name = request.session.get("benutzer_name")

    # Falls kein Benutzer angemeldet ist --> Anmeldeseite
    if not benutzer_name:
        return HttpResponse("Benutzer nicht angemeldet oder Session abgelaufen.")

    return render(request, "LeckerMeister/AGB.html")


# Abmeldung
def Abmeldung(request):
    # Sitzung beenden
    request.session.flush()

    # Sitzungsdatei löschen
    session_file_path = os.path.join(settings.SESSION_FILE_PATH, f'sessionid{request.session.session_key}')
    if os.path.exists(session_file_path):
        os.remove(session_file_path)

    return redirect('Anmeldung')



# Speicher-Funktion für die Rezepte 
def save_recipe(request, recipe_id):

    # Benutzername aus der Session abrufen
    benutzer_name = request.session.get("benutzer_name")
    
    # Falls kein Benutzer angemeldet ist --> Anmeldeseite
    if not benutzer_name:
        return HttpResponse("Unauthorized", status=401)

    # Laden der Benutzerdaten aus der JSON-Datei 
    user_data_file = "/var/www/django-projekt/LeckerMeister/user_Data.json"

    try:
        with open(user_data_file, "r") as file:
            user_list = json.load(file)
    except FileNotFoundError:
        user_list = []

    # Durchsuche die Benutzerliste nach dem aktuellen Benutzer und aktualisiere seine gespeicherten Rezepte
    for user in user_list:
        if user['name'] == benutzer_name:
            if 'gespeicherte_Rezepte' not in user:
                user['gespeicherte_Rezepte'] = []
            
            if int(recipe_id) not in user['gespeicherte_Rezepte']:
                user['gespeicherte_Rezepte'].append(int(recipe_id))

            break

    # Speichere die aktualisierten Benutzerdaten zurück in die JSON-Datei
    with open(user_data_file, "w") as file:
        json.dump(user_list, file, indent=4)

    return redirect('Kochbuch')
 


# Löschfunktion für das Löschen aus dem Kochbuch
def remove_recipe(request, recipe_id):

    # Benutzername aus der Session abrufen
    benutzer_name = request.session.get("benutzer_name")
    
    if request.method == 'POST':
        if recipe_id:
            # Laden der Benutzerdaten aus der JSON-Datei 
            with open("/var/www/django-projekt/LeckerMeister/user_Data.json", "r") as file:
                user_list = json.load(file)
                for user in user_list:
                    if user['name'] == benutzer_name:
                        # Wenn id vorhanden ist --> Löschen
                        if recipe_id in user['gespeicherte_Rezepte']:
                            user['gespeicherte_Rezepte'].remove(recipe_id)
                            break

            # Speichern der aktualisierten Benutzerdaten in JSON-Datei
            with open("/var/www/django-projekt/LeckerMeister/user_Data.json", "w") as file:
                json.dump(user_list, file, indent=4)

            # Rückgabe für eine JSON-Antwort 
            return JsonResponse({'success': True})
        
    # Rückgabe für eine JSON-Antwort 
    return JsonResponse({'success': False})



# Like-Funktion
def like_rezept(request, recipe_id):

    # Benutzername aus der Session abrufen
    benutzer_name = request.session.get("benutzer_name")

    # Laden der Benutzerdaten aus der JSON-Datei
    with open('/var/www/django-projekt/LeckerMeister/user_Data.json', 'r') as user_file:
        user_list = json.load(user_file)

    # Laden der Rezeptdaten aus der JSON-Datei
    with open('/var/www/django-projekt/LeckerMeister/Rezepte.json', 'r') as rezepte_file:
        rezepte_data = json.load(rezepte_file)
    
    found_user = False  # Flag zur Überprüfung, ob der Benutzer gefunden wurde

    # Durchsuchen der Benutzerliste nach dem aktuellen Benutzer
    for user in user_list:
        if user['name'] == benutzer_name:
            found_user = True
            if 'gelikte_rezepte' not in user:
                user['gelikte_rezepte'] = []
            
            # Prüfen, ob das Rezept bereits geliked wurde
            if int(recipe_id) not in user['gelikte_rezepte']:
                user['gelikte_rezepte'].append(int(recipe_id))

                # Erhöhe die Anzahl der Likes für das Rezept
                for rezept in rezepte_data:
                    if rezept['id'] == int(recipe_id):
                        if 'likes' not in rezept:
                            rezept['likes'] = 0
                        rezept['likes'] += 1
                        break
            else:
                # Wenn das Rezept bereits geliked wurde, entferne den Like
                user['gelikte_rezepte'].remove(int(recipe_id))

                # Reduziere die Anzahl der Likes für das Rezept
                for rezept in rezepte_data:
                    if rezept['id'] == int(recipe_id):
                        if 'likes' not in rezept:
                            rezept['likes'] = 0
                        rezept['likes'] -= 1
                        break

            break

    # Wenn der Benutzer nicht gefunden wurde, Fehlermeldung ausgeben und zurückgeben
    if not found_user:
        print(f"Benutzer '{benutzer_name}' wurde nicht gefunden.")
        return HttpResponse(status=404) 

    # Speichere die aktualisierten Benutzerdaten zurück in die JSON-Datei
    with open('/var/www/django-projekt/LeckerMeister/user_Data.json', 'w') as user_file:
        json.dump(user_list, user_file, indent=4)
    
    # Speichere die aktualisierten Rezeptdaten zurück in die JSON-Datei
    with open('/var/www/django-projekt/LeckerMeister/Rezepte.json', 'w') as rezepte_file:
        json.dump(rezepte_data, rezepte_file, indent=4)
