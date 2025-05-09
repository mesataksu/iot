from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import sensors, rules
from .timer_service import TimerService
from .rule_service import RuleChecker
from .database import SessionLocal

app = FastAPI(title="IoT Monitoring and Control API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sensors.router, prefix="/api", tags=["sensors"])
app.include_router(rules.router, prefix="/api", tags=["rules"])

timer_service = TimerService()
rule_checker = RuleChecker()

def get_db_session():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

@app.on_event("startup")
def startup_event():
    rule_checker.start(get_db_session)
    print("Rule checker service started")

@app.on_event("shutdown")
def shutdown_event():
    timer_service.stop()
    rule_checker.stop()
    print("All services stopped")

@app.get("/")
def read_root():
    return {"message": "IoT Monitoring and Control API is running"}