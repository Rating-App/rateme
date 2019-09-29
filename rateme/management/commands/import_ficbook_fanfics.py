from django.core.management.base import BaseCommand, CommandError
from rateme.models import RatingCard, Rating
from django.db import IntegrityError
import os
from django.contrib.auth.models import User

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
            i = 0
            for line in movies_file:
                if i > 0:
                    fanfic = line.split(",")
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
