from django.shortcuts import render
from django.views import generic

from .models import Rating

# Create your views here.

# stub
def vote(request):
    return HttpResponse("Hello, world. You're at the polls index.")

class RateView(generic.DetailView):
    model = Rating
    template_name = 'polls/rate.html'
