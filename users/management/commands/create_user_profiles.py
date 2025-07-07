from django.core.management.base import BaseCommand
from users.models import create_profiles_for_existing_users

class Command(BaseCommand):
    help = 'Creates user profiles for existing users'

    def handle(self, *args, **kwargs):
        create_profiles_for_existing_users()
        self.stdout.write(self.style.SUCCESS('Successfully created user profiles'))

