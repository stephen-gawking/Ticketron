from django.test import TestCase

# Create your tests here.


from catalog.models import Client
from django.urls import reverse


class ClientListViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Create authors for pagination tests
        number_of_authors = 13
        for author_id in range(number_of_authors):
            Client.objects.create(first_name='Christian {0}'.format(author_id),
                                  last_name='Surname {0}'.format(author_id))

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/catalog/authors/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('authors'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('authors'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/client_list.html')

    def test_pagination_is_ten(self):
        response = self.client.get(reverse('authors'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] is True)
        self.assertTrue(len(response.context['author_list']) == 10)

    def test_lists_all_authors(self):
        # Get second page and confirm it has (exactly) the remaining 3 items
        response = self.client.get(reverse('authors')+'?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] is True)
        self.assertTrue(len(response.context['author_list']) == 3)


import datetime
from django.utils import timezone

from catalog.models import Task, Ticket, Status, Employee
from django.contrib.auth.models import User  # Required to assign User as a employee


class LoanedTasksByUserListViewTest(TestCase):

    def setUp(self):
        # Create two users
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')

        test_user1.save()
        test_user2.save()

        # Create a ticket
        test_author = Client.objects.create(first_name='John', last_name='Smith')
        test_status = Status.objects.create(name='Fantasy')
        test_language = Employee.objects.create(name='English')
        test_ticket = Ticket.objects.create(
            title='Ticket Title',
            summary='My ticket summary',
            isbn='ABCDEFG',
            client=test_author,
            employee=test_language,
        )
        # Create status as a post-step
        status_objects_for_ticket = Status.objects.all()
        test_ticket.status.set(status_objects_for_ticket)
        test_ticket.save()

        # Create 30 Task objects
        number_of_ticket_copies = 30
        for ticket_copy in range(number_of_ticket_copies):
            return_date = timezone.now() + datetime.timedelta(days=ticket_copy % 5)
            if ticket_copy % 2:
                the_employee = test_user1
            else:
                the_employee = test_user2
            status = 'm'
            Task.objects.create(ticket=test_ticket, Work_Summary=' ', scheduled_day=return_date,
                                        employee=the_employee, status=status)

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('my-borrowed'))
        self.assertRedirects(response, '/accounts/login/?next=/catalog/mytickets/')

    def test_logged_in_uses_correct_template(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('my-borrowed'))

        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'testuser1')
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)

        # Check we used correct template
        self.assertTemplateUsed(response, 'catalog/task_list_borrowed_user.html')

    def test_only_borrowed_tickets_in_list(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('my-borrowed'))

        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'testuser1')
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)

        # Check that initially we don't have any tickets in list (none on loan)
        self.assertTrue('task_list' in response.context)
        self.assertEqual(len(response.context['task_list']), 0)

        # Now change all tickets to be on loan
        get_ten_tickets = Task.objects.all()[:10]

        for copy in get_ten_tickets:
            copy.status = 'o'
            copy.save()

        # Check that now we have borrowed tickets in the list
        response = self.client.get(reverse('my-borrowed'))
        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'testuser1')
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)

        self.assertTrue('task_list' in response.context)

        # Confirm all tickets belong to testuser1 and are on loan
        for ticketitem in response.context['task_list']:
            self.assertEqual(response.context['user'], ticketitem.employee)
            self.assertEqual('o', ticketitem.status)

    def test_pages_paginated_to_ten(self):

        # Change all tickets to be on loan.
        # This should make 15 test user ones.
        for copy in Task.objects.all():
            copy.status = 'o'
            copy.save()

        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('my-borrowed'))

        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'testuser1')
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)

        # Confirm that only 10 items are displayed due to pagination
        # (if pagination not enabled, there would be 15 returned)
        self.assertEqual(len(response.context['task_list']), 10)

    def test_pages_ordered_by_scheduled_day(self):

        # Change all tickets to be on loan
        for copy in Task.objects.all():
            copy.status = 'o'
            copy.save()

        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('my-borrowed'))

        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'testuser1')
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)

        # Confirm that of the items, only 10 are displayed due to pagination.
        self.assertEqual(len(response.context['task_list']), 10)

        last_date = 0
        for copy in response.context['task_list']:
            if last_date == 0:
                last_date = copy.scheduled_day
            else:
                self.assertTrue(last_date <= copy.scheduled_day)


from django.contrib.auth.models import Permission  # Required to grant the permission needed to set a ticket as returned.


class RenewTasksViewTest(TestCase):

    def setUp(self):
        # Create a user
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user1.save()

        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')
        test_user2.save()
        permission = Permission.objects.get(name='Set ticket as returned')
        test_user2.user_permissions.add(permission)
        test_user2.save()

        # Create a ticket
        test_author = Client.objects.create(first_name='John', last_name='Smith')
        test_status = Status.objects.create(name='Fantasy')
        test_language = Employee.objects.create(name='English')
        test_ticket = Ticket.objects.create(title='Ticket Title', summary='My ticket summary',
                                        isbn='ABCDEFG', client=test_author, employee=test_language,)
        # Create status as a post-step
        status_objects_for_ticket = Status.objects.all()
        test_ticket.status.set(status_objects_for_ticket)
        test_ticket.save()

        # Create a Task object for test_user1
        return_date = datetime.date.today() + datetime.timedelta(days=5)
        self.test_task1 = Task.objects.create(ticket=test_ticket,
                                                              Work_Summary=' ', scheduled_day=return_date,
                                                              employee=test_user1, status='o')

        # Create a Task object for test_user2
        return_date = datetime.date.today() + datetime.timedelta(days=5)
        self.test_task2 = Task.objects.create(ticket=test_ticket, Work_Summary='Unlikely Imprint, 2016',
                                                              scheduled_day=return_date, employee=test_user2, status='o')

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('renew-ticket-librarian', kwargs={'pk': self.test_task1.pk}))
        # Manually check redirect (Can't use assertRedirect, because the redirect URL is unpredictable)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_redirect_if_logged_in_but_not_correct_permission(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('renew-ticket-librarian', kwargs={'pk': self.test_task1.pk}))

        # Manually check redirect (Can't use assertRedirect, because the redirect URL is unpredictable)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_logged_in_with_permission_borrowed_ticket(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('renew-ticket-librarian', kwargs={'pk': self.test_task2.pk}))

        # Check that it lets us login - this is our ticket and we have the right permissions.
        self.assertEqual(response.status_code, 200)

    def test_logged_in_with_permission_another_users_borrowed_ticket(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('renew-ticket-librarian', kwargs={'pk': self.test_task1.pk}))

        # Check that it lets us login. We're a librarian, so we can view any users ticket
        self.assertEqual(response.status_code, 200)

    def test_uses_correct_template(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('renew-ticket-librarian', kwargs={'pk': self.test_task1.pk}))
        self.assertEqual(response.status_code, 200)

        # Check we used correct template
        self.assertTemplateUsed(response, 'catalog/ticket_renew_librarian.html')

    def test_form_renewal_date_initially_has_date_three_weeks_in_future(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('renew-ticket-librarian', kwargs={'pk': self.test_task1.pk}))
        self.assertEqual(response.status_code, 200)

        date_3_weeks_in_future = datetime.date.today() + datetime.timedelta(weeks=3)
        self.assertEqual(response.context['form'].initial['renewal_date'], date_3_weeks_in_future)

    def test_form_invalid_renewal_date_past(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')

        date_in_past = datetime.date.today() - datetime.timedelta(weeks=1)
        response = self.client.post(reverse('renew-ticket-librarian', kwargs={'pk': self.test_task1.pk}),
                                    {'renewal_date': date_in_past})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'renewal_date', 'Invalid date - renewal in past')

    def test_form_invalid_renewal_date_future(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        
        invalid_date_in_future = datetime.date.today() + datetime.timedelta(weeks=5)
        response = self.client.post(reverse('renew-ticket-librarian', kwargs={'pk': self.test_task1.pk}),
                                    {'renewal_date': invalid_date_in_future})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'renewal_date', 'Invalid date - renewal more than 4 weeks ahead')

    def test_redirects_to_all_borrowed_ticket_list_on_success(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        valid_date_in_future = datetime.date.today() + datetime.timedelta(weeks=2)
        response = self.client.post(reverse('renew-ticket-librarian', kwargs={'pk': self.test_task1.pk}),
                                    {'renewal_date': valid_date_in_future})
        self.assertRedirects(response, reverse('all-borrowed'))

    def test_HTTP404_for_invalid_ticket_if_logged_in(self):
        import uuid
        test_uid = uuid.uuid4()  # unlikely UID to match our task!
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('renew-ticket-librarian', kwargs={'pk': test_uid}))
        self.assertEqual(response.status_code, 404)


class ClientCreateViewTest(TestCase):
    """Test case for the ClientCreate view (Created as Challenge)."""

    def setUp(self):
        # Create a user
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')

        test_user1.save()
        test_user2.save()

        permission = Permission.objects.get(name='Set ticket as returned')
        test_user2.user_permissions.add(permission)
        test_user2.save()

        # Create a ticket
        test_author = Client.objects.create(first_name='John', last_name='Smith')

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('author_create'))
        self.assertRedirects(response, '/accounts/login/?next=/catalog/client/create/')

    def test_redirect_if_logged_in_but_not_correct_permission(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('author_create'))
        self.assertEqual(response.status_code, 403)

    def test_logged_in_with_permission(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('author_create'))
        self.assertEqual(response.status_code, 200)

    def test_uses_correct_template(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('author_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/client_form.html')

    #def test_form_date_of_death_initially_set_to_expected_date(self):
       # login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        #response = self.client.get(reverse('author_create'))
        #self.assertEqual(response.status_code, 200)

       # expected_initial_date = datetime.date(2018, 1, 5)
       # response_date = response.context['form'].initial['date_of_death']
        #response_date = datetime.datetime.strptime(response_date, "%d/%m/%Y").date()
       # self.assertEqual(response_date, expected_initial_date)

    def test_redirects_to_detail_view_on_success(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.post(reverse('author_create'),
                                    {'first_name': 'Christian Name', 'last_name': 'Surname'})
        # Manually check redirect because we don't know what client was created
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/catalog/client/'))
