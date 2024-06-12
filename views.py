from django.shortcuts import render, redirect
from django.http import HttpResponse
import json, os


def Anmeldung(request):
	user_filename = "/var/www/django-projekt/LeckerMeister/user_Data.json"

	with open(user_filename, "r") as file: 
		user_list = json.load(file)

	if request.method == 'POST':
		benutzer_name = request.POST.get('benutzer_name')
		password = request.POST.get('Passwort')
		for user in user_list:
			if user['name'] == benutzer_name and user['Passwort'] == password:
				return redirect('Homeseite.html')

		return render(request, 'LeckerMeister/Anmeldung.html', {'error': 'UngÃ¼ltiges Passwort'}) 

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

        return redirect("Homeseite.html")

    return render(request, 'LeckerMeister/Registrierung.html')
		


def Homeseite(request):

	Rezept_Filename = "/var/www/django-projekt/LeckerMeister/Rezepte.json"

	with open(Rezept_Filename, "r") as file: 
		Rezept_list = json.loads(file.read())

	rezepte = []
	for rezept in Rezept_list:
		rezepte.append({
			"Rezeptbild": rezept.get("Rezeptbild", ""),
			"name": rezept.get("name", ""),
			"Zutaten": rezept.get("Zutaten", ""),
			"Zubereitung": rezept.get("Zubereitung", ""),
			"Zubereitungszeit": rezept.get("Zubereitungszeit", ""),
			"Kategorie": rezept.get("Kategorie", ""),
		})


	return render(request, "LeckerMeister/Homeseite.html", {"rezepte": rezepte})


def Suchseite(request):
	return render(request, "LeckerMeister/Suchseite.html")

def Upload(request):

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
            "Rezeptbild": rezept_bild.name,  # Bildname speichern, tatsÃƒÂ¤chliche Handhabung erforderlich
            "name": rezept_name,
            "Zutaten": zutaten,
            "Zubereitung": zubereitung,
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
	return render(request, "LeckerMeister/Kochbuch.html")

def Profil(request):
	benutzer = request.GET.get("benutzer", False)
	user_Data_Filename = "/var/www/django-projekt/LeckerMeister/user_Data.json"

	if not os.path.isfile(user_Data_Filename):
		return HttpResponse(f"Der User mit dem Benutzername {benutzer} existiert nicht!")

	with open(user_Data_Filename, "r") as file: 
		user_Data_list = json.load(file)

	user_Data = None
	for data in user_Data_list:
		if data["name"] == benutzer:
			user_Data = data
			break

	if user_Data is None:
		return HttpResponse(f"Der Benutzer mit dem Benutzernamen {benutzer} existiert nicht!")


	img_Pfad = user_Data.get("Profilbild", "")

	vars = {
		"Profilbild": img_Pfad,
		"Name": user_Data.get("name", ""),
		"EMail": user_Data.get("email", ""),
		"Wohnort": user_Data.get("Wohnort",""),
		"Bio": user_Data.get("bio", ""),
		"Passwort": user_Data.get("Passwort", "")
	}
		
	return render(request, "LeckerMeister/Profil.html", vars)

def Datenschutz(request):
	return render(request, "LeckerMeister/Datenschutz.html")

def Impressum(request):
	return render(request, "LeckerMeister/Impressum.html")

def AGB(request):
	return render(request, "LeckerMeister/AGB.html")



