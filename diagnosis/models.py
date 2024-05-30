from django.db import models
from django.contrib.auth.models import AbstractUser
from ckeditor.fields import RichTextField
from django.contrib.gis.db import models as geomodels
from django.contrib.gis.geos import Point


class User(AbstractUser):
    is_client = models.BooleanField(default=False)
    is_company = models.BooleanField(default=False)


class ChatMessage(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender} to {self.receiver} at {self.timestamp}"
class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.CharField(max_length=15)
    phone_number = models.CharField(max_length=15)
    identification_number = models.CharField(max_length=15, unique=True, null=True, blank=True)

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"


# Модель для специализаций
class Specialty(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "RestaurantCategory"
        verbose_name_plural = "RestaurantCategories"


class City(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    specialties = models.ManyToManyField(Specialty, related_name='doctors')  # Специализации врача
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, related_name='doctors')
    photo = models.FileField(upload_to='licenses/', null=True, blank=True)
    about = models.TextField()
    license = models.FileField(upload_to='licenses/', null=True, blank=True)  # Лицензия на медицинскую практику
    identification_document = models.FileField(upload_to='identifications/', null=True, blank=True)  # Идентификационные документы
    phone_number = models.CharField(max_length=15)
    verified = models.BooleanField(default=False)  # Поле для верификации доктора администратором
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    coordinates = geomodels.PointField(default=Point(0, 0))
    services = models.ManyToManyField('Service', related_name='services')
    dishes = models.ManyToManyField('Dishes', related_name='dishes')
    seats = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = "Restaurant"
        verbose_name_plural = "Restaurants"


class Service(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=300, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.name


class Dishes(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=300, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.name


class DoctorPhoto(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='photos')
    photo = models.ImageField(upload_to="licenses/restoraunt")


class PreliminaryDiagnosis(models.Model):
    # Основная информация
    full_name = models.CharField(max_length=100)

    # Контактная информация
    phone = models.CharField(max_length=20)

    # Текущие Симптомы
    symptoms = models.TextField()

    services = models.ManyToManyField(Service, related_name='prebuyed_services', blank=True)

    dishes = models.ManyToManyField(Dishes, related_name='prebuyed_dishes', blank=True)

    def __str__(self):
        return self.full_name


class Appointment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    date = models.DateTimeField()
    services = models.ManyToManyField(Service, related_name='buyed_services', blank=True)
    dishes = models.ManyToManyField(Dishes, related_name='buyed_dishes', blank=True)
    status = models.CharField(max_length=10, choices=[('pending', 'Pending'), ('confirmed', 'Confirmed')], default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.patient} - {self.doctor} on {self.date.strftime('%Y-%m-%d %H:%M')}"


class DiagnosisHistory(models.Model):
    user = models.ForeignKey(Patient, on_delete=models.CASCADE)
    text = models.TextField()
    patient_text = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    appointment = models.OneToOneField(Appointment, on_delete=models.SET_NULL, null=True, blank=True)
    services = models.ManyToManyField(Service, related_name='bb_services', blank=True)
    dishes = models.ManyToManyField(Dishes, related_name='bb_dishes', blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name = "Book"
        verbose_name_plural = "Books"


class Rating(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    rating = models.IntegerField()
    text = models.TextField()
    date = models.DateTimeField(auto_now_add=True)


class DonorProfile(models.Model):
    patient = models.OneToOneField(Patient, on_delete=models.CASCADE)
    blood_type = models.CharField(max_length=3)
    age = models.PositiveIntegerField()
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Donor profile of {self.patient.user.username}"


class DoctorRequest(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='doctor_requests')
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Request by {self.doctor.user.username} - {self.title}"


class DonorRequest(models.Model):
    donor_profile = models.ForeignKey(DonorProfile, on_delete=models.CASCADE)
    doctor_request = models.ForeignKey(DoctorRequest, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = RichTextField()
    photo = models.FileField(upload_to='posts/', null=True, blank=True)
    for_doctors = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content[:50]


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = RichTextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content[:50]


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post', 'comment')

    def __str__(self):
        return f"{self.user.username} - {'Post' if self.post else 'Comment'}"













