from django.contrib import admin

# Register your models here.
from .models import CustomUser  # Your custom user model

admin.site.register(CustomUser)
