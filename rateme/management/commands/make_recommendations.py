from django.core.management.base import BaseCommand, CommandError
from rateme.models import RatingCard, Recommendation
from django.db import IntegrityError
from django.contrib.auth.models import User

import numpy as np
from scipy.sparse import csc_matrix
from sparsesvd import sparsesvd
import psycopg2
import time
import sys

NSTEPS = 100
RANK = 100

class Command(BaseCommand):
    help = 'Makes recommendations'

    def handle(self, *args, **options):
        conn = psycopg2.connect("dbname='rateme' user='rateme' host='localhost' password='1'")

        cur = conn.cursor()
        cur.execute("""SELECT * from rateme_rating""")
        rows = cur.fetchall()

        users = {}
        users_back = []
        cards = {}
        cards_back = []

        for row in rows:
            # (66870, 432, 'neutral', 1545)
            rating_id, user_id, rating_val, card_id = row

            user_id = int(user_id)
            card_id = int(card_id)
            
            if user_id not in users:
                users[user_id] = len(users)
                users_back.append(user_id)
            
            if card_id not in cards:
                cards[card_id] = len(cards)
                cards_back.append(card_id)

        num_users = len(users)
        num_cards = len(cards)

        print("There are " + str(num_users) + " users and " + str(num_cards) + " cards")

        def todata(rating_val):
            if rating_val == "completely not interested":
                return -2
            elif rating_val == "not interested":
                return -1
            elif rating_val == "neutral":
                return 0
            elif rating_val == "interested":
                return 1
            elif rating_val == "very interested":
                return 2
            else:
                print("ERROR")
                return 0

        # Rows: users, Columns: cards
        # I.e. users x cards

        mrow = []
        mcol = []
        data = []

        for row in rows:
            # (66870, 432, 'neutral', 1545)
            rating_id, user_id, rating_val, card_id = row

            mrow.append(users[user_id])
            mcol.append(cards[card_id])
            data.append(todata(rating_val))

        def project_low_rank(matrix):
            ut, s, vt = sparsesvd(csc_matrix(matrix), RANK)

            return ut.T @ np.diag(s) @ vt

        observed_padded = csc_matrix((data, (mrow, mcol)), shape=(num_users, num_cards))
        mask = csc_matrix((np.ones(len(data)), (mrow, mcol)), shape=(num_users, num_cards)).toarray()
        M = csc_matrix((np.zeros(len(data)), (mrow, mcol)), shape=(num_users, num_cards)).toarray()
        N = csc_matrix((np.zeros(len(data)), (mrow, mcol)), shape=(num_users, num_cards)).toarray()

        print("iter, time, delay, step, dist")
        starting_time = time.time()
        last_time = time.time()
        for i in range(NSTEPS):
            M = project_low_rank(M + (observed_padded - M*mask))

            print(i, time.time() - starting_time,
                     time.time() - last_time,
                        np.linalg.norm(N-M),
                        np.linalg.norm(M - observed_padded - M*(1-mask)))
            last_time = time.time()
            N = M

        #np.save('recomendations', M)

        print("exporting to DB")

        # i = 0
        Recommendation.objects.all().delete()
        for m in range(num_users):
            for n in range(num_cards):
                if M[m,n] > 0.5:
                    #INSERT INTO rateme_recommendation VALUES (1,1,1);
                    # Ok, donno how to do this, let's just use Django objects for now...
                    # The problem comes from i. How do I know which id to choose??
                    """
                    cur.execute("INSERT INTO rateme_recommendation VALUES (" +\
                                 str(users_back[m]) + "," +\
                                 str(cards_back[n]) + "," + str(i) + ");")
                    i += 1
                    """
                    recommendation = Recommendation()
                    recommendation.user = User.objects.all().get(pk=users_back[m])
                    recommendation.rating_card = RatingCard.objects.all().get(pk=cards_back[n])
                    recommendation.value = M[m,n]
                    recommendation.save()
            
            print(m)
