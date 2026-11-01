import tkinter as tk
from tkinter import messagebox
from database.db_manager import DatabaseManager
from services.ktx_service import KTXService
from ui.theme import Theme
from ui.views.ktx_views import (
    KTXDashboardView,
    KTXSinhVienView,
    KTXPhongView,
    KTXHoaDonDichVuView,
    KTXParkingView,
    KTXVisitorsView
)
from ui.views.account_view import AccountView
from ui.views.report_view import KTXReportView

class MainWindow(tk.Tk):
    def __init__(self, username="admin", role="admin"):
        super().__init__()
        self.current_username = username
        self.current_role = role

        self.title("Hệ Thống Quản Lý Ký Túc Xá Sinh Viên - Dormitory ERP")
        self.geometry("1280x820")
        self.minsize(1080, 720)
        self.configure(bg=Theme.BG_MAIN)

        # Center on screen
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        w = 1280
        h = 820
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.geometry(f"{w}x{h}+{max(0, x)}+{max(0, y)}")

        # Services
        self.db = DatabaseManager()
        self.ktx_service = KTXService(self.db)

        # Theme
        Theme.apply_theme(self)

        self.current_key = "dashboard"
        self._build_layout()
        self._switch_view("dashboard")

    def _build_layout(self):
        # 1. Sidebar bên trái
        self.sidebar = tk.Frame(self, bg=Theme.SIDEBAR_BG, width=260)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        # 2. Vùng làm việc chính bên phải (gồm Topbar + Content)
        self.right_container = tk.Frame(self, bg=Theme.BG_MAIN)
        self.right_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self._build_sidebar()
        self._build_topbar()
        self._build_views()

    def _build_sidebar(self):
        # Brand box
        brand_frame = tk.Frame(self.sidebar, bg=Theme.SIDEBAR_BG, padx=20, pady=22)
        brand_frame.pack(fill=tk.X)

        header_box = tk.Frame(brand_frame, bg=Theme.SIDEBAR_BG)
        header_box.pack(anchor="w")

        icon_badge = tk.Label(
            header_box,
            text="🏛️",
            font=("Segoe UI Emoji", 20),
            bg="#1E293B",
            padx=8,
            pady=4
        )
        icon_badge.pack(side=tk.LEFT, padx=(0, 10))

        title_box = tk.Frame(header_box, bg=Theme.SIDEBAR_BG)
        title_box.pack(side=tk.LEFT)

        tk.Label(
            title_box,
            text="QL_KTX PRO",
            font=("Helvetica Neue", 14, "bold"),
            fg="#60A5FA",
            bg=Theme.SIDEBAR_BG
        ).pack(anchor="w")

        tk.Label(
            title_box,
            text="Hệ Thống Quản Lý KTX",
            font=("Helvetica Neue", 9),
            fg=Theme.SIDEBAR_MUTED,
            bg=Theme.SIDEBAR_BG
        ).pack(anchor="w")

        # Divider
        tk.Frame(self.sidebar, bg="#1E293B", height=1).pack(fill=tk.X, padx=16, pady=(10, 14))

        # Navigation menu
        self.nav_buttons = {}
        self.nav_labels = {
            "dashboard": "📊  Tổng quan Dashboard",
            "sinhvien": "👥  Hồ sơ Sinh viên",
            "phong": "🛌  Phòng & Xếp phòng",
            "hoadon": "🧾  Hoá đơn & Dịch vụ",
            "xe": "🛵  Quản lý Xe KTX",
            "khach": "🧑‍🤝‍🧑  Khách đến thăm",
            "report": "📑  4 Báo Cáo Thống kê",
        }

        # Nếu là tài khoản Admin thì thêm mục Quản lý Tài khoản ngay dưới Báo Cáo Thống kê
        if self.current_role == "admin":
            self.nav_labels["account"] = "🔐  Quản lý Tài khoản"

        menu_label = tk.Label(
            self.sidebar,
            text="DANH MỤC QUẢN LÝ",
            font=("Helvetica Neue", 8, "bold"),
            fg="#64748B",
            bg=Theme.SIDEBAR_BG
        )
        menu_label.pack(anchor="w", padx=20, pady=(0, 8))

        for key, label in self.nav_labels.items():
            btn = tk.Button(
                self.sidebar,
                text=f"  {label}",
                font=("Helvetica Neue", 11),
                fg=Theme.SIDEBAR_TEXT,
                bg=Theme.SIDEBAR_BG,
                activebackground=Theme.SIDEBAR_ITEM,
                activeforeground=Theme.TEXT_WHITE,
                bd=0,
                padx=16,
                pady=10,
                anchor="w",
                cursor="hand2",
                command=lambda k=key: self._switch_view(k)
            )
            btn.pack(fill=tk.X, pady=2, padx=10)
            
            # Hover effect
            btn.bind("<Enter>", lambda e, b=btn, k=key: self._on_nav_hover(b, k, True))
            btn.bind("<Leave>", lambda e, b=btn, k=key: self._on_nav_hover(b, k, False))
            
            self.nav_buttons[key] = btn

        # Bottom info card
        bottom = tk.Frame(self.sidebar, bg=Theme.SIDEBAR_BG, padx=16, pady=16)
        bottom.pack(side=tk.BOTTOM, fill=tk.X)

        badge = tk.Frame(bottom, bg="#1E293B", padx=12, pady=10)
        badge.pack(fill=tk.X, pady=(0, 10))

        tk.Label(
            badge,
            text="● SQLite 10 Bảng + 2 Triggers",
            font=("Helvetica Neue", 9, "bold"),
            fg="#34D399",
            bg="#1E293B"
        ).pack(anchor="w")

        tk.Label(
            badge,
            text="Phiên bản 2.5 - Giao diện Đồ họa",
            font=("Helvetica Neue", 8),
            fg="#94A3B8",
            bg="#1E293B"
        ).pack(anchor="w", pady=(2, 0))

        btn_reset = tk.Button(
            bottom,
            text="↻ Khôi phục dữ liệu mẫu (33 SV)",
            font=("Helvetica Neue", 9),
            fg="#94A3B8",
            bg=Theme.SIDEBAR_BG,
            activeforeground="#EF4444",
            activebackground=Theme.SIDEBAR_BG,
            bd=0,
            cursor="hand2",
            command=self._reset_db_prompt
        )
        btn_reset.pack(anchor="w")

    def _on_nav_hover(self, btn, key, is_hover):
        if key != self.current_key:
            btn.configure(
                bg=Theme.SIDEBAR_ITEM if is_hover else Theme.SIDEBAR_BG,
                fg=Theme.TEXT_WHITE if is_hover else Theme.SIDEBAR_TEXT
            )

    def _build_topbar(self):
        # Top Header Bar trên vùng làm việc chính
        self.topbar = tk.Frame(self.right_container, bg=Theme.SURFACE, height=58, bd=1, relief=tk.SOLID)
        self.topbar.pack(side=tk.TOP, fill=tk.X)
        self.topbar.pack_propagate(False)

        # Breadcrumbs bên trái
        left_top = tk.Frame(self.topbar, bg=Theme.SURFACE, padx=20)
        left_top.pack(side=tk.LEFT, fill=tk.Y)

        self.lbl_breadcrumb = tk.Label(
            left_top,
            text="📍 Trang chủ  /  Tổng quan Dashboard",
            font=("Helvetica Neue", 11, "bold"),
            fg=Theme.TEXT_MAIN,
            bg=Theme.SURFACE
        )
        self.lbl_breadcrumb.pack(side=tk.LEFT, pady=16)

        # Thông tin user & Nút tác vụ bên phải
        right_top = tk.Frame(self.topbar, bg=Theme.SURFACE, padx=20)
        right_top.pack(side=tk.RIGHT, fill=tk.Y)

        role_display = "🟢 Quản trị viên (Admin)" if self.current_role == "admin" else "👤 Quản lý KTX"
        user_badge = tk.Frame(right_top, bg="#EFF6FF", padx=10, pady=5, bd=1, relief=tk.SOLID)
        user_badge.pack(side=tk.LEFT, pady=12, padx=(0, 10))

        tk.Label(
            user_badge,
            text=role_display,
            font=("Helvetica Neue", 10, "bold"),
            fg=Theme.PRIMARY,
            bg="#EFF6FF"
        ).pack(side=tk.LEFT)

        btn_refresh_top = tk.Button(
            right_top,
            text="🔄 Làm mới",
            font=Theme.FONT_SMALL_BOLD,
            bg="#F1F5F9",
            fg=Theme.TEXT_MAIN,
            relief=tk.FLAT,
            bd=0,
            padx=10,
            pady=5,
            cursor="hand2",
            command=self._refresh_current_view
        )
        btn_refresh_top.pack(side=tk.LEFT, pady=12)

    def _build_views(self):
        # Container cho các view
        self.content_container = tk.Frame(self.right_container, bg=Theme.BG_MAIN)
        self.content_container.pack(fill=tk.BOTH, expand=True)

        self.views = {
            "dashboard": KTXDashboardView(self.content_container, self.ktx_service, nav_callback=self._switch_view),
            "sinhvien": KTXSinhVienView(self.content_container, self.ktx_service),
            "phong": KTXPhongView(self.content_container, self.ktx_service),
            "hoadon": KTXHoaDonDichVuView(self.content_container, self.ktx_service),
            "xe": KTXParkingView(self.content_container, self.ktx_service),
            "khach": KTXVisitorsView(self.content_container, self.ktx_service),
            "report": KTXReportView(self.content_container, self.ktx_service),
        }

        # Nếu là admin thì khởi tạo thêm AccountView
        if self.current_role == "admin":
            self.views["account"] = AccountView(self.content_container, self.current_username)

    def _switch_view(self, key: str):
        self.current_key = key

        # Cập nhật breadcrumb
        label_text = self.nav_labels.get(key, "Trang chủ")
        self.lbl_breadcrumb.configure(text=f"📍 Hệ thống  /  {label_text.strip()}")

        for k, v in self.views.items():
            if k == key:
                v.pack(fill=tk.BOTH, expand=True)
                if hasattr(v, "reload_data"):
                    v.reload_data()
                elif hasattr(v, "refresh"):
                    v.refresh()
            else:
                v.pack_forget()

        for k, btn in self.nav_buttons.items():
            if k == key:
                btn.configure(bg=Theme.PRIMARY, fg=Theme.TEXT_WHITE, font=("Helvetica Neue", 11, "bold"))
            else:
                btn.configure(bg=Theme.SIDEBAR_BG, fg=Theme.SIDEBAR_TEXT, font=("Helvetica Neue", 11))

    def _refresh_current_view(self):
        active_view = self.views.get(self.current_key)
        if active_view:
            if hasattr(active_view, "reload_data"):
                active_view.reload_data()
            elif hasattr(active_view, "refresh"):
                active_view.refresh()

    def _reset_db_prompt(self):
        ans = messagebox.askyesno(
            "Khôi phục CSDL mẫu",
            "Bạn có chắc muốn đặt lại cơ sở dữ liệu về trạng thái ban đầu?\nToàn bộ dữ liệu bạn tự thêm sẽ bị xoá.",
            parent=self
        )
        if ans:
            self.db.reset_database()
            messagebox.showinfo("Thành công", "Đã khởi tạo lại 10 bảng CSDL QL_KTX với đầy đủ 33 sinh viên và các triggers!", parent=self)
            self._switch_view("dashboard")