from django.db.models import Avg, FloatField
from django import template
from django.utils.safestring import mark_safe
from booking.models import Rating
from django.db.models.functions import Coalesce
from django.utils.html import strip_tags
from django.utils.text import Truncator


register = template.Library()

@register.simple_tag
def get_restaurant_rating(restaurant_pk):
    average_rating = Rating.objects.filter(restaurant=restaurant_pk).aggregate(average_rating=Avg('rating', output_field=FloatField()))
    return average_rating['average_rating'] if average_rating['average_rating'] is not None else 0


@register.filter
def year_range(start_year, end_year):
    return range(start_year, end_year + 1)

@register.simple_tag
def render_stars(restaurant_pk):
    rating = get_restaurant_rating(restaurant_pk)
    stars = ''
    for i in range(5):  # Предполагаем, что максимальный рейтинг - 5
        if i < rating:
            stars += '<i class="fas fa-star filled"></i>'
        else:
            stars += '<i class="fas fa-star"></i>'
    return mark_safe(stars)

@register.simple_tag
def render_stars_for_detail_page(rating):
    stars = ''
    for i in range(5):  # Предполагаем, что максимальный рейтинг - 5
        if i < rating:
            stars += '<i class="fas fa-star filled"></i>'
        else:
            stars += '<i class="fas fa-star"></i>'
    return mark_safe(stars)

@register.simple_tag
def get_restaurant_reviews_count(restaurant_pk):
    return Rating.objects.filter(restaurant=restaurant_pk).count()


@register.filter
def truncatehtml(value, arg):
    try:
        length = int(arg)
    except ValueError:  # если arg не число
        return value  # возвращаем оригинальное значение без изменений

    text_only = strip_tags(value)  # Удаление HTML тегов
    truncated_text = Truncator(text_only).chars(length)  # Обрезание до заданной длины

    if len(text_only) > length:
        return truncated_text + '...'
    return truncated_text



