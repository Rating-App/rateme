from django.shortcuts import render
from django.views import generic

from .models import Rating, RatingCard
from .forms import RateForm, NewCardForm

def rate_view(request, primary_key):
    card = RatingCard.objects.get(pk=primary_key)
    form = RateForm()

    context = {
    'card': card,
    'form': form,
    }

    if request.method == "GET":
        return render(request, 'rate.html', context)

    # fix: form in POST request can't pass validation

    elif request.method == "POST":
        if form.is_valid():
            try:
                rate = Rating.objects.get(
                    rating_card=primary_key,
                    user=request.user
                    )
                print(rate)
                rate.rating = form.cleaned_data['rating']

                rate.save()

            except Rating.DoesNotExist:
                rate = Rating(
                    rating_card = RatingCard.objects.get(pk=primary_key),
                    user = request.user,
                    rating = form.cleaned_data['rating'],
                )

                rate.save()
            return render(request, 'rate.html', context)
        else:
            print('form is not valid')
            return render(request, 'rate.html', context)

def search_field():
    pass

def index_view(request):
    cards = RatingCard.objects.all()
    context = {
        'cards': zip(
            [card.title for card in cards],
            [card.id for card in cards]
            )}
    return render(request, 'home.html', context)

def my_ratings_view(request):
    user = request.user
    context = {}
    try:
        # don't like that user=user but whatever
        ratings = Rating.objects.filter(user=user)
        context['ratings'] = ratings
    except Rating.DoesNotExist:
        context['ratings'] = None
    return render(request, 'my_ratings.html', context)

def new_card_view(request):
    context = {'form': NewCardForm()}
    if request.method == 'GET':
        return render(request, 'new_card.html', context)
    elif request.method == 'POST':
        pass # todo
