from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from django.views.generic.base import TemplateResponseMixin, View
from .forms import PreliminaryDiagnosisForm, RatingForm, UserRegisterForm, RestaurantProfileForm, GuestProfileForm, RestaurantRequestForm
from .models import DiagnosisHistory, Restaurant, Rating, User, Guest, Service, Dishes
from .openai_integration import generate_text
from django.shortcuts import get_object_or_404
from django.db.models import Q
from datetime import datetime, timedelta
from django.contrib import messages
from django.contrib.gis.geos import GEOSGeometry



from django.views.generic import CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

def role_redirect(request):
    user = request.user
    try:
        restaurant = Restaurant.objects.filter(user=user).first()
        if restaurant and restaurant.verified:
            return redirect('diagnosis:restaurant_dashboard')
        elif Guest.objects.filter(user=user).exists():
            return redirect('diagnosis:restaurant_list')
        elif restaurant and not restaurant.verified:
            return redirect('diagnosis:restaurant_verifying')
        else:
            if user.is_company:
                return redirect('diagnosis:restaurant_profile_create')
            elif user.is_client:
                return redirect('diagnosis:guest_profile_create')
    except Exception as e:

        return redirect('login')

from django.utils.dateparse import parse_date
from django.utils.dateparse import parse_datetime
class PreliminaryDiagnosisFormView(FormView):
    template_name = 'diagnosis/form.html'
    form_class = PreliminaryDiagnosisForm

    def get_context_data(self, **kwargs):
        # Вызов базовой реализации, чтобы получить контекст
        context = super().get_context_data(**kwargs)
        # Получение restaurant_pk из параметров запроса
        restaurant_pk = self.kwargs.get('restaurant_pk')
        context['restaurant_pk'] = restaurant_pk
        date_str = self.request.GET.get('date')
        time_str = self.request.GET.get('time')
        # slot_str = self.request.GET.get('slot').replace('.',
        #                                                 '').upper()  # Ensure that 'AM' or 'PM' is capitalized and without dots
        try:
            print(date_str, 'date_str.....')
            print(time_str, 'slot_str.....')
            def create_appointment_datetime(date_str, time_str):
                # Преобразование строки даты и времени в объект datetime
                appointment_datetime = datetime.strptime(f'{date_str} {time_str}', '%Y-%m-%d %H:%M')
                return appointment_datetime
            appointment_datetime = create_appointment_datetime(date_str, time_str)

            context['appointment_datetime'] = appointment_datetime
        except ValueError:
            # Handle the error if the date or time format is incorrect
            context['error'] = "The provided date and time format is incorrect."
        context['restaurant'] = Restaurant.objects.get(id=restaurant_pk)

        return context

    def form_valid(self, form, **kwargs):
        # Формирование текста для запроса к API
        guest_data = form.cleaned_data
        diagnoses = f"""Клиент: {guest_data['full_name']}.
                Байланыс: {guest_data['phone']}.
                Қосымша ақпарат: {guest_data['symptoms']}
                """
        restaurant_pk = self.kwargs.get('restaurant_pk')
        print("DOCTOR PK", restaurant_pk)
        appointment_datetime_str = self.request.POST.get('appointment_datetime')
        appointment_datetime_str = appointment_datetime_str.replace('a.m.', 'AM').replace('p.m.', 'PM')
        date_format = "%Y-%m-%d %H:%M"
        try:
            appointment_datetime = datetime.strptime(appointment_datetime_str, date_format)
        except ValueError as e:
            print("There was an error converting the date:", e)
        print(appointment_datetime_str, '------------------------')
        restaurant = get_object_or_404(Restaurant, id=restaurant_pk)
        selected_dishes = self.request.POST.getlist('dishes')
        selected_services = self.request.POST.getlist('services')
        total_price = restaurant.price
        for selected_dish in selected_dishes:
            dish = get_object_or_404(Dishes, id=int(selected_dish))
            if dish:
                total_price += dish.price
        for selected_service in selected_services:
            service = get_object_or_404(Service, id=int(selected_service))
            if service:
                total_price += service.price
        pat = Guest.objects.get_or_create(user=self.request.user)
        appointment = Appointment.objects.create(guest=pat[0], restaurant=restaurant, date=appointment_datetime)
        diagnosis_history = DiagnosisHistory.objects.create(
            user=self.request.user.guest,
            text=diagnoses,
            guest_text=diagnoses,
            appointment=appointment,
            total_price=total_price
        )
        diagnosis_history.services.set(selected_services)
        diagnosis_history.dishes.set(selected_dishes)
        diagnosis_history.save()
        # Assign values to the many-to-many fields using set() method
        diagnosis_histories = DiagnosisHistory.objects.filter(user=self.request.user.guest)

        context = {
            'diagnoses': diagnoses,
            'diagnosis_histories': diagnosis_histories,
            'restaurant_pk': restaurant_pk,
            'restaurant': restaurant,
            'appointment': appointment.pk,
        }
        return render(self.request, template_name='diagnosis/payment.html', context=context)


def payment(request):
    if request.method == 'POST':
        diagnoses = request.POST.get("diagnoses")
        restaurant_id = request.POST.get("restaurant_pk")
        restaurant = request.POST.get("restaurant")
        appointment = request.POST.get("appointment")
        diagnosis_histories = DiagnosisHistory.objects.filter(user=request.user.guest)
        appointment = Appointment.objects.get(id=appointment)
        context = {
            'diagnoses': diagnoses,
            'diagnosis_histories': diagnosis_histories,
            'restaurant_pk': restaurant_id,
            'restaurant': restaurant,
            'appointment': appointment,
        }

        return render(request, template_name='diagnosis/form_result.html', context=context)


class GuestDiagnosisView(TemplateResponseMixin, View):
    template_name = 'diagnosis/form_result.html'

    def get(self, request):
        return self.render_to_response({})

class RestaurantVarifingView(TemplateResponseMixin, View):
    template_name = 'restaurants/waiting_varify.html'

    def get(self, request):
        return self.render_to_response({})
        


from .models import City

from django.db.models import Count

class RestaurantListView(TemplateResponseMixin, View):
    template_name = 'restaurants/list.html'

    def get(self, request):
        search_text = request.GET.get('search_text', '').strip()
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')
        city_id = request.GET.get('city')
        date = request.GET.get('date')

        restaurants = Restaurant.objects.all()
        if search_text:
            restaurants = restaurants.filter(
                Q(specialties__name__icontains=search_text) |
                Q(user__first_name__icontains=search_text) |
                Q(user__last_name__icontains=search_text) |
                Q(city__name__icontains=search_text)
            ).distinct()

        if min_price:
            restaurants = restaurants.filter(price__gte=min_price)
        if max_price:
            restaurants = restaurants.filter(price__lte=max_price)
        if city_id:
            restaurants = restaurants.filter(city_id=city_id)
        if date:
            date = datetime.strptime(date, '%Y-%m-%d').date()
            restaurants = restaurants.annotate(appointment_count=Count('appointment', filter=Q(appointment__date__date=date)))
            restaurants = restaurants.filter(appointment_count__lt=2)

        count = restaurants.count()
        cities = City.objects.all()
        return self.render_to_response({
            'restaurants': restaurants,
            'count': count,
            'cities': cities,
            'search_text': search_text,
            'min_price': min_price,
            'max_price': max_price,
            'city_id': city_id,
            'date': date
        })



from datetime import timedelta, time  # Импортируем time

def generate_time_slots(date):
    return [datetime.combine(date, time(11, 0)).time(), datetime.combine(date, time(17, 0)).time()]


def generate_time_slots_for_week(start_date):
    slots = {}
    for day in range(7):  # Для каждого дня в неделе
        date = start_date + timedelta(days=day)
        slots[date] = generate_time_slots(date)
    return slots

def get_available_slots(restaurant_id, date, slots):
    appointments = Appointment.objects.filter(restaurant_id=restaurant_id, date__date=date)
    busy_slots = [appointment.date.time() for appointment in appointments]
    available_slots = [slot for slot in slots if slot not in busy_slots]
    return available_slots

class RestaurantDetailView(TemplateResponseMixin, View):
    template_name = 'restaurants/detail.html'

    def get(self, request, **kwargs):
        restaurant_pk = self.kwargs.get('restaurant_pk')
        restaurant = get_object_or_404(Restaurant, id=restaurant_pk)
        ratings = Rating.objects.filter(restaurant=restaurant)
        form = RatingForm()

        start_date_str = request.GET.get('start_date', datetime.now().strftime('%Y-%m-%d'))
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()

        slots_week = generate_time_slots_for_week(start_date)
        available_slots_week = {}

        for date, slots in slots_week.items():
            available_slots = get_available_slots(restaurant_pk, date, slots)
            available_slots_week[date] = available_slots
        point = GEOSGeometry(restaurant.coordinates.wkb)
        lat, lon = point.y, point.x
        coordinates = {'lat': lat, 'lon': lon}

        return self.render_to_response({
            'restaurant': restaurant,
            'ratings': ratings,
            'form': form,
            'slots': available_slots_week,
            'coordinates': coordinates
        })

    def post(self, request, **kwargs):
        restaurant_pk = self.kwargs.get('restaurant_pk')
        form = RatingForm(request.POST)
        if form.is_valid():
            form_obj = form.save(commit=False)
            form_obj.restaurant = Restaurant.objects.get(id=restaurant_pk)
            form_obj.guest = request.user.guest
            form_obj.save()

        restaurant = Restaurant.objects.get(id=restaurant_pk)
        ratings = Rating.objects.filter(restaurant=restaurant_pk)
        form = RatingForm(request.POST)
        return self.render_to_response({'restaurant': restaurant, 'ratings': ratings, 'form': form})

class DiagnosisHistoryView(TemplateResponseMixin, View):
    template_name = 'diagnosis/result_history.html'

    def get(self, request, **kwargs):
        diagnosis_histories = DiagnosisHistory.objects.filter(user=self.request.user.guest)
        return self.render_to_response({'diagnosis_histories': diagnosis_histories})

from django.shortcuts import redirect

class UserRegisterView(CreateView):
    model = User
    form_class = UserRegisterForm
    template_name = 'registration/register.html'

    def form_valid(self, form):
        self.user = form.save()  # Сохраняем пользователя
        role = form.cleaned_data.get('role')  # Получаем выбранную роль из формы
        if role == 'is_client':
            self.user.is_client = True
        elif role == 'is_company':
            self.user.is_company = True
        self.user.save()
        return super().form_valid(form)

    def get_success_url(self):
        # Теперь self.user гарантированно существует
        print(self.user.is_company, '=========')
        if self.user.is_company:
            return reverse_lazy('diagnosis:restaurant_profile_create')
        elif self.user.is_client:
            return reverse_lazy('diagnosis:guest_profile_create')
        else:
            return reverse_lazy('login')


class RestaurantProfileCreateView(LoginRequiredMixin, CreateView):
    model = Restaurant
    form_class = RestaurantProfileForm
    template_name = 'registration/restaurant_profile_create.html'
    success_url = reverse_lazy('diagnosis:octor_varifing')  # Предполагается, что у вас есть URL с именем 'home'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class GuestProfileCreateView(LoginRequiredMixin, CreateView):
    model = Guest
    form_class = GuestProfileForm
    template_name = 'registration/guest_profile_create.html'
    success_url = reverse_lazy('diagnosis:restaurant_list')

    def form_valid(self, form):
        if Guest.objects.filter(user=self.request.user).exists():
            print(Guest.objects.filter(user=self.request.user), '++++++++++')
            messages.error(self.request, 'Профиль для данного пользователя уже существует.')
            return redirect('diagnosis:guest_profile_create')
        else:
            form.instance.user = self.request.user
            return super().form_valid(form)

from django.shortcuts import render
from django.views import View
from .models import Appointment, Guest
from .forms import GuestSearchForm


class RestaurantDashboardView(View):
    def get(self, request, *args, **kwargs):
        today = datetime.now().date()
        next_week = today + timedelta(days=7)
        next_month = today + timedelta(days=30)

        search_form = GuestSearchForm(request.GET)
        appointments = Appointment.objects.filter(restaurant=request.user.restaurant)

        if search_form.is_valid():
            identification_number = search_form.cleaned_data.get('identification_number')
            period = search_form.cleaned_data.get('period')

            if period == 'today':
                appointments = appointments.filter(date__date=today)
            elif period == 'next_week':
                appointments = appointments.filter(date__date__range=(today, next_week))
            elif period == 'next_month':
                appointments = appointments.filter(date__date__range=(today, next_month))

            if identification_number:
                appointments = appointments.filter(guest__identification_number=identification_number)

            appointments = appointments.order_by('date')  # Сортировка по дате
            print(appointments, '-------------')
            restaurant = Restaurant.objects.get(user_id=request.user.pk)

        return render(request, 'restaurant_part/restaurant_dashboard.html', {
            'appointments': appointments,
            'search_form': search_form,
            'restaurant': restaurant
        })

from django.views.generic import DetailView

class AppointmentDetailView(DetailView):
    model = Appointment
    template_name = 'restaurant_part/guest_detail.html'
    context_object_name = 'appointment'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        appointment = self.get_object()
        context['diagnosis_history'] = DiagnosisHistory.objects.get(appointment=appointment)
        return context

from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

@login_required
def change_appointment_status(request, appointment_id, new_status):
    appointment = get_object_or_404(Appointment, id=appointment_id, restaurant=request.user.restaurant)
    if request.method == "POST":
        appointment.status = new_status
        appointment.save()
        # Перенаправление обратно на детальную страницу пациента
        return HttpResponseRedirect(reverse('diagnosis:guest_detail', args=[appointment.guest.id]))
    else:
        # Возвращаем пользователя обратно, если метод не POST
        return HttpResponseRedirect(reverse('diagnosis:guest_detail', args=[appointment.guest.id]))


from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import ChatMessage
from django.contrib.auth.decorators import login_required

@login_required
def chat_view(request, receiver_id):
    if request.method == 'POST':
        message_text = request.POST.get('message')
        receiver = User.objects.get(id=receiver_id)
        message = ChatMessage.objects.create(sender=request.user, receiver=receiver, text=message_text)
        return redirect('diagnosis:chat_view', receiver_id=receiver_id)
    else:
        receiver = User.objects.get(id=receiver_id)
        messages = ChatMessage.objects.filter(sender=request.user, receiver__id=receiver_id) | \
                   ChatMessage.objects.filter(sender__id=receiver_id, receiver=request.user)
        messages = messages.order_by('timestamp')
        return render(request, 'chat/chat.html', {'messages': messages, 'receiver_id': receiver_id, 'receiver': receiver})

@login_required
def fetch_messages(request, receiver_id):
    messages = ChatMessage.objects.filter(sender=request.user, receiver__id=receiver_id) | \
               ChatMessage.objects.filter(sender__id=receiver_id, receiver=request.user)
    messages = messages.order_by('timestamp')
    return JsonResponse({"messages": list(messages.values('sender__username', 'text', 'timestamp'))})

from .models import RestaurantRequest, DonorRequest, ClientProfile
from django.http import HttpResponse

@login_required
def client_registration_view(request):
    if request.method == 'POST':
        blood_type = request.POST.get('blood_type')
        age = request.POST.get('age')

        # Проверяем, есть ли у текущего пользователя профиль пациента
        try:
            guest = request.user.guest
        except Guest.DoesNotExist:
            return HttpResponse("Только пациенты могут регистрироваться в качестве доноров.", status=403)

        # Создаем профиль донора
        ClientProfile.objects.create(guest=guest, blood_type=blood_type, age=age)
        return redirect('diagnosis:client_registration_confirm')

    # Если GET-запрос, отображаем пустую форму
    return render(request, 'client/register.html')

@login_required
def client_registration_confirm(request):
    return render(request, 'client/confirm_register.html')

from .models import RestaurantRequest
from django.db.models import Count


@login_required
def restaurant_requests_list(request):
    requests = RestaurantRequest.objects.annotate(response_count=Count('clientrequest'))

    # Инициализация переменных для избежания ошибок, если профиль донора отсутствует
    user_responses_ids = []
    user_responses = []

    # Попытка получить профиль донора текущего пользователя
    try:
        client_profile = ClientProfile.objects.get(guest__user=request.user)
        # Получаем список ID заявок, на которые пользователь откликнулся
        user_responses_ids = DonorRequest.objects.filter(client_profile=client_profile).values_list('restaurant_request_id', flat=True)
        # Получаем сами объекты откликов пользователя
        user_responses = DonorRequest.objects.filter(client_profile=client_profile).select_related('restaurant_request')
    except ClientProfile.DoesNotExist:
        pass  # Если профиль донора не найден, списки остаются пустыми

    return render(request, 'client/list.html', {
        'requests': requests,
        'user_responses_ids': list(user_responses_ids),
        'user_responses': user_responses,
    })


@login_required
def respond_to_restaurant_request(request, request_id):
    restaurant_request = get_object_or_404(RestaurantRequest, id=request_id)
    client_profile, created = ClientProfile.objects.get_or_create(guest=request.user.guest)

    # Проверяем, не откликался ли уже пользователь на эту заявку
    if not DonorRequest.objects.filter(client_profile=client_profile, restaurant_request=restaurant_request).exists():
        DonorRequest.objects.create(client_profile=client_profile, restaurant_request=restaurant_request)
        # Перенаправляем пользователя на страницу с подтверждением отклика или обратно к списку заявок
        return redirect('diagnosis:restaurant_list')
    else:
        # Обработка случая, если пользователь уже откликался на заявку
        return redirect('diagnosis:restaurant_list')


@login_required
def restaurant_requests_list_restaurant_part(request):
    all_requests = RestaurantRequest.objects.annotate(response_count=Count('clientrequest'))

    # Проверяем, является ли текущий пользователь доктором
    try:
        current_restaurant = request.user.restaurant
        # Получаем заявки, созданные текущим доктором
        restaurant_own_requests = RestaurantRequest.objects.filter(restaurant=current_restaurant)
    except Restaurant.DoesNotExist:
        restaurant_own_requests = None

    return render(request, 'restaurant_part/client/list.html', {
        'all_requests': all_requests,
        'restaurant_own_requests': restaurant_own_requests,
    })


@login_required
def create_restaurant_request(request):
    if not request.user.is_company:
        # Проверяем, что пользователь является доктором
        return redirect('diagnosis:restaurant_requests_list')

    if request.method == 'POST':
        form = RestaurantRequestForm(request.POST)
        if form.is_valid():
            restaurant_request = form.save(commit=False)
            restaurant_request.restaurant = request.user.restaurant
            restaurant_request.save()
            return redirect('diagnosis:restaurant_requests_list_restaurant_part')  # Перенаправляем на список заявок
    else:
        form = RestaurantRequestForm()
    return render(request, 'restaurant_part/client/create_restaurant_request.html', {'form': form})

@login_required
def edit_restaurant_request(request, request_id):
    restaurant_request = get_object_or_404(RestaurantRequest, id=request_id, restaurant=request.user.restaurant)
    if request.method == 'POST':
        form = RestaurantRequestForm(request.POST, instance=restaurant_request)
        if form.is_valid():
            form.save()
            return redirect('diagnosis:restaurant_requests_list_restaurant_part')  # Например, в список заявок
    else:
        form = RestaurantRequestForm(instance=restaurant_request)
    return render(request, 'restaurant_part/client/edit_restaurant_request.html', {'form': form})

@login_required
def delete_restaurant_request(request, request_id):
    restaurant_request = get_object_or_404(RestaurantRequest, id=request_id, restaurant=request.user.restaurant)
    restaurant_request.delete()
    return redirect('diagnosis:restaurant_requests_list_restaurant_part')


from django.views.generic import ListView
from .models import Post
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.db.models import Count


class RoleBasedPostListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'posts/role_based_post_list.html'
    context_object_name = 'posts'

    def get_queryset(self):
        """Фильтрует посты в зависимости от роли пользователя и добавляет количество комментариев."""
        if not self.request.user.is_authenticated:
            return Post.objects.none()  # Возвращаем пустой queryset, если пользователь не аутентифицирован

        queryset = Post.objects.annotate(comments_count=Count('comments'))

        if self.request.user.is_company:
            return queryset.filter(for_restaurants=True).order_by('-id')
        elif self.request.user.is_client:
            return queryset.filter(for_restaurants=False).order_by('-id')
        else:
            raise Http404("You do not have permission to view any posts.")

    def get_context_data(self, **kwargs):
        """Добавляет посты созданные пользователем в контекст и количество комментариев для каждого поста."""
        context = super().get_context_data(**kwargs)
        user_posts = Post.objects.filter(user=self.request.user).annotate(comments_count=Count('comments')).order_by('-created_at')
        context['user_posts'] = user_posts
        return context


from django.views.generic import DetailView
from django.views.generic.edit import FormMixin
from django.urls import reverse_lazy
from .models import Post
from .forms import CommentForm

class PostDetailView(FormMixin, DetailView):
    model = Post
    template_name = 'posts/post_detail.html'
    form_class = CommentForm

    def get_success_url(self):
        return reverse_lazy('diagnosis:post_detail', kwargs={'pk': self.object.pk})

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.post = self.object
        comment.user = self.request.user
        comment.save()
        return super().form_valid(form)


from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView
from .models import Post
from .forms import PostForm

class PostCreateView(CreateView):
    model = Post
    form_class = PostForm
    template_name = 'posts/post_form.html'
    success_url = reverse_lazy('diagnosis:role_based_post_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        if self.request.user.is_company:
            form.instance.for_restaurants = True
        return super().form_valid(form)

class PostUpdateView(UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'posts/post_form.html'
    success_url = reverse_lazy('diagnosis:role_based_post_list')

class PostDeleteView(DeleteView):
    model = Post
    template_name = 'posts/post_confirm_delete.html'
    success_url = reverse_lazy('diagnosis:role_based_post_list')

