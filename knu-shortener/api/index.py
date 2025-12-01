from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
import random, string, time
from pydantic import BaseModel

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# In-memory DB (Vercel is stateless — fine for starter)
DB = {}

def short_code():
    return "".join(random.choices(string.ascii_letters + string.digits, k=6))

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.get_template("index.html").render({"request": request})

class URL(BaseModel):
    url: str

@app.post("/create")
async def create(url: URL):
    code = short_code()
    DB[code] = {"url": url.url, "clicks": 0, "created": int(time.time())}
    return {"short": f"https://s.knu.day/{code}"}

@app.get("/{code}")
async def redirect(code: str):
    if code not in DB:
        raise HTTPException(404)
    DB[code]["clicks"] += 1
    return RedirectResponse(DB[code]["url"], status_code=301)

@app.get("/stats/{code}", response_class=HTMLResponse)
async def stats(request: Request, code: str):
    if code not in DB:
        raise HTTPException(404)
    data = DB[code]
    return templates.get_template("stats.html").render({
        "request": request,
        "code": code,
        "url": data["url"],
        "clicks": data["clicks"],
        "short": f"https://s.knu.day/{code}"
    })