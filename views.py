from django.shortcuts import render
from django.http import HttpResponse
import json, os

def Anmeldung(request):
	return render(request, "LeckerMeister/Anmeldung.html")

def Homeseite(request):

	Rezept_Filename = "/var/www/django-projekt/LeckerMeister/Rezepte.json"

	if not os.path.isfile(Rezept_Filename):
		return HttpResponse("Die Rezeptdatei existiert nicht!")

	with open(Rezept_Filename, "r") as file: 
		Rezept_list = json.load(file)

	rezepte = []
	for rezept in Rezept_list:
		rezepte.append({
			"Rezeptbild": rezept.get("Rezeptbild", ""),
			"name": rezept.get("name", ""),
			"Zutaten": rezept.get("Zutaten", ""),
			"Zubereitung": rezept.get("Zubereitung", ""),
			"Zubereitungszeit": rezept.get("Zubereitungszeit", ""),
		})

	return render(request, "LeckerMeister/Homeseite.html", {"rezepte": rezepte})

def Suchseite(request):
	return render(request, "LeckerMeister/Suchseite.html")

def Upload(request):
        return render(request, "LeckerMeister/Upload.html")

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


