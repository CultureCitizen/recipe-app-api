from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from core import models
from django.utils.translation import gettext as _
# Register your models here.


# The model.User class is displayed using the UserAdmin class
admin.site.register(models.User, UserAdmin)
