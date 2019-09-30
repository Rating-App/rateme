from django.shortcuts import render, redirect
from django.views import generic
from django.http import HttpResponse
from django.http import JsonResponse

from django.db import IntegrityError
from django.db.models import Q

from .models import Rating, RatingCard, Recommendation
from .forms import RateForm, NewCardForm
from .functions import make_context, make_pagination, process_rate_post_request

import numpy as np
from scipy.sparse import csc_matrix


def rate_view(request, primary_key):
    card = RatingCard.objects.get(pk=primary_key) # get_object_or_404
    tags = card.tag_set.all()
    form = RateForm()

    context = {
    'card': card,
    'tags': tags,
    'form': form,
    }

    if request.method == "GET":
        return render(request, 'rate.html', context)

    elif request.method == "POST":
        process_rate_post_request(
            request,
            primary_key
        )
    return redirect('home')

def search_view(request):
    # todo: length limit
    if request.method == "GET":
        query = request.GET.get('search')
        if query:
            return render(
                request,
                'search.html',
                make_context(
                    request,
                    RatingCard.objects.filter(
                        Q(title__icontains=query) | Q(text__icontains=query)
                    ),
                    '-id',
                    RateForm(),
                    query=query,
                    pagination=(True, 20),
                ),
            )
        else:
            context = {
                'data': None
            }
        return render(request, 'search.html', context)
    elif request.method == "POST":
        process_rate_post_request(
            request,
            int(request.POST.get('rating_card'))
        )
        return redirect('home')

def reload_view(request):
    if request.method == "GET":
        print('success')
    return HttpResponse('text')

def index_view(request):
    if request.method == "GET" and request.user.is_authenticated:
        rated = [i.rating_card.id for i in Rating.objects.filter(user=request.user)]
        return render(
            request,
            'home.html',
            make_context(
                request,
                RatingCard.objects.exclude(id__in=rated),
                '-id',
                RateForm(),
                pagination=(False, 20),
            ),
        )
    elif request.method == "POST" and request.user.is_authenticated:
        process_rate_post_request(
            request,
            int(request.POST.get('rating_card'))
        )
        return redirect('home')
        #return HttpResponse(status=200)
        #return JsonResponse({'status': 'ok'})
    else:
        return render(request, 'home.html')

def my_ratings_view(request):
    if request.method == "GET" and request.user.is_authenticated:
        return render(
            request,
            'my_ratings.html',
            make_context(
                request,
                Rating.objects.filter(user=request.user),
                '-id',
                RateForm(),
                pagination=(True, 20),
            ),
        )
    elif request.method == "POST" and request.user.is_authenticated:
        process_rate_post_request(
            request,
            int(request.POST.get('rating_card'))
        )
        return redirect('home')
    else:
        return render(request, 'home.html')

def my_recommendations_view(request):
    if request.method == "GET" and request.user.is_authenticated:
        try:
            #print("loading...")

            # TODO: all this loading code should be moved to a different place
            #       maybe make a miniserver to retrive this information from?
            #       sort of like a mini fake database...
            data = np.load("data/recommendations.npy", mmap_mode='r')
            users2matrix = np.load("data/users.npy", allow_pickle=True).flat[0] # it's a dictionary, TODO: maybe use pickle?
            matrix2cards = np.load("data/cards_back.npy", mmap_mode='r')
            cards2matrix = np.load("data/cards.npy", allow_pickle=True).flat[0]
            #print("loaded")

            matrix_id = users2matrix[request.user.pk]
            #print("matrix_id")

            predicted_ratings = data[matrix_id]
            #print("predicted_ratings")

            recommendations = [matrix2cards[matrix_card_id] for matrix_card_id in np.where(predicted_ratings > 1)][0]
            #print("recommendations")
            for recommendation in recommendations:
                obj, created = Recommendation.objects.get_or_create(
                    user=request.user,
                    rating_card=RatingCard.objects.get(id=recommendation),
                    defaults={'value': predicted_ratings[cards2matrix[recommendation]]},
                )

                if not created:
                    obj.value = predicted_ratings[cards2matrix[recommendation]]

            # Now update previously created recommendations
            # (since some of them might be totally wrong)
            for recommendation in Recommendation.objects.all().filter(user=request.user):
                recommendation.value = predicted_ratings[cards2matrix[recommendation.rating_card.id]]

        except KeyError:
            pass
            # this user doesn't have any recommendations yet

        return render(
            request,
            'my_recommendations.html',
            make_context(
                request,
                Recommendation.objects.filter(user=request.user),
                '-value',
                RateForm(),
                pagination=(True, 20),
            ),
        )
    if request.method == "POST" and request.user.is_authenticated:
        process_rate_post_request(
            request,
            int(request.POST.get('rating_card'))
        )
        return redirect('home')
    else:
        return render(request, 'home.html')

def new_card_view(request):
    form = NewCardForm()
    context = {'form': form}
    if request.method == 'GET':
        return render(request, 'new_card.html', context)

    elif request.method == 'POST':
        form = NewCardForm(request.POST)
        # do something with duplicates
        if form.is_valid():
            # there should be a way to save data directly, not like this
            card = RatingCard(
                title = form.cleaned_data['title'],
                url = form.cleaned_data['url'],
                text = form.cleaned_data['text'],
            )
            card.save()
            return redirect('home')
        else:
            print('form is not valid')
            return render(request, 'new_card.html', context)

def statistics_view(request):
    if request.method == 'GET':
        return render(request, 'statistics.html')
