import tkinter as tk
from ui.views.login_view import LoginWindow
from ui.main_window import MainWindow
from ui.views.student_portal_view import StudentPortalView  # Nhớ import view sinh viên vừa tạo
from services.ktx_service import KTXService
from database.db_manager import DatabaseManager

def handle_login_success(username, role):
    db = DatabaseManager()
    ktx_service = KTXService(db)

    if role == "student":
        # === NẾU LÀ SINH VIÊN ĐĂNG NHẬP ===
        root = tk.Tk()
        root.title(f"Cổng Thông Tin Sinh Viên - {username}")
        root.geometry("1000x650")
        
        def logout():
            root.destroy()
            main() # Khi bấm đăng xuất sẽ quay lại màn hình Login

        # Gọi giao diện trang cá nhân sinh viên (Truyền số CMT của sinh viên làm username)
        app = StudentPortalView(root, ktx_service, username, on_logout_callback=logout)
        app.pack(fill=tk.BOTH, expand=True)
        root.mainloop()
        
    else:
        # === NẾU LÀ ADMIN HOẶC MANAGER ĐĂNG NHẬP ===
        # Mở giao diện quản trị đầy đủ như cũ
        app = MainWindow(username=username, role=role)
        app.mainloop()

def main():
    # Khởi chạy màn hình đăng nhập
    login_win = LoginWindow(on_login_success=handle_login_success)
    login_win.run()

if __name__ == "__main__":
    main()