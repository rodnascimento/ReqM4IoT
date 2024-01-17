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
from django.contrib import messages
from django.http import JsonResponse
import json



@login_required(login_url="/login/")
def index(request):
    context = {'segment': 'index'}
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
    projetos_usuario = formatar_projetos_usuario(projetos_usuario, request.user)
    return render(request, 'home/index.html',{'projetos': projetos_usuario})

@login_required(login_url="/login/")
def editar_projeto(request, id):
    vnome = request.POST.get("projeto-nome")
    projeto = Projetos.objects.get(id=id)
    projeto.nome_projeto = vnome
    projeto.save()
    return redirect(projetos)

@login_required(login_url="/login/")
def adicionar_membro(request, id):
    vnome = request.POST.get("membro")
    usuario = User.objects.filter(username=vnome).first()
    if usuario:
        projeto = Projetos.objects.get(id=id)
        projeto_usuario = ProjetosUsuarios(user=usuario,projeto=projeto)
        projeto_usuario.save()
    else:
        print("Usuário não existente")

    return redirect(projetos)

@login_required(login_url="/login/")
def sair_membro(request, id):
    projeto = Projetos.objects.get(id=id)
    projeto_usuario = ProjetosUsuarios.objects.get(user=request.user,projeto=projeto)
    projeto_usuario.delete()

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
    projetos_usuario = list(filtrar_projetos_usuario(request.user))
    projetos_usuario = formatar_projetos_usuario(projetos_usuario, request.user)
    escolha = request.POST.get('escolha', '')
    try:
        escolha = Projetos.objects.get(id=escolha)
        nome=escolha.nome_projeto
        requisitos = obter_requisitos(escolha)

    except:
        dados = {
        'requisitos_funcionais': [],
        'requisitos_nao_funcionais': {},
        'casos_de_uso': [],
        'maquina_de_estados': [{'nome': 'Texto', 'imagem': 'texto'}],
        'sequencia': [{'nome': 'Texto', 'imagem': 'texto'}],
        'requisitos_iot': {}
        }
        escolha=Projetos(dados=json.dumps(dados),nome_projeto="",id_criador=0)
        nome=escolha.nome_projeto
        escolha.id=0
        requisitos={}
    
    return render(request, 'home/requirements.html',  {'escolha': escolha,'nome': nome, 'nomes_projeto': projetos_usuario, "requisitos":requisitos})

@login_required(login_url="/login/")
def processamento_requisito(request):
    requisito  = request.POST.get('requisito', '')
    print(requisito)
    if request.method == 'POST':
        requisito  = request.POST.get('requisito', '')
        data_sintatico, headings_sintatico, requisitos = caminho(1,["Req 1:"+requisito])
        data_ambiguidade, headings_ambiguidade, requisitos = caminho(2,["Req 1:"+requisito])
    titulo_sintatico = ""
    for head in headings_sintatico:
        titulo_sintatico=titulo_sintatico+f"<th class='text-center'> {head}</th>"
    conteudo_sintatico = ""
    for dado in data_sintatico:
        dados = dado[1]
        conteudo_sintatico = conteudo_sintatico+"<tr>"
        for campo in dados:
            if campo:
                conteudo_sintatico = conteudo_sintatico+"<td><i class='fas fa-times'></i></td>"
            else:
                conteudo_sintatico = conteudo_sintatico+"<td><i class='fas fa-check'></i></td>"
        conteudo_sintatico = conteudo_sintatico+"</tr>"
    titulo_ambiguidade= ""
    for head in headings_ambiguidade:
        titulo_ambiguidade=titulo_ambiguidade+f"<th class='text-center'> {head}</th>"
    conteudo_ambiguidade = ""
    for dado in data_ambiguidade:
        dados = dado[1]
        conteudo_ambiguidade = conteudo_ambiguidade+"<tr>"
        for campo in dados:
            if campo:
                conteudo_ambiguidade = conteudo_ambiguidade+"<td><i class='fas fa-times'></i></td>"
            else:
                conteudo_ambiguidade = conteudo_ambiguidade+"<td><i class='fas fa-check'></i></td>"
        conteudo_ambiguidade = conteudo_ambiguidade+"</tr>"

    html_code = f'''
        <div class="table-responsive">
            <table class="table tablesorter " id="">
            <h4>Quanto a análise sintática temos: </h4>
            <thead class=" text-primary">
                <tr>
                {titulo_sintatico}
                </tr>
            </thead>
            <tbody>
            {conteudo_sintatico}
        </div>
        <div class="table-responsive">
            <table class="table tablesorter " id="">
            <h4>Quanto a análise de ambiguidade temos: </h4>
            <thead class=" text-primary">
                <tr>
                {titulo_ambiguidade}
                </tr>
            </thead>
            <tbody>
            {conteudo_ambiguidade}
        </div>
    '''
    return JsonResponse({'html_code': html_code})

def processamento_requisito_editar(request):
    chave  = request.POST.get('chave', '')
    requisito  = request.POST.get('requisito', '')
    if request.method == 'POST':
        requisito  = request.POST.get('requisito', '')
        data_sintatico, headings_sintatico, requisitos = caminho(1,["Req 1:"+requisito])
        data_ambiguidade, headings_ambiguidade, requisitos = caminho(2,["Req 1:"+requisito])
    titulo_sintatico = ""
    for head in headings_sintatico:
        titulo_sintatico=titulo_sintatico+f"<th class='text-center'> {head}</th>"
    conteudo_sintatico = ""
    for dado in data_sintatico:
        dados = dado[1]
        conteudo_sintatico = conteudo_sintatico+"<tr>"
        for campo in dados:
            if campo:
                conteudo_sintatico = conteudo_sintatico+"<td><i class='fas fa-times'></i></td>"
            else:
                conteudo_sintatico = conteudo_sintatico+"<td><i class='fas fa-check'></i></td>"
        conteudo_sintatico = conteudo_sintatico+"</tr>"
    titulo_ambiguidade= ""
    for head in headings_ambiguidade:
        titulo_ambiguidade=titulo_ambiguidade+f"<th class='text-center'> {head}</th>"
    conteudo_ambiguidade = ""
    for dado in data_ambiguidade:
        dados = dado[1]
        conteudo_ambiguidade = conteudo_ambiguidade+"<tr>"
        for campo in dados:
            if campo:
                conteudo_ambiguidade = conteudo_ambiguidade+"<td><i class='fas fa-times'></i></td>"
            else:
                conteudo_ambiguidade = conteudo_ambiguidade+"<td><i class='fas fa-check'></i></td>"
        conteudo_ambiguidade = conteudo_ambiguidade+"</tr>"

    html_code = f'''
        <div class="table-responsive">
            <table class="table tablesorter " id="{chave}1">
            <h4>Quanto a análise sintática temos: </h4>
            <thead class=" text-primary">
                <tr>
                {titulo_sintatico}
                </tr>
            </thead>
            <tbody>
            {conteudo_sintatico}
        </div>
        <div class="table-responsive">
            <table class="table tablesorter " id="{chave}2">
            <h4>Quanto a análise de ambiguidade temos: </h4>
            <thead class=" text-primary">
                <tr>
                {titulo_ambiguidade}
                </tr>
            </thead>
            <tbody>
            {conteudo_ambiguidade}
        </div>
    '''
    return JsonResponse({'html_code': html_code})

@login_required(login_url="/login/")
def salvar_requisito(request, id):
    requisito  = request.POST.get('requisito', '')
    projeto = Projetos.objects.get(id=id)
    dados = json.loads(projeto.dados)
    dados['requisitos_funcionais'].append(requisito)
    projeto.dados = json.dumps(dados)
    projeto.save()
    projetos_usuario = list(filtrar_projetos_usuario(request.user))
    projetos_usuario = formatar_projetos_usuario(projetos_usuario, request.user)
    return render(request, 'home/requirements.html',  {'escolha': projeto,'nome': projeto.nome_projeto, 'nomes_projeto': projetos_usuario, "requisitos":obter_requisitos(projeto)})

@login_required(login_url="/login/")
def excluir_requisito(request, id, id_requisito):
    projeto = Projetos.objects.get(id=id)
    dados = json.loads(projeto.dados)
    dados['requisitos_funcionais'].pop(id_requisito)
    projeto.dados = json.dumps(dados)
    projeto.save()
    projetos_usuario = list(filtrar_projetos_usuario(request.user))
    projetos_usuario = formatar_projetos_usuario(projetos_usuario, request.user)
    return render(request, 'home/requirements.html',  {'escolha': projeto,'nome': projeto.nome_projeto, 'nomes_projeto': projetos_usuario, "requisitos":obter_requisitos(projeto)})
def editar_requisito(request, id, id_requisito):
    requisito  = request.POST.get(f'requisito{id_requisito}', '')
    projeto = Projetos.objects.get(id=id)
    dados = json.loads(projeto.dados)
    dados['requisitos_funcionais'].pop(id_requisito)
    dados['requisitos_funcionais'].insert(id_requisito,requisito)
    projeto.dados = json.dumps(dados)
    projeto.save()
    projetos_usuario = list(filtrar_projetos_usuario(request.user))
    projetos_usuario = formatar_projetos_usuario(projetos_usuario, request.user)
    return render(request, 'home/requirements.html',  {'escolha': projeto,'nome': projeto.nome_projeto, 'nomes_projeto': projetos_usuario, "requisitos":obter_requisitos(projeto)})


@login_required(login_url="/login/")
def modeling(request):
    return render(request, 'home/modeling.html',)

