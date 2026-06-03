from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import pandas as pd
import pickle
from sklearn.metrics.pairwise import cosine_similarity

app = FastAPI(title="CineVerse AI API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

POSTER_BASE = "https://image.tmdb.org/t/p/w500"
BACKDROP_BASE = "https://image.tmdb.org/t/p/original"

# Dummy data for testing
MOVIES = [
    {"id": 1, "title": "Inception", "genres": ["Action", "Sci-Fi"], "director": "Christopher Nolan", "cast": ["Leonardo DiCaprio"], "rating": 8.8, "release_year": "2010", "poster_path": "/9gk7adHYeDvHkCSEqAvQNLV5Uge.jpg", "overview": "A thief who steals corporate secrets through dream-sharing technology.", "trailer_key": "YoHD9XEInc0", "backdrop_path": "/s3TBrRGB1iav7gFOCNx3H31MoES.jpg", "tagline": "Your mind is the scene of the crime", "runtime": 148},
    {"id": 2, "title": "The Dark Knight", "genres": ["Action", "Crime"], "director": "Christopher Nolan", "cast": ["Christian Bale", "Heath Ledger"], "rating": 9.0, "release_year": "2008", "poster_path": "/qJ2tW6WMUDux911r6m7haRef0WH.jpg", "overview": "Batman faces the Joker, a criminal mastermind.", "trailer_key": "EXeTwQWrcwY", "backdrop_path": "/hqkIcbrOHL86UncnHIsHVcVmzue.jpg", "tagline": "Why so serious?", "runtime": 152},
    {"id": 3, "title": "Interstellar", "genres": ["Sci-Fi", "Drama"], "director": "Christopher Nolan", "cast": ["Matthew McConaughey"], "rating": 8.6, "release_year": "2014", "poster_path": "/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg", "overview": "A team of explorers travel through a wormhole in space.", "trailer_key": "zSWdZVtXT7E", "backdrop_path": "/xJHokMbljvjADYdit5fK5VQsXEG.jpg", "tagline": "Mankind was born on Earth. It was never meant to die here.", "runtime": 169},
]

def format_movie(m):
    m = dict(m)
    if m.get('poster_path'):
        m['poster_url'] = POSTER_BASE + m['poster_path']
    if m.get('backdrop_path'):
        m['backdrop_url'] = BACKDROP_BASE + m['backdrop_path']
    if m.get('trailer_key'):
        m['trailer_url'] = f"https://www.youtube.com/embed/{m['trailer_key']}"
    return m

@app.get("/")
def root():
    return {"message": "CineVerse AI is running!", "movies": len(MOVIES)}

@app.get("/trending")
def trending(n: int = 20):
    return {"results": [format_movie(m) for m in MOVIES[:n]]}

@app.get("/search")
def search(q: str = Query(..., min_length=1), limit: int = 10):
    results = [m for m in MOVIES if q.lower() in m['title'].lower()]
    return {"results": [format_movie(m) for m in results[:limit]]}

@app.get("/recommend/{title}")
def recommend(title: str, n: int = 10):
    results = [m for m in MOVIES if m['title'].lower() != title.lower()]
    return {"source_movie": title, "results": [format_movie(m) for m in results[:n]]}

@app.get("/movie/{movie_id}")
def movie_detail(movie_id: int):
    movie = next((m for m in MOVIES if m['id'] == movie_id), None)
    if not movie:
        return {"error": "Movie not found"}
    return format_movie(movie)
# Run with: uvicorn main:app --reload --port 8000
