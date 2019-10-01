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

NSTEPS = 10#3 # number of iteration steps between saving
# NOTE: rank 15 is too small, let's try 30
# 30 is still too small, try 60. NOTE: 100 was ok but felt like overfitting. Overfitting better?

RANK = 10 # 7 # 5
CONSIDER_ACTIVE = 30*60*60*24 # in seconds, 
                              # i.e. 60*60*24 -- only update those users that logged in at least a day ago
MINRATING = 0.1 # minimum rating to consider for recommendation
SMALL = 0.1 # if predicted rating changed by less than this, don't update the records
EPSILON = 0.5#0.45#0.37 # used for regularization

class Command(BaseCommand):
    help = 'Makes recommendations'

    def handle(self, *args, **options):
        conn = psycopg2.connect("dbname='rateme' user='rateme' host='localhost' password='1'")

        cur = conn.cursor()

        try:
            users = np.load("data/users.npy", allow_pickle=True).flat[0]
            users_back = list(np.load('data/users_back.npy'))
            cards = np.load("data/cards.npy", allow_pickle=True).flat[0]
            cards_back = list(np.load('data/cards_back.npy'))
            M = np.load('data/recommendations.npy')

        except:
            users = {}
            users_back = []
            cards = {}
            cards_back = []
            M = csc_matrix((1, 1)).toarray()

        iter_num = 0
        starting_time = time.time()
        while True:
            cur.execute("""SELECT id,user_id,rating,rating_card_id from rateme_rating""")
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
            #M = csc_matrix((np.zeros(len(data)), (mrow, mcol)), shape=(num_users, num_cards)).toarray()
            M.resize((num_users, num_cards), refcheck=False)
            N = csc_matrix((np.zeros(len(data)), (mrow, mcol)), shape=(num_users, num_cards)).toarray()

            #M[:old_row_num, :old_col_num] = Mold
            #N[:old_row_num, :old_col_num] = Mold
            #old_row_num = num_users
            #old_col_num = num_cards

            def project_one_rank(matrix):
                ut, s, vt = sparsesvd(csc_matrix(matrix), 1)

                return ut.T @ np.diag(s) @ vt

            W = project_one_rank(mask)

            print("glabal iter, iter, time, delay, step, dist")
            last_time = time.time()
            for i in range(NSTEPS):
                M = project_low_rank(M + (observed_padded - M*mask)/(W + EPSILON))

                print(iter_num, i, time.time() - starting_time,
                         time.time() - last_time,
                            np.linalg.norm(N-M),
                            np.linalg.norm(M - observed_padded - M*(1-mask)))
                last_time = time.time()
                N = M

                iter_num += 1

            np.save('data/recommendations', M)
            np.save('data/users', users)
            np.save('data/users_back', users_back)
            np.save('data/cards', cards)
            np.save('data/cards_back', cards_back)
