# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import sys
sys.path.insert(0, '/home/bruno/ReqM4IoT/ReqM4IoT/apps/home/funcoesutilitarias.py')

from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.shortcuts import render, redirect
from .funcoesutilitarias import *
from django.contrib.auth.models import User



@login_required(login_url="/login/")
def index(request):
    context = {'segment': 'index'}
    print(context)
    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def pages(request):
    context = {}
    
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template

        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def salva_projeto(request):
    nome = request.POST.get("projeto-nome")
    criar_projeto({'nome': nome}, request.user.id)
    return render(request, 'home/choice.html')

@login_required(login_url="/login/")
def projetos(request):
    
    projetos_usuario = list(filtrar_projetos_usuario(request.user))
    projetos_usuario = formatar_projetos_usuario(projetos_usuario)
    return render(request, 'home/index.html',{'projetos': projetos_usuario})

@login_required(login_url="/login/")
def editar_projeto(request, id):
    vnome = request.POST.get("projeto-nome")
    projeto = Projetos.objects.get(id=id)
    projeto.nome_projeto = vnome
    projeto.save()
    return redirect(projetos)

@login_required(login_url="/login/")
def excluir_projeto(request, id):
    projeto = Projetos.objects.get(id=id)
    id_criador = projeto.id_criador
    if (request.user.id == id_criador):
        projeto = Projetos.objects.get(id=id)
        projeto.delete()
    else:
        messages.info(request, "Você não é o proprietário do projeto, portanto não pode exclui-lo!!!")
    return redirect(projetos)

@login_required(login_url="/login/")
def escolha(request, id):
    if id==1:
        return render(request, 'home/requirements.html')
    else:
        return render(request, 'home/modeling.html')

@login_required(login_url="/login/")
def requirements(request):
    return render(request, 'home/requirements.html')

@login_required(login_url="/login/")
def modeling(request):
    return render(request, 'home/modeling.html')

