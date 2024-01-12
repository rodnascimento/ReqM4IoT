# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import LoginForm, SignUpForm

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
#from .models import GraphData
import json

@csrf_exempt
def save_graph_data(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        # Salvar os dados do gráfico no banco de dados ou em um arquivo
        # Exemplo: GraphData.objects.create(data=data)
        return JsonResponse({'message': 'Graph data saved successfully.'})
    return JsonResponse({'error': 'Invalid request method.'}, status=400)

def load_graph_data(request):
    # Carregar os dados do gráfico do banco de dados ou de um arquivo
    # Exemplo: graph_data = GraphData.objects.first()
    # data = graph_data.data if graph_data else {}
    data = {} # Simulação de dados de carregamento vazios
    return JsonResponse(data)


def login_view(request):
    form = LoginForm(request.POST or None)

    msg = None

    if request.method == "POST":

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("/")
            else:
                msg = 'Invalid credentials'
        else:
            msg = 'Error validating the form'

    return render(request, "accounts/login.html", {"form": form, "msg": msg})


def register_user(request):
    msg = None
    success = False

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=raw_password)

            msg = 'User created successfully.'
            success = True

            # return redirect("/login/")

        else:
            msg = 'Form is not valid'
    else:
        form = SignUpForm()

    return render(request, "accounts/register.html", {"form": form, "msg": msg, "success": success})
