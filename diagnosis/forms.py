from django import forms

from mediog.settings import BASE_DIR
from .models import PreliminaryDiagnosis, Rating, User, Restaurant, Guest, Specialty, Service, Dishes
from django.contrib.auth.forms import UserCreationForm


class PreliminaryDiagnosisForm(forms.ModelForm):
    class Meta:
        model = PreliminaryDiagnosis
        fields = ('full_name', 'phone', 'symptoms', 'services', 'dishes')  # Включает все поля модели

        labels = {
            'full_name': 'Аты жөні',
            'phone': 'Телефон',
            'symptoms': 'Қосымша ақпарат',
            'services': 'Қызметтер',
            'dishes': 'Тамақтар',
        }

        # Опционально: добавление кастомных виджетов для отдельных полей
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'symptoms': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'services': forms.CheckboxSelectMultiple(attrs={'class': 'form-check'}),
            'dishes': forms.CheckboxSelectMultiple(attrs={'class': 'form-check'}),
        }


class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['rating', 'text']
        exclude = ('guest', 'restaurant')


class UserRegisterForm(UserCreationForm):
    ROLE_CHOICES = (
        ('is_client', 'Клиент'),
        ('is_company', 'Мекеме'),
    )

    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.RadioSelect, required=True)

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'role', 'first_name', 'last_name']




class RestaurantProfileForm(forms.ModelForm):
    class Meta:
        model = Restaurant
        fields = ['photo', 'about', 'license', 'identification_document', 'phone_number', 'specialties']
        widgets = {'specialties': forms.CheckboxSelectMultiple}


class GuestProfileForm(forms.ModelForm):
    class Meta:
        model = Guest
        fields = ['email', 'phone_number', 'identification_number']


class GuestSearchForm(forms.Form):
    identification_number = forms.CharField(max_length=12, required=False, label='ИИН')
    period = forms.ChoiceField(choices=[('today', 'На сегодня'), ('next_week', 'На следующую неделю'), ('next_month', 'На следующий месяц')], required=False, label='Период')


from .models import RestaurantRequest

class RestaurantRequestForm(forms.ModelForm):
    class Meta:
        model = RestaurantRequest
        fields = ['title', 'description']

from .models import Comment

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Введите ваш комментарий здесь...'})
        }

from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content', 'photo', 'for_restaurants']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
            'for_restaurants': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
