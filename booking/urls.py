from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'booking'

urlpatterns = [
    path('guest/form/<int:restaurant_pk>', PreliminaryBookingFormView.as_view(), name='guest_form'),
    path("guest/payment", payment, name="payment"),
    path('guest/booking', GuestBookingView.as_view(), name='guest_booking'),
    path('restaurant/list', RestaurantListView.as_view(), name='restaurant_list'),
    path('restaurant/detail/<restaurant_pk>', RestaurantDetailView.as_view(), name='restaurant_detail'),
    path('booking/history/', BookingHistoryView.as_view(), name='booking_history'),
    path('register/', UserRegisterView.as_view(), name='register'),
    path('restaurant/profile/create/', RestaurantProfileCreateView.as_view(), name='restaurant_profile_create'),
    path('guest/profile/create/', GuestProfileCreateView.as_view(), name='guest_profile_create'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('restaurant-Varifing/', RestaurantVarifingView.as_view(), name='octor_varifing'),

    path('role-redirect/', role_redirect, name='role_redirect'),

    path('restaurant-dashboard/', RestaurantDashboardView.as_view(), name='restaurant_dashboard'),
    path('guest-detail/<int:pk>/', AppointmentDetailView.as_view(), name='guest_detail'),
    path('appointment/<int:appointment_id>/change-status/<str:new_status>/', change_appointment_status, name='change_appointment_status'),

    path('chat/<int:receiver_id>/', chat_view, name='chat_view'),
    path('fetch-messages/<int:receiver_id>/', fetch_messages, name='fetch_messages'),

    path('client/registration/view', client_registration_view, name='client_registration'),
    path('client/registration/confirm', client_registration_confirm, name='client_registration_confirm'),
    path('respond-to-request/<int:request_id>/', respond_to_restaurant_request, name='respond_to_request'),
    path('restaurant/requests/list/', restaurant_requests_list, name='restaurant_requests_list'),

    path('restaurant-request/list/', restaurant_requests_list_restaurant_part, name='restaurant_requests_list_restaurant_part'),
    path('restaurant-request/create/', create_restaurant_request, name='create_restaurant_request'),
    path('restaurant-request/edit/<int:request_id>/', edit_restaurant_request, name='edit_restaurant_request'),
    path('restaurant-request/delete/<int:request_id>/', delete_restaurant_request, name='delete_restaurant_request'),

    path('role-based-post-list/', RoleBasedPostListView.as_view(), name='role_based_post_list'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post_detail'),
    path('post/new/', PostCreateView.as_view(), name='post_create'),
    path('post/<int:pk>/edit/', PostUpdateView.as_view(), name='post_edit'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post_delete'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
