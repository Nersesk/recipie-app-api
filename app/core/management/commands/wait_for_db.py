"""
Command to wait for db to connect

"""
import time
from django.core.management import BaseCommand
from psycopg2 import OperationalError as Psycopg2Error
from django.db.utils import OperationalError


class Command(BaseCommand):
    """
    Command which waits for db

    """

    def handle(self, *args, **kwargs):
        self.stdout.write("Waiting for database ...")
        db_up = False
        while db_up is False:
            try:
                self.check(databases=['default', ])
                db_up = True
            except (Psycopg2Error, OperationalError):
                self.stdout.write("Database unavailable, waiting one second..")
                time.sleep(1)

        self.stdout.write((self.style.SUCCESS("DATABASE IS READY!!")))
