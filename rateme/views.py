from django.shortcuts import render, redirect
from django.views import generic

from django.db import IntegrityError
from django.db.models import Q

from .models import Rating, RatingCard, Recommendation
from .forms import RateForm, NewCardForm

def process_form(form):
    pass

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
        form = RateForm(request.POST)
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
            return redirect('home')
        else:
            print('form is not valid')
            return render(request, 'rate.html', context)

def search_view(request):
    # todo: length limit
    # todo: fix bug with pagination
    if request.method == "GET":
        query = request.GET.get('search')
        context = {}
        form = RateForm()
        if query:
            try:
                pagination, data = make_page(
                    int(request.GET.get('page')) if request.GET.get('page') else 1,
                    20,
                    RatingCard.objects.filter(
                        Q(title__icontains=query) | Q(text__icontains=query)
                    ),
                    '-id'
                )
                context.update({
                    'pagination': pagination,
                    'data': data,
                    'form': form
                })
            except RatingCard.DoesNotExist:
                pass # todo
        else:
            context = {
                'data': None
            }
        return render(request, 'search.html', context)

def make_page(current_page, n, db_query, order):
    rows_count = db_query.count()
    pages_count = int(rows_count / n) + 1 if rows_count % n > 0 else int(rows_count / n)
    pagination = []
    for page in range(1, pages_count+1):
        if page == current_page:
            string = '[ <a class="active" href="?page=%s">%s</a> ]' % (
                current_page,
                current_page
                )
        else:
            string = '[ <a href="?page=%s">%s</a> ]' % (
                page,
                page
                )
        pagination.append(string)
    limit = n * current_page
    offset = limit - n
    limited_query = db_query.order_by(order)[offset:limit]
    return pagination, limited_query

def index_view(request):
    if request.user.is_authenticated:
        form = RateForm()
        context = {}
        # get all cards rated by current user
        rated = [i.rating_card.id for i in Rating.objects.filter(user=request.user)]
        try:
            pagination, data = make_page(
                int(request.GET.get('page')) if request.GET.get('page') else 1,
                20,
                RatingCard.objects.exclude(id__in=rated),
                '-id'
            )
            context.update({
                'pagination': pagination,
                'data': data,
                'form': form
            })
        except RatingCard.DoesNotExist:
            context['data'] = None
        if request.method == "POST":
            form = RateForm(request.POST)
            if form.is_valid():
                print(form.cleaned_data)
                print(request.POST.get('rating_card'))
                try:
                    rate = Rating(
                        rating_card = RatingCard.objects.get\
                            (pk=int(request.POST.get('rating_card'))),
                        user = request.user,
                    )
                    print(rate)
                    rate.rating = form.cleaned_data['rating']

                    rate.save() # field won't update for some reason
                except Rating.DoesNotExist:
                    rate = Rating(
                        rating_card = RatingCard.objects.get\
                            (pk=int(request.POST.get('rating_card'))),
                        user = request.user,
                        rating = form.cleaned_data['rating'],
                    )

                    rate.save()
                except ValueError:
                    pass # todo
                except IntegrityError:
                    pass
            return render(request, 'home.html', context)

    else:
        context = {}
    return render(request, 'home.html', context)

def my_ratings_view(request):
    user = request.user
    form = RateForm()
    context = {}
    if user.is_authenticated:
        try:
            pagination, data = make_page(
                int(request.GET.get('page')) if request.GET.get('page') else 1,
                20,
                Rating.objects.filter(user=user),
                '-id'
            )
            context.update({
                'pagination': pagination,
                'data': data,
                'form': form
            })
        except Rating.DoesNotExist:
            context['data'] = None
    return render(request, 'my_ratings.html', context)

def my_recommendations_view(request):
    user = request.user
    form = RateForm()
    context = {}
    if user.is_authenticated:
        try:
            pagination, data = make_page(
                int(request.GET.get('page')) if request.GET.get('page') else 1,
                20,
                Recommendation.objects.filter(user=user),
                '-value'
            )
            context.update({
                'pagination': pagination,
                'data': data,
                'form': form
            })
        except Rating.DoesNotExist:
            context['data'] = None
    return render(request, 'my_recommendations.html', context)

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
