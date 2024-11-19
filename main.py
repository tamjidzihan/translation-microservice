from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from router import websocket
from pathlib import Path


app = FastAPI()


app.include_router(websocket.router)


# Frontend HTML rendering
@app.get("/", response_class=HTMLResponse)
async def get_form():
    with open("templates/index.html", "r") as file:
        return file.read()


# Serve static files (CSS, JS)
@app.get("/static/{file_name}")
async def serve_static(file_name: str):
    return Path(f"static/{file_name}").read_text()


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
