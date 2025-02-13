import logging
import random
import openai
from django.conf import settings

logger = logging.getLogger(__name__)

class NLG:
    """Generates property descriptions using predefined templates."""

    templates = [
        "{bedrooms}-bedroom {property_type} available in {location}! This spacious {area} sqft home is listed at just ${price}. Don't miss out on this opportunity!",
        "Looking for a {property_type} in {location}? This {bedrooms}-bedroom gem offers {area} sqft of space at a great price of ${price}. Schedule a visit today!",
        "A stunning {bedrooms}-bedroom {property_type} in {location} with {area} sqft of space, available for just ${price}. A must-see property!",
    ]

    @staticmethod
    def generate_description(row):
        """Creates a description using property data."""
        property_type = row.get("property_type", "home")
        description = random.choice(NLG.templates).format(
            bedrooms=row["bedrooms"],
            property_type=property_type,
            location=row["location"].title(),
            area=int(row["area"]),
            price=int(row["price"])
        )
        logger.error(f"generating property description: {str(description)}")
        return description


    
    @staticmethod
    def generate_description_openai(row):
        """Uses OpenAI GPT to generate property descriptions."""
        openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)  # ✅ New API format

        prompt = f"""
        Generate a compelling real estate listing description for a property with the following details:
        - Location: {row['location'].title()}
        - Type: {row.get('property_type', 'home')}
        - Price: ${int(row['price'])}
        - Bedrooms: {row['bedrooms']}
        - Bathrooms: {row['bathrooms']}
        - Area: {int(row['area'])} sqft
        - Market Status: {'Overpriced' if row.get('is_overpriced', False) else 'Underpriced' if row.get('is_underpriced', False) else 'Fairly Priced'}

        The description should be engaging, highlight unique selling points, and be appealing to buyers.
        """

        try:
            response = openai_client.chat.completions.create(  # ✅ New API format
                model="gpt-4",
                messages=[{"role": "system", "content": "You are a professional real estate listing assistant."},
                          {"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=200
            )
            return response.choices[0].message.content.strip()

        except Exception as e:
            return f"AI Description Error: {str(e)}"