import uuid

from django.db import models

from authentication.models import User
from common.models import DateAwareModel


class Organization(DateAwareModel):
    name = models.CharField(
        max_length=255
    )
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    users = models.ManyToManyField(
        'tenants.Tenant'
    )


class Tenant(DateAwareModel, User):
    pass


class OrganizationAwareModel(DateAwareModel):
    organization = models.ForeignKey(
        'tenants.Organization',
        on_delete=models.CASCADE,
        null=True
    )

    class Meta:
        abstract = True
