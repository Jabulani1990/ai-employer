# ai_property_manager/services/qa_system.py
import logging

logger = logging.getLogger(__name__)

def validate_property_listing(listing_data):
    """
    Ensures the listing meets compliance and accuracy standards.
    :param listing_data: dict (finalized listing data)
    :return: bool (is valid or not)
    """
    try:
        if listing_data["price"] <= 0:
            return False
        if listing_data["bedrooms"] <= 0 or listing_data["bathrooms"] <= 0:
            return False
        return True

    except Exception as e:
        logger.error(f"Error validating property listing: {str(e)}")
        return False
