"""
Main Module
-----------
The entry point for the Contacts REST API. This module initializes the FastAPI 
application, configures middlewares, sets up rate limiting, and includes 
all API routers.
"""

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import  _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from contextlib import asynccontextmanager
from routes import auth, contacts, users
from database.db import engine
from database.models import Base
from services.limiter import limiter

# Base.metadata.create_all(bind=engine)

app = FastAPI(title="Contacts REST API")
app.state.limiter = limiter

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages the application lifespan.
    Initializes the database tables on startup.
    """
    Base.metadata.create_all(bind=engine)
    yield
   

app = FastAPI(lifespan=lifespan)

app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix='/api')
app.include_router(contacts.router, prefix='/api')
app.include_router(users.router, prefix='/api')

@app.get("/")
def read_root():
    """
    Root endpoint that returns a welcome message.
    
    :return: Dictionary with a welcome message.
    """
    return {"message": "Welcome to Contacts API. Go to /docs for Swagger UI"}

@app.get("/api/healthchecker")
@limiter.limit("5/minute")
async def healthchecker(request: Request):
    """
    Health check endpoint to verify the API status.
    Limited to 5 requests per minute.
    
    :param request: The incoming HTTP request.
    :return: Status OK message.
    """
    return {"status": "OK", "message": "Welcome to FastAPI!"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)