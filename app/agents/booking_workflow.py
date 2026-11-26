
from app.schemas.booking_schema import BookingRequest


# =========================================================
# 1. BOOKING CONVERSATION STATE
# =========================================================

booking_states = {}


# =========================================================
# 2. INITIALIZE BOOKING
# =========================================================

def initialize_booking(
    conversation_id: str,
    service_type: str,
    service_name: str
):

    if service_type not in ["hotel", "flight", "train"]:
        return "Unsupported booking service."

    booking_states[conversation_id] = {
        "service_type": service_type,
        "service_name": service_name,
        "customer_name": None,
        "customer_email": None,
        "booking_status": "collecting_details",
        "booking_request": None
    }

    return (
        f"You selected: {service_name}\n\n"
        "Let's proceed with your booking request.\n"
        "Please provide your full name."
    )


# =========================================================
# 2A. INITIALIZE BOOKING FROM SEARCH RESULT
# =========================================================

def initialize_booking_from_search(
    conversation_id: str,
    selection_result: dict
):

    if selection_result.get("status") != "selected":
        return "Please select a valid travel option first."

    service_type = selection_result["search_category"]
    selected_option = selection_result["selected_option"]

    # Generate a readable service name
    if service_type == "hotel":

        service_name = selected_option.get(
            "name",
            "Selected Hotel"
        )

    elif service_type == "flight":

        segments = selected_option.get("flights", [])

        if segments:
            first = segments[0]
            service_name = (
                f"{first.get('airline', 'Unknown Airline')} "
                f"{first.get('flight_number', '')}"
            )
        else:
            service_name = "Selected Flight"

    elif service_type == "train":

        service_name = (
            f"{selected_option.get('extended_train_name', 'Selected Train')} "
            f"({selected_option.get('train_number', 'N/A')})"
        )

    else:
        return "Unsupported booking service."

    response = initialize_booking(
        conversation_id=conversation_id,
        service_type=service_type,
        service_name=service_name
    )

    # Preserve the complete original search result
    booking_states[conversation_id]["selected_option"] = (
        selected_option
    )

    booking_states[conversation_id]["selection_number"] = (
        selection_result.get("selection_number")
    )

    return response


# =========================================================
# 3. COLLECT CUSTOMER DETAILS
# =========================================================

def collect_booking_details(
    conversation_id: str,
    user_query: str
):

    booking_state = booking_states.get(conversation_id)

    if booking_state is None:
        return "No active booking request found."

    if booking_state["customer_name"] is None:

        booking_state["customer_name"] = user_query.strip()

        return "Thank you. Please provide your email address."

    if booking_state["customer_email"] is None:

        try:
            booking_request = BookingRequest(
                service_type=booking_state["service_type"],
                service_name=booking_state["service_name"],
                customer_name=booking_state["customer_name"],
                customer_email=user_query.strip()
            )

        except Exception:
            return (
                "That email address doesn't appear to be valid. "
                "Please provide a valid email address."
            )

        booking_state["customer_email"] = str(
            booking_request.customer_email
        )

        booking_state["booking_request"] = booking_request.model_dump()

        booking_state["booking_status"] = "awaiting_confirmation"

        return (
            "Please review your booking request:\n\n"
            f"Service: {booking_request.service_type}\n"
            f"Selected option: {booking_request.service_name}\n"
            f"Name: {booking_request.customer_name}\n"
            f"Email: {booking_request.customer_email}\n\n"
            "Would you like to confirm this booking request?"
        )

    return "Your booking request is awaiting confirmation."


# =========================================================
# 4. BOOKING CONFIRMATION
# =========================================================


import re

def confirm_booking(
    conversation_id: str,
    user_query: str
):

    booking_state = booking_states.get(conversation_id)

    if booking_state is None:
        return "No active booking request found."

    if booking_state["booking_status"] != "awaiting_confirmation":
        return "Your booking request is not awaiting confirmation."

    # Normalize input: remove punctuation and standardize spaces
    response = re.sub(
        r"[^\w\s]",
        "",
        user_query.lower()
    )
    response = " ".join(response.split())

    positive_responses = [
        "yes",
        "confirm",
        "confirmed",
        "proceed",
        "yes confirm",
        "yes please",
        "yes please confirm",
        "confirm booking",
        "go ahead",
        "i agree"
    ]

    negative_responses = [
        "no",
        "cancel",
        "cancel booking",
        "dont proceed",
        "do not proceed",
        "no cancel",
        "no dont proceed"
    ]

    if response in positive_responses:

        booking_state["booking_status"] = "ready_for_booking"

        return (
            "Your booking request has been confirmed successfully.\n\n"
            f"Service: {booking_state['service_type']}\n"
            f"Selected option: {booking_state['service_name']}\n\n"
            "Your request is ready for booking submission. "
            "No reservation or payment has been made yet."
        )

    elif response in negative_responses:

        booking_states.pop(conversation_id, None)

        return (
            "Your booking request has been cancelled. "
            "No reservation or payment was made."
        )

    return (
        "Please reply with Yes to confirm your booking request "
        "or No to cancel it."
    )
