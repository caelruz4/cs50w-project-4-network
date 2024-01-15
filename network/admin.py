from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(Follower)
admin.site.register(Like)
admin.site.register(Post)
admin.site.register(User)