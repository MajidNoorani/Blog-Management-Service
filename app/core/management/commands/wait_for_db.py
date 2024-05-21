"""Django command to wait for database to be avilable.
"""
import time
from django.core.management.base import BaseCommand
from psycopg2.errors import OperationalError as Psycopg2OpError
from django.db.utils import OperationalError


class Command(BaseCommand):
    """Django command to wait for database"""

    def handle(self, *args, **kwargs):
        """Entry Point for command"""
        # log a message to screen
        self.stdout.write("waiting for database ...")
        db_up = False
        while db_up is False:
            try:
                self.check(databases=['default'])
                db_up = True
            except (OperationalError, Psycopg2OpError):
                self.stdout.write("Database unavailable! waiting 1 second ...")
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS("Database available!"))