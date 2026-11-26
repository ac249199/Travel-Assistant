
import asyncio

from app.orchestration.orchestrator import orchestrate


async def main():

    conversation_id = "real_hotel_test_001"

    # First message
    print("\n========== FIRST MESSAGE ==========")

    response1 = await orchestrate(
        user_query="Find hotels in Varanasi",
        conversation_id=conversation_id
    )

    print(response1)

    # Second message
    print("\n========== SECOND MESSAGE ==========")

    response2 = await orchestrate(
        user_query="Check-in is 25 November 2026",
        conversation_id=conversation_id
    )

    print(response2)

    # Third message
    print("\n========== THIRD MESSAGE ==========")

    response3 = await orchestrate(
        user_query="Check-out is 28 November 2026 and 2 guests",
        conversation_id=conversation_id
    )

    print("\n========== REAL HOTEL SEARCH RESULTS ==========")

    print(response3)

    # Verify response
    assert response3["status"] == "completed"

    assert response3["response"]["status"] == "completed"

    hotels = response3["response"]["hotels"]

    assert len(hotels) > 0

    print("\n========== HOTEL DETAILS ==========")

    for index, hotel in enumerate(hotels, start=1):

        print(f"\nHotel {index}")
        print("Name:", hotel.get("name"))
        print("Address:", hotel.get("address"))
        print("Price:", hotel.get("display_price"))
        print("Rating:", hotel.get("guest_rating"))
        print("Reviews:", hotel.get("review_count"))
        print("Room:", hotel.get("room_name"))
        print("Free Cancellation:", hotel.get("free_cancellation"))
        print("No Prepayment:", hotel.get("no_prepayment"))
        print("Booking ID:", hotel.get("hotel_id"))

    print("\nReal StayAPI integration test completed!")


if __name__ == "__main__":
    asyncio.run(main())
