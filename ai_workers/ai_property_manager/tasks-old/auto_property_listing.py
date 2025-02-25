
import os
import shutil
import logging
from celery import shared_task
from ai_workers.ai_property_manager.services.auto_property_listing.data_processing import DataProcessing


logger = logging.getLogger(__name__)

@shared_task
def process_csv_task(file_path):
    try:
        print(f"Processing: {file_path}")

        # Process CSV file
        DataProcessing.process_data(file_path)

        # Move file to archive folder
        archive_directory = "media/processed"
        os.makedirs(archive_directory, exist_ok=True)
        archive_path = os.path.join(archive_directory, os.path.basename(file_path))
        shutil.move(file_path, archive_path)

        print(f"Moved to archive: {archive_path}")

    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
