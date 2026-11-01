import tkinter as tk
from tkinter import ttk

class Theme:
    # --- PALETTE PHỐI MÀU HIỆN ĐẠI (ROYAL SAPPHIRE & SLATE) ---
    PRIMARY = "#2563EB"          # Royal Blue chủ đạo
    PRIMARY_HOVER = "#1D4ED8"
    PRIMARY_LIGHT = "#EFF6FF"    # Xanh dương pastel
    PRIMARY_DARK = "#1E40AF"

    SECONDARY = "#475569"        # Slate xám khói
    SECONDARY_LIGHT = "#F1F5F9"

    SUCCESS = "#059669"          # Xanh ngọc Emerald
    SUCCESS_HOVER = "#047857"
    SUCCESS_LIGHT = "#ECFDF5"

    WARNING = "#D97706"          # Vàng cam Amber
    WARNING_LIGHT = "#FFFBEB"

    DANGER = "#DC2626"           # Đỏ Crimson
    DANGER_HOVER = "#B91C1C"
    DANGER_LIGHT = "#FEF2F2"

    INFO = "#0284C7"             # Xanh biển Sky
    INFO_LIGHT = "#F0F9FF"

    PURPLE = "#7C3AED"           # Tím Violet
    PURPLE_LIGHT = "#F5F3FF"

    TEAL = "#0D9488"             # Xanh Teal
    TEAL_LIGHT = "#F0FDFA"

    # Neutrals & Layout
    SIDEBAR_BG = "#0F172A"       # Slate 900 huyền bí
    SIDEBAR_ITEM = "#1E293B"     # Slate 800
    SIDEBAR_HOVER = "#334155"    # Slate 700
    SIDEBAR_ACTIVE = "#2563EB"   # Active pill xanh dương
    SIDEBAR_TEXT = "#E2E8F0"
    SIDEBAR_MUTED = "#94A3B8"

    BG_MAIN = "#F1F5F9"          # Nền canvas xám nhẹ Slate-100 tạo chiều sâu nổi khối
    SURFACE = "#FFFFFF"          # Thẻ Card trắng tinh khiết
    SURFACE_ALT = "#F8FAFC"      # Hàng bảng xen kẽ
    BORDER = "#CBD5E1"           # Viền card sắc nét, thanh thoát
    BORDER_LIGHT = "#E2E8F0"

    TEXT_MAIN = "#0F172A"        # Màu chữ chính Slate 900
    TEXT_MUTED = "#64748B"       # Màu chữ phụ Slate 500
    TEXT_WHITE = "#FFFFFF"

    # Fonts
    FONT_BRAND = ("Helvetica Neue", 16, "bold")
    FONT_TITLE = ("Helvetica Neue", 15, "bold")
    FONT_HEADER = ("Helvetica Neue", 13, "bold")
    FONT_SUBTITLE = ("Helvetica Neue", 11, "bold")
    FONT_BODY = ("Helvetica Neue", 11)
    FONT_BODY_BOLD = ("Helvetica Neue", 11, "bold")
    FONT_SMALL = ("Helvetica Neue", 10)
    FONT_SMALL_BOLD = ("Helvetica Neue", 10, "bold")
    FONT_STAT_NUM = ("Helvetica Neue", 22, "bold")

    @classmethod
    def apply_theme(cls, root: tk.Tk):
        root.configure(bg=cls.BG_MAIN)
        style = ttk.Style(root)

        available_themes = style.theme_names()
        if "clam" in available_themes:
            style.theme_use("clam")

        # Treeview (Bảng dữ liệu tiêu chuẩn cao cấp)
        style.configure(
            "Treeview",
            background=cls.SURFACE,
            foreground=cls.TEXT_MAIN,
            fieldbackground=cls.SURFACE,
            font=cls.FONT_BODY,
            rowheight=34,
            borderwidth=0
        )
        style.map(
            "Treeview",
            background=[("selected", "#DBEAFE")],
            foreground=[("selected", "#1E40AF")]
        )
        
        # Tiêu đề bảng màu Navy đậm chuyên nghiệp
        style.configure(
            "Treeview.Heading",
            background="#1E293B",
            foreground="#FFFFFF",
            font=cls.FONT_SUBTITLE,
            padding=(10, 9),
            relief="flat"
        )
        style.map(
            "Treeview.Heading",
            background=[("active", "#334155")],
            foreground=[("active", "#FFFFFF")]
        )

        # Buttons chuẩn hóa màu sắc
        # 1. Primary Button (Xanh dương)
        style.configure(
            "Primary.TButton",
            background=cls.PRIMARY,
            foreground=cls.TEXT_WHITE,
            font=cls.FONT_BODY_BOLD,
            padding=(14, 7),
            borderwidth=0,
            focuscolor=cls.PRIMARY
        )
        style.map(
            "Primary.TButton",
            background=[("active", cls.PRIMARY_HOVER), ("pressed", cls.PRIMARY_DARK)]
        )

        # 2. Success Button (Xanh lục ngọc)
        style.configure(
            "Success.TButton",
            background=cls.SUCCESS,
            foreground=cls.TEXT_WHITE,
            font=cls.FONT_BODY_BOLD,
            padding=(14, 7),
            borderwidth=0
        )
        style.map(
            "Success.TButton",
            background=[("active", cls.SUCCESS_HOVER)]
        )

        # 3. Danger Button (Đỏ rực)
        style.configure(
            "Danger.TButton",
            background=cls.DANGER,
            foreground=cls.TEXT_WHITE,
            font=cls.FONT_BODY_BOLD,
            padding=(14, 7),
            borderwidth=0
        )
        style.map(
            "Danger.TButton",
            background=[("active", cls.DANGER_HOVER)]
        )

        # 4. Info Button (Xanh biển)
        style.configure(
            "Info.TButton",
            background=cls.INFO,
            foreground=cls.TEXT_WHITE,
            font=cls.FONT_BODY_BOLD,
            padding=(14, 7),
            borderwidth=0
        )
        style.map(
            "Info.TButton",
            background=[("active", "#0369A1")]
        )

        # 5. Secondary / Outline Button
        style.configure(
            "Secondary.TButton",
            background=cls.SECONDARY,
            foreground=cls.TEXT_WHITE,
            font=cls.FONT_BODY_BOLD,
            padding=(14, 7),
            borderwidth=0
        )
        style.map(
            "Secondary.TButton",
            background=[("active", "#334155")]
        )

        # Entries & Comboboxes
        style.configure(
            "TEntry",
            padding=6,
            fieldbackground=cls.SURFACE,
            foreground=cls.TEXT_MAIN,
            font=cls.FONT_BODY
        )
        style.configure(
            "TCombobox",
            padding=5,
            fieldbackground=cls.SURFACE,
            foreground=cls.TEXT_MAIN,
            font=cls.FONT_BODY
        )

        # Notebook (Các tab chuyển đổi)
        style.configure(
            "TNotebook",
            background=cls.BG_MAIN,
            borderwidth=0
        )
        style.configure(
            "TNotebook.Tab",
            padding=(20, 9),
            font=cls.FONT_SUBTITLE,
            background="#E2E8F0",
            foreground="#475569"
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", cls.PRIMARY)],
            foreground=[("selected", cls.TEXT_WHITE)]
        )
