# 🇳🇬 NAIJA — AI Banking Agent

> An AI-powered banking assistant for Nigeria that helps customers discover banks, find branches and banking services, check real-time appointment availability, and book appointments through natural language.

---

## 🚀 Overview

**NAIJA** is an agentic AI banking assistant built with FastAPI, PostgreSQL, and Groq.

Instead of forcing customers to navigate multiple banking screens, customers can simply describe what they want:

> "I want to book an appointment at the Ikeja branch for Personal Account Opening today at 1 PM."

The AI agent understands the request, identifies the required banking information, checks real appointment availability, validates the requested slot, and books the appointment when the customer confirms an available time.

The system uses real backend tools and database records rather than allowing the AI to invent banking information.

---

## ✨ Features

### 🏦 Banking Discovery

- List available banks
- Search bank branches
- Filter branches by city
- List available banking services

### 📅 Appointment Management

- Check real appointment availability
- Search availability by branch
- Search availability by banking service
- Search availability by date
- Validate appointment slots before booking
- Book appointments
- Generate appointment references
- Retrieve appointment details
- Handle unavailable appointment times

### 🤖 AI Agent

- Natural-language banking conversations
- Groq-powered LLM
- Function/tool calling
- Multi-step agent workflow
- Conversation/session memory
- Real backend tool execution
- No invented banks, branches, services, slots, or references

### 🛡️ Booking Safety

The agent does not automatically select an alternative appointment time.

If the requested time is unavailable, the agent returns the available times and asks the customer to choose.

Before booking, the selected slot is validated against the real availability returned by the backend.

---

# 🏗️ Architecture

```text
                         ┌─────────────────────┐
                         │      Customer       │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │    FastAPI API      │
                         │   /api/v1/agent     │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   Naija AI Agent    │
                         │                     │
                         │  Groq LLM           │
                         │  Tool Calling       │
                         │  Session Memory     │
                         └──────────┬──────────┘
                                    │
                 ┌──────────────────┼──────────────────┐
                 │                  │                  │
                 ▼                  ▼                  ▼
        ┌────────────────┐ ┌────────────────┐ ┌────────────────┐
        │ Banking Tools  │ │ Availability   │ │ Appointment    │
        │                │ │                │ │ Booking        │
        └───────┬────────┘ └───────┬────────┘ └───────┬────────┘
                │                  │                  │
                └──────────────────┼──────────────────┘
                                   ▼
                         ┌─────────────────────┐
                         │    PostgreSQL       │
                         │      Database       │
                         └─────────────────────┘



Customer
   │
   │ "Book an appointment at Ikeja tomorrow at 1 PM"
   ▼
AI Agent
   │
   ├── Find branch
   │
   ├── Find banking service
   │
   ├── Determine appointment date
   │
   ├── Check real availability
   │
   ├── Validate requested time
   │
   └── Collect customer information
            │
            ▼
      Book appointment
            │
            ▼
     PostgreSQL Database
            │
            ▼
     Appointment Reference
            │
            ▼
        Customer




| Technology    | Purpose                        |
| ------------- | ------------------------------ |
| Python        | Core application language      |
| FastAPI       | Backend REST API               |
| Groq          | LLM inference                  |
| PostgreSQL    | Relational database            |
| SQLAlchemy    | Database ORM                   |
| Pydantic      | Request/response validation    |
| Uvicorn       | ASGI server                    |
| Docker        | Database/container environment |
| python-dotenv | Environment configuration      |
| Git/GitHub    | Version control                |


