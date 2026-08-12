import json
import os
from datetime import datetime

from dotenv import load_dotenv
from groq import Groq

from app.agent.service import (
    get_banks,
    get_branches,
    get_services,
    get_available_slots,
    book_appointment,
)


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv(override=True)

MODEL = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-120b",
)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise RuntimeError(
        "GROQ_API_KEY is not configured."
    )

client = Groq(
    api_key=GROQ_API_KEY
)


# ============================================================
# SESSION MEMORY
# ============================================================

# Stores conversation history by session.
CONVERSATIONS: dict[str, list[dict]] = {}

# Stores real availability returned by the database/API.
SESSION_STATE: dict[str, dict] = {}


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are Naija Banking Agent, an AI banking assistant
for customers in Nigeria.

You help customers:

- find banks
- find bank branches
- find banking services
- check appointment availability
- book banking appointments

IMPORTANT RULES:

1. Never invent banks, branches, services, dates,
   appointment slots, slot IDs, or appointment references.

2. Always use tools when real banking information is required.

3. Remember information already provided in the current
   conversation.

4. If the customer already provided a branch, service,
   date, name, phone number, or requested time, do not
   ask for it again unless it is genuinely missing.

5. For appointment requests identify:

   - branch
   - banking service
   - date
   - requested time

6. ALWAYS check real availability before booking.

7. Never assume a requested time is available.

8. If the requested time is unavailable:

   - do not book another time automatically
   - show the actual available times
   - ask the customer which time they prefer

9. If the customer selects an available time from a
   previous availability response, book that exact slot.

10. Never invent or guess a slot_id.

11. Never book a slot that has not been confirmed as
    available by the availability tool.

12. Never book without:

    - full name
    - phone number
    - valid available slot

13. Email is optional.

14. If the customer says "today", use today's date.

15. If the customer says "tomorrow", use tomorrow's date.

16. Do not silently change the customer's requested date.

17. If a requested time is unavailable, never choose
    another time without explicit customer approval.

18. When booking succeeds, clearly provide the exact
    appointment reference returned by the booking system.

19. Only say an appointment is confirmed when the booking
    operation actually succeeds.

20. If booking fails, do not claim that it was booked.

21. Do not expose internal tool names, API URLs,
    database details, or implementation details.

22. Be concise, friendly, and helpful.
"""


# ============================================================
# TOOL FUNCTIONS
# ============================================================

TOOL_FUNCTIONS = {
    "get_banks": get_banks,
    "get_branches": get_branches,
    "get_services": get_services,
    "get_available_slots": get_available_slots,
    "book_appointment": book_appointment,
}


# ============================================================
# TOOL SCHEMAS
# ============================================================

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_banks",
            "description": (
                "Get the available banks in the banking system."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_branches",
            "description": (
                "Get bank branches. Optionally filter "
                "branches by city."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": (
                            "City to search for, "
                            "for example Ikeja."
                        ),
                    }
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_services",
            "description": (
                "Get the available banking services."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_available_slots",
            "description": (
                "Check real appointment availability "
                "for a branch, banking service and date. "
                "This must be used before booking."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "branch_id": {
                        "type": "integer",
                        "description": (
                            "The bank branch ID."
                        ),
                    },
                    "service_id": {
                        "type": "integer",
                        "description": (
                            "The banking service ID."
                        ),
                    },
                    "date": {
                        "type": "string",
                        "description": (
                            "Appointment date in "
                            "YYYY-MM-DD format."
                        ),
                    },
                },
                "required": [
                    "branch_id",
                    "service_id",
                ],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "book_appointment",
            "description": (
                "Book an exact appointment slot that "
                "has already been confirmed as available."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "slot_id": {
                        "type": "integer",
                        "description": (
                            "Exact available appointment "
                            "slot ID."
                        ),
                    },
                    "full_name": {
                        "type": "string",
                        "description": (
                            "Customer's full name."
                        ),
                    },
                    "phone": {
                        "type": "string",
                        "description": (
                            "Customer's phone number."
                        ),
                    },
                    "email": {
                        "type": "string",
                        "description": (
                            "Customer's email address. "
                            "Optional."
                        ),
                    },
                },
                "required": [
                    "slot_id",
                    "full_name",
                    "phone",
                ],
            },
        },
    },
]


# ============================================================
# TOOL EXECUTION
# ============================================================

def execute_tool_call(tool_call):
    function_name = tool_call.function.name

    arguments = json.loads(
        tool_call.function.arguments or "{}"
    )

    function = TOOL_FUNCTIONS.get(function_name)

    if function is None:
        raise ValueError(
            f"Unknown tool requested: {function_name}"
        )

    return function(**arguments)


# ============================================================
# DATE/TIME HELPERS
# ============================================================

def format_slot_time(slot: dict) -> str:
    start_time = slot.get("start_time")
    end_time = slot.get("end_time")

    if not start_time:
        return "Unknown time"

    try:
        start = datetime.fromisoformat(
            str(start_time).replace(
                "Z",
                "+00:00",
            )
        )

        result = start.strftime("%I:%M %p")

        if end_time:
            end = datetime.fromisoformat(
                str(end_time).replace(
                    "Z",
                    "+00:00",
                )
            )

            result += (
                f" - {end.strftime('%I:%M %p')}"
            )

        return result

    except (ValueError, TypeError):
        return str(start_time)


def format_slot_date(slot: dict) -> str:
    start_time = slot.get("start_time")

    if not start_time:
        return ""

    try:
        start = datetime.fromisoformat(
            str(start_time).replace(
                "Z",
                "+00:00",
            )
        )

        return start.strftime("%d %B %Y")

    except (ValueError, TypeError):
        return ""


# ============================================================
# AVAILABILITY RESPONSE
# ============================================================

def format_available_slots(
    slots: list[dict],
) -> str:

    available = [
        slot
        for slot in slots
        if not slot.get(
            "is_booked",
            False,
        )
    ]

    if not available:
        return (
            "There are currently no available "
            "appointment slots for that date."
        )

    date_text = format_slot_date(
        available[0]
    )

    if date_text:
        message = (
            f"Available appointment times "
            f"for {date_text}:\n\n"
        )
    else:
        message = (
            "Available appointment times:\n\n"
        )

    for slot in available:
        message += (
            f"- {format_slot_time(slot)}\n"
        )

    message += (
        "\nWhich time would you like me to book?"
    )

    return message


# ============================================================
# BOOKING RESPONSE
# ============================================================

def format_booking_confirmation(
    appointment: dict,
) -> str:

    reference = appointment.get(
        "reference"
    )

    message = (
        "Your appointment has been confirmed."
    )

    start_time = appointment.get(
        "start_time"
    )

    end_time = appointment.get(
        "end_time"
    )

    if start_time:

        try:
            start = datetime.fromisoformat(
                str(start_time).replace(
                    "Z",
                    "+00:00",
                )
            )

            message += (
                f"\n\nDate: "
                f"{start.strftime('%d %B %Y')}"
            )

            message += (
                f"\nTime: "
                f"{start.strftime('%I:%M %p')}"
            )

            if end_time:
                end = datetime.fromisoformat(
                    str(end_time).replace(
                        "Z",
                        "+00:00",
                    )
                )

                message += (
                    f" - "
                    f"{end.strftime('%I:%M %p')}"
                )

        except (ValueError, TypeError):
            pass

    if reference:
        message += (
            f"\nAppointment reference: "
            f"{reference}"
        )

    return message


# ============================================================
# MAIN AGENT
# ============================================================

def run_agent(
    user_message: str,
    session_id: str = "default",
) -> str:

    # --------------------------------------------------------
    # Create conversation
    # --------------------------------------------------------

    if session_id not in CONVERSATIONS:
        CONVERSATIONS[session_id] = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            }
        ]

    messages = CONVERSATIONS[
        session_id
    ]

    # --------------------------------------------------------
    # Create session state
    # --------------------------------------------------------

    if session_id not in SESSION_STATE:
        SESSION_STATE[session_id] = {
            "available_slots": [],
            "branch_id": None,
            "service_id": None,
            "date": None,
        }

    state = SESSION_STATE[
        session_id
    ]

    # --------------------------------------------------------
    # IMPORTANT:
    # Keep booking result across all tool iterations.
    # --------------------------------------------------------

    booking_result = None

    # --------------------------------------------------------
    # Add user message
    # --------------------------------------------------------

    messages.append(
        {
            "role": "user",
            "content": user_message,
        }
    )

    # --------------------------------------------------------
    # Agent loop
    # --------------------------------------------------------

    for _ in range(8):

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            temperature=0.2,
            max_completion_tokens=512,
        )

        assistant_message = (
            response.choices[0].message
        )

        messages.append(
            assistant_message
        )

        # ====================================================
        # FINAL RESPONSE
        # ====================================================

        if not assistant_message.tool_calls:

            # ------------------------------------------------
            # FIRST PRIORITY:
            # A booking was successfully completed.
            # ------------------------------------------------

            if booking_result is not None:

                if isinstance(
                    booking_result,
                    dict,
                ):

                    appointment = (
                        booking_result.get(
                            "appointment"
                        )
                    )

                    if isinstance(
                        appointment,
                        dict,
                    ):

                        return format_booking_confirmation(
                            appointment
                        )

                return (
                    "Your appointment was processed, "
                    "but I could not retrieve the "
                    "confirmation details."
                )

            # ------------------------------------------------
            # SECOND PRIORITY:
            # Availability was checked.
            # ------------------------------------------------

            if state["available_slots"]:

                return format_available_slots(
                    state["available_slots"]
                )

            # ------------------------------------------------
            # NORMAL AI RESPONSE
            # ------------------------------------------------

            return (
                assistant_message.content or ""
            ).strip()

        # ====================================================
        # TOOL CALLS
        # ====================================================

        for tool_call in assistant_message.tool_calls:

            function_name = (
                tool_call.function.name
            )

            try:

                arguments = json.loads(
                    tool_call.function.arguments
                    or "{}"
                )

                # ============================================
                # GET BANKS
                # ============================================

                if function_name == "get_banks":

                    result = get_banks()

                # ============================================
                # GET BRANCHES
                # ============================================

                elif function_name == "get_branches":

                    result = get_branches(
                        city=arguments.get(
                            "city"
                        )
                    )

                # ============================================
                # GET SERVICES
                # ============================================

                elif function_name == "get_services":

                    result = get_services()

                # ============================================
                # GET AVAILABILITY
                # ============================================

                elif (
                    function_name
                    == "get_available_slots"
                ):

                    branch_id = arguments[
                        "branch_id"
                    ]

                    service_id = arguments[
                        "service_id"
                    ]

                    date = arguments.get(
                        "date"
                    )

                    result = get_available_slots(
                        branch_id=branch_id,
                        service_id=service_id,
                        date=date,
                    )

                    # ----------------------------------------
                    # Store ONLY real available slots.
                    # ----------------------------------------

                    available_slots = [
                        slot
                        for slot in result
                        if not slot.get(
                            "is_booked",
                            False,
                        )
                    ]

                    state[
                        "available_slots"
                    ] = available_slots

                    state[
                        "branch_id"
                    ] = branch_id

                    state[
                        "service_id"
                    ] = service_id

                    state[
                        "date"
                    ] = date

                # ============================================
                # BOOK APPOINTMENT
                # ============================================

                elif (
                    function_name
                    == "book_appointment"
                ):

                    requested_slot_id = (
                        arguments.get(
                            "slot_id"
                        )
                    )

                    # ----------------------------------------
                    # Check against REAL slots stored
                    # in session state.
                    # ----------------------------------------

                    valid_slot = None

                    for slot in state[
                        "available_slots"
                    ]:

                        if (
                            slot.get("id")
                            == requested_slot_id
                        ):
                            valid_slot = slot
                            break

                    # ----------------------------------------
                    # Invalid slot
                    # ----------------------------------------

                    if valid_slot is None:

                        result = {
                            "error": (
                                "The selected appointment "
                                "slot is not currently "
                                "available. Please select "
                                "one of the available "
                                "appointment times."
                            )
                        }

                    # ----------------------------------------
                    # Valid slot
                    # ----------------------------------------

                    else:

                        result = book_appointment(
                            slot_id=(
                                requested_slot_id
                            ),
                            full_name=arguments[
                                "full_name"
                            ],
                            phone=arguments[
                                "phone"
                            ],
                            email=arguments.get(
                                "email"
                            ),
                        )

                        # ------------------------------------
                        # IMPORTANT:
                        # Store the booking result BEFORE
                        # removing the slot from state.
                        # ------------------------------------

                        if isinstance(
                            result,
                            dict,
                        ):

                            appointment = (
                                result.get(
                                    "appointment"
                                )
                            )

                            if isinstance(
                                appointment,
                                dict,
                            ):

                                status = (
                                    appointment.get(
                                        "status"
                                    )
                                )

                                # Only treat a real
                                # confirmed appointment
                                # as a successful booking.
                                if status == "CONFIRMED":

                                    booking_result = result

                                    # --------------------------------
                                    # Remove booked slot from
                                    # available session state.
                                    # --------------------------------

                                    state[
                                        "available_slots"
                                    ] = [
                                        slot
                                        for slot in state[
                                            "available_slots"
                                        ]
                                        if slot.get(
                                            "id"
                                        )
                                        != requested_slot_id
                                    ]

                # ============================================
                # UNKNOWN TOOL
                # ============================================

                else:

                    result = execute_tool_call(
                        tool_call
                    )

                # ============================================
                # SEND RESULT TO MODEL
                # ============================================

                tool_content = json.dumps(
                    result,
                    default=str,
                )

            except Exception as exc:

                tool_content = json.dumps(
                    {
                        "error": str(exc)
                    }
                )

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": tool_content,
                }
            )

    # ========================================================
    # TOO MANY ITERATIONS
    # ========================================================

    raise RuntimeError(
        "The banking agent exceeded the maximum "
        "number of tool iterations."
    )


# ============================================================
# LOCAL TEST
# ============================================================

if __name__ == "__main__":

    response = run_agent(
        "What banks are available?",
        session_id="local-test",
    )

    print("\nAI:")
    print(response)