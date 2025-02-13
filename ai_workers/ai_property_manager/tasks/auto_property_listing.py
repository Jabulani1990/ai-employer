# ai_property_manager/tasks.py
import logging
from celery import shared_task

from ai_workers.ai_property_manager.models import PropertyListing
from ai_workers.ai_property_manager.services.auto_property_listing.data_ingestion import ingest_property_data
from ai_workers.ai_property_manager.services.auto_property_listing.data_processing import process_property_data
from ai_workers.ai_property_manager.services.auto_property_listing.nlg_engine import generate_property_description
from ai_workers.ai_property_manager.services.auto_property_listing.qa_system import validate_property_listing

logger = logging.getLogger(__name__)

@shared_task
def auto_generate_property_listing(raw_data):
    """
    Celery task to process and auto-generate a property listing.
    """
    try:
        # Step 1: Ingest data
        clean_data = ingest_property_data(raw_data)
        if not clean_data:
            return {"status": "error", "message": "Invalid data"}

        # Step 2: Process data
        processed_data = process_property_data(clean_data)

        # Step 3: Generate description
        description = generate_property_description(processed_data)
        processed_data["description"] = description

        # Step 4: Validate listing
        if not validate_property_listing(processed_data):
            return {"status": "error", "message": "Listing failed QA check"}

        # Step 5: Save to database
        PropertyListing.objects.create(**processed_data)
        logger.info("✅ Property listing generated successfully!")

        return {"status": "success"}

    except Exception as e:
        logger.error(f"Error auto-generating listing: {str(e)}")
        return {"status": "error", "message": str(e)}
