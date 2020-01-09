import logging

from django.http import JsonResponse
from rest_framework.decorators import (
    permission_classes,
    api_view
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.status import HTTP_404_NOT_FOUND

from api.permissions import (
    IsOrganizationTenantPermission
)
from authentication.decorators.tenant_view import tenancy_required
from mocks.services import MockService


logger = logging.getLogger(__name__)


@tenancy_required
@api_view(('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
@permission_classes((IsAuthenticated & IsOrganizationTenantPermission,))
def fetch_mock(request):
    logger.info(f'fetch_mock tenant {request.tenant.uuid}')

    query_params = {**request.GET.dict(), **request.POST.dict()}
    mock_route = request.path.rstrip('/')

    mock = MockService.get_tenant_mocks(request.tenant, mock_route, request.method, query_params)

    if mock is None:
        logger.info(f'mock not found tenant {request.tenant.uuid}')
        return JsonResponse(
            {'detail': 'mock does not exist'},
            status=HTTP_404_NOT_FOUND
        )

    response = JsonResponse(
        mock.content.content,
        status=mock.status_code,
        safe=False
    )
    for header in mock.header_set.all():
        header_type, value = header.as_response_header
        response[header_type] = value

    logger.info(f'end fetch_mock tenant {request.tenant.uuid}')
    return response
