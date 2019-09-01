import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets

from core.models import Mock
from core.serializers import MockSerializer


class MockViewset(viewsets.ModelViewSet):
    queryset = Mock.objects.all()
    serializer_class = MockSerializer


@csrf_exempt  # This allows verbs besides GET
def fetch_mock(request):
    try:
        existing = Mock.objects.filter(
            path__startswith=request.path.rstrip('/'),
            verb=request.method
        ).first()
    except Mock.DoesNotExist as e:
        raise e

    content = json.loads(existing.content)
    status_code = int(existing.status_code)

    response = JsonResponse(
        content,
        status=status_code,
        safe=False
    )
    for header in existing.header_set.all():
        header_type, value = header.as_response_header
        response[header_type] = value

    return response
