import tkinter as tk
from tkinter import messagebox
from services.auth_service import AuthService
from ui.theme import Theme

class LoginWindow:
    def __init__(self, on_login_success):
        self.on_login_success = on_login_success
        self.auth_service = AuthService()

        self.root = tk.Tk()
        self.root.title("Hệ Thống Quản Lý Ký Túc Xá Sinh Viên - Đăng Nhập")
        self.root.configure(bg=Theme.BG_MAIN)
        self.root.resizable(False, False)

        # Căn giữa màn hình kích thước gọn gàng hơn vì bỏ đăng ký (420x450)
        self.window_width = 420
        self.window_height = 450
        self.center_window(self.window_width, self.window_height)

        # Container chính
        self.main_frame = tk.Frame(self.root, bg=Theme.BG_MAIN)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=24, pady=24)

        # Khởi chạy form đăng nhập
        self.show_login_form()

    def center_window(self, width, height):
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - width) // 2
        y = (sh - height) // 2
        self.root.geometry(f"{width}x{height}+{max(0, x)}+{max(0, y)}")

    def _clear_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    # =========================================================================
    # FORM ĐĂNG NHẬP
    # =========================================================================
    def show_login_form(self):
        self._clear_frame()

        # Thẻ Card chứa toàn bộ giao diện
        card = tk.Frame(self.main_frame, bg=Theme.SURFACE, bd=1, relief=tk.SOLID)
        card.pack(fill=tk.BOTH, expand=True)

        # Header banner màu xanh Navy phối Royal Blue
        header = tk.Frame(card, bg=Theme.SIDEBAR_BG, padx=20, pady=18)
        header.pack(fill=tk.X)

        lbl_icon = tk.Label(header, text="🏛️", font=("Segoe UI Emoji", 26), bg=Theme.SIDEBAR_BG)
        lbl_icon.pack()

        lbl_brand = tk.Label(
            header,
            text="HỆ THỐNG QUẢN LÝ KTX",
            font=("Helvetica Neue", 13, "bold"),
            fg="#93C5FD",
            bg=Theme.SIDEBAR_BG
        )
        lbl_brand.pack(pady=(4, 2))

        lbl_sub = tk.Label(
            header,
            text="Cổng Xác Thực Quản Trị Viên",
            font=("Helvetica Neue", 10),
            fg=Theme.SIDEBAR_MUTED,
            bg=Theme.SIDEBAR_BG
        )
        lbl_sub.pack()

        # Body chứa các ô nhập
        body = tk.Frame(card, bg=Theme.SURFACE, padx=26, pady=20)
        body.pack(fill=tk.BOTH, expand=True)

        # Username
        tk.Label(
            body,
            text="👤 Tên đăng nhập:",
            font=Theme.FONT_BODY_BOLD,
            bg=Theme.SURFACE,
            fg=Theme.TEXT_MAIN
        ).pack(anchor="w", pady=(0, 5))

        self.txt_login_user = tk.Entry(
            body,
            font=Theme.FONT_BODY,
            bd=1,
            relief=tk.SOLID,
            highlightthickness=1,
            highlightcolor=Theme.PRIMARY,
            bg=Theme.SURFACE_ALT
        )
        self.txt_login_user.pack(fill=tk.X, ipady=5, pady=(0, 14))

        # Password
        tk.Label(
            body,
            text="🔒 Mật khẩu:",
            font=Theme.FONT_BODY_BOLD,
            bg=Theme.SURFACE,
            fg=Theme.TEXT_MAIN
        ).pack(anchor="w", pady=(0, 5))

        self.txt_login_pass = tk.Entry(
            body,
            show="•",
            font=Theme.FONT_BODY,
            bd=1,
            relief=tk.SOLID,
            highlightthickness=1,
            highlightcolor=Theme.PRIMARY,
            bg=Theme.SURFACE_ALT
        )
        self.txt_login_pass.pack(fill=tk.X, ipady=5, pady=(0, 18))

        # Enter key event
        self.txt_login_user.bind("<Return>", lambda e: self.do_login())
        self.txt_login_pass.bind("<Return>", lambda e: self.do_login())

        # Nút Đăng nhập (Màu Royal Blue nổi bật)
        btn_login = tk.Button(
            body,
            text="Đăng Nhập Hệ Thống  →",
            bg=Theme.PRIMARY,
            fg=Theme.TEXT_WHITE,
            activebackground=Theme.PRIMARY_HOVER,
            activeforeground=Theme.TEXT_WHITE,
            font=Theme.FONT_BODY_BOLD,
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            pady=8,
            command=self.do_login
        )
        btn_login.pack(fill=tk.X, pady=(0, 14))

        # Footer badge
        footer = tk.Label(
            body,
            text="🔒 Bảo mật SHA-256 | SQLite v3 QL_KTX",
            font=("Helvetica Neue", 9),
            fg=Theme.TEXT_MUTED,
            bg=Theme.SURFACE
        )
        footer.pack(side=tk.BOTTOM, pady=(12, 0))

        self.txt_login_user.focus()

    def do_login(self):
        username = self.txt_login_user.get().strip()
        password = self.txt_login_pass.get()

        # Đổi thành nhận 3 giá trị: ok, msg, role
        ok, msg, role = self.auth_service.login(username, password) 
        if ok:
            messagebox.showinfo("Đăng nhập thành công", f"Chào mừng bạn quay trở lại!", parent=self.root)
            self.root.destroy()
            # Truyền thêm role vào callback để main.py nhận diện mở đúng giao diện (Admin hay Sinh viên)
            self.on_login_success(username, role)
        else:
            messagebox.showerror("Đăng nhập thất bại", msg, parent=self.root)

    def run(self):
        self.root.mainloop()