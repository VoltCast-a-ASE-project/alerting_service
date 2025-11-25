from fastapi import FastAPI

from database import engine, Base
from routers import alert_rules, ingestion

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="VoltCast Notification & Alerting Service",
    description="A microservice for managing alert rules and triggering notifications.",
    version="1.0.0",
)

app.include_router(alert_rules.router)
app.include_router(ingestion.router)


@app.get("/")
def read_root():
    return {"message": "Welcome to the VoltCast Notification & Alerting Service"}
