from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
import argparse
import getpass

from django.http import QueryDict

from assets.constants import ADMIN
from authentication.models import UserRole
from authentication.serializers import AccountSerializer


class PasswordPromptAction(argparse.Action):
    def __init__(self,
                 option_strings,
                 dest=None,
                 nargs=0,
                 default=None,
                 required=False,
                 type=None,
                 metavar=None,
                 help=None):
        super(PasswordPromptAction, self).__init__(
            option_strings=option_strings,
            dest=dest,
            nargs=nargs,
            default=default,
            required=required,
            metavar=metavar,
            type=type,
            help=help)

    def __call__(self, parser, args, values, option_string=None):
        password = getpass.getpass()
        setattr(args, self.dest, password)


class Command(BaseCommand):
    help = 'Creates an administrator.'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str)
        parser.add_argument('email', type=str)
        parser.add_argument('first_name', type=str)
        parser.add_argument('last_name', type=str)
        parser.add_argument('-p', dest='password', action=PasswordPromptAction, type=str, required=True)

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        first_name = options['first_name']
        last_name = options['last_name']
        password = options['password']
        # TODO: is_staff needed for admin panel?
        account_data = {'username': username, 'password': password, 'email': email, 'first_name': first_name,
                        'last_name': last_name, 'is_superuser': True}
        account_data_qd = QueryDict('', mutable=True)
        account_data_qd.update(account_data)
        serializer = AccountSerializer(data=account_data_qd)

        if serializer.is_valid():
            user = User.objects.create_user(**serializer.validated_data)
            UserRole.objects.create(name=ADMIN, user=user)
            self.stdout.write('Successfully created admin "%s"' % options['username'])
            return

        self.stdout.write('Invalid data!')
