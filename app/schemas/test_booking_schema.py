from app.schemas.booking_schema import BookingRequest


# Test 1: Valid booking details
try:
    booking = BookingRequest(
        service_type="hotel",
        service_name="Hotel Taj",
        customer_name="Ravi",
        customer_email="ravi@gmail.com"
    )

    print("Test 1: Valid booking")
    print(booking)
    print()

except Exception as e:
    print(e)


# Test 2: Invalid service type
try:
    booking = BookingRequest(
        service_type="flight",
        service_name="Flight to Delhi",
        customer_name="Ravi",
        customer_email="ravi@gmail.com"
    )

except Exception as e:
    print("Test 2: Invalid service type")
    print(e)
    print()


# Test 3: Invalid email
try:
    booking = BookingRequest(
        service_type="hotel",
        service_name="Hotel Taj",
        customer_name="Ravi",
        customer_email="ravi123"
    )

except Exception as e:
    print("Test 3: Invalid email")
    print(e)