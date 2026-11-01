import hashlib
import re
from typing import Optional, Tuple
from database.db_manager import DatabaseManager
from database import queries

class AuthService:
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.db = db_manager or DatabaseManager()

    @staticmethod
    def hash_password(password: str) -> str:
        """Băm mật khẩu bằng thuật toán SHA-256"""
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def verify_password(self, stored_pass: str, input_pass: str) -> bool:
        """
        Kiểm tra mật khẩu nhập vào có khớp với mật khẩu trong DB hay không.
        Hỗ trợ cả mật khẩu dạng plain text mặc định ('123456') và mật khẩu đã băm SHA-256.
        """
        if stored_pass == input_pass:
            return True
        return stored_pass == self.hash_password(input_pass)

    def login(self, username: str, password: str) -> Tuple[bool, str, str]:
        """
        Xác thực đăng nhập tài khoản. Trả về: (success, message, role)
        Hỗ trợ: admin, manager và sinh viên (username = SoCMT trong bảng SINHVIEN).
        """
        username = username.strip()
        if not username or not password:
            return False, "Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu.", ""

        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                # 1. Kiểm tra trong bảng admins trước (Admin hoặc Manager)
                cursor.execute(queries.SQL_GET_ADMIN_BY_USERNAME, (username,))
                row = cursor.fetchone()

                if row:
                    stored_password = row["password"]
                    if not self.verify_password(stored_password, password):
                        return False, "Mật khẩu không chính xác.", ""
                    return True, "Đăng nhập thành công!", row["role"]

                # 2. Nếu không có trong admins, kiểm tra xem có phải là Sinh viên (SoCMT) không
                cursor.execute("SELECT SoCMT, MaSV FROM SINHVIEN WHERE SoCMT = ?", (username,))
                student_row = cursor.fetchone()

                if student_row:
                    # Kiểm tra xem sinh viên đã đổi mật khẩu và lưu trong bảng admins chưa
                    cursor.execute(queries.SQL_GET_ADMIN_BY_USERNAME, (username,))
                    admin_check = cursor.fetchone()

                    if admin_check:
                        if not self.verify_password(admin_check["password"], password):
                            return False, "Mật khẩu không chính xác.", ""
                    else:
                        # Tài khoản mặc định chưa đổi mật khẩu -> Mật khẩu là '123456'
                        if password != "123456":
                            return False, "Mật khẩu không chính xác (Mật khẩu mặc định là 123456).", ""

                    return True, "Đăng nhập thành công!", "student"

                return False, "Tài khoản hoặc Số Căn cước không tồn tại trong hệ thống.", ""
        except Exception as e:
            return False, f"Lỗi xác thực: {str(e)}", ""

    def get_all_accounts(self):
        """Lấy danh sách tất cả tài khoản quản trị"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, username, role FROM admins")
                return cursor.fetchall()
        except Exception:
            return []

    def create_account(self, current_user: str, username: str, password: str, role: str) -> Tuple[bool, str]:
        """Admin tạo tài khoản mới (có thể chọn role là admin hoặc manager)"""
        username = username.strip()
        if not username or not password:
            return False, "Vui lòng nhập đầy đủ thông tin."
        if len(password) < 4:
            return False, "Mật khẩu phải có ít nhất 4 ký tự."

        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(queries.SQL_GET_ADMIN_BY_USERNAME, (username,))
                if cursor.fetchone():
                    return False, f"Tài khoản '{username}' đã tồn tại."

                hashed = self.hash_password(password)
                cursor.execute(
                    "INSERT INTO admins (username, password, role) VALUES (?, ?, ?)",
                    (username, hashed, role)
                )
                conn.commit()
            return True, "Thêm tài khoản thành công!"
        except Exception as e:
            return False, f"Lỗi: {str(e)}"

    def update_account(self, current_user: str, target_id: int, new_username: str, new_role: str, new_password: str = "") -> Tuple[bool, str]:
        """Sửa tài khoản, chặn việc admin tự hạ quyền chính mình"""
        new_username = new_username.strip()
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                # Lấy thông tin tài khoản cần sửa
                cursor.execute("SELECT username, role FROM admins WHERE id = ?", (target_id,))
                target = cursor.fetchone()
                if not target:
                    return False, "Không tìm thấy tài khoản."

                target_username = target["username"]

                # Ràng buộc: Admin không được tự đổi quyền của chính mình thành manager
                if target_username == current_user and new_role != "admin":
                    return False, "Bạn không thể tự hạ quyền Admin của chính mình!"

                # Cập nhật thông tin cơ bản
                if new_password:
                    hashed = self.hash_password(new_password)
                    cursor.execute(
                        "UPDATE admins SET username = ?, role = ?, password = ? WHERE id = ?",
                        (new_username, new_role, hashed, target_id)
                    )
                else:
                    cursor.execute(
                        "UPDATE admins SET username = ?, role = ? WHERE id = ?",
                        (new_username, new_role, target_id)
                    )
                conn.commit()
            return True, "Cập nhật tài khoản thành công!"
        except Exception as e:
            return False, f"Lỗi: {str(e)}"

    def delete_account(self, current_user: str, target_id: int) -> Tuple[bool, str]:
        """Xóa tài khoản, chặn việc admin tự xóa chính mình"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT username FROM admins WHERE id = ?", (target_id,))
                target = cursor.fetchone()
                if not target:
                    return False, "Không tìm thấy tài khoản."

                if target["username"] == current_user:
                    return False, "Bạn không thể tự xóa tài khoản của chính mình!"

                cursor.execute("DELETE FROM admins WHERE id = ?", (target_id,))
                conn.commit()
            return True, "Xóa tài khoản thành công!"
        except Exception as e:
            return False, f"Lỗi: {str(e)}"