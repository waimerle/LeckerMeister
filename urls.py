from django.urls import path
from LeckerMeister import views as app_views
from . import views

urlpatterns = [
	path("Anmeldung.html", app_views.Anmeldung, name='Anmeldung'),
	path("Abmeldung/", app_views.Abmeldung, name='Abmeldung'),
	path("Registrierung.html", app_views.Registrierung, name='registrierung'),
	path("Homeseite.html", app_views.Homeseite, name='Homeseite'),
	path("Suchseite.html", app_views.Suchseite, name='Suchseite'),
	path("Upload.html", app_views.Upload, name='Upload'),
	path("Kochbuch.html", app_views.Kochbuch, name='Kochbuch'),
	path("Profil.html", app_views.Profil, name='Profil'),
	path("AGB.html", app_views.AGB, name='AGB'),
	path("Datenschutz.html", app_views.Datenschutz, name='Datenschutz'),
	path("Impressum.html", app_views.Impressum, name='Impressum'),
	path('save_recipe/<int:recipe_id>/', app_views.save_recipe, name='save_recipe'),
	path('remove_recipe/<int:recipe_id>/', views.remove_recipe, name='remove_recipe'),
	path('like_rezept/<int:recipe_id>/', views.like_rezept, name='like_rezept'),

]
