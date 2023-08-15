"""
Command to wait for db to connect

"""

django.core.managment.base import BaseCommand

class Command(BaseCommand):
    """
    Command which waits for db

    """
    def handle(self, *args, **kwargs):
        pass