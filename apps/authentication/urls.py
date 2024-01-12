# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('save-graph-data/', views.save_graph_data, name='save_graph_data'),
    path('load-graph-data/', views.load_graph_data, name='load_graph_data'),
    # outras URLs da sua aplicação
]

urlpatterns = [
    path('login/', views.login_view, name="login"),
    path('register/', views.register_user, name="register"),
    path("logout/", LogoutView.as_view(), name="logout")
]
