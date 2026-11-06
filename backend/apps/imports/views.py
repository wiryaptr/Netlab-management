from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from .service import preview_csv, commit_csv


class ImportView(APIView):
    """Preview dan commit impor CSV (multipart/form-data)."""

    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        file_obj = request.FILES.get("file")
        resource = request.data.get("resource")
        mode = request.data.get("mode", "preview")

        if not file_obj or not resource:
            return Response(
                {
                    "error": {
                        "code": "validation_error",
                        "message": "File dan resource wajib diisi.",
                        "details": {},
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            if mode == "commit":
                result = commit_csv(file_obj, resource)
            else:
                result = preview_csv(file_obj, resource)
        except Exception as exc:  # noqa: BLE001
            return Response(
                {
                    "error": {
                        "code": "import_invalid",
                        "message": str(exc) or "Gagal memproses berkas impor.",
                        "details": {},
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        http_status = status.HTTP_400_BAD_REQUEST if result.get("error") else status.HTTP_200_OK
        return Response(result, status=http_status)
