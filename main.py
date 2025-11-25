from fastapi import FastAPI


app = FastAPI(
    title="VoltCast Notification & Alerting Service",
    description="A microservice for managing alert rules and triggering notifications.",
    version="1.0.0",
)


@app.get("/")
def read_root():
    return {"message": "Welcome to the VoltCast Notification & Alerting Service"}
