from app.services.stayapi_service import lookup_destination


def main():

    print("Searching StayAPI for Varanasi...")

    try:
        results = lookup_destination("Varanasi")

        print("\n========== DESTINATION RESULTS ==========")
        print(results)

    except Exception as e:
        print("\nStayAPI Error:", e)


if __name__ == "__main__":
    main()