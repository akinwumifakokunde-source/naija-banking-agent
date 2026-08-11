# Naija Banking Agent

AI-powered banking assistant infrastructure designed for Nigerian banking workflows.

This project provides a backend API for discovering banks, branches, banking services, appointment availability, and managing customer appointments.

The long-term goal is to build an AI banking agent that can understand customer requests and securely interact with banking services through structured APIs.

## Current Features

- Bank directory
- Bank branch directory
- Banking service directory
- Branch and service availability
- Appointment slot management
- Customer creation and lookup
- Appointment booking
- Appointment lookup by reference
- Appointment cancellation
- PostgreSQL database
- Docker-based database setup
- FastAPI interactive API documentation
- Concurrent-safe appointment booking using database row locking

## Architecture

```text
Customer
   |
   v
AI Banking Agent
   |
   v
FastAPI API
   |
   +-------------------+
   |                   |
   v                   v
Banking Services    Appointment System
   |                   |
   v                   v
PostgreSQL <-----------+
