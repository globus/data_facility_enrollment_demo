"""
Users are created when logging in through Python Social Auth. In this way, users are not typically
created the "normal" way on the command line, and it's easier to promote existing users instead.

Use this script to promote users.

Example: 

python manage.py add_super_user
    * Lists all available users in database and their staff status if they have one
python manage.py add_super_user --users mal@myuniversity.edu
    * Adds a user as a super user

Once a single user has super user status, they can tweak more fine-grained controls at /admin using
the Django UI instead.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Make a user a super user'

    def add_arguments(self, parser):
        parser.add_argument('--users', nargs='+', required=False)

    def handle(self, *args, **options):
        users = options.get('users')
        if users:
            for user in users:
                u = User.objects.filter(username=user).first()
                if not u:
                    self.stderr.write(f'User {user} does not exist!')
                    continue
                if u.is_staff and u.is_superuser:
                    self.stderr.write(f'User {u.username} is already a '
                                      f'superuser!')
                    continue
                u.is_staff = True
                u.is_superuser = True
                u.save()
                self.stdout.write(f'{u.username} is now a superuser')

        else:
            self.stderr.write('Users:')
            for user in User.objects.all():
                staff = '(staff)' if user.is_staff else ''
                superuser = '(superuser)' if user.is_superuser else ''
                self.stderr.write(f'\t* {user.username} {staff} {superuser}')
