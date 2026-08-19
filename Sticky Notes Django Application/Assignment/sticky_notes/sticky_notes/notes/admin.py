from django.contrib import admin
from .models import Note
from .models import User

# Register your models here.

# Note Model
admin.site.register(Note)


# User Model
admin.site.register(User)
