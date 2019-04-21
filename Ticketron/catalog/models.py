import uuid
from django.db import models

# Create your models here.

from django.urls import reverse  # To generate URLS by reversing URL patterns


class Status(models.Model):
    """Model representing a ticket status (e.g. In Progress, Resolved)."""
    name = models.CharField(
        max_length=200,
        help_text="Enter a ticket status (e.g. In Progress, Resolved)"
        )

    def __str__(self):
        """String for representing the Model object (in Admin site etc.)"""
        return self.name


#NO LONGER NEEDED.
#class Employee(models.Model):
 #   """Model representing a Employee (e.g. Tom, Vladan etc.)"""
  #  name = models.CharField(max_length=200,
   #                         help_text="Enter the ticket owners' name/names ")

   # def __str__(self):
   #     """String for representing the Model object (in Admin site etc.)"""
   #     return self.name


class Ticket(models.Model):
    """Model representing a ticket (but not a specific copy of a ticket)."""
    title = models.CharField(max_length=200)
    client = models.ForeignKey('Client', on_delete=models.SET_NULL, null=True)
    ticket_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Foreign Key used because ticket can only have one client, but authors can have multiple tickets
    # Client as a string rather than object because it hasn't been declared yet in file.
    summary = models.TextField(max_length=1000, help_text="Enter a brief description of what needs to be done")
    status = models.ForeignKey('Status', default='new', on_delete=models.SET_NULL, null=True, help_text="Select a status for this ticket")
    # ManyToManyField used because a status can contain many tickets and a Ticket can cover many status.
    # Status class has already been defined so we can specify the object above.

    ticket_severity = (
        ('h', 'High'),
        ('m', 'Medium'),
        ('l', 'Low'),

    )

    severity = models.CharField(
        max_length=1,
        choices=ticket_severity,
        blank=True,
        default='m',
        help_text='Ticket Severity')


    def display_status(self):
        """Creates a string for the Status. This is required to display status in Admin."""
        return ', '.join([status.name for status in self.status.all()[:3]])

    display_status.short_description = 'Status'

    def get_absolute_url(self):
        """Returns the url to access a particular ticket instance."""
        return reverse('ticket-detail', args=[str(self.ticket_id)])

    def __str__(self):
        """String for representing the Model object."""
        return self.title


import uuid  # Required for unique ticket instances
from datetime import date

from django.contrib.auth.models import User  # Required to assign User as a employee


class Task(models.Model):
    """Model representing a specific copy of a ticket (i.e. that can be borrowed from the library)."""
    ticket = models.ForeignKey('Ticket', on_delete=models.SET_NULL, null=True)

    Work_Summary = models.TextField(max_length=500)
    Completion_Notes = models.TextField(max_length=500,blank=True)
    scheduled_day = models.DateField(null=True, blank=True)
    employee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    task_checker = models.BooleanField('Done Yet?', default=False)


    @property
    def is_overdue(self):
        if self.scheduled_day and date.today() > self.scheduled_day:
            return True
        return False



    class Meta:
        ordering = ['scheduled_day']
        permissions = (("can_mark_returned", "Set ticket as returned"),)

    def __str__(self):
        """String for representing the Model object."""
        return '{0} ({1})'.format(self.id, self.ticket.title)


class Client(models.Model):
    """Model representing an client."""
    company_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company_name = models.CharField(max_length=100, default='Bogus Inc')
    first_name = models.CharField(max_length=100, default='Jon')
    last_name = models.CharField(max_length=100, default='Smith')
    email_add = models.EmailField(max_length=100, default='bogus@test.com')
    phone_number = models.CharField(max_length=100, default='5555555555')
    address1 = models.CharField(max_length=100, default='123 Bogus Ave')
    #address2 = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, default='Midland')
    state = models.CharField(max_length=100, default='Texas')
    client_since = models.DateField(null=True, blank=True)


    class Meta:
        ordering = ['last_name', 'first_name']

    def get_absolute_url(self):
        """Returns the url to access a particular client instance."""
        return reverse('client-detail', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object."""
        return '{0}, {1}'.format(self.company_name, self.client_since)
