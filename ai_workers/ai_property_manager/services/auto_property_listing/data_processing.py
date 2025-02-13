import pandas as pd
import numpy as np
import logging
from ai_workers.ai_property_manager.models import PropertyListing
from ai_workers.ai_property_manager.services.auto_property_listing.nlg_engine import NLG
from ai_workers.ai_property_manager.services.auto_property_listing.qa_system import QualityAssurance

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
            
            return DataProcessing.save_to_database(df)
        except Exception as e:
            return f"Error in data processing: {str(e)}"
