from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import requests

app = FastAPI(title="CineVerse AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

TMDB_KEY = "your_tmdb_api_key_here"
TMDB_BASE = "https://api.themoviedb.org/3"
POSTER = "https://image.tmdb.org/t/p/w500"
BACKDROP = "https://image.tmdb.org/t/p/original"

def format_movie(m):
    if m.get('poster_path'):
        m['poster_url'] = POSTER + m['poster_path']
    if m.get('backdrop_path'):
        m['backdrop_url'] = BACKDROP + m['backdrop_path']
    if m.get('videos'):
        trailers = [v for v in m['videos'].get('results', []) if v['type'] == 'Trailer' and v['site'] == 'YouTube']
        if trailers:
            m['trailer_key'] = trailers[0]['key']
    if m.get('credits'):
        directors = [c['name'] for c in m['credits'].get('crew', []) if c['job'] == 'Director']
        m['director'] = directors[0] if directors else 'Unknown'
        m['cast'] = [c['name'] for c in m['credits'].get('cast', [])[:5]]
    if m.get('genres'):
        m['genres'] = [g['name'] for g in m['genres']]
    m['release_year'] = str(m.get('release_date', ''))[:4]
    m['rating'] = round(m.get('vote_average', 0), 1)
    return m

def tmdb_get(endpoint, params={}):
    params['api_key'] = TMDB_KEY
    params['language'] = 'en-US'
    r = requests.get(f"{TMDB_BASE}{endpoint}", params=params)
    return r.json()

@app.get("/")
def root():
    return {"message": "CineVerse AI is running!"}

@app.get("/trending")
def trending(n: int = 20):
    data = tmdb_get("/movie/popular", {"page": 1})
    movies = []
    for m in data.get('results', [])[:n]:
        detail = tmdb_get(f"/movie/{m['id']}", {"append_to_response": "credits,videos"})
        movies.append(format_movie(detail))
    return {"results": movies}

@app.get("/search")
def search(q: str = Query(...), limit: int = 10):
    data = tmdb_get("/search/movie", {"query": q})
    results = []
    for m in data.get('results', [])[:limit]:
        m['poster_url'] = POSTER + m['poster_path'] if m.get('poster_path') else None
        m['release_year'] = str(m.get('release_date', ''))[:4]
        m['rating'] = round(m.get('vote_average', 0), 1)
        m['genres'] = []
        results.append(m)
    return {"results": results}

@app.get("/recommend/{title}")
def recommend(title: str, n: int = 10):
    search_data = tmdb_get("/search/movie", {"query": title})
    results_raw = search_data.get('results', [])
    if not results_raw:
        return {"source_movie": title, "results": []}
    source = results_raw[0]
    source_detail = tmdb_get(f"/movie/{source['id']}", {"append_to_response": "similar,credits,videos"})
    similar = source_detail.get('similar', {}).get('results', [])[:n]
    movies = []
    for m in similar:
        detail = tmdb_get(f"/movie/{m['id']}", {"append_to_response": "credits,videos"})
        fm = format_movie(detail)
        fm['similarity'] = round(85 + (m.get('vote_average', 7) * 1.2), 1)
        movies.append(fm)
    return {"source_movie": title, "results": movies}

@app.get("/movie/{movie_id}")
def movie_detail(movie_id: int):
    m = tmdb_get(f"/movie/{movie_id}", {"append_to_response": "credits,videos"})
    return format_movie(m)

@app.get("/genre/{genre_name}")
def by_genre(genre_name: str, n: int = 20):
    genres_data = tmdb_get("/genre/movie/list")
    genre_map = {g['name'].lower(): g['id'] for g in genres_data.get('genres', [])}
    genre_id = genre_map.get(genre_name.lower())
    if not genre_id:
        return {"results": []}
    data = tmdb_get("/discover/movie", {"with_genres": genre_id, "sort_by": "popularity.desc"})
    movies = []
    for m in data.get('results', [])[:n]:
        m['poster_url'] = POSTER + m['poster_path'] if m.get('poster_path') el
