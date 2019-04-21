from django.contrib import admin

# Register your models here.

from .models import Client, Status, Ticket, Task

"""Minimal registration of Models.
admin.site.register(Ticket)
admin.site.register(Client)
admin.site.register(Task)
admin.site.register(Status)
admin.site.register(Employee)
"""

admin.site.register(Status)



class TicketsInline(admin.TabularInline):
    """Defines format of inline ticket insertion (used in ClientAdmin)"""
    model = Ticket


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    """Administration object for Client models.
    Defines:
     - fields to be displayed in list view (list_display)
     - orders fields in detail view (fields),
       grouping the date fields horizontally
     - adds inline addition of tickets in client view (inlines)
    """
    #list_display = ('last_name','first_name', 'client_since')
    list_display = ('company_name', 'email_add', 'first_name', 'last_name', 'phone_number', 'address1',
                    'city', 'state', 'client_since')
    #fields = ['first_name', 'last_name', ('client_since')]
    fields = [('company_name', 'email_add', 'first_name', 'last_name', 'phone_number', 'address1', 'city',
               'state', 'client_since')]
    #inlines = [TicketsInline]


class TaskInline(admin.TabularInline):
    """Defines format of inline ticket instance insertion (used in TicketAdmin)"""
    model = Task


class TicketAdmin(admin.ModelAdmin):
    """Administration object for Ticket models.
    Defines:
     - fields to be displayed in list view (list_display)
     - adds inline addition of ticket instances in ticket view (inlines)
    """
    list_display = ('ticket_id', 'title', 'client', 'status')
    inlines = [TaskInline]


admin.site.register(Ticket, TicketAdmin)


@admin.register(Task)
class Task(admin.ModelAdmin):
    """Administration object for Task models.
    Defines:
     - fields to be displayed in list view (list_display)
     - filters that will be displayed in sidebar (list_filter)
     - grouping of fields into sections (fieldsets)
    """
    list_display = ('task_checker', 'ticket', 'employee', 'scheduled_day',)
    list_filter = ('task_checker', 'scheduled_day')

    fieldsets = (
        (None, {
            'fields': ('ticket', 'Work_Summary', 'Completion_Notes',)
        }),
        ('Availability', {
            'fields': ('scheduled_day', 'employee')
        }),
    )
