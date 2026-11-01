"""Ô nhập ngày có kiểm tra hợp lệ + nút 📅 mở lịch chọn ngày (chỉ dùng Tkinter)."""
import calendar
import tkinter as tk
from datetime import date
from tkinter import ttk, messagebox
from typing import Callable, Optional

from ui.theme import Theme
from utils.date_utils import (
    MAX_YEAR, MIN_YEAR, normalize_date_str, parse_date, validate_date_str,
)

_MONTHS = [f"Tháng {i}" for i in range(1, 13)]
_WEEKDAYS = ["T2", "T3", "T4", "T5", "T6", "T7", "CN"]
_ERROR_FG = "#c0392b"


class CalendarPopup(tk.Toplevel):
    """Cửa sổ lịch nhỏ: chọn tháng/năm ở trên, bấm vào ngày để chọn."""

    def __init__(self, owner: tk.Misc, initial: date, on_select: Callable[[date], None], anchor: Optional[tk.Widget] = None):
        super().__init__(owner)
        self._owner_top = owner.winfo_toplevel()
        self._on_select = on_select
        self._selected = initial
        self._view_year, self._view_month = initial.year, initial.month

        self.title("Chọn ngày")
        self.resizable(False, False)
        self.configure(bg=Theme.SURFACE)
        self.transient(self._owner_top)

        # --- Thanh điều hướng tháng / năm ---
        nav = tk.Frame(self, bg=Theme.SURFACE, padx=8, pady=8)
        nav.pack(fill=tk.X)
        ttk.Button(nav, text="◀", width=3, command=lambda: self._shift_month(-1)).pack(side=tk.LEFT)
        ttk.Button(nav, text="▶", width=3, command=lambda: self._shift_month(1)).pack(side=tk.RIGHT)

        mid = tk.Frame(nav, bg=Theme.SURFACE)
        mid.pack(side=tk.LEFT, expand=True)
        self.month_var = tk.StringVar(value=_MONTHS[self._view_month - 1])
        self.cb_month = ttk.Combobox(mid, textvariable=self.month_var, values=_MONTHS, state="readonly", width=9)
        self.cb_month.pack(side=tk.LEFT, padx=(0, 6))
        self.cb_month.bind("<<ComboboxSelected>>", lambda e: self._on_month_pick())
        self.year_var = tk.StringVar(value=str(self._view_year))
        self.sp_year = ttk.Spinbox(mid, from_=MIN_YEAR, to=MAX_YEAR, textvariable=self.year_var, width=6, command=self._on_year_pick)
        self.sp_year.pack(side=tk.LEFT)
        self.sp_year.bind("<Return>", lambda e: self._on_year_pick())
        self.sp_year.bind("<FocusOut>", lambda e: self._on_year_pick())

        # --- Lưới ngày ---
        self.grid_frame = tk.Frame(self, bg=Theme.SURFACE, padx=8)
        self.grid_frame.pack()

        # --- Chân: Hôm nay / Đóng ---
        foot = tk.Frame(self, bg=Theme.SURFACE, padx=8, pady=8)
        foot.pack(fill=tk.X)
        ttk.Button(foot, text="Hôm nay", command=lambda: self._pick(date.today())).pack(side=tk.LEFT)
        ttk.Button(foot, text="Đóng", command=self._close).pack(side=tk.RIGHT)

        self._render()
        self.bind("<Escape>", lambda e: self._close())
        self.protocol("WM_DELETE_WINDOW", self._close)

        # Đặt vị trí ngay dưới nút bấm
        self.update_idletasks()
        ref = anchor or owner
        x = ref.winfo_rootx()
        y = ref.winfo_rooty() + ref.winfo_height() + 4
        x = min(x, self.winfo_screenwidth() - self.winfo_reqwidth() - 10)
        y = min(y, self.winfo_screenheight() - self.winfo_reqheight() - 40)
        self.geometry(f"+{max(0, x)}+{max(0, y)}")
        self.grab_set()
        self.focus_set()

    # ---- điều hướng ----
    def _shift_month(self, delta: int):
        idx = self._view_year * 12 + (self._view_month - 1) + delta
        y, m = divmod(idx, 12)
        if MIN_YEAR <= y <= MAX_YEAR:
            self._view_year, self._view_month = y, m + 1
            self._sync_nav()
            self._render()

    def _on_month_pick(self):
        self._view_month = _MONTHS.index(self.month_var.get()) + 1
        self._render()

    def _on_year_pick(self):
        try:
            y = int(self.year_var.get())
        except ValueError:
            y = self._view_year
        y = max(MIN_YEAR, min(MAX_YEAR, y))
        self._view_year = y
        self._sync_nav()
        self._render()

    def _sync_nav(self):
        self.month_var.set(_MONTHS[self._view_month - 1])
        self.year_var.set(str(self._view_year))

    # ---- vẽ lịch ----
    def _render(self):
        for w in self.grid_frame.winfo_children():
            w.destroy()
        for c, name in enumerate(_WEEKDAYS):
            tk.Label(self.grid_frame, text=name, width=4, font=Theme.FONT_SUBTITLE,
                     bg=Theme.SURFACE, fg=Theme.PRIMARY).grid(row=0, column=c, pady=(0, 4))

        today = date.today()
        weeks = calendar.Calendar(firstweekday=0).monthdayscalendar(self._view_year, self._view_month)
        for r, week in enumerate(weeks, start=1):
            for c, day in enumerate(week):
                if day == 0:
                    continue  # ô trống: ngày không thuộc tháng này -> không thể chọn
                d = date(self._view_year, self._view_month, day)
                is_sel = d == self._selected
                is_today = d == today
                tk.Button(
                    self.grid_frame, text=str(day), width=3, relief=tk.FLAT, cursor="hand2",
                    bg=Theme.PRIMARY if is_sel else Theme.SURFACE,
                    fg=Theme.TEXT_WHITE if is_sel else Theme.TEXT_MAIN,
                    activebackground=Theme.PRIMARY, activeforeground=Theme.TEXT_WHITE,
                    font=Theme.FONT_SUBTITLE,
                    highlightthickness=1 if is_today else 0, highlightbackground=Theme.PRIMARY,
                    command=lambda dd=d: self._pick(dd),
                ).grid(row=r, column=c, padx=1, pady=1)

    def _pick(self, d: date):
        self._on_select(d)
        self._close()

    def _close(self):
        top = self._owner_top
        self.grab_release()
        self.destroy()
        try:  # trả lại "grab" cho form đang mở bên dưới
            top.grab_set()
        except tk.TclError:
            pass


class DateEntry(tk.Frame):
    """Ô nhập ngày YYYY-MM-DD + nút 📅.

    Dùng như ttk.Entry (get / insert / delete / focus_set) và có thêm:
      - validate(): kiểm tra ngày tồn tại, báo lỗi bằng messagebox.
      - value(): chuỗi đã chuẩn hoá (YYYY-MM-DD) hoặc '' nếu để trống.
    """

    def __init__(self, parent, initial: str = "", allow_empty: bool = True,
                 label: str = "Ngày", not_future: bool = False):
        super().__init__(parent, bg=Theme.SURFACE)
        self.allow_empty = allow_empty
        self.label = label
        self.not_future = not_future

        self.entry = ttk.Entry(self)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.btn = ttk.Button(self, text="📅", width=3, command=self._open_calendar)
        self.btn.pack(side=tk.RIGHT, padx=(6, 0))

        if initial:
            self.entry.insert(0, initial)
        self.entry.bind("<KeyRelease>", lambda e: self._live_check())
        self.entry.bind("<FocusOut>", lambda e: self._live_check())

    # ---- giao diện giống Entry ----
    def get(self) -> str:
        return self.entry.get()

    def insert(self, index, text):
        self.entry.insert(index, text)
        self._live_check()

    def delete(self, first, last=None):
        self.entry.delete(first, last)
        self._live_check()

    def set(self, text: str):
        self.entry.delete(0, tk.END)
        self.entry.insert(0, text or "")
        self._live_check()

    def focus_set(self):
        self.entry.focus_set()

    # ---- kiểm tra ----
    def _check(self):
        return validate_date_str(self.get(), self.allow_empty, self.label, self.not_future)

    def _live_check(self):
        """Chữ đỏ khi đang nhập ngày sai (không bật hộp thoại)."""
        ok, _ = self._check()
        try:
            self.entry.configure(foreground="" if ok else _ERROR_FG)
        except tk.TclError:
            pass

    def validate(self, parent: Optional[tk.Misc] = None) -> bool:
        ok, msg = self._check()
        if not ok:
            messagebox.showerror("Ngày không hợp lệ", msg, parent=parent or self.winfo_toplevel())
            self.entry.focus_set()
            self.entry.select_range(0, tk.END)
            return False
        norm = normalize_date_str(self.get())
        if norm and norm != self.get().strip():
            self.set(norm)  # '2026-9-1' -> '2026-09-01'
        return True

    def value(self) -> str:
        """Chuỗi YYYY-MM-DD chuẩn hoá (rỗng nếu không nhập)."""
        return normalize_date_str(self.get())

    # ---- lịch ----
    def _open_calendar(self):
        initial = parse_date(self.get()) or date.today()
        CalendarPopup(self, initial, self._on_pick, anchor=self.btn)

    def _on_pick(self, d: date):
        self.set(d.strftime("%Y-%m-%d"))
        self.focus_set()
