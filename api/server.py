# built-in modules
import os

# pip modules
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# local modules
from configs.db import connect_db


# Routes
from routers.auth_router import router as auth_router
from routers.user_router import router as user_router
from routers.news_router import router as news_router
from routers.tickers_router import router as tickers_router
from routers.quotes_router import router as quotes_router
from routers.prices_router import router as prices_router
from routers.sentiments_router import router as sentiments_router
from routers.search_router import router as search_router


load_dotenv()
connect_db()

PORT = int(os.getenv("PORT") or 8000)


app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_ORIGIN"), "http://localhost:3500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_origin_regex=".*",
)

# Routers
app.include_router(router=auth_router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(router=user_router, prefix="/api/v1/user", tags=["User"])
app.include_router(router=news_router, prefix="/api/v1/news", tags=["News"])
app.include_router(router=tickers_router, prefix="/api/v1/tickers", tags=["Tickers"])
app.include_router(router=quotes_router, prefix="/api/v1/quotes", tags=["Quotes"])
app.include_router(router=prices_router, prefix="/api/v1/prices", tags=["Prices"])
app.include_router(
    router=sentiments_router, prefix="/api/v1/sentiments", tags=["Sentiments"]
)
app.include_router(router=search_router, prefix="/api/v1/search", tags=["Search"])

if __name__ == "__main__":
    uvicorn.run(app="server:app", host="0.0.0.0", port=PORT, reload=False)
