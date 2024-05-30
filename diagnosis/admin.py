from django.contrib import admin
from .models import User, Patient, Doctor, Specialty, PreliminaryDiagnosis, DiagnosisHistory, City, Appointment, DoctorPhoto
from .models import DonorProfile, DoctorRequest, DonorRequest, Post, Comment, Service, Dishes
from leaflet.admin import LeafletGeoAdmin


@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


class DoctorPhotoInline(admin.TabularInline):
    model = DoctorPhoto
    extra = 1


@admin.register(Doctor)
class DoctorAdmin(LeafletGeoAdmin, admin.ModelAdmin):
    list_display = ('user', 'verified', 'phone_number')
    list_filter = ('verified', 'specialties')
    search_fields = ('user__username', 'phone_number', 'specialties__name')
    filter_horizontal = ('specialties',)
    inlines = [DoctorPhotoInline]


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('user', 'email', 'phone_number')
    search_fields = ('user__username', 'email', 'phone_number')


@admin.register(DiagnosisHistory)
class DiagnosisHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'date')
    list_filter = ('date',)
    search_fields = ('user__username', 'text')

# Если вы еще не зарегистрировали модель User, вы можете сделать это также.
# Пример может выглядеть так, если вы хотите добавить дополнительную функциональность для пользователей:
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_client', 'is_company')
    list_filter = ('is_client', 'is_company')
    search_fields = ('username', 'email')


admin.site.register(City)
admin.site.register(Appointment)

# Администратор для модели Post
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'for_doctors', 'content_short')
    list_filter = ('for_doctors', 'user')
    search_fields = ('content',)

    def content_short(self, obj):
        return obj.content[:50]

# Администратор для модели Comment
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'user', 'created_at', 'content_short')
    list_filter = ('user', 'created_at')
    search_fields = ('content',)

    def content_short(self, obj):
        return obj.content[:50]

# Регистрируем модели с соответствующими администраторами
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Service, admin.ModelAdmin)
admin.site.register(Dishes, admin.ModelAdmin)
