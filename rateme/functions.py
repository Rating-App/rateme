from .forms import RateForm, NewCardForm
from django.shortcuts import render, redirect
from .models import Rating, RatingCard, Recommendation

def make_context(request, n, db_query, order, form):
    context = {}
    current_page = int(request.GET.get('page')) \
        if request.GET.get('page') else 1
    try:
        pagination, data = make_page(
            current_page,
            n,
            db_query,
            order,
        )
        context.update({
            'pagination': pagination,
            'data': data,
            'form': form,
        })
    except RatingCard.DoesNotExist:
        context['data'] = None
    return context

def make_page(current_page, n, db_query, order):
    rows_count = db_query.count()
    pages_count = int(rows_count / n) + 1 if rows_count % n > 0 \
        else int(rows_count / n)
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

def process_rate_post_request(request, pk):
    form = RateForm(request.POST)
    if form.is_valid():
        print(form.cleaned_data)
        print(request.POST.get('rating_card'))
        try:
            rate = Rating(
                rating_card = RatingCard.objects.get(pk=pk),
                user = request.user,
            )
            print(rate)
            rate.rating = form.cleaned_data['rating']
            rate.save(update_fields=['rating']) # field won't update for some reason
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
            pass
        return redirect('home')
    else:
        print('form is not valid')
        return redirect('rate', pk)
