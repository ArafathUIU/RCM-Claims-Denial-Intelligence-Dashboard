"""RCM Claims Denial Intelligence - Excel Dashboard Builder.

Reads the generated claims CSV and produces a formatted
multi-sheet Excel workbook with charts and KPIs.
"""
import os
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import (
    Font, PatternFill, Alignment, Border, Side, numbers
)
from openpyxl.chart import BarChart, LineChart, PieChart, Reference, BarChart3D
from openpyxl.chart.series import DataPoint
from openpyxl.chart.label import DataLabelList
from openpyxl.utils import get_column_letter
from copy import copy

# ============================================================
# CONFIGURATION
# ============================================================
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "claims_data.csv")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "RCM_Denial_Dashboard.xlsx")

# ============================================================
# STYLE CONSTANTS
# ============================================================
DARK_BLUE = "1B3A5C"
MED_BLUE = "2E75B6"
LIGHT_BLUE = "BDD7EE"
WHITE = "FFFFFF"
RED_ACCENT = "C00000"
GREEN_ACCENT = "006100"
GRAY_BG = "F2F2F2"
ORANGE = "ED7D31"
TEAL = "2B9C8E"

HEADER_FONT = Font(name="Calibri", size=11, bold=True, color=WHITE)
HEADER_FILL = PatternFill(start_color=DARK_BLUE, end_color=DARK_BLUE, fill_type="solid")
TITLE_FONT = Font(name="Calibri", size=16, bold=True, color=DARK_BLUE)
SUBTITLE_FONT = Font(name="Calibri", size=10, color="666666")
KPI_VALUE_FONT = Font(name="Calibri", size=24, bold=True, color=DARK_BLUE)
KPI_LABEL_FONT = Font(name="Calibri", size=10, color="888888")
THIN_BORDER = Border(
    left=Side(style="thin", color="CCCCCC"),
    right=Side(style="thin", color="CCCCCC"),
    top=Side(style="thin", color="CCCCCC"),
    bottom=Side(style="thin", color="CCCCCC"),
)
ALT_FILL = PatternFill(start_color=GRAY_BG, end_color=GRAY_BG, fill_type="solid")

CHART_COLORS = ["2E75B6", "ED7D31", "A5A5A5", "FFC000", "4472C4",
                "70AD47", "C00000", "5B9BD5", "264478", "636363"]


def apply_header_style(ws, row, cols):
    """Apply header styling to a row of cells."""
    for col in range(1, cols + 1):
        cell = ws.cell(row=row, column=col)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = THIN_BORDER


def apply_body_style(ws, start_row, end_row, cols):
    """Apply alternating row colors and borders to data rows."""
    for r in range(start_row, end_row + 1):
        for c in range(1, cols + 1):
            cell = ws.cell(row=r, column=c)
            cell.border = THIN_BORDER
            cell.alignment = Alignment(horizontal="center", vertical="center")
            if (r - start_row) % 2 == 1:
                cell.fill = ALT_FILL


def auto_width(ws, min_width=10, max_width=40):
    """Auto-fit column widths."""
    for col_cells in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col_cells[0].column)
        for cell in col_cells:
            if cell.value:
                max_len = max(max_len, len(str(cell.value)))
        ws.column_dimensions[col_letter].width = min(max(max_len + 3, min_width), max_width)


def add_title(ws, title, row=1, col=1):
    """Add a sheet title."""
    cell = ws.cell(row=row, column=col, value=title)
    cell.font = TITLE_FONT


def add_subtitle(ws, text, row=2, col=1):
    """Add a subtitle / description."""
    cell = ws.cell(row=row, column=col, value=text)
    cell.font = SUBTITLE_FONT
