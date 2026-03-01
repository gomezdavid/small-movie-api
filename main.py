from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
import sqlite3
from typing import Optional

app = FastAPI()


# DDBB
DB_PATH = "movies.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS movies(
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT    NOT NULL,
            genre       TEXT    NOT NULL,
            rating      REAL    NOT NULL,
            review TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


init_db()

# MODELS


class MovieBase(BaseModel):
    title: str
    genre: str
    rating: int
    review: str

# This is what the client sends


class MovieCreate(MovieBase):
    pass

# This is for the API when returns the movie


class Movie(MovieBase):
    id: int


class MoviePatch(BaseModel):
    title: Optional[str] = None
    genre: Optional[str] = None
    rating: Optional[float] = None
    review: Optional[str] = None


# HELPER
# Como SQLITE returns me Rows, and i need a dictionary, this function helps with that
# Example without helper:
# row = db.execute("SELECT * FROM movies WHERE id = 1").fetchone()

# print(type(row))   # <class 'sqlite3.Row'>
# print(row["id"])         # 1
# print(row["title"])      # "Inception"
# print(row["director"])   # "Christopher Nolan"

def row_to_movie(row):
    return Movie(**dict(row))

# Movie(**dict(row))
# el ** "desempaqueta" el diccionario y se lo pasa a Movie como si fueran argumentos con nombre:
# Es exactamente igual a esto:
# Movie(id=1, title="Inception", director="Nolan", ...)

# ENDPOINTS


@app.get("/")
def get_root():
    return {"Message": "Welcome to Movies API"}


@app.get("/movies",)
def get_movies(db: sqlite3.Connection = Depends(get_db)):
    rows = db.execute("SELECT * FROM movies").fetchall()
    return [row_to_movie(r) for r in rows]


@app.get("/movies/{movie_id}")
def get_movie(movie_id: int, db: sqlite3.Connection = Depends(get_db)):
    row = db.execute("SELECT * FROM movies WHERE id = ?",
                     (movie_id,)).fetchone()
    if not row:
        raise HTTPException(
            status_code=404, detail=f"Película con id {movie_id} no encontrada.")
    return row_to_movie(row)


@app.post("/movies")
def post_movie(movie: MovieCreate, db: sqlite3.Connection = Depends(get_db)):
    """Crea una nueva película."""
    cursor = db.execute(
        "INSERT INTO movies (title, genre, rating, review) VALUES (?,?,?,?)",
        (movie.title, movie.genre, movie.rating,
         movie.review)
    )
    db.commit()
    new_id = cursor.lastrowid  # this returns the id that we just created.
    row = db.execute("SELECT * FROM movies WHERE id = ?",
                     (new_id,)).fetchone()
    return row_to_movie(row)


@app.patch("/movies/{movie_id}")
def patch_movie(movie_id: int, movie: MoviePatch, db: sqlite3.Connection = Depends(get_db)):
    """Actualiza solo los campos enviados de una película."""
    row = db.execute("SELECT * FROM movies WHERE id = ?",
                     (movie_id,)).fetchone()
    if not row:
        raise HTTPException(
            status_code=404, detail=f"Película con id {movie_id} no encontrada.")

    # This ignores the rest of the parameters that were not sent
    fields = movie.model_dump(exclude_unset=True)
    if not fields:
        raise HTTPException(
            status_code=400, detail="No se enviaron campos para actualizar.")

    set_clause = ", ".join(f"{k} = ?" for k in fields)
    values = list(fields.values()) + [movie_id]
    db.execute(f"UPDATE movies SET {set_clause} WHERE id = ?", values)
    db.commit()

    updated = db.execute(
        "SELECT * FROM movies WHERE id = ?", (movie_id,)).fetchone()
    return row_to_movie(updated)


@app.delete("/movies/{movie_id}")
def delete_movie(movie_id: int, db: sqlite3.Connection = Depends(get_db)):
    """Elimina una película por su ID."""
    row = db.execute("SELECT * FROM movies WHERE id = ?",
                     (movie_id,)).fetchone()
    if not row:
        raise HTTPException(
            status_code=404, detail=f"Película con id {movie_id} no encontrada.")
    db.execute("DELETE FROM movies WHERE id = ?", (movie_id,))
    db.commit()
    return {"message": f"Película {movie_id} eliminada correctamente."}
