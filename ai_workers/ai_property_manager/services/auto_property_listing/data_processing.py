import pandas as pd
import numpy as np
import logging
from ai_workers.ai_property_manager.models import PropertyListing, PropertyMedia, TemporaryMedia
from ai_workers.ai_property_manager.services.auto_property_listing.nlg_engine import NLG
from ai_workers.ai_property_manager.services.auto_property_listing.qa_system import QualityAssurance
from fuzzywuzzy import fuzz

# Configure logging for data processing
logging.basicConfig(
    filename="data_processing.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class DataProcessing:
    """Handles cleaning, standardization, feature extraction, and classification of property data"""

    @staticmethod
    def clean_data(df):
        """Cleans and standardizes data"""
        df.dropna(subset=["title", "price", "location"], inplace=True)
        df["price"] = df["price"].astype(float).astype(int)
        df["area"] = df["area"].astype(float)
        df["location"] = df["location"].str.lower().str.strip()
        df["bedrooms"] = df["bedrooms"].fillna(0).astype(int)
        df["bathrooms"] = df["bathrooms"].fillna(0).astype(int)
        return df
    

    @staticmethod
    def analyze_market(df):
        """Performs market analysis and suggests prices based on similar listings"""
        grouped = df.groupby(["location", "bedrooms", "area"])["price"].mean().reset_index()
        grouped.rename(columns={"price": "average_market_price"}, inplace=True)
        
        df = df.merge(grouped, on=["location", "bedrooms", "area"], how="left")
        
        # Identify overpriced or underpriced listings
        df["price_deviation"] = df["price"] - df["average_market_price"]
        df["is_overpriced"] = df["price_deviation"] > (0.1 * df["average_market_price"])
        df["is_underpriced"] = df["price_deviation"] < (-0.1 * df["average_market_price"])
        
        # Suggest optimal price range
        df["suggested_price"] = df["average_market_price"].round(2)
        
        return df


    @staticmethod
    def standardize_data(df):
        """Standardizes property data for consistency"""
        df["title"] = df["title"].str.lower().str.strip()
        df["description"] = df["description"].fillna("").str.lower().str.strip()
        df["price_per_sqm"] = df["price"] / df["area"]  # Feature extraction
        return df

    @staticmethod
    def classify_property(df):
        """Classifies properties into categories"""
        conditions = [
            (df["bedrooms"] >= 3) & (df["area"] > 100),  # Large properties
            (df["bedrooms"] <= 2) & (df["area"] < 80),  # Small properties
        ]
        categories = ["Luxury", "Standard"]
        df["property_category"] = np.select(conditions, categories, default="Basic")
        return df

    @staticmethod
    def estimate_price(df):
        """Fills missing prices using median price per square meter"""
        median_price_per_sqm = df["price_per_sqm"].median()
        df.loc[df["price"].isna(), "price"] = df["area"] * median_price_per_sqm
        return df

    @staticmethod
    def remove_duplicates(df):
        """Removes duplicate property listings"""
        df.drop_duplicates(subset=["title", "price", "location"], keep="first", inplace=True)
        return df

    @staticmethod
    def save_to_database(df):
        """Saves processed data into the Django database"""
        properties = []
        for _, row in df.iterrows():
            properties.append(
                PropertyListing(
                    title=row["title"],
                    description=row.get("description", ""),
                    price=row["price"],
                    location=row["location"],
                    bedrooms=row["bedrooms"],
                    bathrooms=row["bathrooms"],
                    area=row["area"],
                    is_published=row.get("is_published", True),
                    is_suspicious=False,  # Placeholder for AI fraud detection
                    property_category=row["property_category"],  # Save classification
                    average_market_price=row.get("average_market_price"), #  Save analyzed market data
                    price_deviation=row.get("price_deviation"), # Save analyzed market data
                    is_overpriced=row.get("is_overpriced", False), #  Save analyzed market data
                    is_underpriced=row.get("is_underpriced", False), #  Save analyzed market data
                    suggested_price=row.get("suggested_price"), #  Save analyzed market data
                )
            )
        PropertyListing.objects.bulk_create(properties)
        return f"Saved {len(properties)} properties to the database."
    

    @staticmethod
    def process_data(csv_path):
        """Full processing pipeline"""
        try:
            logging.info(f"Starting data processing for file: {csv_path}")

            df = pd.read_csv(csv_path)
            df = DataProcessing.clean_data(df)
            df = DataProcessing.standardize_data(df)
            df = DataProcessing.classify_property(df)
            df = DataProcessing.estimate_price(df)
            df = DataProcessing.analyze_market(df)
            df = DataProcessing.remove_duplicates(df)

            # 🔹 Generate descriptions - USING TEMPLATE METHOD OR LLM
            df["description"] = df.apply(NLG.generate_description_openai, axis=1)
            
            

            # Run Quality Assurance Checks before saving to DB
            df = QualityAssurance.process_quality_assurance(df)

            # ✅ Save to database
            saved_properties = DataProcessing.save_to_database(df)

            # 🔄 Auto-Match Media for Each Property
            for property_instance in saved_properties:
                DataProcessing.match_temporary_media(property_instance)

            logging.info("✅ CSV processing and media matching completed.")

            return saved_properties
        except Exception as e:
            return f"Error in data processing: {str(e)}"

    # @staticmethod -   Working but approach not smart Commented out to avoid conflicts with the updated method
    # def match_temporary_media(property_instance):
    #     """
    #     Matches temporary media to properties based on extracted property names.
    #     """
    #     try:
    #         unmatched_media = TemporaryMedia.objects.filter(matched_property__isnull=True)

    #         for temp_media in unmatched_media:

    #             print(f"🔍 Matching media: {temp_media.extracted_property_name}")

    #             extracted_name = temp_media.extracted_property_name.strip().lower()  # Normalize input

    #             potential_matches = PropertyListing.objects.filter(title__icontains=extracted_name)
    #             print(f"🔍 Found {potential_matches.count()} matches")


    #             if potential_matches.exists():
    #                 matched_property = potential_matches.first()  # Pick the first match
    #                 temp_media.matched_property = matched_property
    #                 temp_media.save()

    #                 # Move the media to PropertyMedia
    #                 PropertyMedia.objects.create(property=matched_property, file=temp_media.file)

    #                 print(f"✅ Matched {getattr(temp_media.file, 'name', 'Unknown File')} to {getattr(matched_property, 'title', 'Unknown Property')}")


    #         return f"✅ {unmatched_media.count()} media files processed."

    #     except Exception as e:
    #         print(f"❌ Error matching media: {str(e)}")



    @staticmethod
    def match_temporary_media(property_instance):
        """
        Matches temporary media to properties using fuzzy matching for better accuracy.
        """
        try:
            unmatched_media = TemporaryMedia.objects.filter(matched_property__isnull=True)

            for temp_media in unmatched_media:
                extracted_name = temp_media.extracted_property_name.strip().lower()  # Normalize input

                print(f"🔍 Matching media: {extracted_name}")

                best_match = None
                best_score = 0  # Store highest similarity score
                
                # Fetch all properties to compare
                potential_matches = PropertyListing.objects.all()

                for property_listing in potential_matches:
                    property_title = property_listing.title.strip().lower()
                    similarity_score = fuzz.ratio(extracted_name, property_title)  # Compute similarity

                    print(f"🔍 Comparing '{extracted_name}' with '{property_title}' - Score: {similarity_score}")

                    # Check if similarity score is high enough (adjust threshold if needed)
                    if similarity_score > best_score and similarity_score >= 80:  # Threshold set at 80%
                        best_match = property_listing
                        best_score = similarity_score

                if best_match:
                    temp_media.matched_property = best_match
                    temp_media.save()

                    # Move the media to PropertyMedia
                    PropertyMedia.objects.create(property=best_match, file=temp_media.file)

                    print(f"✅ Matched {getattr(temp_media.file, 'name', 'Unknown File')} to {best_match.title} with confidence {best_score}%")

            return f"✅ {unmatched_media.count()} media files processed."

        except Exception as e:
            print(f"❌ Error matching media: {str(e)}")
