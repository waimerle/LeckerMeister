from django.shortcuts import render
from django.http import HttpResponse
import json, os

def Anmeldung(request):
	return render(request, "LeckerMeister/Anmeldung.html")

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
        zutaten = request.POST.get('ingredients')
        zubereitung = request.POST.get('instructions')
        kategorie = request.POST.get('category')

        neues_rezept = {
            "Rezeptbild": rezept_bild.name,  # Bildname speichern, tatsÃ¤chliche Handhabung erforderlich
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


        rezepte.append(neues_rezept)

        with open(rezept_filename, 'w') as file:
            json.dump(rezepte, file, indent=4)


        with open(f'/var/www/django-projekt/LeckerMeister/uploads/{rezept_bild.name}', 'wb+') as destination:
            for chunk in rezept_bild.chunks():
                destination.write(chunk)

        return HttpResponse("Rezept erfolgreich hochgeladen")

    return render(request, 'LeckerMeister/Upload.html')

def Kochbuch(request):
	return render(request, "LeckerMeister/Kochbuch.html")

def Profil(request):
	nutzer = request.GET.get("nutzer", False)
	user_Data_Filename = "/var/www/django-projekt/LeckerMeister/user_Data.json"

	if not os.path.isfile(user_Data_Filename):
		return HttpResponse(f"Der User mit dem Benutzername {nutzer} existiert nicht!")

	with open(user_Data_Filename, "r") as file: 
		user_Data_list = json.load(file)

	user_Data = None
	for data in user_Data_list:
		if data["name"] == nutzer:
			user_Data = data
			break

	if user_Data is None:
		return HttpResponse(f"Der Benutzer mit dem Benutzernamen {nutzer} existiert nicht!")


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


