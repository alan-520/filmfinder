from . import search
from flask import render_template, flash, redirect, url_for, request
from app import db
from flask_login import current_user
from flask_wtf import FlaskForm
from .forms import SearchForm
import json

@search.route('/film_search', methods=['GET', 'POST'])
def film_search():
    mycol = db['movies']
    form = SearchForm(request.form)
    if request.method == 'POST':
        arr = []
        data = form.search.data
        result = mycol.find({"$or": [{'movie_name': {"$regex": data, "$options": "$i"}},
                                     {'movie_type': {"$regex": data, "$options": "$i"}},
                                     {'actor': {"$regex": data, "$options": "$i"}},
                                     {'director': {"$regex": data, "$options": "$i"}},
                                     {'description': {"$regex": data, "$options": "$i"}},
                                     ]})
        for i in result:
            del i['_id']
            arr.append(i['movie_id'])
        arr = json.dumps(arr)
        return redirect(url_for('search.film_search_results', movie_id=arr))
    return render_template('/search/film_search.html', form=form)

@search.route('/film_search_results/?<string:movie_id>', methods=['GET', 'POST'])
def film_search_results(movie_id):
    res = []
    movie_id = json.loads(movie_id)
    mycoll = db['movies']
    for j in movie_id:
        a = mycoll.find_one({"movie_id": j})
        del a['_id']
        del a['description']
        res.append(a)
    list = res
    return render_template('/search/film_search_results.html', list = list)