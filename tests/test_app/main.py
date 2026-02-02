from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from app.database import pool, get_db  # Import the pool and the generator

from app.routers import post, user, auth, vote

@asynccontextmanager
async def lifespan(app: FastAPI):
    pool.open()
    yield
    pool.close()

app = FastAPI(lifespan=lifespan)

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)