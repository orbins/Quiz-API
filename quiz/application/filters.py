from django_filters import rest_framework as filters
from django.db import models
from .models import Categories


class CategoryFilter(filters.FilterSet):
    """Фильтр для категорий по имени"""
    name = filters.CharFilter(method='find_by_name')

    def find_by_name(self, queryset, name, value):
        # Сначала проверяются совпадения по началу слова, аннотируются значением
        # qs_order=0
        if not value:
            return queryset
        starts_with = queryset.filter(name__istartswith=value).annotate(
            qs_order=models.Value(0, models.IntegerField())
        )
        contains = queryset.filter(name__icontains=value).exclude(
            name__in=starts_with.values('name')).annotate(
            qs_order=models.Value(1, models.IntegerField()))

        return starts_with.union(contains).order_by('qs_order')

    class Meta:
        model = Categories
        fields = ('name',)
