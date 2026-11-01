import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from ui.theme import Theme
from database.db_manager import DatabaseManager
from services.auth_service import AuthService

class StudentPortalView(tk.Frame):
    def __init__(self, parent, ktx_service, username: str, on_logout_callback=None):
        super().__init__(parent, bg=Theme.BG_MAIN)
        self.ktx_service = ktx_service
        self.student_cmt = username  # Tài khoản đăng nhập chính là số CMT của sinh viên
        self.on_logout_callback = on_logout_callback
        self.db = DatabaseManager()

        self._build_ui()
        self.load_student_data()

    def _build_ui(self):
        # Top banner tiêu đề trang cá nhân sinh viên
        top_banner = tk.Frame(self, bg=Theme.SURFACE, padx=24, height=70, bd=1, relief=tk.SOLID)
        top_banner.pack(fill=tk.X, padx=20, pady=20)
        top_banner.pack_propagate(False)

        tk.Label(
            top_banner,
            text="🎓 CỔNG THÔNG TIN SINH VIÊN NỘI TRÚ",
            font=("Helvetica Neue", 14, "bold"),
            fg=Theme.PRIMARY,
            bg=Theme.SURFACE
        ).pack(side=tk.LEFT, pady=20)

        # Nút đổi mật khẩu & Đăng xuất
        btn_frame = tk.Frame(top_banner, bg=Theme.SURFACE)
        btn_frame.pack(side=tk.RIGHT, pady=15)

        btn_change_pw = tk.Button(
            btn_frame,
            text="🔑 Đổi Mật Khẩu",
            font=Theme.FONT_SMALL_BOLD,
            bg=Theme.PRIMARY,
            fg=Theme.TEXT_WHITE,
            relief=tk.FLAT,
            padx=12,
            pady=6,
            cursor="hand2",
            command=self.change_password
        )
        btn_change_pw.pack(side=tk.LEFT, padx=(0, 10))

        if self.on_logout_callback:
            btn_logout = tk.Button(
                btn_frame,
                text="🚪 Đăng Xuất",
                font=Theme.FONT_SMALL_BOLD,
                bg="#EF4444",
                fg=Theme.TEXT_WHITE,
                relief=tk.FLAT,
                padx=12,
                pady=6,
                cursor="hand2",
                command=self.on_logout_callback
            )
            btn_logout.pack(side=tk.LEFT)

        # Nội dung chính (chia làm 2 phần: Thông tin phòng & Bảng hóa đơn)
        content_frame = tk.Frame(self, bg=Theme.BG_MAIN)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        # --- Card 1: Thông tin cá nhân & Phòng trọ ---
        info_card = tk.LabelFrame(content_frame, text=" 🛏️ Trạng Thái Phòng KTX Hiện Tại ", font=Theme.FONT_BODY_BOLD, bg=Theme.SURFACE, fg=Theme.TEXT_MAIN, padx=16, pady=16)
        info_card.pack(fill=tk.X, pady=(0, 16))

        self.lbl_info_sv = tk.Label(info_card, text="Đang tải thông tin sinh viên...", font=Theme.FONT_BODY, bg=Theme.SURFACE, fg=Theme.TEXT_MAIN, justify=tk.LEFT)
        self.lbl_info_sv.pack(anchor="w")

        # --- Card 2: Danh sách hóa đơn dạng bảng (Treeview) ---
        invoice_card = tk.LabelFrame(content_frame, text=" 🧾 Lịch Sử & Trạng Thái Hóa Đơn ", font=Theme.FONT_BODY_BOLD, bg=Theme.SURFACE, fg=Theme.TEXT_MAIN, padx=16, pady=16)
        invoice_card.pack(fill=tk.BOTH, expand=True)

        # Tạo khung chứa bảng và thanh cuộn
        table_container = tk.Frame(invoice_card, bg=Theme.SURFACE)
        table_container.pack(fill=tk.BOTH, expand=True, pady=5)

        self.columns = ("MaHD", "KyThu", "TienPhong", "TienDV", "TongTien", "TrangThai")
        self.invoice_tree = ttk.Treeview(table_container, columns=self.columns, show="headings", selectmode="browse")
        
        # Đặt tiêu đề cột
        self.invoice_tree.heading("MaHD", text="Mã HĐ")
        self.invoice_tree.heading("KyThu", text="Kỳ Thu")
        self.invoice_tree.heading("TienPhong", text="Tiền Phòng")
        self.invoice_tree.heading("TienDV", text="Tiền Dịch Vụ")
        self.invoice_tree.heading("TongTien", text="Tổng Tiền")
        self.invoice_tree.heading("TrangThai", text="Trạng Thái")

        # Định dạng chiều rộng và căn lề cho các cột
        self.invoice_tree.column("MaHD", width=80, anchor="center")
        self.invoice_tree.column("KyThu", width=120, anchor="center")
        self.invoice_tree.column("TienPhong", width=140, anchor="center")
        self.invoice_tree.column("TienDV", width=140, anchor="center")
        self.invoice_tree.column("TongTien", width=140, anchor="center")
        self.invoice_tree.column("TrangThai", width=150, anchor="center")

        # Thanh cuộn dọc cho bảng
        scrollbar = ttk.Scrollbar(table_container, orient=tk.VERTICAL, command=self.invoice_tree.yview)
        self.invoice_tree.configure(yscrollcommand=scrollbar.set)

        self.invoice_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def load_student_data(self):
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                # Lấy thông tin sinh viên dựa vào số CMT (username)
                cursor.execute("""
                    SELECT sv.MaSV, sv.SoCMT, sv.NgaySinh, sv.Lop, sv.QueQuan, 
                           dk.SoPhong, p.LoaiPhong, p.DonGia 
                    FROM SINHVIEN sv
                    LEFT JOIN DANGKY_PHONG dk ON sv.MaSV = dk.MaSV AND (dk.NgayKetThuc IS NULL OR dk.NgayKetThuc >= '2026-10-01')
                    LEFT JOIN PHONG p ON dk.SoPhong = p.SoPhong
                    WHERE sv.SoCMT = ?
                """, (self.student_cmt,))
                sv_row = cursor.fetchone()

                if not sv_row:
                    self.lbl_info_sv.config(text="Không tìm thấy thông tin sinh viên khớp với số Căn cước này!")
                    return

                ma_sv = sv_row["MaSV"]
                so_phong = sv_row["SoPhong"] if sv_row["SoPhong"] else "Chưa xếp phòng"
                loai_phong = sv_row["LoaiPhong"] if sv_row["LoaiPhong"] else "N/A"
                don_gia = f"{sv_row['DonGia']:,.0f} đ" if sv_row["DonGia"] else "0 đ"

                info_text = (
                    f"• Mã sinh viên: {ma_sv}\n"
                    f"• Số Căn cước (Tài khoản): {sv_row['SoCMT']}\n"
                    f"• Lớp: {sv_row['Lop']}    |    Ngày sinh: {sv_row['NgaySinh']}    |    Quê quán: {sv_row['QueQuan']}\n"
                    f"------------------------------------------------------------------------------------\n"
                    f"• Phòng đang trọ: {so_phong} (Loại: {loai_phong})\n"
                    f"• Tiền phòng định mức: {don_gia}"
                )
                self.lbl_info_sv.config(text=info_text)

                # Lấy danh sách hóa đơn của sinh viên này
                cursor.execute("""
                    SELECT hd.MaHD, hd.Thang, hd.Nam, hd.TienPhong, hd.TienDichVu, hd.TongTien, hd.TrangThai
                    FROM HOADON hd
                    JOIN DANGKY_PHONG dk ON hd.MaDKPHONG = dk.MaDKPHONG
                    WHERE dk.MaSV = ?
                    ORDER BY hd.Nam DESC, hd.Thang DESC
                """, (ma_sv,))
                invoices = cursor.fetchall()

                # Xóa dữ liệu cũ trên bảng
                for item in self.invoice_tree.get_children():
                    self.invoice_tree.delete(item)

                # Đổ dữ liệu mới vào bảng Treeview
                for inv in invoices:
                    ky_thu = f"Tháng {inv['Thang']}/{inv['Nam']}"
                    tien_phong = f"{inv['TienPhong']:,.0f} đ"
                    tien_dv = f"{inv['TienDichVu']:,.0f} đ"
                    tong_tien = f"{inv['TongTien']:,.0f} đ"
                    trang_thai = inv['TrangThai']

                    self.invoice_tree.insert("", tk.END, values=(
                        inv['MaHD'], ky_thu, tien_phong, tien_dv, tong_tien, trang_thai
                    ))

        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải dữ liệu: {str(e)}", parent=self)

    def change_password(self):
        new_pw = simpledialog.askstring("Đổi mật khẩu", "Nhập mật khẩu mới (tối thiểu 4 ký tự):", show="*", parent=self)
        if new_pw is None:
            return
        if len(new_pw.strip()) < 4:
            messagebox.showwarning("Cảnh báo", "Mật khẩu mới phải có ít nhất 4 ký tự!", parent=self)
            return

        try:
            hashed = AuthService.hash_password(new_pw.strip())
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM admins WHERE username = ?", (self.student_cmt,))
                row = cursor.fetchone()
                if row:
                    cursor.execute("UPDATE admins SET password = ? WHERE username = ?", (hashed, self.student_cmt))
                else:
                    cursor.execute("INSERT INTO admins (username, password, role) VALUES (?, ?, ?)", (self.student_cmt, hashed, "student"))
                conn.commit()
            messagebox.showinfo("Thành công", "Đổi mật khẩu thành công!", parent=self)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể đổi mật khẩu: {str(e)}", parent=self)

    def reload_data(self):
        self.load_student_data()