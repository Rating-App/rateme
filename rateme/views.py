from django.shortcuts import render
from django.views import generic

from .models import Rating, RatingCard
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
            return render(request, 'rate.html', context)
        else:
            print('form is not valid')
            return render(request, 'rate.html', context)

def search_view(request):
    if request.method == "GET":
        pass
    #return render(request, 'search.html', context)

def make_pagination(current_page, pages_count):
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
    return pagination

def index_view(request):
    if request.user.is_authenticated:
        form = RateForm()
        current_page = int(request.GET.get('page')) if request.GET.get('page') else 1
        n = 20
        # get all cards rated by current user
        rated = [i.rating_card.id for i in Rating.objects.filter(user=request.user)]
        # exclude all rated cards and count unrated cards
        cards_count = RatingCard.objects.exclude(id__in=rated).count()
        pages_count = int(cards_count / n) + 1 if cards_count % n > 0 else int(cards_count / n)
        pagination = make_pagination(current_page, pages_count)
        # calculate offset and limit based on current page
        limit = n * current_page
        offset = limit - n
        # get 20 objects from unrated cards
        cards = RatingCard.objects.order_by('-id').exclude(id__in=rated)[offset:limit]
        context = {
            'cards': zip(
                [card.title for card in cards],
                [card.id for card in cards]
                # tags, ratings
                ),
            'pagination': pagination,
            'form': form,
            }
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
                        rating = form.cleaned_data['rating'],
                    )

                    rate.save()
                except Rating.DoesNotExist:
                    pass # todo
                except ValueError:
                    pass # todo
            return render(request, 'rate.html', context)

    else:
        context = {}
    return render(request, 'home.html', context)

def my_ratings_view(request):
    user = request.user
    context = {}
    if user.is_authenticated:
        try:
            # don't like that user=user but whatever
            ratings = Rating.objects.filter(user=user).order_by('-id')
            context['ratings'] = ratings
        except Rating.DoesNotExist:
            context['ratings'] = None
    return render(request, 'my_ratings.html', context)

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
            return render(request, 'new_card.html', context)
        else:
            print('form is not valid')
            return render(request, 'new_card.html', context)
