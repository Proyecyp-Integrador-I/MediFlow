from django.contrib import admin
from .models import Patient, Ophthalmologist#, Exam
from administrator.models import CustomUser

class CustomUserAdmin(admin.ModelAdmin):
    model = CustomUser
    list_display = ('email', 'first_name', 'last_name', 'ophthalmologist', 'is_active', 'is_staff')
    list_filter = ('is_active', 'is_staff', 'ophthalmologist')
    search_fields = ('email', 'first_name', 'last_name', 'ophthalmologist__name')  # Búsqueda por nombre de oftalmólogo
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'ophthalmologist')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'ophthalmologist', 'password1', 'password2'),
        }),
    )
    filter_horizontal = ()

admin.site.register(CustomUser, CustomUserAdmin)
#admin.site.register(Exam)
admin.site.register(Patient)
admin.site.register(Ophthalmologist)