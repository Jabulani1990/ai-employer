import os
import time
from django.core.management.base import BaseCommand
from ai_workers.ai_property_manager.services.auto_property_listing.data_processing import DataProcessing
from ai_workers.ai_property_manager.tasks import process_csv_task


# class Command(BaseCommand):
#     help = "Watches for new CSV files in media/uploads and processes them"

#     def handle(self, *args, **kwargs):
#         watch_directory = "media/uploads"
#         processed_files = set()

#         self.stdout.write(self.style.SUCCESS("Starting file watcher..."))

#         while True:
#             files = set(os.listdir(watch_directory))
#             new_files = files - processed_files

#             for file in new_files:
#                 if file.endswith(".csv"):
#                     file_path = os.path.join(watch_directory, file)
#                     self.stdout.write(self.style.SUCCESS(f"Processing: {file_path}"))
#                     DataProcessing.process_data(file_path)

#             processed_files = files
#             time.sleep(5)  # Check every 5 seconds




class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        watch_directory = "media/uploads"
        processed_files = set()

        self.stdout.write(self.style.SUCCESS("Starting file watcher..."))

        while True:
            files = set(os.listdir(watch_directory))
            new_files = files - processed_files

            for file in new_files:
                if file.endswith(".csv"):
                    file_path = os.path.join(watch_directory, file)
                    self.stdout.write(self.style.SUCCESS(f"Queuing task for: {file_path}"))

                    # Send task to Celery instead of blocking execution
                    process_csv_task.delay(file_path)

            processed_files = files
            time.sleep(5)  # Reduce CPU usage
