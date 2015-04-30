from django.contrib import admin
from bestmenu.models import Category, Restaurant, UserProfile

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('name',)}

class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'url')

# Update the registeration to include customised interface
admin.site.register(Category, CategoryAdmin)
admin.site.register(Restaurant, RestaurantAdmin)
admin.site.register(UserProfile)
