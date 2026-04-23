"""
agent_tools.py
Agentic RAG tool registry for AskGillu 2.0.

Defines mock tools that demonstrate the agentic pattern:
  - check_fee_status(student_id)
  - book_facility(facility_name, date)
  - raise_grievance(category, description)

These return simulated responses for demo purposes.
The router uses LLM intent classification to decide which tool to call.
"""
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, Optional


# ── Tool implementations ────────────────────────────────────────────────────

def check_fee_status(student_id: str = "UNKNOWN", **kwargs) -> Dict[str, Any]:
    """
    Check fee payment status for a student.
    Args:
        student_id: Student enrollment number (e.g., SRMU2024001)
    Returns:
        Fee status summary with payment history
    """
    # Mock response — replace with real university API call when available
    statuses = ["Paid", "Pending", "Partially Paid"]
    import random
    status_choice = random.choice(statuses)
    return {
        "tool": "check_fee_status",
        "student_id": student_id,
        "status": status_choice,
        "amount_due": 0 if status_choice == "Paid" else 25000,
        "last_payment": "2025-01-15" if status_choice != "Pending" else "None",
        "next_due": "2025-04-01",
        "message": (
            f"Fee status for {student_id}: **{status_choice}**. "
            + ("No dues pending. ✅" if status_choice == "Paid"
               else f"Amount Due: ₹25,000. Please visit the finance office or pay online at srmu.ac.in/fees.")
        ),
    }


def book_facility(
    facility_name: str = "Seminar Hall",
    date: str = "",
    time_slot: str = "10:00 AM - 12:00 PM",
    **kwargs,
) -> Dict[str, Any]:
    """
    Book a university facility (seminar hall, sports complex, computer lab, etc.)
    Args:
        facility_name: Name of facility to book
        date: Date in YYYY-MM-DD format (defaults to tomorrow)
        time_slot: Preferred time slot
    Returns:
        Booking confirmation with reference ID
    """
    if not date:
        date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    booking_id = f"BK{uuid.uuid4().hex[:8].upper()}"
    facilities = {
        "seminar hall": "Seminar Hall A (Capacity: 200)",
        "computer lab": "Computer Lab 3 (50 systems)",
        "sports": "Sports Complex — Main Ground",
        "library": "Library Discussion Room 2",
        "default": f"{facility_name} (Main Campus)",
    }
    facility_key = next(
        (k for k in facilities if k in facility_name.lower()), "default"
    )
    full_name = facilities[facility_key]

    return {
        "tool": "book_facility",
        "booking_id": booking_id,
        "facility": full_name,
        "date": date,
        "time_slot": time_slot,
        "status": "Confirmed",
        "message": (
            f"✅ **Booking Confirmed!**\n\n"
            f"- **Facility**: {full_name}\n"
            f"- **Date**: {date}\n"
            f"- **Time**: {time_slot}\n"
            f"- **Reference ID**: `{booking_id}`\n\n"
            f"Please bring your student ID card at the time of visit. "
            f"For cancellations, contact the facility manager 24 hours in advance."
        ),
    }


def raise_grievance(
    category: str = "General",
    description: str = "",
    **kwargs,
) -> Dict[str, Any]:
    """
    Raise a student grievance or complaint.
    Args:
        category: Type of grievance (Academic/Administrative/Hostel/Fee/General)
        description: Brief description of the issue
    Returns:
        Ticket details with tracking ID
    """
    ticket_id = f"GRV{uuid.uuid4().hex[:6].upper()}"
    expected_resolution = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")

    return {
        "tool": "raise_grievance",
        "ticket_id": ticket_id,
        "category": category,
        "description": description[:200] if description else "Not specified",
        "status": "Submitted",
        "expected_resolution": expected_resolution,
        "message": (
            f"🎫 **Grievance Submitted Successfully!**\n\n"
            f"- **Ticket ID**: `{ticket_id}`\n"
            f"- **Category**: {category}\n"
            f"- **Status**: Under Review\n"
            f"- **Expected Resolution**: {expected_resolution}\n\n"
            f"You will receive an email update within 48 hours. "
            f"Track your grievance at srmu.ac.in/grievance using ticket ID `{ticket_id}`."
        ),
    }


# ── Tool Registry ────────────────────────────────────────────────────────────

TOOL_REGISTRY: Dict[str, Dict] = {
    "check_fee_status": {
        "fn": check_fee_status,
        "description": "Check student fee payment status. Call when user asks about fees, dues, payments, or fee balance.",
        "keywords": ["fee", "dues", "payment", "paid", "balance", "challan", "fees"],
        "args_schema": {"student_id": "string (optional, defaults to UNKNOWN)"},
    },
    "book_facility": {
        "fn": book_facility,
        "description": "Book a university facility. Call when user wants to book a room, hall, lab, or sports facility.",
        "keywords": ["book", "reserve", "seminar hall", "computer lab", "sports", "library room", "facility", "booking"],
        "args_schema": {
            "facility_name": "string (name of facility)",
            "date": "string YYYY-MM-DD (optional)",
            "time_slot": "string (optional)",
        },
    },
    "raise_grievance": {
        "fn": raise_grievance,
        "description": "Raise a student grievance or complaint. Call when user has a complaint, issue, or problem to report.",
        "keywords": ["complaint", "grievance", "issue", "problem", "report", "dispute", "raise", "submit"],
        "args_schema": {
            "category": "string (Academic/Administrative/Hostel/Fee/General)",
            "description": "string (brief description)",
        },
    },
}


def get_intent_prompt(query: str) -> str:
    """
    Build the intent classification prompt for the LLM.
    The LLM must respond with valid JSON only.
    """
    tools_desc = "\n".join(
        f'- "{name}": {info["description"]}'
        for name, info in TOOL_REGISTRY.items()
    )
    return f"""You are an intent classifier for AskGillu, SRMU's AI assistant.

Available tools:
{tools_desc}
- "rag_only": No tool needed — answer from the knowledge base.

Given the user query below, respond with ONLY a JSON object (no explanation):
{{
  "intent": "tool_name_or_rag_only",
  "args": {{
    // key-value pairs extracted from the query, or {{}} if none
  }},
  "confidence": 0.0 to 1.0
}}

User query: "{query}"

JSON response:"""


def classify_intent(query: str, groq_client) -> Dict[str, Any]:
    """
    Use LLM to classify intent and extract tool arguments.
    Returns: { intent, args, confidence }
    Falls back to rag_only on parse errors.
    """
    import json
    prompt = get_intent_prompt(query)
    try:
        response = groq_client.invoke(prompt)
        text = response.content.strip()
        # Extract JSON block if wrapped in markdown fences
        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
            text = text.strip()
        result = json.loads(text)
        if result.get("intent") not in TOOL_REGISTRY and result.get("intent") != "rag_only":
            result["intent"] = "rag_only"
        return result
    except Exception as e:
        print(f"[AGENT] Intent classification failed: {e}. Falling back to rag_only.")
        return {"intent": "rag_only", "args": {}, "confidence": 0.0}


def execute_tool(intent: str, args: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Execute a registered tool. Returns None if tool not found."""
    if intent not in TOOL_REGISTRY:
        return None
    tool_fn = TOOL_REGISTRY[intent]["fn"]
    return tool_fn(**args)
