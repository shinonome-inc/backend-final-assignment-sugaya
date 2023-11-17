from django.contrib import admin

from .models import FriendShip, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass


@admin.register(FriendShip)
class FriendShipAdmin(admin.ModelAdmin):
    pass
