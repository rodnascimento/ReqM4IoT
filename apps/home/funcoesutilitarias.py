from .models import *
from django.contrib.auth.models import User
import json
from django.shortcuts import get_object_or_404

def criar_projeto(dados_projeto, id_usuario):
    '''
    dados = {
        'requisitos_funcionais': [],
        'requisitos_nao_funcionais': {},
        'casos_de_uso': [],
        'maquina_de_estados': [{'nome': Texto, 'imagem': 'texto'}],
        'sequencia': [{'nome': Texto, 'imagem': 'texto'}],
        'requisitos_iot': {}
    }
    dados_projeto = {'nome': 'Nome', 'dados' = None}
    '''
    dados = {
        'requisitos_funcionais': [],
        'requisitos_nao_funcionais': {},
        'casos_de_uso': [],
        'maquina_de_estados': [{'nome': 'Texto', 'imagem': 'texto'}],
        'sequencia': [{'nome': 'Texto', 'imagem': 'texto'}],
        'requisitos_iot': {}
    }
    try:
        projeto = Projetos(dados=json.dumps(dados), nome_projeto=dados_projeto['nome'], id_criador=id_usuario)
        projeto.save()
        try: 
            usuario = get_object_or_404(User, pk=id_usuario)
            projeto_usuario = ProjetosUsuarios(user=usuario, projeto=projeto)
            projeto_usuario.save()
        except Exception as e:
            # Trate o erro de maneira mais específica (ex: log, mensagem)
            print(f"Erro ao deletar projeto: {e}")

        return True
    except Exception as e:
        # Trate o erro de maneira mais específica (ex: log, mensagem)
        print(f"Erro ao criar projeto: {e}")
        return False
'''
def deletar_projeto(pk):
    try:
        projeto = get_object_or_404(Projetos, pk=pk)
        projeto.delete()
        return True
    except Exception as e:
        # Trate o erro de maneira mais específica (ex: log, mensagem)
        print(f"Erro ao deletar projeto: {e}")
        return False
'''
def atualizar_projeto(dados_projeto_original, dados_projeto_novos):
    resultado = Projetos.objects.filter(nome_projeto=dados_projeto_original['nome']).first()
    if resultado:
        resultado.nome_projeto = dados_projeto_novos['nome']
        resultado.dados = dados_projeto_novos['dados']
        resultado.save()
        return True
    return False

def filtrar_projetos_usuario(usuario):
    
    projetos = ProjetosUsuarios.objects.filter(user=usuario.id)
    print(usuario.id)
    return projetos

def formatar_projetos_usuario(projetos,usuario):
    retorno = []
    for projeto in projetos:
        dados = {}
        id_projeto = projeto.projeto.id
        dados_projeto = get_object_or_404(Projetos, id=id_projeto)
        dados['id'] = id_projeto
        dados['nome']= dados_projeto.nome_projeto
        dados['criacao'] = dados_projeto.criacao.strftime("%d/%m/%Y")
        dados['criador'] = get_object_or_404(User, id=dados_projeto.id_criador).username
        dados['e_o_criador'] = usuario.id==dados_projeto.id_criador
        retorno.append(dados)
    return retorno
