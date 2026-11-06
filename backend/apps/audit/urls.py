from django.urls import path
from .views import AuditEventViewSet

audit_list = AuditEventViewSet.as_view({"get": "list"})
audit_detail = AuditEventViewSet.as_view({"get": "retrieve"})

urlpatterns = [
    path("", audit_list, name="audit_list"),
    path("<int:pk>/", audit_detail, name="audit_detail"),
]
