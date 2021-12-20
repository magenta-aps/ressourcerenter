from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Create admin user'

    def handle(self, *args, **options):
        if settings.DEBUG is False:
            print('DEBUG needs to be True (dev-environment)')
            return
        User = get_user_model()
        user, _ = User.objects.get_or_create(username='admin')
        user.set_password('admin')
        user.save()
