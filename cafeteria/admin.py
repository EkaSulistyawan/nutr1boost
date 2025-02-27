from django.contrib import admin
from .models import Menu

## adding custom admin
from django.http import HttpResponse
from django.template import loader
from django.urls import path

# 
class MenuModified(admin.ModelAdmin):
  list_display = ("meal_name", "showmeal")

# Register your models here.
admin.site.register(Menu,MenuModified)