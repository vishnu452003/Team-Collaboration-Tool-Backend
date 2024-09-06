from django.contrib import admin

# Register your models here.
from .models import CustomUser  # Your custom user model
from .models import Workspace
from .models import Project


admin.site.register(CustomUser)
admin.site.register(Workspace)
admin.site.register(Project)
