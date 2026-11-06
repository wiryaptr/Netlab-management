from django.urls import path
from .views import ConnectionViewSet

conn_list = ConnectionViewSet.as_view({"get": "list", "post": "create"})
conn_detail = ConnectionViewSet.as_view({"get": "retrieve", "patch": "partial_update"})
conn_archive = ConnectionViewSet.as_view({"post": "archive"})
conn_restore = ConnectionViewSet.as_view({"post": "restore"})

urlpatterns = [
    path("", conn_list, name="connection_list"),
    path("<int:pk>/", conn_detail, name="connection_detail"),
    path("<int:pk>/archive/", conn_archive, name="connection_archive"),
    path("<int:pk>/restore/", conn_restore, name="connection_restore"),
]
