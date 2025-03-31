from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from routers import gifts, users, db

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://wishesbook.ru",
        "https://wishesbook.ru"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up...")
    yield
    print("Shutting down...")
    db.close()


app.router.lifespan_context = lifespan

app.include_router(gifts.router)
app.include_router(users.router)
