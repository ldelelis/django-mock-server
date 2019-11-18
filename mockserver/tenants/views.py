import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from mocks.models import Content
from mocks.services import MockService
from tenants.utils import tenant_from_request


@csrf_exempt  # This allows verbs besides GET
def fetch_mock(request):
    tenant = tenant_from_request(request)  # TODO: I dont like this. Auth should be pluggable
    query_params = {**request.GET.dict(), **request.POST.dict()}
    mock_route = request.path.rstrip('/')

    mock = MockService.get_tenant_mocks(tenant, mock_route, request.method, query_params)

    try:
        content = json.loads(mock.content)
    except Content.DoesNotExist:
        content = {}
    status_code = mock.status_code

    response = JsonResponse(
        content,
        status=status_code,
        safe=False
    )
    for header in mock.header_set.all():
        header_type, value = header.as_response_header
        response[header_type] = value

    return response
