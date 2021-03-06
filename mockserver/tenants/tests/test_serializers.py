from django.test import TestCase
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIRequestFactory

from common.tests.mixins import MockTestMixin
from tenants.serializers import (
    TenantSerializer,
    OrganizationSerializer,
    OrganizationPromotionSerializer,
    OrganizationDemotionSerializer,
)


class TenantSerializerValidationTestCase(MockTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.serializer = TenantSerializer
        cls.tenant = cls.create_bare_minimum_tenant()

    def test_field_validation_hashes_password(self):
        old_password = self.tenant.password
        data = {
            'email': self.tenant.email,
            'password': 'adifferentpasswordthanthedefaultone'}
        serializer = self.serializer(self.tenant, data=data)

        new_passwd = serializer.validate_password(data['password'])

        self.assertNotEqual(old_password, new_passwd)


class OrganizationSerializerTestCase(MockTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.serializer = OrganizationSerializer
        cls.tenant = cls.create_bare_minimum_tenant()
        cls.factory = APIRequestFactory()

    def test_created_organization_automatically_adds_authenticated_user(self):
        data = {
            'name': 'aaaaaaaaa',
        }
        request = self.factory.post('/some/url')
        request.user = self.tenant.user_ptr
        serializer = self.serializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        organization = serializer.save()

        self.assertIn(self.tenant, organization.users.all())
        self.assertTrue(organization.organizationmembership_set.first().is_owner)
        self.assertTrue(organization.organizationmembership_set.first().is_admin)


class OrganizationPromotionSerializerTestCase(MockTestMixin, TestCase):
    @classmethod
    def setUpClass(cls):
        super(OrganizationPromotionSerializerTestCase, cls).setUpClass()
        cls.serializer = OrganizationPromotionSerializer
        cls.organization = cls.create_bare_minimum_organization()
        cls.tenant = cls.create_bare_minimum_tenant()

    def test_promoting_non_existent_member_fails(self):
        data = {
            'organization': self.organization.pk,
            'tenant': self.tenant.pk
        }
        ser = self.serializer(data=data)

        with self.assertRaises(ValidationError, msg='tenant is not part of the organization'):
            ser.is_valid(raise_exception=True)

    def test_serializer_creation_sets_member_as_admin(self):
        other_tenant = self.create_bare_minimum_tenant()
        other_org = self.create_bare_minimum_organization(other_tenant)
        data = {
            'organization': other_org.pk,
            'tenant': other_tenant.pk
        }
        ser = self.serializer(data=data)
        ser.is_valid()

        result = ser.save()

        self.assertTrue(result.is_admin)


class OrganizationDemotionSerializerTestCase(MockTestMixin, TestCase):
    @classmethod
    def setUpClass(cls):
        super(OrganizationDemotionSerializerTestCase, cls).setUpClass()
        cls.serializer = OrganizationDemotionSerializer
        cls.organization = cls.create_bare_minimum_organization()
        cls.tenant = cls.create_bare_minimum_tenant()

    def test_demoting_non_existent_member_fails(self):
        data = {
            'organization': self.organization.pk,
            'tenant': self.tenant.pk
        }
        ser = self.serializer(data=data)

        with self.assertRaises(ValidationError, msg='tenant is not part of the organization'):
            ser.is_valid(raise_exception=True)

    def test_serializer_creation_sets_member_as_admin(self):
        other_tenant = self.create_bare_minimum_tenant()
        other_org = self.create_bare_minimum_organization(other_tenant)
        data = {
            'organization': other_org.pk,
            'tenant': other_tenant.pk
        }
        ser = self.serializer(data=data)
        ser.is_valid()

        result = ser.save()

        self.assertFalse(result.is_admin)
