# Movies API

REST API for managing movies, built with FastAPI and SQLite.

## Technologies
- **FastAPI** — web framework for building APIs with Python
- **SQLite** — file-based database, no external server required
- **Pydantic** — data validation and serialization
- **Uvicorn** — ASGI server to run the application

## Concepts applied
- REST endpoints with GET, POST, PATCH and DELETE methods
- Data validation with Pydantic models
- SQLite persistence with `sqlite3` from the Python standard library
- Dependency injection with `Depends` for database connection management
- Partial updates with PATCH using `model_dump(exclude_unset=True)`
- Automatic error handling with `HTTPException`

## Installation
```bash
pip install "fastapi[standard]"
fastapi dev main.py
```

The database file `movies.db` is created automatically on first run.

Interactive documentation available at `http://localhost:8000/docs`.

## Data model

| Field | Type | Required |
|-------|------|----------|
| id | integer | auto-generated |
| title | string | yes |
| genre | string | yes |
| rating | float | yes |
| review | string | no |

## Endpoints

### GET /movies
Returns all movies.

```
GET /movies
```

### GET /movies/{id}
Returns a single movie by ID. Returns 404 if not found.

```
GET /movies/1
```

### POST /movies
Creates a new movie.

```
POST /movies

{
  "title": "The Dark Knight",
  "genre": "Action",
  "rating": 9.0,
  "review": "One of the best superhero films ever made."
}
```

### PATCH /movies/{id}
Partially updates a movie. Only the fields included in the request body will be modified.

```
PATCH /movies/1

{
  "rating": 9.5
}
```

### DELETE /movies/{id}
Deletes a movie by ID. Returns 404 if not found.

```
DELETE /movies/1
```

## Project structure

```
.
├── main.py       # application, models and endpoints
└── movies.db     # SQLite database (auto-generated)
```
