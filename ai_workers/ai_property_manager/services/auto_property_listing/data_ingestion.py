import json
import pandas as pd
from ai_workers.ai_property_manager.models import PropertyListing

class DataIngestion:
    """Handles property data ingestion from multiple sources"""
    
    @staticmethod
    def ingest_from_json(json_data):
        """Ingest property listings from a JSON payload"""
        try:
            properties = json.loads(json_data)
            listings = []
            for prop in properties:
                listings.append(PropertyListing(
                    title=prop["title"],
                    description=prop["description"],
                    price=prop["price"],
                    location=prop["location"],
                    bedrooms=prop.get("bedrooms", 0),  # Default 0 for land
                    bathrooms=prop.get("bathrooms", 0),  # Default 0 for land
                    area=prop.get("area", 0.0),
                    is_published=prop.get("is_published", False),
                ))
            PropertyListing.objects.bulk_create(listings)
            return f"{len(listings)} properties ingested successfully!"
        except Exception as e:
            return f"Error ingesting JSON data: {str(e)}"

    @staticmethod
    def ingest_from_csv(csv_path):
        """Ingest property listings from a CSV file"""
        try:
            df = pd.read_csv(csv_path)
            listings = []
            for _, row in df.iterrows():
                listings.append(PropertyListing(
                    title=row["title"],
                    description=row["description"],
                    price=row["price"],
                    location=row["location"],
                    bedrooms=row.get("bedrooms", 0),
                    bathrooms=row.get("bathrooms", 0),
                    area=row.get("area", 0.0),
                    is_published=row.get("is_published", False),
                    is_suspicious=False,  # Placeholder for fraud detection
                    property_category=row.get("property_category", "Basic"),  # Save classification
                ))
            PropertyListing.objects.bulk_create(listings)
            return f"{len(listings)} properties ingested from CSV!"
        except Exception as e:
            return f"Error ingesting CSV data: {str(e)}"
