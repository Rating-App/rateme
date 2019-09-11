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

    # needs to be fixed: form in POST request can't pass validation

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
    pass # todo

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
    form = NewCardForm()
    context = {'form': form}
    if request.method == 'GET':
        return render(request, 'new_card.html', context)
    
    # This form can't pass validation too -_-
    # Probably simpliest way to solve this problem is
    # just google it so I'll do it later
    
    elif request.method == 'POST':
        # do something with duplicates
        if form.is_valid():
            # there should be a way to save data directly, not like this
            card = RatingCard(
                title = form.cleaned_data['title'],
                url = form.cleaned_data['url'],
                text = form.cleaned_data['text'],
            )
            card.save()
            return render(request, 'new_card.html', context)
        else:
            print('form is not valid')
            return render(request, 'new_card.html', context)
