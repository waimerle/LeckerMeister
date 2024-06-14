from django.shortcuts import render, redirect
from django.http import HttpResponse
import json, os

def Allgemein(request):
        return render(request, "LeckerMeister/Allgemein.html")
