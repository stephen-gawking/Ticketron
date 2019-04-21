from django.urls import path

from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('tickets/', views.TicketListView.as_view(), name='tickets'),
    path('ticket/<int:pk>', views.TicketDetailView.as_view(), name='ticket-detail'),
    path('authors/', views.ClientListView.as_view(), name='authors'),
    path('client/<int:pk>',
         views.ClientDetailView.as_view(), name='client-detail'),
]


urlpatterns += [
    path('mytickets/', views.LoanedTicketsByUserListView.as_view(), name='my-borrowed'),
    path(r'borrowed/', views.LoanedTicketsAllListView.as_view(), name='all-borrowed'),  # Added for challenge
]


# Add URLConf for librarian to renew a ticket.
urlpatterns += [
    path('ticket/<uuid:pk>/renew/', views.renew_ticket_librarian, name='renew-ticket-librarian'),
]


# Add URLConf to create, update, and delete authors
urlpatterns += [
    path('client/create/', views.ClientCreate.as_view(), name='author_create'),
    path('client/<int:pk>/update/', views.ClientUpdate.as_view(), name='author_update'),
    path('client/<int:pk>/delete/', views.ClientDelete.as_view(), name='author_delete'),
]

# Add URLConf to create, update, and delete tickets
urlpatterns += [
    path('ticket/create/', views.TicketCreate.as_view(), name='ticket_create'),
    path('ticket/<int:pk>/update/', views.TicketUpdate.as_view(), name='ticket_update'),
    path('ticket/<int:pk>/delete/', views.TicketDelete.as_view(), name='ticket_delete'),
]
