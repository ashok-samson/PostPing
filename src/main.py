from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, FileResponse
from sqlalchemy import create_engine, Column, Integer, Text, DateTime, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from sqlalchemy.engine import URL
from datetime import datetime
from dotenv import load_dotenv
import os

try:
    from azure.identity import DefaultAzureCredential
except ImportError:
    DefaultAzureCredential = None

load_dotenv()
app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/favicon.ico")
def favicon():
    return FileResponse("static/favicon.ico")

# Create base and engine variables
Base = declarative_base()
SessionLocal = None
engine = None

class Log(Base):
    __tablename__ = 'logs'
    id = Column(Integer, primary_key=True, index=True)
    log_time = Column(DateTime, default=datetime.utcnow)
    log_text = Column(Text, nullable=False)

def get_engine():
    use_managed_identity = os.getenv("USE_MANAGED_IDENTITY", "false").lower() == "true"
    print(f"[DEBUG] USE_MANAGED_IDENTITY: {use_managed_identity}")

    if use_managed_identity:
        if not DefaultAzureCredential:
            raise ImportError("azure-identity is required for Managed Identity support")
        print("🔐 Using Managed Identity for PostgreSQL connection")
        credential = DefaultAzureCredential()
        token = credential.get_token("https://ossrdbms-aad.database.windows.net/.default")
        host = os.getenv("DB_HOST")
        dbname = os.getenv("DB_NAME")
        user = os.getenv("DB_USER")
        print(f"[DEBUG] DB_HOST: {host}")
        print(f"[DEBUG] DB_NAME: {dbname}")
        print(f"[DEBUG] DB_USER: {user}")
        return create_engine(
            URL.create(
                drivername="postgresql+psycopg2",
                username=user,
                password=token.token,
                host=host,
                port=5432,
                database=dbname
            ),
            echo=True
        )
    else:
        print("🔓 Using traditional username/password for PostgreSQL connection")
        db_url = os.getenv("DATABASE_URL")
        print(f"[DEBUG] DATABASE_URL: {db_url}")
        return create_engine(db_url, echo=True)

@app.on_event("startup")
def startup():
    global SessionLocal, engine
    try:
        engine = get_engine()
        SessionLocal = sessionmaker(bind=engine)
        Base.metadata.create_all(bind=engine)
        print("[DEBUG] SQLAlchemy setup completed")
    except OperationalError as e:
        print(f"[ERROR] Database initialization failed: {e}")
        engine = None
        SessionLocal = None

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    if not SessionLocal:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "connected": False,
            "logs": [],
            "error_message": "Could not connect to database."
        })

    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        connected = True
        logs = db.query(Log).order_by(Log.log_time.desc()).all()
    except Exception as e:
        connected = False
        logs = []
        print(f"[ERROR] During request: {e}")
        return templates.TemplateResponse("index.html", {
            "request": request,
            "connected": False,
            "logs": [],
            "error_message": str(e)
        })

    return templates.TemplateResponse("index.html", {
        "request": request,
        "connected": connected,
        "logs": logs,
        "error_message": ""
    })

@app.post("/submit", response_class=HTMLResponse)
def submit_log(request: Request, log_text: str = Form(...)):
    db = SessionLocal()
    new_log = Log(log_text=log_text)
    db.add(new_log)
    db.commit()
    db.close()
    return read_root(request)

@app.get("/delete/{log_id}", response_class=HTMLResponse)
def delete_log(request: Request, log_id: int):
    db = SessionLocal()
    log = db.query(Log).filter(Log.id == log_id).first()
    if log:
        db.delete(log)
        db.commit()
    db.close()
    return RedirectResponse(url="/", status_code=302)
