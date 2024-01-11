# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.utils import timezone
class Projetos(models.Model):
    id = models.AutoField(primary_key=True)
    dados = models.TextField()
    nome_projeto = models.TextField()
    criacao = models.DateTimeField(default=timezone.now)
    id_criador = models.IntegerField(default=1)
    def __str__(self):
        return f"DadosJSON #{self.id}"

class ProjetosUsuários(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    projeto = models.ForeignKey(Projetos, on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.id}'s ProjetosUsuários"

