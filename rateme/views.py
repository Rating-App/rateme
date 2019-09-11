from django.shortcuts import render
from django.views import generic

from .models import Rating, RatingCard

# Create your views here.

# stub
def vote(request):
    return HttpResponse("Hello, world. You're at the polls index.")

class RateView(generic.DetailView):
    model = Rating
    template_name = 'rateme/rate.html'

def search_field():
    pass

def index(request):
    cards = RatingCard.objects.all()
    context = {
        'cards': zip(
            [card.title for card in cards],
            [card.id for card in cards]
            )}
    return render(request, 'home.html', context)

def personal_card_list(request):
    pass

def card_form():
    pass
