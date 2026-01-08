"""
This test file only focuses on the `insert_dummy_devices()` function in createcmdb.py.
It tests:
- That the correct number of dummy records are inserted
- That rollback happens when insertion fails

Unlike other tests that validate DB connection or input values,
this test isolates the data insertion logic only, making it unique.
"""

import unittest
from unittest import mock
from unittest.mock import MagicMock
import mysql.connector
from createcmdb import insert_dummy_devices, DUMMY_DEVICES

class TestInsertLogic(unittest.TestCase):

    def test_insert_dummy_devices_success(self):
        mock_cursor = MagicMock()
        mock_connection = MagicMock()
        mock_cursor.rowcount = len(DUMMY_DEVICES)

        inserted = insert_dummy_devices(mock_cursor, mock_connection, DUMMY_DEVICES)

        # Check that executemany was called with correct data (ignore exact SQL string)
        mock_cursor.executemany.assert_called_once()
        mock_cursor.executemany.assert_called_with(mock.ANY, DUMMY_DEVICES)

        mock_connection.commit.assert_called_once()
        self.assertEqual(inserted, len(DUMMY_DEVICES))

    def test_insert_dummy_devices_failure(self):
        mock_cursor = MagicMock()
        mock_connection = MagicMock()

        # Simulate MySQL error
        mock_cursor.executemany.side_effect = mysql.connector.Error("Insert failed")

        with self.assertRaises(mysql.connector.Error):
            insert_dummy_devices(mock_cursor, mock_connection, DUMMY_DEVICES)

        mock_connection.rollback.assert_called_once()

if __name__ == '__main__':
    unittest.main()
