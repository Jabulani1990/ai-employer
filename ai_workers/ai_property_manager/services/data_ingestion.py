# ai_property_manager/services/data_ingestion.py
import logging

logger = logging.getLogger(__name__)

def ingest_property_data(raw_data):
    """
    Handles raw property data ingestion.
    :param raw_data: dict containing property details.
    :return: dict (cleaned data)
    """
    try:
        # Basic validation
        required_fields = ["title", "price", "location", "bedrooms", "bathrooms", "area"]
        for field in required_fields:
            if field not in raw_data:
                raise ValueError(f"Missing required field: {field}")

        # Return cleaned data
        return {
            "title": raw_data["title"],
            "price": float(raw_data["price"]),
            "location": raw_data["location"],
            "bedrooms": int(raw_data["bedrooms"]),
            "bathrooms": int(raw_data["bathrooms"]),
            "area": float(raw_data["area"]),
        }

    except Exception as e:
        logger.error(f"Error ingesting property data: {str(e)}")
        return None
