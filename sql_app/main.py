from typing import Optional
from fastapi import FastAPI, Request, Header, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import models
from database import SessionLocal, engine


models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="sql_app/templates")
app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
@app.on_event("startup")
def startup_populate_db():
    db = SessionLocal()
    num_films = db.query(models.Film).count()
    if num_films == 0:
        films = [
        {'name': 'Blade Runner', 'director': 'Ridley Scott'},
        {'name': 'Pulp Fiction', 'director': 'Quentin Tarantino'},
        {'name': 'Mulholland Drive', 'director': 'David Lynch'},
        ]
        for film in films:
            db.add(models.Film(**film))
        db.commit
    else:
        print(f"{num_films} films already in database")

@app.get("/index/", response_class=HTMLResponse)
async def movielist(request: Request, 
                    hx_request: Optional[str] = Header(None),
                    db: Session = Depends(get_db)):
    films = db.query(models.Film).all()
    print(films)
    context = {"request": request, 'films': films}
    if hx_request:
        return templates.TemplateResponse("partials/table.html", context)
    return templates.TemplateResponse("index.html", context)