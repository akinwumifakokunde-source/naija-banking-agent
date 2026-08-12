from fastapi import FastAPI
from sqlalchemy import text

from app.core.database import Base, engine

from app.models import (
    Bank,
    Branch,
    BankingService,
    AppointmentSlot,
    Customer,
    Appointment,
)

from app.api.banks import router as banks_router
from app.api.branches import router as branches_router
from app.api.services import router as services_router
from app.api.appointments import router as appointments_router
from app.api.availability import router as availability_router
from app.api.agent import router as agent_router


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="NAIJA",
    description="AI Banking Agent for Nigeria",
    version="0.1.0",
)


app.include_router(banks_router)
app.include_router(branches_router)
app.include_router(services_router)
app.include_router(availability_router)
app.include_router(appointments_router)
app.include_router(agent_router)


@app.get("/")
def root():
    return {
        "name": "NAIJA",
        "description": "AI Banking Agent for Nigeria",
        "version": "0.1.0",
        "status": "running",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }


@app.get("/health/database")
def database_health():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        value = result.scalar()

    return {
        "database": "connected",
        "test": value,
    }