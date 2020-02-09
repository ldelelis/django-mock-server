import uuid

from django.db import models

from authentication.models import User
from common.models import DateAwareModel
from tenants.tasks import mail_membership_invite


class OrganizationAwareModel(DateAwareModel):
    organization = models.ForeignKey(
        'tenants.Organization',
        on_delete=models.CASCADE,
        null=True
    )

    class Meta:
        abstract = True


class OrganizationMembership(DateAwareModel):
    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.CASCADE
    )
    organization = models.ForeignKey(
        'tenants.Organization',
        on_delete=models.CASCADE
    )
    is_owner = models.BooleanField(
        default=False
    )
    is_admin = models.BooleanField(
        default=False
    )

    class Meta:
        unique_together = (
            ('tenant', 'organization'),
            ('is_owner', 'organization'),
        )


class Technology(DateAwareModel):
    code = models.CharField(max_length=3)
    name = models.CharField(max_length=255)


class OrganizationProfile(models.Model):
    public_name = models.CharField(max_length=255)
    description = models.TextField(null=True)
    technologies = models.ManyToManyField(
        'tenants.Technology',
        blank=True
    )
    avatar = models.ImageField(default="default.png")
    website = models.URLField(null=True)
    twitter = models.CharField(max_length=512, null=True)
    facebook = models.CharField(max_length=512, null=True)
    linkedin = models.CharField(max_length=512, null=True)
    instagram = models.CharField(max_length=512, null=True)


class Organization(DateAwareModel):
    name = models.CharField(
        max_length=255
    )
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    is_playground = models.BooleanField(
        default=False
    )
    users = models.ManyToManyField(
        'tenants.Tenant',
        through=OrganizationMembership,
        blank=True
    )
    profile = models.OneToOneField(
        'tenants.OrganizationProfile',
        on_delete=models.CASCADE,
        null=True
    )

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.pk:
            self.profile = OrganizationProfile.objects.create(
                public_name=self.name
            )
        return super(Organization, self).save(force_insert, force_update, using, update_fields)

    @property
    def member_count(self):
        return self.organizationmembership_set.count()

    @property
    def mock_count(self):
        return self.mock_set.count()

    def __str__(self):
        return f"{self.name} ({self.uuid})"


class Tenant(DateAwareModel, User):
    pass


class OrganizationInvite(OrganizationAwareModel):
    email = models.EmailField()
    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.SET_NULL,
        null=True
    )
    from_domain = models.CharField(
        max_length=256,
        null=False,
        default="",
    )
    is_accepted = models.BooleanField(
        default=False
    )

    def save(self, *args, **kwargs):
        if not self.pk:
            is_existing = self.tenant is not None
            mail_membership_invite.delay(is_existing, self.email, self.organization.name,
                                         self.from_domain)
