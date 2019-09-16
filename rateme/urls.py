from django.contrib import admin
from django.urls import path, include

from django.views.generic.base import TemplateView
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('', views.index_view, name='home'),
    path('<int:primary_key>/', views.rate_view, name='rate'),
    path('my-ratings/', views.my_ratings_view, name='my-ratings'),
    path('my-recommendations/', views.my_recommendations_view, name='my-recommendations'),
    path('new-card/', views.new_card_view, name='new-card')
]

