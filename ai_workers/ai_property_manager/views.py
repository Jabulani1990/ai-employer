import hashlib
import uuid
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status, generics,filters

from ai_workers.ai_property_manager.services.auto_property_listing.multi_channel_publisher import MultiChannelPublisher
from .models import PropertyListing, PropertyMedia, TemporaryMedia
from .serializers import PropertyListingSerializer, PropertyMediaSerializer, TemporaryMediaSerializer
from ai_workers.ai_property_manager.services.auto_property_listing.data_ingestion import DataIngestion
from ai_workers.ai_property_manager.services.auto_property_listing.data_processing import DataProcessing
import pandas as pd
import os
from django.core.files.storage import default_storage
from django.conf import settings
from django.db.models import Q
from .models import PropertyListing
from .serializers import PropertyListingSerializer
from rest_framework.pagination import PageNumberPagination



# class PropertyMediaUploadView(generics.CreateAPIView):
#     """Handles uploading multiple property media files."""
#     serializer_class = PropertyMediaSerializer
#     parser_classes = (MultiPartParser, FormParser)

#     def post(self, request, *args, **kwargs):
#         """Allows multiple file uploads for a single property."""

#         property_id = request.data.get("property")  # Get property ID
#         files = request.FILES.getlist("files")  # Get multiple files correctly

#         if not property_id or not files:
#             return Response({"error": "Property ID and files are required."}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             # Convert to UUID
#             property_uuid = uuid.UUID(property_id)
#             property_instance = get_object_or_404(PropertyListing, id=property_uuid)
#         except (ValueError, PropertyListing.DoesNotExist):
#             return Response({"error": "Invalid Property ID or Property not found."}, status=status.HTTP_404_NOT_FOUND)

#         uploaded_files = []
#         for file in files:
#             media_instance = PropertyMedia(property=property_instance, file=file)
#             media_instance.save()
#             uploaded_files.append(PropertyMediaSerializer(media_instance).data)

#         return Response({"message": "Files uploaded successfully.", "uploaded_files": uploaded_files}, status=status.HTTP_201_CREATED)


# class PropertyMediaUploadView(generics.CreateAPIView):
#     """Handles uploading multiple property media files."""
#     serializer_class = PropertyMediaSerializer
#     parser_classes = (MultiPartParser, FormParser)

#     def post(self, request, *args, **kwargs):
#         """Allows multiple file uploads for a single property."""
        
#         property_id = request.data.get("property")  # Get property ID
#         files = request.FILES.getlist("files")  # Get multiple files correctly

#         if not files:
#             return Response({"error": "Files are required."}, status=status.HTTP_400_BAD_REQUEST)

#         uploaded_files = []

#         if property_id:
#             # Property exists, attach media
#             try:
#                 property_uuid = uuid.UUID(property_id)
#                 property_instance = get_object_or_404(PropertyListing, id=property_uuid)
#             except (ValueError, PropertyListing.DoesNotExist):
#                 return Response({"error": "Invalid Property ID or Property not found."}, status=status.HTTP_404_NOT_FOUND)

#             for file in files:
#                 media_instance = PropertyMedia(property=property_instance, file=file)
#                 media_instance.save()
#                 uploaded_files.append(PropertyMediaSerializer(media_instance).data)

#             return Response({"message": "Files uploaded successfully.", "uploaded_files": uploaded_files}, status=status.HTTP_201_CREATED)
        
#         else:
#             # No property ID, store in TemporaryMedia for future matching
#             for file in files:
#                 temp_media = TemporaryMedia(file=file)
#                 temp_media.save()
#                 uploaded_files.append(TemporaryMediaSerializer(temp_media).data)

#             return Response({"message": "Files uploaded and will be matched to properties later.", "uploaded_files": uploaded_files}, status=status.HTTP_202_ACCEPTED)

class PropertyMediaUploadView(generics.CreateAPIView):
    """Handles uploading multiple property media files."""
    serializer_class = PropertyMediaSerializer
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        """Allows multiple file uploads for a single property."""

        property_id = request.data.get("property")  # Property ID if provided
        files = request.FILES.getlist("files")  # Get multiple files

        if not files:
            return Response({"error": "Files are required."}, status=status.HTTP_400_BAD_REQUEST)

        uploaded_files = []

        if property_id:
            # ✅ Property exists, attach media
            try:
                property_uuid = uuid.UUID(property_id)
                property_instance = get_object_or_404(PropertyListing, id=property_uuid)
            except (ValueError, PropertyListing.DoesNotExist):
                return Response({"error": "Invalid Property ID or Property not found."}, status=status.HTTP_404_NOT_FOUND)

            for file in files:
                media_instance = PropertyMedia(property=property_instance, file=file)
                media_instance.save()
                uploaded_files.append(PropertyMediaSerializer(media_instance).data)

            return Response({"message": "Files uploaded successfully.", "uploaded_files": uploaded_files}, status=status.HTTP_201_CREATED)
        
        else:
            # 🚀 No Property ID, store in TemporaryMedia for future matching
            for file in files:
                # Generate a title hash based on the filename
                title_hash = hashlib.md5(file.name.encode()).hexdigest()

                temp_media = TemporaryMedia(file=file, title_hash=title_hash, processed=False)
                temp_media.save()

                uploaded_files.append(TemporaryMediaSerializer(temp_media).data)

            return Response({"message": "Files uploaded and will be matched to properties later.", "uploaded_files": uploaded_files}, status=status.HTTP_202_ACCEPTED)

class PropertyListCreateView(generics.ListCreateAPIView):
    queryset = PropertyListing.objects.all()
    serializer_class = PropertyListingSerializer

    def create(self, request, *args, **kwargs):
        """Override create method to process and ingest data through the pipeline"""
        try:
            # Step 1: Validate Incoming Data
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            raw_data = serializer.validated_data  # Dictionary format

            # Step 2: Process Data
            df = DataProcessing.clean_data(pd.DataFrame([raw_data]))  # Convert to DataFrame
            df = DataProcessing.standardize_data(df)
            df = DataProcessing.classify_property(df)
            df = DataProcessing.estimate_price(df)
            df = DataProcessing.analyze_market(df)
            df = DataProcessing.remove_duplicates(df)

            # Step 3: Ingest Data
            message = DataProcessing.save_to_database(df)

            return Response(
                {"message": message},
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Retrieve, Update, and Delete a single property
class PropertyRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PropertyListing.objects.all()
    serializer_class = PropertyListingSerializer



class CSVUploadView(APIView):
    """
    Handles CSV file upload and processes property data.
    """

    def post(self, request, *args, **kwargs):
        if "file" not in request.FILES:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        uploaded_file = request.FILES["file"]

        # Validate file type (only allow CSV)
        if not uploaded_file.name.endswith(".csv"):
            return Response({"error": "Invalid file format. Only CSV files are allowed."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Define the path to save the uploaded file in MEDIA_ROOT
            file_path = os.path.join(settings.MEDIA_ROOT, "uploads", uploaded_file.name)

            # Ensure the uploads directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # Save the file to MEDIA_ROOT/uploads/
            with default_storage.open(file_path, "wb+") as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)

            # Process the CSV file
            #result = DataProcessing.process_data(file_path)

            return Response(
                {"message": "CSV file processed successfully.", "details": file_path},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response({"error": f"Error processing file: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



#THIS IMPLEMENTATION IS NOT COMPLETE
class PublishPropertyView(APIView):
    """API endpoint to trigger multi-channel property publishing."""

    def post(self, request):
        property_id = request.data.get("property_id")

        if not property_id:
            return Response({"error": "Missing property_id"}, status=status.HTTP_400_BAD_REQUEST)

        publisher = MultiChannelPublisher(property_id)
        result = publisher.publish()

        return Response({"message": "Publishing completed", "result": result}, status=status.HTTP_200_OK)


# class PropertySearchView(generics.ListAPIView):
#     """
#     API endpoint to search properties based on filters.
#     """
#     serializer_class = PropertyListingSerializer

#     def get_queryset(self):
#         """
#         Filters properties based on query parameters.
#         """
#         queryset = PropertyListing.objects.all()
#         params = self.request.query_params

#         property_type = params.get("property_type", None)
#         listing_type = params.get("listing_type", None)
#         status = params.get("status", None)
#         location = params.get("location", None)
#         min_price = params.get("min_price", None)
#         max_price = params.get("max_price", None)
#         bedrooms = params.get("bedrooms", None)
#         bathrooms = params.get("bathrooms", None)
#         min_area = params.get("min_area", None)
#         max_area = params.get("max_area", None)
#         is_published = params.get("is_published", None)
#         is_suspicious = params.get("is_suspicious", None)
#         property_category = params.get("property_category", None)
        
#         # Apply filters
#         if property_type:
#             queryset = queryset.filter(property_type=property_type)
#         if listing_type:
#             queryset = queryset.filter(listing_type=listing_type)
#         if status:
#             queryset = queryset.filter(status=status)
#         if location:
#             queryset = queryset.filter(location__icontains=location)  # Partial match
#         if min_price:
#             queryset = queryset.filter(price__gte=min_price)
#         if max_price:
#             queryset = queryset.filter(price__lte=max_price)
#         if bedrooms:
#             queryset = queryset.filter(bedrooms=bedrooms)
#         if bathrooms:
#             queryset = queryset.filter(bathrooms=bathrooms)
#         if min_area:
#             queryset = queryset.filter(area__gte=min_area)
#         if max_area:
#             queryset = queryset.filter(area__lte=max_area)
#         if is_published is not None:
#             queryset = queryset.filter(is_published=is_published.lower() == "true")
#         if is_suspicious is not None:
#             queryset = queryset.filter(is_suspicious=is_suspicious.lower() == "true")
#         if property_category:
#             queryset = queryset.filter(property_category=property_category)

#         return queryset

#     def get(self, request, *args, **kwargs):
#         """
#         Returns a list of properties based on search filters.
#         """
#         queryset = self.get_queryset()
#         serializer = self.get_serializer(queryset, many=True)
        
#         return Response({
#             "count": queryset.count(),
#             "results": serializer.data
#         }, status=status.HTTP_200_OK)

#     def list(self, request, *args, **kwargs):
#         queryset = self.get_queryset()
#         page = request.GET.get("page", 1)
#         paginator = Paginator(queryset, 10)  # Show 10 listings per page

#         try:
#             properties = paginator.page(page)
#         except PageNotAnInteger:
#             properties = paginator.page(1)
#         except EmptyPage:
#             properties = paginator.page(paginator.num_pages)

#         serializer = self.get_serializer(properties, many=True)
#         return Response({
#             "count": paginator.count,
#             "num_pages": paginator.num_pages,
#             "results": serializer.data
#         })




class PropertyPagination(PageNumberPagination):
    page_size = 10  # Default number of properties per page
    page_size_query_param = 'page_size'  # Allow users to change page size
    max_page_size = 100  # Limit maximum results per page

class PropertySearchView(generics.ListAPIView):
    """
    API endpoint to search properties based on filters with pagination.
    """
    serializer_class = PropertyListingSerializer
    pagination_class = PropertyPagination  # Use DRF's pagination

    def get_queryset(self):
        """
        Filters properties based on query parameters.
        """
        queryset = PropertyListing.objects.all()
        params = self.request.query_params

        # Extract parameters
        filters = {
            "property_type": params.get("property_type"),
            "listing_type": params.get("listing_type"),
            "status": params.get("status"),
            "location__icontains": params.get("location"),
            "price__gte": params.get("min_price"),
            "price__lte": params.get("max_price"),
            "bedrooms": params.get("bedrooms"),
            "bathrooms": params.get("bathrooms"),
            "area__gte": params.get("min_area"),
            "area__lte": params.get("max_area"),
            "property_category": params.get("property_category"),
        }

        # Filter by boolean fields correctly
        is_published = params.get("is_published")
        is_suspicious = params.get("is_suspicious")

        if is_published is not None:
            filters["is_published"] = is_published.lower() == "true"
        if is_suspicious is not None:
            filters["is_suspicious"] = is_suspicious.lower() == "true"

        return queryset.filter(**{k: v for k, v in filters.items() if v is not None})


class PropertyDetailView(generics.RetrieveAPIView):
    """
    API endpoint to retrieve a single property with its media files.
    """
    serializer_class = PropertyListingSerializer
    queryset = PropertyListing.objects.all()
    lookup_field = "id"  # Use UUID as the identifier

    def get(self, request, *args, **kwargs):
        property_instance = get_object_or_404(PropertyListing, id=kwargs["id"])
        serializer = self.get_serializer(property_instance)
        return Response(serializer.data, status=status.HTTP_200_OK)