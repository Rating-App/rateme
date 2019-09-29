from django.core.management.base import BaseCommand, CommandError
from rateme.models import RatingCard, Rating
from django.db import IntegrityError
import os
from django.contrib.auth.models import User
import csv

class Command(BaseCommand):
    help = 'Import rating card data from ficbook.net'

    def handle(self, *args, **options):
        # TODO: refactor
        # - combine common parts of the functions
        # - first parse the string to parameters, then pass those around

        path = os.path.dirname(os.path.realpath(__file__))

        # Movies (move to helper)
        movies_path = path + "/../../../../scrapy/ficbook/FanficItem.csv"

        with open(movies_path, 'r') as movies_file:
            print("Importing fanfics...")
            parsed_file = csv.reader(movies_file, delimiter=',', quotechar='|')
            i = 0
            for fanfic in parsed_file:
                if i > 0:
                    if not RatingCard.objects.filter(card_id=fanfic[0]):
                        # only add if it wasn't added before
                        ratingCard = RatingCard()
                        ratingCard.card_id = fanfic[0]
                        ratingCard.title = ",".join(fanfic[1:-1])
                        ratingCard.url = fanfic[-1]
                        try:
                            ratingCard.save()
                        except IntegrityError:
                            print("already exists")
                    else:
                        print("was added before")
                    print(str(i))
                i += 1
