from django.core.management.base import BaseCommand, CommandError
from rateme.models import RatingCard, Recommendation
from django.db import IntegrityError
from django.contrib.auth.models import User
import time

import numpy as np
from scipy.sparse import csc_matrix
from sparsesvd import sparsesvd
import psycopg2
import time
import sys

NSTEPS = 1
RANK = 200
CONSIDER_ACTIVE = 60*60*24 # in seconds, i.e. 60*60*24 -- only update those users that logged in at least a day ago
MINRATING = 0.5 # minimum rating to consider for recommendation
SMALL = 0.1 # if predicted rating changed by less than this, don't update the records

class Command(BaseCommand):
    help = 'Makes recommendations'

    def handle(self, *args, **options):
        conn = psycopg2.connect("dbname='rateme' user='rateme' host='localhost' password='1'")

        cur = conn.cursor()

        users = {}
        users_back = []
        cards = {}
        cards_back = []

        # matrices to store result in;
        # we need two to compute the rate of change
        old_row_num = 1
        old_col_num = 1
        Mold = csc_matrix((old_row_num, old_col_num)).toarray()

        Recommendation.objects.all().delete()
        while True:
            cur.execute("""SELECT * from rateme_rating""")
            rows = cur.fetchall()

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

#            del rows # free some memory
            print("There are " + str(num_users) + " users, " +\
                   str(num_cards) + " cards and " + str(len(data)) + " votes. Sparseness is " +\
                   str(len(data)/(num_users*num_cards)*100) + "%")

            def project_low_rank(matrix):
                ut, s, vt = sparsesvd(csc_matrix(matrix), RANK)

                return ut.T @ np.diag(s) @ vt

            observed_padded = csc_matrix((data, (mrow, mcol)), shape=(num_users, num_cards))
            mask = csc_matrix((np.ones(len(data)), (mrow, mcol)), shape=(num_users, num_cards)).toarray()
            M = csc_matrix((np.zeros(len(data)), (mrow, mcol)), shape=(num_users, num_cards)).toarray()
            N = csc_matrix((np.zeros(len(data)), (mrow, mcol)), shape=(num_users, num_cards)).toarray()

            M[:old_row_num, :old_col_num] = Mold
            N[:old_row_num, :old_col_num] = Mold
            Mold = M
            old_row_num = num_users
            old_col_num = num_cards

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

            i = 0
            for m,n in np.argwhere(M >= MINRATING):
                if m < old_row_num and n < old_col_num and np.abs(M[m,n] - Mold[m,n]) > SMALL:
                    #INSERT INTO rateme_recommendation VALUES (1,1,1);
                    # Ok, donno how to do this, let's just use Django objects for now...
                    # The problem comes from i. How do I know which id to choose??
                    """
                    cur.execute("INSERT INTO rateme_recommendation VALUES (" +\
                                 str(users_back[m]) + "," +\
                                 str(cards_back[n]) + "," + str(i) + ");")
                    i += 1
                    """
                    user = User.objects.all().get(pk=users_back[m])
                    if user.last_login and \
                       int(time.time()) - int(user.last_login.strftime('%s')) < CONSIDER_ACTIVE:

                        try:
                            recommendation = Recommendation()
                            recommendation.user = User.objects.all().get(pk=users_back[m])
                            recommendation.rating_card = RatingCard.objects.all().get(pk=cards_back[n])
                            recommendation.value = M[m,n]
                            recommendation.save()
                        except IntegrityError:
                            pass # TODO: modify previous value 
                    i = i + 1
                    if i % 1000 == 0:
                        print(i, time.time() - starting_time)
                else:
                    print("didn't change")

