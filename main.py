from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from router import websocket, history

app = FastAPI(
    title="Translation Microservice API",
    description="An API that handles file translation using Google Gemini and stores translation history.",
    version="1.0.0"
)

# Include the routers
app.include_router(websocket.router)
app.include_router(history.router)

# Mount static files for frontend
app.mount("/static", StaticFiles(directory="static"), name="static")

# Frontend HTML rendering for root endpoint
@app.get("/", response_class=HTMLResponse, summary="Get the frontend form")
async def get_form():
    """
    Renders the HTML form for file upload and translation initiation.
    """
    with open("templates/index.html", "r") as file:
        return file.read()

# CORS middleware
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
