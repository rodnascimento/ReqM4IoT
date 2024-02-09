# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import sys
sys.path.insert(0, '/home/bruno/ReqM4IoT/ReqM4IoT/apps/home/funcoesutilitarias.py')
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
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
from django.contrib.auth import authenticate, login
from .forms import EditUserForm


@login_required(login_url="/login/")
def index(request):
    context = {'segment': 'index'}
    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def salva_projeto(request):
    nome = request.POST.get("projeto-nome")
    descricao = request.POST.get("descricao")
    criar_projeto({'nome': nome, 'descricao':descricao}, request.user.id)
    return render(request, 'home/choice.html')

@login_required(login_url="/login/")
def projetos(request):
    projetos_usuario = list(filtrar_projetos_usuario(request.user))
    projetos_usuario = formatar_projetos_usuario(projetos_usuario, request.user)

    return render(request, 'home/index.html',{'projetos': projetos_usuario})

def membros(request):
    usuario_atual = request.user.id
    projeto_id = request.POST.get('id_projeto', '')
    membros=''
    usuarios = []
    try:
        usuarios = ProjetosUsuarios.objects.filter(projeto=projeto_id)
        usuarios = [i for i in usuarios.values_list('user', flat=True)]
        usuarios.pop(usuarios.index(usuario_atual))
        usuarios = [User.objects.get(id=i) for i in usuarios]
        print(usuarios)
    except:
        print("deu ruim")

    membros = ""
    for usuario in usuarios:
        membros += "<tr>"
        membros += f"<td>{usuario.username}</td>"
        membros += f'<td><a class="btn btn-danger excluir-membro" data-usuario-id="{usuario.id}"><i class="bi bi-trash"></i> Excluir</a></td>'
        membros += "</tr>"

    # Script JavaScript para manipular o clique nos botões de exclusão
    script_js = '''
    <script>
        document.addEventListener('click', function (event) {
            if (event.target.classList.contains('excluir-membro')) {
                var usuarioId = event.target.getAttribute('data-usuario-id');
                $.ajax({
                    url: "{% url 'excluir_membro'%}",
                    type: 'POST',
                    data: {
                        csrfmiddlewaretoken: $('{% csrf_token %}').val(),
                        id_usuario: usuarioId
                    },
                    success: function (data) {
                        // Se a exclusão for bem-sucedida, você pode querer recarregar a lista de membros
                        // por exemplo:
                        // window.location.reload();
                    },
                    error: function (error) {
                        console.log(error);
                    }
                });
            }
        });
    </script>
    '''

    membros=membros+script_js

    html_code = f'''
        <div class="table-responsive">
            <h4>Membros participantes: </h4>
            <table class="table tablesorter ">
            
            <thead class=" text-primary">
                
                    <tr>
                    <th>
                    membro
                    </th>
                    <th>
                    ação
                    </th>
                    </tr>
                </thead>
                <tbody>
                    {membros}
                </tbody>
            </table>
            
        </div>
    '''
    return JsonResponse({'html_code': html_code})

@login_required(login_url="/login/")
def excluir_membro(request):
    if request.method == 'POST' and request.is_ajax():
        usuario_id = request.POST.get('id_usuario')
        # Coloque sua lógica para excluir o membro aqui
        # Por exemplo:
        # Membro.objects.get(id=usuario_id).delete()
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False})

@login_required(login_url="/login/")
def editar_projeto(request, id):
    vnome = request.POST.get("projeto-nome")
    descricao = request.POST.get("descricao")
    projeto = Projetos.objects.get(id=id)
    projeto.nome_projeto = vnome
    projeto.descricao = descricao
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
    
    escolha = request.POST.get('escolha', projetos_usuario[0]['id'])
    try:
        escolha = Projetos.objects.get(id=escolha)
        nome=escolha.nome_projeto
        requisitos_funcionais = obter_requisitos(escolha)
        lista_de_objetos = [{'chave': chave, 'valor': valor} for chave, valor in requisitos_funcionais.items()]
    except Exception as e:
        dados = {
        'requisitos_funcionais': [],
        'requisitos_nao_funcionais': {},
        'casos_de_uso': [],
        'maquina_de_estados': [{'nome': 'Texto', 'imagem': 'texto'}],
        'sequencia': [{'nome': 'Texto', 'imagem': 'texto'}],
        'requisitos_iot': {"Contextualizados":[], "SensoresIncompletos":[],"AtuadoresIncompletos":[]},
        'classificador': {
            'centroids': False,
            'labels': False
            }
        }
        escolha=Projetos(dados=json.dumps(dados),nome_projeto="",id_criador=0)
        nome=escolha.nome_projeto
        escolha.id=0
        requisitos_funcionais={}
    

    requisitos_iot = json.loads(escolha.dados)['requisitos_iot']
    Contex = requisitos_iot['Contextualizados']
    Sensores = requisitos_iot['SensoresIncompletos']
    Atuadores = requisitos_iot["AtuadoresIncompletos"]
    Data = []
    for i in range(len(requisitos_funcionais)):
        aux = []
        aux.append(i in Contex)
        aux.append(i in Sensores)
        aux.append(i in Atuadores)
        if True in aux:
            Data.append((requisitos_funcionais[i][0], aux))
        else:
            continue
    

    return render(request, 'home/requirements.html',  {'escolha': escolha,'nome': nome, 'nomes_projeto': projetos_usuario, "requisitos":lista_de_objetos, 'requisitos_iot':Data})

@login_required(login_url="/login/")
def processamento_requisito(request):
    requisito  = request.POST.get('requisito', '')
    arquivo_requisitos = request.FILES.get('arquivo_requisitos')
    if arquivo_requisitos:
        requisitos = tratar_requisitos(arquivo_requisitos)
        data_sintatico, headings_sintatico, requisitos = caminho(1,requisitos)
        data_ambiguidade, headings_ambiguidade, requisitos = caminho(2,requisitos)
    
    else:

        requisito  = request.POST.get('requisito', '')
        if request.method == 'POST':
            requisito  = request.POST.get('requisito', '')
            data_sintatico, headings_sintatico, requisitos = caminho(1,[requisito])
            data_ambiguidade, headings_ambiguidade, requisitos = caminho(2,[requisito])
    titulo_sintatico = ""
    for head in headings_sintatico:
        titulo_sintatico=titulo_sintatico+f"<th class='text-center'> {head}</th>"
    
    conteudo_sintatico = ""
    for dado in data_sintatico:
        dados = dado[1]
        requisito = dado[0]
        conteudo_sintatico = conteudo_sintatico+"<tr>"
        conteudo_sintatico=conteudo_sintatico+f"<td>{requisito}</td>"
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
        requisito = dado[0]
        conteudo_ambiguidade = conteudo_ambiguidade+"<tr>"
        conteudo_ambiguidade=conteudo_ambiguidade+f"<td>{requisito}</td>"
        for campo in dados:
            if campo:
                conteudo_ambiguidade = conteudo_ambiguidade+"<td><i class='fas fa-times'></i></td>"
            else:
                conteudo_ambiguidade = conteudo_ambiguidade+"<td><i class='fas fa-check'></i></td>"
        conteudo_ambiguidade = conteudo_ambiguidade+"</tr>"

    html_code = f'''
        <div class="table-responsive">
            <h4>Quanto a análise sintática temos: </h4>
            <table class="table tablesorter ">
            
            <thead class=" text-primary">
                
                    <tr>
                    <th>
                    Requisito
                    </th>
                    {titulo_sintatico}
                    </tr>
                </thead>
                <tbody>
                {conteudo_sintatico}
                </tbody>
            </table>

            <h4>Quanto a análise de ambiguidade temos: </h4>
            <table class="table tablesorter ">
            
            <thead class=" text-primary">
                
                    <tr>
                    <th>
                    Requisito
                    </th>
                    {titulo_ambiguidade}
                    </tr>
                </thead>
                <tbody>
                {conteudo_ambiguidade}
                </tbody>
            </table>
            

        </div>
    '''
    return JsonResponse({'html_code': html_code})

def processamento_requisito_editar(request):
    chave  = request.POST.get('chave', '')
    requisito  = request.POST.get('requisito', '')

    if request.method == 'POST':
        requisito  = request.POST.get('requisito', '')
        data_sintatico, headings_sintatico, requisitos = caminho(1,{0:[requisito,'Funcional']})
        data_ambiguidade, headings_ambiguidade, requisitos = caminho(2,{0:[requisito,'Funcional']})
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

    arquivo_requisitos = request.FILES.get('fileInput')
    projeto = Projetos.objects.get(id=id)
    projetos_usuario = list(filtrar_projetos_usuario(request.user))
    projetos_usuario = formatar_projetos_usuario(projetos_usuario, request.user)
    dados = json.loads(projeto.dados)
    if arquivo_requisitos:
        requisitos = tratar_requisitos(arquivo_requisitos)
        for requisito in requisitos:
            if (requisito in dados['requisitos_funcionais']) or (requisito in dados['requisitos_funcionais']):
                pass
            else:
                dados['requisitos_funcionais'].append(requisito)
    else:
        requisito  = request.POST.get('requisito', '')
        dados['requisitos_funcionais'].append(requisito)
    projeto.dados = json.dumps(dados)
    projeto.save()

    return redirect(requirements)


@login_required(login_url="/login/")
def excluir_requisito(request, id, id_requisito):
    projeto = Projetos.objects.get(id=id)
    dados = json.loads(projeto.dados)
    requisito = obter_requisitos(projeto)[id_requisito][0]
    if id_requisito< len(dados['requisitos_funcionais']):
        dados['requisitos_funcionais'].pop(id_requisito)
    else:
        for chave,valor in dados['requisitos_nao_funcionais'].items():
            if requisito in valor:
                dados['requisitos_nao_funcionais'][chave].pop(dados['requisitos_nao_funcionais'][chave].index(requisito))

    projeto.dados = json.dumps(dados)
    projeto.save()
    return redirect(requirements)

def editar_requisito(request, id, id_requisito):
    requisito  = request.POST.get(f'requisito{id_requisito}', '')
    classe  = request.POST.get(f'classe_requisito{id_requisito}', '')
    projeto = Projetos.objects.get(id=id)
    requisitos = obter_requisitos(projeto)
    print(requisitos[id_requisito])
    
    dados = json.loads(projeto.dados)
    if requisitos[id_requisito][1]=='Functional':
        dados['requisitos_funcionais'].pop(id_requisito)
        if classe=='Functional':
            dados['requisitos_funcionais'].insert(id_requisito,requisito)
        else:
            try:
                dados['requisitos_nao_funcionais'][classe].append(requisito)
            except:
                if classe != '':
                    dados['requisitos_nao_funcionais'][classe]=[requisito] 
    else:
        for chave,valor in dados['requisitos_nao_funcionais'].items():
            if requisitos[id_requisito][0] in valor:
                dados['requisitos_nao_funcionais'][chave].pop(dados['requisitos_nao_funcionais'][chave].index(requisitos[id_requisito][0]))
                break
        if classe=='Functional':
            dados['requisitos_funcionais'].append(requisito) 
        else:
            try:
                dados['requisitos_nao_funcionais'][classe].append(requisito)
            except:
                if classe != '':
                    dados['requisitos_nao_funcionais'][classe]=[requisito]
    projeto.dados = json.dumps(dados)
    projeto.save()
    return redirect(requirements)
    #return render(request, 'home/requirements.html',  {'escolha': projeto,'nome': projeto.nome_projeto, 'nomes_projeto': projetos_usuario, "requisitos":lista_de_objetos, 'requisitos_iot':Data})

@login_required(login_url="/login/")
def classificador_iot(request,id):
    projeto = Projetos.objects.get(id=id)
    dados = json.loads(projeto.dados)
    print(obter_requisitos(projeto))
    save,requisitos_iot,pesos = caminho(3, obter_requisitos(projeto))
    dados['requisitos_iot']=save
    dados['classificador']=pesos
    projeto.dados = json.dumps(dados)
    projeto.save()
    return redirect('requisitos')

@login_required(login_url="/login/")
def usuario(request):
    return render(request, 'home/user.html',{'usuario': request.user})

@login_required(login_url="/login/")
def editar_usuario(request):
    username = request.POST.get('username')
    email = request.POST.get('email')
    senha_atual = request.POST.get('senha_atual')
    senha_nova = request.POST.get('password1')
    confirmar_senha = request.POST.get('password2')
    data = request.POST.copy()  # Copie os dados para evitar alterar o original
    data.pop('senha_atual', None) 
    if(authenticate(username=username, password=senha_atual)):
        if senha_nova==confirmar_senha:
            request.user.set_password(senha_nova)
            request.user.save()
        else:
            print("senhas não são iguais")
    else:
        print("Falso")
    

    return redirect('usuario')



@login_required(login_url="/login/")
def modeling(request):
    projetos_usuario = list(filtrar_projetos_usuario(request.user))
    projetos_usuario = formatar_projetos_usuario(projetos_usuario, request.user)
    
    escolha = request.POST.get('escolha', projetos_usuario[0]['id'])

    escolha = Projetos.objects.get(id=escolha)
    dados = json.loads(escolha.dados)['modelagens']

    nome=escolha.nome_projeto

    return render(request, 'home/modeling.html',{'escolha': escolha,'nome': nome, 'nomes_projeto': projetos_usuario, 'modelagens':dados})

@login_required(login_url="/login/")
def salvar_projeto_modelagem(request,id):
    projetos_usuario = list(filtrar_projetos_usuario(request.user))
    projetos_usuario = formatar_projetos_usuario(projetos_usuario, request.user)

    nome_diagrama = request.POST.get('projeto-nome', '')
    tipo_projeto = request.POST.get('tipo_projeto', '')
    linguagem = request.POST.get('linguagem', '')
    
    escolha = Projetos.objects.get(id=id)
    
    nome=escolha.nome_projeto
    dados = json.loads(escolha.dados)
    
    if(len([float(i) for i in list(dados['modelagens'].keys())])==0):
        indice=0
        aux = {'nome':nome_diagrama,'ling_model':linguagem, 'tipo': tipo_projeto,'dados':'<mxGraphModel><root><mxCell id="0"/><mxCell id="1" parent="0"/></root></mxGraphModel>' }
    else:
        indice = max([int(i) for i in list(dados['modelagens'].keys())])+1
        aux = {'nome':nome_diagrama,'ling_model':linguagem, 'tipo': tipo_projeto,'dados':'<mxGraphModel><root><mxCell id="0"/><mxCell id="1" parent="0"/></root></mxGraphModel>' }
    dados['modelagens'][indice]=aux
    escolha.dados = json.dumps(dados)
    escolha.save()

    return redirect(modeling)

@login_required(login_url="/login/")
def salvar_modelagem(request):
    if request.method == 'POST':
        try:
            xml_data = request.body.decode('utf-8')
            print(xml_data)
            response_data = {'status': 'success', 'message': 'Diagrama salvo com sucesso.'}
            print(response_data)

        except Exception as e:
            response_data = {'status': 'error', 'message': f'Erro ao salvar o diagrama: {str(e)}'}

    return render(request, 'home/modeling.html',)

def about(request):
    return render(request, 'home/about.html',)

def help(request):
    return render(request, 'home/help.html',)

@login_required(login_url="/login/")
def excluir_modelagem(request, id, id_modelagem):
    projeto = Projetos.objects.get(id=id)
    dados = json.loads(projeto.dados)
    dados['modelagens'].pop(str(id_modelagem))
    indices=[i for i in list(dados['modelagens'].keys())]
    novos_dados={}
    for i, indice in enumerate(indices):
        novos_dados[str(i)]=dados['modelagens'][indice]
    dados['modelagens']=novos_dados
    projeto.dados = json.dumps(dados)
    projeto.save()
    return redirect(modeling)

@login_required(login_url="/login/")
def editar_projeto_modelagem(request,id,id_modelagem):
    nome_diagrama = request.POST.get('projeto-nome', '')
    tipo_projeto = request.POST.get('tipo_projeto', '')
    linguagem = request.POST.get('linguagem', '')
    escolha = Projetos.objects.get(id=id)
    nome=escolha.nome_projeto
    dados = json.loads(escolha.dados)
    modelagem_anterior = dados['modelagens'][str(id_modelagem)]['dados']
    dados['modelagens'].pop(str(id_modelagem))
    aux = {'nome':nome_diagrama,'ling_model':linguagem, 'tipo': tipo_projeto,'dados':modelagem_anterior}
    dados['modelagens'][str(id_modelagem)]=aux
    escolha.dados = json.dumps(dados)
    escolha.save()

    return redirect(modeling)

