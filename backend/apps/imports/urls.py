from django.urls import path
from .views import ImportView

urlpatterns = [
    path("", ImportView.as_view(), name="import_csv"),
]
