from unittest.mock import patch
from psycopg2 import OperationalError as Psycopg2Error
from django.db.utils import OperationalError
from django.core.management import call_command
from django.test import SimpleTestCase


@patch('core.management.commands.wait_for_db.Command.check')
class CommandTest(SimpleTestCase):
    """Test commands"""

    def test_db_for_ready(self, patched_check):
        """Test command to be setup correctly and case when db works"""
        patched_check.returned_value = True
        call_command("wait_for_db")
        patched_check.assert_called_once_with(databases=['default', ])

    @patch('time.sleep')
    def test_database_for_delay(self, patched_sleep, patched_check):
        """Testing db getting OperationErrors"""
        patched_check.side_effect = ([Psycopg2Error] * 2 +
                                     [OperationalError] * 3 + [True])
        call_command("wait_for_db")
        self.assertEqual(patched_check.call_count, 6)
        patched_check.assert_called_with(databases=['default', ])
