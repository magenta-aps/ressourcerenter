from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group


class Command(BaseCommand):
    help = 'Create admin user'

    def handle(self, *args, **options):
        if settings.DEBUG is False:
            print('DEBUG needs to be True (dev-environment)')
            return

        User = get_user_model()

        administration_group, _ = Group.objects.get_or_create(name='administration')
        statistik_group, _ = Group.objects.get_or_create(name='statistik')

        admin_user, _ = User.objects.get_or_create(username='admin')
        admin_user.set_password('admin')
        admin_user.groups.add(administration_group, statistik_group)
        admin_user.save()

        statistik_user, _ = User.objects.get_or_create(username='statistik')
        statistik_user.set_password('statistik')
        statistik_user.groups.add(statistik_group)
        statistik_user.save()
