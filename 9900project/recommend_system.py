import pandas as pd
import numpy as np
from pandas import DataFrame
import math
import pymongo
import random
from operator import itemgetter

class Recommendation_System():
    def __init__(self, comments):
        self.comments = comments
        self.movie_sim_matrix = {}
        self.movie_popular = {}
        self.movie_count = 0

    def dbcomments2dataframe(self):
        df = pd.DataFrame(columns=['username', 'movie_id', 'movie_name', 'ratings'])
        i = 0
        for x in self.comments.find():
            df.loc[i, 'username'] = x['username']
            df.loc[i, 'movie_name'] = x['movie_name']
            df.loc[i, 'ratings'] = x['ratings']
            df.loc[i, 'movie_id'] = x['movie_id']
            i += 1
        X = df['username']
        Y = df['movie_id']
        data = df.copy()
        return X, Y, data

    def ItemSimilarity(self, X, Y):
        user_item = dict()
        for i in range(Y.count()):
            user = X.iloc[i]
            item = Y.iloc[i]
            if user not in user_item:
                user_item[user] = set()
            user_item[user].add(item)
        C = {}
        N = {}
        for u, items in user_item.items():
            for i in items:
                N.setdefault(i, 0)
                N[i] += 1
                C.setdefault(i, {})
                for j in items:
                    if i == j:
                        continue
                    C[i].setdefault(j, 0)
                    C[i][j] += 1 / math.log(1 + len(user_item[u]))
        W = C.copy()
        maxw = np.zeros(len(W) + 1)
        for i, related_items in C.items():
            for j, cij in related_items.items():
                W[i][j] = cij / math.sqrt(N[i] * N[j])
        return W, user_item

    def recommend(self, user, user_item, W, K):
        rank = {}
        interacted_items = user_item[user]
        for i in interacted_items:
            for j, wij in sorted(W[i].items(), key=lambda x: x[1], reverse=True)[0:K]:
                if j in interacted_items:
                    continue
                rank.setdefault(j, 0)
                rank[j] += wij
        rank = sorted(rank.items(), key=lambda x: x[1], reverse=True)
        return rank

    def movie_rank(self, data, rank):
        movie_id_rank = [x[0] for x in rank]
        movie_rank = set()
        for i in range(data.shape[0]):
            if data.loc[i, 'movie_id'] in movie_id_rank:
                movie_rank.add(data.loc[i, 'movie_name'])
        movie_rank = list(movie_rank)
        return movie_rank

    def get_dataset(self, data, pivot=0.75):
        trainSet = {}
        testSet = {}
        trainSet_len = 0
        testSet_len = 0
        for i in range(data.shape[0]):
            user = data.loc[i, 'username']
            movie = data.loc[i, 'movie_id']
            rating = data.loc[i, 'ratings']
            if (random.random() < pivot):
                trainSet.setdefault(user, {})
                trainSet[user][movie] = rating
                trainSet_len += 1
            else:
                testSet.setdefault(user, {})
                testSet[user][movie] = rating
                testSet_len += 1
        return trainSet, testSet

    def calc_movie_sim(self, trainSet):
        movie_sim_matrix = {}
        movie_popular = {}
        movie_count = 0
        for user, movies in trainSet.items():
            for movie in movies:
                if movie not in movie_popular:
                    movie_popular[movie] = 0
                else:
                    movie_popular[movie] += 1
        movie_count = len(movie_popular)
        for user, movies in trainSet.items():
            for m1 in movies:
                for m2 in movies:
                    if m1 == m2:
                        continue
                    movie_sim_matrix.setdefault(m1, {})
                    movie_sim_matrix[m1].setdefault(m2, 0)
                    movie_sim_matrix[m1][m2] += 1
        for m1, related_movies in movie_sim_matrix.items():
            for m2, count in related_movies.items():
                if movie_popular[m1] == 0 or movie_popular[m2] == 0:
                    movie_sim_matrix[m1][m2] = 0
                else:
                    movie_sim_matrix[m1][m2] = count / math.sqrt(movie_popular[m1] * movie_popular[m2])
        return movie_sim_matrix, movie_popular, movie_count

    def item_based_recommend(self, user, K, N, trainSet, movie_sim_matrix):
        # K = int(self.n_sim_movie)
        # N = int(self.n_rec_movie)
        rank = {}
        watched_movies = trainSet[user]
        for movie, rating in watched_movies.items():
            for related_movie, w in sorted(movie_sim_matrix[movie].items(), key=itemgetter(1), reverse=True)[:K]:
                if related_movie in watched_movies:
                    continue
                rank.setdefault(related_movie, 0)
                rank[related_movie] += w * float(rating)
        return sorted(rank.items(), key=itemgetter(1), reverse=True)[:N]

    def evaluate(self, N, reuserN, trainSet, testSet, movie_sim_matrix, movie_count):
        # N = int(self.n_rec_movie)
        # reuserN = input("请输入参与评估的用户数量：（总用户数为457）")
        # reuserN = int(reuserN)
        hit = 0
        rec_count = 0
        test_count = 0
        all_rec_movies = set()
        for user, m in list(trainSet.items())[:reuserN]:
            test_moives = testSet.get(user, {})
            rec_movies = self.item_based_recommend(user, 70, N, trainSet, movie_sim_matrix)
            for movie, w in rec_movies:
                if movie in test_moives:
                    hit += 1
                all_rec_movies.add(movie)
            rec_count += N
            test_count += len(test_moives)

        precision = hit / (1.0 * rec_count)
        recall = hit / (1.0 * test_count)
        coverage = len(all_rec_movies) / (1.0 * movie_count)

    def precommend(self, rec_m, movies):
        movie_recom_item_based = []
        for x, y in rec_m:
            result = movies.find_one({"movie_id": x})
            movie_name = result['movie_name']
            movie_recom_item_based.append(movie_name)
        return movie_recom_item_based