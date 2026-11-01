import tkinter as tk
from tkinter import ttk, messagebox
from services.auth_service import AuthService
from ui.theme import Theme

class AccountView(tk.Frame):
    def __init__(self, parent, current_username):
        super().__init__(parent, bg=Theme.BG_MAIN)
        self.auth_service = AuthService()
        self.current_username = current_username

        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        # Tiêu đề trang
        header_frame = tk.Frame(self, bg=Theme.BG_MAIN)
        header_frame.pack(fill=tk.X, padx=20, pady=15)

        lbl_title = tk.Label(
            header_frame,
            text="🔐 Quản Lý Tài Khoản Hệ Thống",
            font=("Helvetica Neue", 16, "bold"),
            bg=Theme.BG_MAIN,
            fg=Theme.TEXT_MAIN
        )
        lbl_title.pack(side=tk.LEFT)

        # Thanh công cụ (Nút Thêm, Sửa, Xóa, Làm mới)
        toolbar = tk.Frame(self, bg=Theme.BG_MAIN)
        toolbar.pack(fill=tk.X, padx=20, pady=(0, 15))

        btn_add = tk.Button(
            toolbar, text="➕ Thêm tài khoản", bg=Theme.SUCCESS, fg=Theme.TEXT_WHITE,
            font=Theme.FONT_BODY_BOLD, relief=tk.FLAT, padx=12, pady=6, cursor="hand2",
            command=self.open_add_dialog
        )
        btn_add.pack(side=tk.LEFT, padx=(0, 8))

        btn_edit = tk.Button(
            toolbar, text="✏️ Sửa thông tin", bg=Theme.PRIMARY, fg=Theme.TEXT_WHITE,
            font=Theme.FONT_BODY_BOLD, relief=tk.FLAT, padx=12, pady=6, cursor="hand2",
            command=self.open_edit_dialog
        )
        btn_edit.pack(side=tk.LEFT, padx=(0, 8))

        btn_delete = tk.Button(
            toolbar, text="🗑️ Xóa tài khoản", bg=Theme.DANGER, fg=Theme.TEXT_WHITE,
            font=Theme.FONT_BODY_BOLD, relief=tk.FLAT, padx=12, pady=6, cursor="hand2",
            command=self.delete_account
        )
        btn_delete.pack(side=tk.LEFT, padx=(0, 8))

        btn_refresh = tk.Button(
            toolbar, text="🔄 Làm mới", bg=Theme.SURFACE_ALT, fg=Theme.TEXT_MAIN,
            font=Theme.FONT_BODY_BOLD, relief=tk.SOLID, bd=1, padx=12, pady=5, cursor="hand2",
            command=self.load_data
        )
        btn_refresh.pack(side=tk.RIGHT)

        # Bảng hiển thị danh sách tài khoản (Treeview)
        table_frame = tk.Frame(self, bg=Theme.SURFACE, bd=1, relief=tk.SOLID)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        columns = ("id", "username", "role")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        
        self.tree.heading("id", text="ID")
        self.tree.heading("username", text="Tên Đăng Nhập")
        self.tree.heading("role", text="Vai Trò (Role)")

        self.tree.column("id", width=60, anchor="center")
        self.tree.column("username", width=250, anchor="w")
        self.tree.column("role", width=200, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def load_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        accounts = self.auth_service.get_all_accounts()
        for acc in accounts:
            # acc có dạng tuple hoặc row mapping: (id, username, role)
            role_display = "👑 Admin" if acc["role"] == "admin" else "👤 Quản lý KTX"
            self.tree.insert("", tk.END, values=(acc["id"], acc["username"], role_display))

    def open_add_dialog(self):
        self.show_account_modal(title="Thêm tài khoản mới", is_edit=False)

    def open_edit_dialog(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn tài khoản cần sửa!", parent=self)
            return
        
        item = self.tree.item(selected)
        acc_id, username, role_display = item["values"]
        role_val = "admin" if "Admin" in role_display else "manager"

        self.show_account_modal(title="Sửa thông tin tài khoản", is_edit=True, acc_id=acc_id, old_username=username, old_role=role_val)

    def show_account_modal(self, title, is_edit, acc_id=None, old_username="", old_role="manager"):
        modal = tk.Toplevel(self)
        modal.title(title)
        modal.geometry("380#420".replace("#", "x"))
        modal.configure(bg=Theme.BG_MAIN)
        modal.resizable(False, False)
        modal.grab_set() # Khóa cửa sổ chính cho đến khi tắt modal

        frame = tk.Frame(modal, bg=Theme.SURFACE, padx=20, pady=20, bd=1, relief=tk.SOLID)
        frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        tk.Label(frame, text="👤 Tên đăng nhập:", font=Theme.FONT_BODY_BOLD, bg=Theme.SURFACE, fg=Theme.TEXT_MAIN).pack(anchor="w", pady=(0, 4))
        txt_user = tk.Entry(frame, font=Theme.FONT_BODY, bg=Theme.SURFACE_ALT, bd=1, relief=tk.SOLID)
        txt_user.pack(fill=tk.X, ipady=4, pady=(0, 12))
        if old_username:
            txt_user.insert(0, old_username)

        tk.Label(frame, text="🛡️ Vai trò hệ thống:", font=Theme.FONT_BODY_BOLD, bg=Theme.SURFACE, fg=Theme.TEXT_MAIN).pack(anchor="w", pady=(0, 4))
        role_var = tk.StringVar(value=old_role)
        cb_role = ttk.Combobox(frame, textvariable=role_var, values=["admin", "manager"], state="readonly", font=Theme.FONT_BODY)
        cb_role.pack(fill=tk.X, ipady=3, pady=(0, 12))

        pwd_label_text = "🔒 Mật khẩu mới (Bỏ trống nếu không đổi):" if is_edit else "🔒 Mật khẩu:"
        tk.Label(frame, text=pwd_label_text, font=Theme.FONT_BODY_BOLD, bg=Theme.SURFACE, fg=Theme.TEXT_MAIN).pack(anchor="w", pady=(0, 4))
        txt_pass = tk.Entry(frame, show="•", font=Theme.FONT_BODY, bg=Theme.SURFACE_ALT, bd=1, relief=tk.SOLID)
        txt_pass.pack(fill=tk.X, ipady=4, pady=(0, 20))

        def on_save():
            username = txt_user.get().strip()
            role = role_var.get()
            password = txt_pass.get()

            if is_edit:
                ok, msg = self.auth_service.update_account(self.current_username, acc_id, username, role, password)
            else:
                if not password:
                    messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập mật khẩu cho tài khoản mới!", parent=modal)
                    return
                ok, msg = self.auth_service.create_account(self.current_username, username, password, role)

            if ok:
                messagebox.showinfo("Thành công", msg, parent=modal)
                modal.destroy()
                self.load_data()
            else:
                messagebox.showerror("Lỗi", msg, parent=modal)

        btn_save = tk.Button(frame, text="Lưu Thay Đổi ✓", bg=Theme.PRIMARY, fg=Theme.TEXT_WHITE, font=Theme.FONT_BODY_BOLD, relief=tk.FLAT, pady=8, cursor="hand2", command=on_save)
        btn_save.pack(fill=tk.X)

    def delete_account(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn tài khoản cần xóa!", parent=self)
            return

        item = self.tree.item(selected)
        acc_id, username, _ = item["values"]

        if messagebox.askyesno("Xác nhận xóa", f"Bạn có chắc chắn muốn xóa tài khoản '{username}' không?", parent=self):
            ok, msg = self.auth_service.delete_account(self.current_username, acc_id)
            if ok:
                messagebox.showinfo("Thành công", msg, parent=self)
                self.load_data()
            else:
                messagebox.showerror("Lỗi", msg, parent=self)