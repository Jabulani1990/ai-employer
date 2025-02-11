# ai_property_manager/services/nlg_engine.py
import logging
import random

logger = logging.getLogger(__name__)

# Sample templates
TEMPLATES = [
    "{title} is a stunning {bedrooms}-bedroom, {bathrooms}-bathroom home in {location}. Priced at ₦{price}, this {category} property offers {area} sqm of living space.",
    "Discover the elegance of {title}, a {category} home in {location} with {bedrooms} bedrooms and {bathrooms} bathrooms, available for ₦{price}. Spanning {area} sqm, it's the perfect choice for your dream home.",
]

def generate_property_description(property_data):
    """
    Generates a property listing description using AI templates.
    :param property_data: dict (processed property data)
    :return: str (property description)
    """
    try:
        template = random.choice(TEMPLATES)
        description = template.format(**property_data)
        return description

    except Exception as e:
        logger.error(f"Error generating property description: {str(e)}")
        return None
