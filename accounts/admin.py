from django.contrib import admin
from django.apps import apps

# Get all models in the 'accounts' app
models = apps.get_app_config('accounts').get_models()

# Register each model dynamically
for model in models:
    admin.site.register(model)
