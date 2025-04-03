from django.contrib import admin
from .models import Story, UserStoryInteraction
# Register your models here.

admin.site.register(Story)
admin.site.register(UserStoryInteraction)
