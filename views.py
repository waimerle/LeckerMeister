from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
import json, os
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt


def Anmeldung(request):
    user_filename = "/var/www/django-projekt/LeckerMeister/user_Data.json"

    with open(user_filename, "r", encoding="utf-8") as file:
        user_list = json.load(file)

    if request.method == 'POST':
        benutzer_name = request.POST.get('benutzer_name')
        password = request.POST.get('Passwort')
        
        for user in user_list:
            if user['name'] == benutzer_name and user['Passwort'] == password:
                request.session['benutzer_name'] = benutzer_name
                return redirect('Homeseite.html')

    return render(request, 'LeckerMeister/Anmeldung.html')

def Registrierung(request):

    if request.method == 'POST':
        # Formulardaten abrufen
        benutzer_name = request.POST.get('benutzer_name')
        profil_bild = request.FILES.get('profil_bild')
        email = request.POST.get('email')
        Wohnort = request.POST.get('Wohnort')
        Biografie = request.POST.get('Biografie') 
        Passwort = request.POST.get('Passwort')

        profil_bild_name = profil_bild.name if profil_bild else None

        neuer_Benutzer = {
            "Profilbild": profil_bild_name, 
            "name": benutzer_name, 
            "email": email,
            "Wohnort": Wohnort,
            "Passwort": Passwort,
            "bio": Biografie
        }

        user_filename = "/var/www/django-projekt/LeckerMeister/user_Data.json"
        try:
            with open(user_filename, 'r') as file:
                benutzer = json.load(file)
        except FileNotFoundError:
            benutzer = []

        benutzer.append(neuer_Benutzer)

        with open(user_filename, 'w') as file:
            json.dump(benutzer, file, indent=4)


        if profil_bild:
            with open(f'/var/www/static/users/{profil_bild.name}', 'wb+') as destination:
                for chunk in profil_bild.chunks():
                    destination.write(chunk)

        return redirect("Anmeldung.html")

    return render(request, 'LeckerMeister/Registrierung.html')



def Homeseite(request):
    benutzer_name = request.session.get("benutzer_name")

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
        ersteller_data = next((user for user in user_data if user["name"] == ersteller_name), None)
        
        if ersteller_data:
            rezepte.append({
                "Ersteller": ersteller_name,
                "Profilbild": ersteller_data.get("Profilbild", ""),  # Profilbild des Erstellers hinzufügen
                "Rezeptbild": rezept.get("Rezeptbild", ""),
                "name": rezept.get("name", ""),
                "Zutaten": rezept.get("Zutaten", ""),
                "Zubereitung": rezept.get("Zubereitung", ""),
                "Zubereitungszeit": rezept.get("Zubereitungszeit", ""),
                "Kategorie": rezept.get("Kategorie", ""),
            })

    # Rendern der HTML-Seite mit den Rezepten als Kontext
    return render(request, "LeckerMeister/Homeseite.html", {"rezepte": rezepte})


def Suchseite(request):
    benutzer_name = request.session.get("benutzer_name")

    if not benutzer_name:
        return redirect("Anmeldung.html")

    Rezept_Filename = "/var/www/django-projekt/LeckerMeister/Rezepte.json"

    with open(Rezept_Filename, "r") as file:
        Rezept_list = json.loads(file.read())

    query = request.GET.get('query')
    category = request.GET.get('category')

    rezepte = Rezept_list

    if query:
        rezepte = [rezept for rezept in rezepte if query.lower() in rezept.get('name', '').lower()]

    if category:
        rezepte = [rezept for rezept in rezepte if rezept.get('Kategorie') == category]

    return render(request, "LeckerMeister/Suchseite.html", {"rezepte": rezepte})

def Upload(request):
    benutzer_name = request.session.get("benutzer_name")

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

        neues_rezept = {
            "Ersteller": benutzer_name,
            "Rezeptbild": rezept_bild.name,  # Bildname speichern, tatsÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Â ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¤chliche Handhabung erforderlich
            "name": rezept_name,
            "Zutaten": zutaten,
            "Zubereitung": zubereitung,
            "Zubereitungszeit": zubereitungszeit,
            "Kategorie": kategorie
        }

        rezept_filename = "/var/www/django-projekt/LeckerMeister/Rezepte.json"
        try:
            with open(rezept_filename, 'r') as file:
                rezepte = json.load(file)
        except FileNotFoundError:
            rezepte = []


        rezepte.insert(0, neues_rezept)

        with open(rezept_filename, 'w') as file:
            json.dump(rezepte, file, indent=4)

	
        with open(f'/var/www/static/uploads/{rezept_bild.name}', 'wb+') as destination:
            for chunk in rezept_bild.chunks():
                destination.write(chunk)

        return redirect("Homeseite.html")

    return render(request, 'LeckerMeister/Upload.html')

def Kochbuch(request):
    benutzer_name = request.session.get("benutzer_name")

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

def Profil(request):
    benutzer_name = request.session.get("benutzer_name")

    if not benutzer_name:
        return redirect("Anmeldung.html")

    user_data_filename = "/var/www/django-projekt/LeckerMeister/user_Data.json"

    if not os.path.isfile(user_data_filename):
        return HttpResponse(f"Die Datei {user_data_filename} existiert nicht oder ist nicht zugaenglich.")

    with open(user_data_filename, "r", encoding="utf-8") as file: 
        user_data_list = json.load(file)

    user_data = None
    for data in user_data_list:
        if data["name"] == benutzer_name:
            user_data = data
            break

    if user_data is None:
        return HttpResponse(f"Der Benutzer mit dem Benutzernamen {benutzer_name} wurde nicht gefunden.")

    img_path = user_data.get("Profilbild", "")

    vars = {
        "Profilbild": img_path,
        "Name": user_data.get("name", ""),
        "EMail": user_data.get("email", ""),
        "Wohnort": user_data.get("Wohnort", ""),
        "Bio": user_data.get("bio", ""),
        "Passwort": user_data.get("Passwort", "")
    }

    return render(request, "LeckerMeister/Profil.html", vars)

def Datenschutz(request):
    benutzer_name = request.session.get("benutzer_name")

    if not benutzer_name:
        return HttpResponse("Benutzer nicht angemeldet oder Session abgelaufen.")

    return render(request, "LeckerMeister/Datenschutz.html")

def Impressum(request):
    benutzer_name = request.session.get("benutzer_name")

    if not benutzer_name:
        return HttpResponse("Benutzer nicht angemeldet oder Session abgelaufen.")

    return render(request, "LeckerMeister/Impressum.html")

def AGB(request):
    benutzer_name = request.session.get("benutzer_name")

    if not benutzer_name:
        return HttpResponse("Benutzer nicht angemeldet oder Session abgelaufen.")

    return render(request, "LeckerMeister/AGB.html")

def Abmeldung(request):
    # Sitzung beenden
    request.session.flush()

    # Sitzungsdatei loeschen (optional)
    session_file_path = os.path.join(settings.SESSION_FILE_PATH, f'sessionid{request.session.session_key}')
    if os.path.exists(session_file_path):
        os.remove(session_file_path)

    return redirect('Anmeldung')

def save_recipe(request):
    benutzer_name = request.session.get("benutzer_name")
    
    with open("/var/www/django-projekt/LeckerMeister/user_Data.json", "r") as file:
        user_list = json.load(file)
        for user in user_list:
            if user['name'] == benutzer_name:
                user['gespeicherte_Rezepte'] = []
                
                with open("/var/www/django-projekt/LeckerMeister/Rezepte.json", "r") as rezepte_file:
                    rezepte_data = json.load(rezepte_file)
                    for rezept in rezepte_data:
                        user['gespeicherte_Rezepte'].append(rezept['id'])  # Adjust to match your JSON structure

    with open("/var/www/django-projekt/LeckerMeister/user_Data.json", "w") as file:
        json.dump(user_list, file, indent = 4)
    
    return redirect('Kochbuch')

def remove_recipe(request, recipe_id):
    benutzer_name = request.session.get("benutzer_name")
    
    if request.method == 'POST':
        if recipe_id:
            with open("/var/www/django-projekt/LeckerMeister/user_Data.json", "r") as file:
                user_list = json.load(file)
                for user in user_list:
                    if user['name'] == benutzer_name:
                        if recipe_id in user['gespeicherte_Rezepte']:
                            user['gespeicherte_Rezepte'].remove(recipe_id)
                            break

            with open("/var/www/django-projekt/LeckerMeister/user_Data.json", "w") as file:
                json.dump(user_list, file, indent=4)

            return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})
