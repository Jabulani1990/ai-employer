import pandas as pd
import logging

# Configure logging
logging.basicConfig(
    filename="qa_system.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

class QualityAssurance:
    """Performs quality checks on property listings before they are published."""

    @staticmethod
    def detect_missing_data(df):
        """Flags properties with missing critical fields."""
        required_fields = ["title", "description", "price", "location", "bedrooms", "bathrooms", "area"]
        df["has_missing_data"] = df[required_fields].isnull().any(axis=1)

        missing_count = df["has_missing_data"].sum()
        if missing_count > 0:
            logging.warning(f"Detected {missing_count} listings with missing data.")

        return df

    @staticmethod
    def validate_price_accuracy(df):
        """Detects unrealistic pricing based on market averages."""
        df["is_price_unrealistic"] = (df["price"] <= 0) | (df["price"] > 10 * df["average_market_price"])
        unrealistic_count = df["is_price_unrealistic"].sum()

        if unrealistic_count > 0:
            logging.warning(f"Detected {unrealistic_count} listings with unrealistic pricing.")

        return df

    @staticmethod
    def check_compliance(df):
        """Ensures property listings follow real estate compliance rules."""
        forbidden_terms = ["discriminatory", "illegal", "restricted"]
        df["is_non_compliant"] = df["description"].str.contains('|'.join(forbidden_terms), case=False, na=False)
        non_compliant_count = df["is_non_compliant"].sum()

        if non_compliant_count > 0:
            logging.warning(f"Found {non_compliant_count} non-compliant property listings.")

        return df

    @staticmethod
    def ensure_consistent_descriptions(df):
        """Verifies AI-generated descriptions follow brand voice guidelines."""
        df["is_description_short"] = df["description"].str.len() < 50
        short_description_count = df["is_description_short"].sum()

        if short_description_count > 0:
            logging.info(f"Detected {short_description_count} listings with short descriptions.")

        return df

    @staticmethod
    def process_quality_assurance(df):
        """Runs all QA checks on the dataset."""
        logging.info("Starting quality assurance checks on property listings...")
        
        df = QualityAssurance.detect_missing_data(df)
        df = QualityAssurance.validate_price_accuracy(df)
        df = QualityAssurance.check_compliance(df)
        df = QualityAssurance.ensure_consistent_descriptions(df)

        logging.info("Quality assurance checks completed.")

        return df
