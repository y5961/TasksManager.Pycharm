
from django.contrib import admin
from .models import User, Team, Task

# רישום המודלים ל-Admin
admin.site.register(User)
admin.site.register(Team)
admin.site.register(Task)