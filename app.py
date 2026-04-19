from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import json

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Load admin settings
with open('config/settings.json') as f:
    settings = json.load(f)

@app.get("/")
async def root():
    return {"message": "HomeNet Admin API"}

@app.get("/admin")
async def admin(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request, "settings": settings})

if __name__ == "__main__":
    
uvicorn.run(app, host="0.0.0.0", port=8000)

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from dash_app import app as dash_app

app = FastAPI()
app.mount("/dashboard", dash_app.server)
