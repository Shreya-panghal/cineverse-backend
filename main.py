from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from recommender import CineVerseRecommender
from typing import Optional

app = FastAPI(title="CineVerse AI API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

recommender = CineVerseRecommender()
POSTER_BASE = "https://image.tmdb.org/t/p/w500"
BACKDROP_BASE = "https://image.tmdb.org/t/p/original"

def format_movie(m: dict) -> dict:
    import ast
    for field in ['genres', 'cast', 'keywords']:
        if isinstance(m.get(field), str):
            try:
                m[field] = ast.literal_eval(m[field])
            except:
                m[field] = []
    if m.get('poster_path'):
        m['poster_url'] = POSTER_BASE + m['poster_path']
    if m.get('backdrop_path'):
        m['backdrop_url'] = BACKDROP_BASE + m['backdrop_path']
    if m.get('trailer_key'):
        m['trailer_url'] = f"https://www.youtube.com/embed/{m['trailer_key']}"
        m['trailer_thumbnail'] = f"https://img.youtube.com/vi/{m['trailer_key']}/maxresdefault.jpg"
    return m

@app.get("/")
def root():
    return {"message": "🎬 CineVerse AI is running!", "movies": len(recommender.df)}

@app.get("/recommend/{title}")
def recommend(title: str, n: int = 10, genre: Optional[str] = None,
              year_from: Optional[int] = None, min_rating: Optional[float] = None):
    filters = {"genre": genre, "year_from": year_from, "min_rating": min_rating}
    filters = {k: v for k, v in filters.items() if v is not None}
    result = recommender.get_recommendations(title, n, filters)
    result['results'] = [format_movie(m) for m in result['results']]
    return result

@app.get("/search")
def search(q: str = Query(..., min_length=1), limit: int = 10):
    results = recommender.search_movies(q, limit)
    return {"results": [format_movie(m) for m in results]}

@app.get("/movie/{movie_id}")
def movie_detail(movie_id: int):
    movie = recommender.get_movie_by_id(movie_id)
    if not movie:
        return {"error": "Movie not found"}
    return format_movie(movie)

@app.get("/trending")
def trending(n: int = 20):
    movies = recommender.get_trending(n)
    return {"results": [format_movie(m) for m in movies]}

@app.get("/genre/{genre}")
def by_genre(genre: str, n: int = 20):
    movies = recommender.get_by_genre(genre, n)
    return {"results": [format_movie(m) for m in movies]}

# Run with: uvicorn main:app --reload --port 8000