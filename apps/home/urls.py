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
    path('escolha/<int:id>',views.escolha, name='escolha'),
    path('requisitos',views.requirements, name='requisitos'),
    path('modelagem',views.modeling, name='modelagem')

    # Matches any html file
    #re_path(r'^.*\.*', views.pages, name='pages'),

]
