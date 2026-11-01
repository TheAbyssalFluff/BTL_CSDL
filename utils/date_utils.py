"""Tiện ích kiểm tra & chuẩn hoá ngày tháng dùng chung cho toàn dự án.

Mọi form / service nên gọi các hàm ở đây thay vì tự kiểm tra, để cách
kiểm tra thống nhất (kể cả năm nhuận: 29/02 chỉ hợp lệ ở năm nhuận).
"""
import calendar
from datetime import date
from typing import Optional, Tuple

MIN_YEAR = 1900
MAX_YEAR = 2100
DATE_HINT = "YYYY-MM-DD (ví dụ 2026-09-01)"


def validate_date_str(
    text: Optional[str],
    allow_empty: bool = False,
    label: str = "Ngày",
    not_future: bool = False,
) -> Tuple[bool, str]:
    """Kiểm tra chuỗi ngày dạng YYYY-MM-DD. Trả về (hợp_lệ, thông_báo_lỗi)."""
    text = (text or "").strip()
    if not text:
        return (True, "") if allow_empty else (False, f"Vui lòng nhập {label.lower()}.")

    parts = text.split("-")
    if (
        len(parts) != 3
        or not all(p.isascii() and p.isdigit() for p in parts)
        or len(parts[0]) != 4
        or len(parts[1]) > 2
        or len(parts[2]) > 2
    ):
        return False, f"{label} '{text}' sai định dạng.\nVui lòng nhập theo dạng {DATE_HINT} hoặc bấm nút 📅 để chọn."

    y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
    if not (MIN_YEAR <= y <= MAX_YEAR):
        return False, f"Năm {y} không hợp lệ (chỉ chấp nhận từ {MIN_YEAR} đến {MAX_YEAR})."
    if not (1 <= m <= 12):
        return False, f"Tháng {m} không hợp lệ (phải từ 1 đến 12)."

    max_day = calendar.monthrange(y, m)[1]
    if not (1 <= d <= max_day):
        return False, f"Ngày {d:02d}/{m:02d}/{y} không tồn tại: tháng {m} năm {y} chỉ có {max_day} ngày."

    if not_future and date(y, m, d) > date.today():
        return False, f"{label} {d:02d}/{m:02d}/{y} không được lớn hơn ngày hôm nay."

    return True, ""


def parse_date(text: Optional[str]) -> Optional[date]:
    """Chuyển chuỗi YYYY-MM-DD (đã hợp lệ) thành date; sai thì trả về None."""
    ok, _ = validate_date_str(text)
    if not ok:
        return None
    y, m, d = (int(p) for p in text.strip().split("-"))
    return date(y, m, d)


def normalize_date_str(text: Optional[str]) -> str:
    """'2026-9-1' -> '2026-09-01'. Chuỗi rỗng/không hợp lệ trả về ''."""
    dt = parse_date(text)
    return dt.strftime("%Y-%m-%d") if dt else ""


def validate_month_year(month: int, year: int) -> Tuple[bool, str]:
    """Kiểm tra cặp tháng/năm (dùng cho hoá đơn theo kỳ)."""
    if not (1 <= month <= 12):
        return False, f"Tháng {month} không hợp lệ (phải từ 1 đến 12)."
    if not (MIN_YEAR <= year <= MAX_YEAR):
        return False, f"Năm {year} không hợp lệ (chỉ chấp nhận từ {MIN_YEAR} đến {MAX_YEAR})."
    return True, ""
