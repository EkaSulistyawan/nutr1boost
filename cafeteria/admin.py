from django.contrib import admin
from .models import Menu



class MenuModified(admin.ModelAdmin):
  list_display = ("meal_name", "showmeal")

# Register your models here.
# Register your models here.
admin.site.register(Menu,MenuModified)