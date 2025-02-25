import logging
import random
import openai
from django.conf import settings
import google.generativeai as genai

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
        


    @staticmethod
    def generate_description_gemini(row):
        """Uses Gemini Pro to generate property descriptions."""

        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)  # Configure the API key globally

            model = genai.GenerativeModel('gemini-pro') # Or 'gemini-pro-vision' if you need image input

            prompt = f"""
            Generate a compelling real estate listing description for a property with the following details:
            - Location: {row['location'].title()}
            - Type: {row.get('property_type', 'home')}
            - Price: ${int(row['price'])}
            - Bedrooms: {row['bedrooms']}
            - Bathrooms: {row['bathrooms']}
            - Area: {int(row['area'])} sqft
            - Market Status: {'Overpriced' if row.get('is_overpriced', False) else 'Underpriced' if row.get('is_underpriced', False) else 'Fairly Priced'}

            The description should be engaging, highlight unique selling points, and be appealing to buyers. Keep it to around 200 words.
            """

            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    candidate_count=1,  # Request only one response
                    max_output_tokens=250, #slightly more generous than original's 200.  Gemini can return shorter results too.
                    temperature=0.7,  # Adjust temperature as needed
                ),
            )

            return response.text.strip()  # Extract and strip the text from the response

        except Exception as e:
            return f"AI Description Error: {str(e)}"