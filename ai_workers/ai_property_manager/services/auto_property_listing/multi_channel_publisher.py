import logging

from ai_workers.ai_property_manager.models import PropertyListing
from ai_workers.ai_property_manager.services.auto_property_listing.distribution import FacebookMarketplacePublisher, JijiPublisher

logger = logging.getLogger(__name__)

class MultiChannelPublisher:
    """Handles multi-channel property publishing to Jiji and Facebook Marketplace."""

    def __init__(self, property_id):
        self.property_id = property_id
        self.property = None
        self.jiji_publisher = JijiPublisher()
        self.fb_publisher = FacebookMarketplacePublisher()

    def get_property(self):
        """Fetches the property from the database."""
        try:
            self.property = PropertyListing.objects.get(id=self.property_id)
            return self.property
        except PropertyListing.DoesNotExist:
            logger.error(f"Property with ID {self.property_id} not found.")
            return None

    def publish_to_jiji(self):
        """Publishes property to Jiji."""
        try:
            response = self.jiji_publisher.publish(self.property)
            return {"status": "success", "platform": "Jiji", "response": response}
        except Exception as e:
            logger.error(f"Jiji publishing failed for {self.property_id}: {str(e)}")
            return {"status": "failed", "platform": "Jiji", "error": str(e)}

    def publish_to_facebook(self):
        """Publishes property to Facebook Marketplace."""
        try:
            response = self.fb_publisher.publish(self.property)
            return {"status": "success", "platform": "Facebook Marketplace", "response": response}
        except Exception as e:
            logger.error(f"Facebook Marketplace publishing failed for {self.property_id}: {str(e)}")
            return {"status": "failed", "platform": "Facebook Marketplace", "error": str(e)}

    def publish(self):
        """Handles multi-channel publishing."""
        if not self.get_property():
            return {"error": f"Property with ID {self.property_id} not found."}

        jiji_result = self.publish_to_jiji()
        fb_result = self.publish_to_facebook()

        return {"jiji": jiji_result, "facebook": fb_result}
