
from app.schemas.travel_search_extraction_schema import TravelSearchExtraction


result = TravelSearchExtraction(
    search_category="hotel",
    destination="Varanasi"
)

print(result)
print("\nSchema test passed!")
