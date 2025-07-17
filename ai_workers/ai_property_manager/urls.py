from django.urls import path, include
from ai_workers.ai_property_manager.views import CSVUploadView, PropertyDetailView, PropertyListCreateView, PropertyRetrieveUpdateDeleteView, PropertySearchView, PublishPropertyView

urlpatterns = [
    # 🏠 Property Management URLs
    path('properties/', PropertyListCreateView.as_view(), name='property-list-create'),
    path('properties/<uuid:pk>/', PropertyRetrieveUpdateDeleteView.as_view(), name='property-detail'),
    path("properties/upload-csv/", CSVUploadView.as_view(), name="upload-csv"),
    path("properties/publish-property/", PublishPropertyView.as_view(), name="publish_property"),
    path('properties/search/', PropertySearchView.as_view(), name='property-search'),
    path("properties/detail/<uuid:id>/", PropertyDetailView.as_view(), name="property-detail"),
    
    # 🤖 Autonomous AI Chatbot URLs
    path('chatbot/', include('ai_workers.ai_property_manager.chatbot_urls')),
]
