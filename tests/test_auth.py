import os
import unittest
import tempfile
from database.db_manager import DatabaseManager
from services.auth_service import AuthService

class TestAuthService(unittest.TestCase):
    def setUp(self):
        self.temp_db_fd, self.temp_db_path = tempfile.mkstemp(suffix=".db")
        DatabaseManager._instance = None
        self.db = DatabaseManager(self.temp_db_path)
        self.auth_service = AuthService(self.db)

    def tearDown(self):
        os.close(self.temp_db_fd)
        if os.path.exists(self.temp_db_path):
            os.remove(self.temp_db_path)
        DatabaseManager._instance = None

    def test_default_admin_login(self):
        # Default admin is 'admin' / '123456'
        ok, msg = self.auth_service.login("admin", "123456")
        self.assertTrue(ok)
        self.assertIn("thành công", msg.lower())

        # Wrong password
        ok, msg = self.auth_service.login("admin", "wrongpass")
        self.assertFalse(ok)

        # Non-existing user
        ok, msg = self.auth_service.login("unknown_user", "123456")
        self.assertFalse(ok)

    def test_register_validation(self):
        # Empty username
        ok, msg = self.auth_service.register("", "pass123", "pass123")
        self.assertFalse(ok)

        # Short username (< 3 chars)
        ok, msg = self.auth_service.register("ab", "pass123", "pass123")
        self.assertFalse(ok)

        # Password mismatch
        ok, msg = self.auth_service.register("newuser", "pass123", "pass456")
        self.assertFalse(ok)

        # Duplicate username with existing 'admin'
        ok, msg = self.auth_service.register("admin", "pass123", "pass123")
        self.assertFalse(ok)
        self.assertIn("đã tồn tại", msg)

    def test_register_and_login_success(self):
        # Register new user
        ok, msg = self.auth_service.register("manager1", "mysecret", "mysecret")
        self.assertTrue(ok)

        # Login with new user
        ok, msg = self.auth_service.login("manager1", "mysecret")
        self.assertTrue(ok)
        self.assertIn("thành công", msg.lower())

        # Login with wrong password for new user
        ok, msg = self.auth_service.login("manager1", "wrongsecret")
        self.assertFalse(ok)

if __name__ == "__main__":
    unittest.main()
