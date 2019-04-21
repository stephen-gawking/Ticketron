from django.test import TestCase

# Create your tests here.

from catalog.models import Client


class ClientModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Set up non-modified objects used by all test methods."""
        Client.objects.create(first_name='Big', last_name='Bob')

    def test_first_name_label(self):
        client = Client.objects.get(id=1)
        field_label = client._meta.get_field('first_name').verbose_name
        self.assertEquals(field_label, 'first name')

    def test_last_name_label(self):
        client = Client.objects.get(id=1)
        field_label = client._meta.get_field('last_name').verbose_name
        self.assertEquals(field_label, 'last name')

    def test_client_since_label(self):
        client = Client.objects.get(id=1)
        field_label = client._meta.get_field('client_since').verbose_name
        self.assertEquals(field_label, 'client since')

    def test_first_name_max_length(self):
        client = Client.objects.get(id=1)
        max_length = client._meta.get_field('first_name').max_length
        self.assertEquals(max_length, 100)

    def test_last_name_max_length(self):
        client = Client.objects.get(id=1)
        max_length = client._meta.get_field('last_name').max_length
        self.assertEquals(max_length, 100)

    def test_object_name_is_last_name_comma_first_name(self):
        client = Client.objects.get(id=1)
        expected_object_name = '{0}, {1}'.format(client.last_name, client.first_name)

        self.assertEquals(expected_object_name, str(client))

    def test_get_absolute_url(self):
        client = Client.objects.get(id=1)
        # This will also fail if the urlconf is not defined.
        self.assertEquals(client.get_absolute_url(), '/catalog/client/1')
