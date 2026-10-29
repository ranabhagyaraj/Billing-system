from fastapi import FastAPI
from app.db import engine, Base
from app.routes.routes import router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="SubLedger Backend", version="1.0.0")

app.include_router(router, prefix="/api/v1")

@app.get("/")
def health_check():
    return {"status": "healthy", "system": "SubLedger API"}
