from django.shortcuts import render

# Create your views here.

from .models import Ticket, Client, Task, Status


def index(request):
    """View function for home page of site."""
    # Generate counts of some of the main objects
    num_tickets = Ticket.objects.all().count()
    num_instances = Task.objects.all().count()
    # Available copies of tickets
    num_instances_available = Task.objects.filter(status__exact='a').count()
    num_authors = Client.objects.count()  # The 'all()' is implied by default.

    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits+1

    # Render the HTML template index.html with the data in the context variable.
    return render(
        request,
        'index.html',
        context={'num_tickets': num_tickets, 'num_instances': num_instances,
                 'num_instances_available': num_instances_available, 'num_authors': num_authors,
                 'num_visits': num_visits},
    )


from django.views import generic


class TicketListView(generic.ListView):
    """Generic class-based view for a list of tickets."""
    model = Ticket
    paginate_by = 10


class TicketDetailView(generic.DetailView):
    """Generic class-based detail view for a ticket."""
    model = Ticket


class ClientListView(generic.ListView):
    """Generic class-based list view for a list of authors."""
    model = Client
    paginate_by = 10


class ClientDetailView(generic.DetailView):
    """Generic class-based detail view for an client."""
    model = Client


from django.contrib.auth.mixins import LoginRequiredMixin


class LoanedTicketsByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing tickets on loan to current user."""
    model = Task
    template_name = 'catalog/task_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return Task.objects.filter(employee=self.request.user).filter(status__exact='o').order_by('scheduled_day')


# Added as part of challenge!
from django.contrib.auth.mixins import PermissionRequiredMixin


class LoanedTicketsAllListView(PermissionRequiredMixin, generic.ListView):
    """Generic class-based view listing all tickets on loan. Only visible to users with can_mark_returned permission."""
    model = Task
    permission_required = 'catalog.can_mark_returned'
    template_name = 'catalog/task_list_borrowed_all.html'
    paginate_by = 10

    def get_queryset(self):
        return Task.objects.filter(status__exact='o').order_by('scheduled_day')


from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
import datetime
from django.contrib.auth.decorators import permission_required

# from .forms import RenewTicketForm
from catalog.forms import RenewTicketForm


@permission_required('catalog.can_mark_returned')
def renew_ticket_librarian(request, pk):
    """View function for renewing a specific Task by librarian."""
    task = get_object_or_404(Task, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewTicketForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model scheduled_day field)
            task.scheduled_day = form.cleaned_data['renewal_date']
            task.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed'))

    # If this is a GET (or any other method) create the default form
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewTicketForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'task': task,
    }

    return render(request, 'catalog/ticket_renew_librarian.html', context)


from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Client


class ClientCreate(PermissionRequiredMixin, CreateView):
    model = Client
    fields = '__all__'
    initial = {'client_since': '01/01/2019'}
    permission_required = 'catalog.can_mark_returned'


class ClientUpdate(PermissionRequiredMixin, UpdateView):
    model = Client
    fields = ['first_name', 'last_name', 'client_since']
    permission_required = 'catalog.can_mark_returned'


class ClientDelete(PermissionRequiredMixin, DeleteView):
    model = Client
    success_url = reverse_lazy('authors')
    permission_required = 'catalog.can_mark_returned'


# Classes created for the forms challenge
class TicketCreate(PermissionRequiredMixin, CreateView):
    model = Ticket
    fields = '__all__'
    permission_required = 'catalog.can_mark_returned'


class TicketUpdate(PermissionRequiredMixin, UpdateView):
    model = Ticket
    fields = '__all__'
    permission_required = 'catalog.can_mark_returned'


class TicketDelete(PermissionRequiredMixin, DeleteView):
    model = Ticket
    success_url = reverse_lazy('tickets')
    permission_required = 'catalog.can_mark_returned'
