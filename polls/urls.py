# accounts/urls.py
from django.urls import path

from . import views

urlpatterns = [
    #path('signup/', views.SignUp.as_view(), name='signup'),
    path('<int:pk>/', views.RateView.as_view(), name='rate'),
    path('<int:ok>/vote/', views.vote, name='vote'),

]

