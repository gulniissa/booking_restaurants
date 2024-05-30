from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'diagnosis'

urlpatterns = [
    path('patient/form/<int:doctor_pk>', PreliminaryDiagnosisFormView.as_view(), name='patient_form'),
    path("patient/payment", payment, name="payment"),
    path('patient/diagnosis', PatientDiagnosisView.as_view(), name='patient_diagnosis'),
    path('doctor/list', DoctorListView.as_view(), name='doctor_list'),
    path('doctor/detail/<doctor_pk>', DoctorDetailView.as_view(), name='doctor_detail'),
    path('diagnosis/history/', DiagnosisHistoryView.as_view(), name='diagnosis_history'),
    path('register/', UserRegisterView.as_view(), name='register'),
    path('doctor/profile/create/', DoctorProfileCreateView.as_view(), name='doctor_profile_create'),
    path('patient/profile/create/', PatientProfileCreateView.as_view(), name='patient_profile_create'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('doctor-Varifing/', DoctorVarifingView.as_view(), name='octor_varifing'),

    path('role-redirect/', role_redirect, name='role_redirect'),

    path('doctor-dashboard/', DoctorDashboardView.as_view(), name='doctor_dashboard'),
    path('patient-detail/<int:pk>/', AppointmentDetailView.as_view(), name='patient_detail'),
    path('appointment/<int:appointment_id>/change-status/<str:new_status>/', change_appointment_status, name='change_appointment_status'),

    path('chat/<int:receiver_id>/', chat_view, name='chat_view'),
    path('fetch-messages/<int:receiver_id>/', fetch_messages, name='fetch_messages'),

    path('donor/registration/view', donor_registration_view, name='donor_registration'),
    path('donor/registration/confirm', donor_registration_confirm, name='donor_registration_confirm'),
    path('respond-to-request/<int:request_id>/', respond_to_doctor_request, name='respond_to_request'),
    path('doctor/requests/list/', doctor_requests_list, name='doctor_requests_list'),

    path('doctor-request/list/', doctor_requests_list_doctor_part, name='doctor_requests_list_doctor_part'),
    path('doctor-request/create/', create_doctor_request, name='create_doctor_request'),
    path('doctor-request/edit/<int:request_id>/', edit_doctor_request, name='edit_doctor_request'),
    path('doctor-request/delete/<int:request_id>/', delete_doctor_request, name='delete_doctor_request'),

    path('role-based-post-list/', RoleBasedPostListView.as_view(), name='role_based_post_list'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post_detail'),
    path('post/new/', PostCreateView.as_view(), name='post_create'),
    path('post/<int:pk>/edit/', PostUpdateView.as_view(), name='post_edit'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post_delete'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
