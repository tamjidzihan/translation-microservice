from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from router import websocket,history

app = FastAPI()

app.include_router(websocket.router)
app.include_router(history.router)


# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


# Frontend HTML rendering
@app.get("/", response_class=HTMLResponse)
async def get_form():
    with open("templates/index.html", "r") as file:
        return file.read()


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
