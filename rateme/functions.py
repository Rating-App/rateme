from .forms import RateForm, NewCardForm
from django.shortcuts import render, redirect
from .models import Rating, RatingCard, Recommendation
from django.db import IntegrityError

def make_context(request, db_query, order, form, **kwargs):
    '''
    Optional arguments:
    query='string': search query
    pagination=(True/False, n): enable/disable pagination, number of items per page
    '''
    context = {}
    try:
        if 'pagination' in kwargs:
            current_page = int(request.GET.get('page')) \
                if request.GET.get('page') else 1
            n = kwargs['pagination'][1]
            limit = n * current_page
            offset = limit - n
            limited_query = db_query.order_by(order)[offset:limit]
            rows_count = db_query.count()
            pages_count = int(rows_count / n) + 1 if rows_count % n > 0 \
                else int(rows_count / n)
            if kwargs['pagination'][0] == True:
                if 'query' in kwargs:
                    pagination = make_pagination(current_page, n, pages_count, query=kwargs['query'])
                else:
                    pagination = make_pagination(current_page, n, pages_count)
                context.update({
                    'data': limited_query,
                    'pagination': pagination,
                    'form': form,
                })
            elif kwargs['pagination'][0] == False:
                context.update({
                    'data': limited_query,
                    'form': form,
                })
        else:
            context.update({
                'data': db_query,
                'form': form,
            })
    except RatingCard.DoesNotExist: # todo
        context['data'] = None
    return context

def make_pagination(current_page, n, pages_count, **kwargs):
    pagination = []
    if 'query' in kwargs:
        for page in range(1, pages_count+1):
            if page == current_page:
                string = '[ <a class="active" href="?search=%s&page=%s">%s</a> ]' % (
                    kwargs['query'],
                    current_page,
                    current_page
                    )
            else:
                string = '[  <a href="?search=%s&page=%s">%s</a> ]' % (
                    kwargs['query'],
                    page,
                    page
                    )
            pagination.append(string)
    else:
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

def process_rate_post_request(request, pk):
    form = RateForm(request.POST)
    if form.is_valid():
        print(form.cleaned_data)
        print(request.POST.get('rating_card'))
        try:
            rate = Rating(
                user = request.user,
                rating = form.cleaned_data['rating'],
                rating_card = RatingCard.objects.get(pk=pk),
            )
            #print(rate)
            #rate.rating = form.cleaned_data['rating']
            print(rate)
            rate.save() # field won't update for some reason
        except Rating.DoesNotExist:
            rate = Rating(
                rating_card = RatingCard.objects.get(pk=pk),
                user = request.user,
                rating = form.cleaned_data['rating'],
            )
            rate.save()
        except ValueError:
            pass # todo
        except IntegrityError:
            pass # do this as well!
        return redirect('home')
    else:
        print('form is not valid')
        return redirect('rate', pk)
