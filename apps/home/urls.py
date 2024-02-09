# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from apps.home import views

urlpatterns = [

    # The home page
    #path('', views.index, name='home'),
    path('salva_projeto', views.salva_projeto, name='salva_projeto'),
    path('', views.projetos, name='projetos'),
    path('editar_projeto/<int:id>',views.editar_projeto, name='editar_projeto'),
    path('excluir_projeto/<int:id>',views.excluir_projeto, name='excluir_projeto'),
    path('adicionar_membro/<int:id>',views.adicionar_membro, name='adicionar_membro'),
    path('sair_membro/<int:id>',views.sair_membro, name='sair_membro'),
    path('escolha/<int:id>',views.escolha, name='escolha'),
    path('requisitos',views.requirements, name='requisitos'),
    path('processamento_requisito',views.processamento_requisito, name='processamento_requisito'),
    path('classificador_iot/<int:id>',views.classificador_iot, name='classificador_iot'),
    path('salvar_requisito/<int:id>',views.salvar_requisito, name='salvar_requisito'),
    path('salvar_requisito/<int:id>',views.salvar_requisito, name='salvar_requisito'),
    path('excluir_requisito/<int:id>/<int:id_requisito>',views.excluir_requisito, name='excluir_requisito'),
    path('editar_requisito/<int:id>/<int:id_requisito>',views.editar_requisito, name='editar_requisito'),
    path('processamento_requisito_editar',views.processamento_requisito_editar, name='processamento_requisito_editar'),
    path('usuario',views.usuario, name='usuario'),
    path('editar_usuario',views.editar_usuario, name='editar_usuario'),

    path('modelagem',views.modeling, name='modelagem'),
    path('salvar_projeto_modelagem/<int:id>',views.salvar_projeto_modelagem, name='salvar_projeto_modelagem'),

    path('salvar_modelagem',views.salvar_modelagem, name='salvar_modelagem'),
    path('excluir_modelagem/<int:id>/<int:id_modelagem>',views.excluir_modelagem, name='excluir_modelagem'),
    path('editar_projeto_modelagem/<int:id>/<int:id_modelagem>',views.editar_projeto_modelagem, name='editar_projeto_modelagem'),
    # Matches any html file
    #re_path(r'^.*\.*', views.pages, name='pages'),

]
