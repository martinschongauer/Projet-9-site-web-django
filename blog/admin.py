from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserFollows, Ticket, Review


class UserFollowsAdmin(admin.ModelAdmin):
    list_display = ('user', 'followed_user')


class TicketAdmin(admin.ModelAdmin):
    list_display = ('user', 'title')


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'headline')


admin.site.register(User, UserAdmin)
admin.site.register(UserFollows, UserFollowsAdmin)
admin.site.register(Ticket, TicketAdmin)
admin.site.register(Review, ReviewAdmin)
