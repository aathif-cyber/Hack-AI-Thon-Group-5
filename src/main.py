"""
GreenGrid - Smart Energy Consumption & Carbon Tracker
HACK-AI-THON 2026

Single-file Python application.
Run with:
    python greengrid.py

Uses only Python standard-library modules:
    tkinter, csv, json, datetime, pathlib, math
"""

import csv
import json
import math
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from dataclasses import dataclass
from datetime import date
from pathlib import Path


# ============================================================
# 1. CONFIGURATION
# ============================================================

APP_TITLE = "GreenGrid | Smart Energy & Carbon Tracker"
DEFAULT_TARIFF = 7.50          # ₹ per kWh
DEFAULT_EMISSION_FACTOR = 0.82 # kg CO₂ per kWh
DATA_FILE = Path(__file__).with_name("greengrid_data.json")


# ============================================================
# 2. OOP MODEL
# ============================================================

@dataclass
class Appliance:
    name: str
    power_watts: float
    category: str = "Other"

    def __post_init__(self):
        self.name = self.name.strip()
        self.category = self.category.strip() or "Other"
        self.power_watts = float(self.power_watts)

        if not self.name:
            raise ValueError("Appliance name cannot be empty.")
        if self.power_watts <= 0:
            raise ValueError("Power rating must be greater than 0.")

    def energy_for_hours(self, hours: float) -> float:
        hours = float(hours)
        if hours < 0:
            raise ValueError("Usage hours cannot be negative.")
        return (self.power_watts * hours) / 1000.0


@dataclass
class EnergyRecord:
    appliance: Appliance
    usage_hours: float
    period: str = "Daily"
    record_date: str = ""

    def __post_init__(self):
        self.usage_hours = float(self.usage_hours)
        if self.usage_hours < 0:
            raise ValueError("Usage hours cannot be negative.")
        if not self.record_date:
            self.record_date = date.today().isoformat()

    @property
    def energy_kwh(self) -> float:
        return self.appliance.energy_for_hours(self.usage_hours)


class EnergyReport:
    """Calculates energy, cost, emissions and appliance rankings."""

    def __init__(self, records, tariff_per_kwh=DEFAULT_TARIFF,
                 emission_factor=DEFAULT_EMISSION_FACTOR):
        self.records = list(records)
        self.tariff_per_kwh = float(tariff_per_kwh)
        self.emission_factor = float(emission_factor)

    @property
    def total_kwh(self):
        return sum(r.energy_kwh for r in self.records)

    @property
    def estimated_cost(self):
        return self.total_kwh * self.tariff_per_kwh

    @property
    def estimated_emissions_kg(self):
        return self.total_kwh * self.emission_factor

    def appliance_totals(self):
        totals = {}
        for record in self.records:
            totals[record.appliance.name] = (
                totals.get(record.appliance.name, 0) + record.energy_kwh
            )
        return dict(sorted(totals.items(), key=lambda x: x[1], reverse=True))

    def top_consumers(self, limit=5):
        return list(self.appliance_totals().items())[:limit]

    def efficiency_score(self):
        """Simple explainable score based on total daily-equivalent usage."""
        if not self.records:
            return 100.0

        # A transparent heuristic: higher average appliance energy lowers score.
        avg = self.total_kwh / max(len(self.records), 1)
        score = 100 - (avg * 7)
        return max(0.0, min(100.0, score))

    def summary(self):
        return {
            "total_kwh": self.total_kwh,
            "cost": self.estimated_cost,
            "emissions": self.estimated_emissions_kg,
            "score": self.efficiency_score(),
            "top_consumers": self.top_consumers(),
        }


# ============================================================
# 3. SMART RECOMMENDATION ENGINE
# ============================================================

def recommendations_for(record):
    name = record.appliance.name.lower()
    category = record.appliance.category.lower()
    hours = record.usage_hours
    kwh = record.energy_kwh

    tips = []

    if "ac" in name or "air conditioner" in name or category == "cooling":
        tips.append("Set the AC around 24–26°C and reduce unnecessary runtime.")
    elif "refrigerator" in name or "fridge" in name:
        tips.append("Keep the refrigerator door closed and maintain efficient temperature settings.")
    elif "heater" in name or category == "heating":
        tips.append("Reduce heater runtime and use a timer where practical.")
    elif "light" in name or category == "lighting":
        tips.append("Use LED lighting and switch lights off when rooms are unoccupied.")
    elif "fan" in name:
        tips.append("Use the fan at the lowest comfortable speed and switch it off when not needed.")
    elif "washing" in name or "washer" in name:
        tips.append("Prefer full-load washing and efficient/cold cycles where suitable.")
    elif "tv" in name or "television" in name:
        tips.append("Turn the TV completely off instead of leaving it on standby.")
    elif "computer" in name or "laptop" in name or category == "computing":
        tips.append("Enable sleep mode and shut down devices during long periods of inactivity.")
    elif "pump" in name:
        tips.append("Check for leaks and avoid running the pump longer than necessary.")
    else:
        tips.append("Switch the appliance off when it is not required and avoid unnecessary runtime.")

    if hours > 8:
        tips.append("Usage is high; reducing daily runtime could produce meaningful savings.")
    elif kwh > 5:
        tips.append("This appliance has a high energy impact; consider an efficient model or shorter usage.")

    return tips


def build_recommendations(records):
    if not records:
        return ["Add appliance usage records to receive personalized energy-saving recommendations."]

    ranked = sorted(records, key=lambda r: r.energy_kwh, reverse=True)
    result = []

    for record in ranked[:5]:
        tip = recommendations_for(record)[0]
        result.append(f"{record.appliance.name}: {tip}")

    if not result:
        result.append("Use appliances only when required and monitor high-consumption devices.")

    return result


# ============================================================
# 4. SAMPLE DATA
# ============================================================

SAMPLE_RECORDS = [
    {"name": "Air Conditioner", "power": 1500, "category": "Cooling", "hours": 4},
    {"name": "Refrigerator", "power": 180, "category": "Kitchen", "hours": 10},
    {"name": "Ceiling Fan", "power": 75, "category": "Cooling", "hours": 8},
    {"name": "LED Lights", "power": 40, "category": "Lighting", "hours": 6},
    {"name": "Television", "power": 120, "category": "Entertainment", "hours": 4},
    {"name": "Washing Machine", "power": 500, "category": "Laundry", "hours": 1},
]


# ============================================================
# 5. MAIN APPLICATION
# ============================================================

class GreenGridApp(tk.Tk):

    def __init__(self):
        super().__init__()

        self.title(APP_TITLE)
        self.geometry("1280x820")
        self.minsize(1050, 700)
        self.configure(bg="#0b1220")

        self.records = []
        self.tariff = DEFAULT_TARIFF
        self.emission_factor = DEFAULT_EMISSION_FACTOR
        self.current_page = "Dashboard"

        self.setup_style()
        self.load_data()

        if not self.records:
            self.load_sample_data(silent=True)

        self.build_layout()
        self.show_dashboard()

    # --------------------------------------------------------
    # Styling
    # --------------------------------------------------------

    def setup_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "Treeview",
            background="#111b2e",
            foreground="#e7eef8",
            fieldbackground="#111b2e",
            rowheight=34,
            borderwidth=0,
            font=("Segoe UI", 10),
        )
        style.configure(
            "Treeview.Heading",
            background="#17243a",
            foreground="#9fb3c8",
            font=("Segoe UI", 10, "bold"),
            padding=8,
        )
        style.map("Treeview", background=[("selected", "#1c6b55")])

        style.configure(
            "TCombobox",
            fieldbackground="#17243a",
            background="#17243a",
            foreground="#ffffff",
        )

    def make_button(self, parent, text, command, bg="#1fa774",
                    fg="white", width=None):
        button = tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg,
            fg=fg,
            activebackground=bg,
            activeforeground="white",
            relief="flat",
            bd=0,
            padx=14,
            pady=9,
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
        )
        if width:
            button.config(width=width)
        return button

    # --------------------------------------------------------
    # Layout
    # --------------------------------------------------------

    def build_layout(self):
        self.sidebar = tk.Frame(self, bg="#08101d", width=220)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.content = tk.Frame(self, bg="#0b1220")
        self.content.pack(side="right", fill="both", expand=True)

        # Logo
        logo = tk.Frame(self.sidebar, bg="#08101d")
        logo.pack(fill="x", padx=20, pady=(25, 30))

        tk.Label(
            logo, text="GREEN", bg="#08101d", fg="#41d39a",
            font=("Segoe UI", 22, "bold")
        ).pack(anchor="w")
        tk.Label(
            logo, text="GRID", bg="#08101d", fg="white",
            font=("Segoe UI", 22, "bold")
        ).pack(anchor="w")
        tk.Label(
            logo, text="Smart Energy Tracker", bg="#08101d", fg="#71849c",
            font=("Segoe UI", 9)
        ).pack(anchor="w", pady=(3, 0))

        self.nav_buttons = {}
        for text, command in [
            ("Dashboard", self.show_dashboard),
            ("Appliances", self.show_appliances),
            ("Reports", self.show_reports),
            ("Settings", self.show_settings),
        ]:
            b = tk.Button(
                self.sidebar,
                text="  " + text,
                command=command,
                anchor="w",
                bg="#08101d",
                fg="#8fa2b8",
                activebackground="#132337",
                activeforeground="#ffffff",
                relief="flat",
                bd=0,
                font=("Segoe UI", 11),
                padx=18,
                pady=13,
                cursor="hand2",
            )
            b.pack(fill="x", padx=10, pady=2)
            self.nav_buttons[text] = b

        # Bottom sidebar
        bottom = tk.Frame(self.sidebar, bg="#08101d")
        bottom.pack(side="bottom", fill="x", padx=18, pady=20)

        tk.Label(
            bottom,
            text="HACK-AI-THON 2026\nSDG 7 • SDG 11 • SDG 13",
            bg="#08101d",
            fg="#61758e",
            font=("Segoe UI", 8),
            justify="left",
        ).pack(anchor="w")

        # Content header
        self.header = tk.Frame(self.content, bg="#0b1220")
        self.header.pack(fill="x", padx=30, pady=(25, 10))

        self.page_title = tk.Label(
            self.header, text="Dashboard",
            bg="#0b1220", fg="white",
            font=("Segoe UI", 25, "bold")
        )
        self.page_title.pack(side="left")

        self.page_subtitle = tk.Label(
            self.header, text="Monitor consumption, cost and carbon impact",
            bg="#0b1220", fg="#71849c",
            font=("Segoe UI", 10)
        )
        self.page_subtitle.pack(side="left", padx=18, pady=(10, 0))

        self.page = tk.Frame(self.content, bg="#0b1220")
        self.page.pack(fill="both", expand=True, padx=30, pady=10)

    def clear_page(self):
        for widget in self.page.winfo_children():
            widget.destroy()

    def set_active_nav(self, name):
        for key, button in self.nav_buttons.items():
            if key == name:
                button.config(bg="#123226", fg="#41d39a")
            else:
                button.config(bg="#08101d", fg="#8fa2b8")

    # --------------------------------------------------------
    # Dashboard
    # --------------------------------------------------------

    def show_dashboard(self):
        self.current_page = "Dashboard"
        self.page_title.config(text="Dashboard")
        self.page_subtitle.config(text="Monitor consumption, cost and carbon impact")
        self.set_active_nav("Dashboard")
        self.clear_page()

        report = EnergyReport(self.records, self.tariff, self.emission_factor)

        # KPI row
        kpi_frame = tk.Frame(self.page, bg="#0b1220")
        kpi_frame.pack(fill="x", pady=(0, 18))

        kpis = [
            ("TOTAL ENERGY", f"{report.total_kwh:.2f} kWh", "#41d39a"),
            ("ESTIMATED COST", f"₹{report.estimated_cost:,.2f}", "#5ba7ff"),
            ("CO₂ EMISSIONS", f"{report.estimated_emissions_kg:.2f} kg", "#ffb454"),
            ("GREEN SCORE", f"{report.efficiency_score():.0f}/100", "#d17cff"),
        ]

        for i, (title, value, accent) in enumerate(kpis):
            card = tk.Frame(kpi_frame, bg="#111b2e", height=115)
            card.grid(row=0, column=i, sticky="nsew", padx=5)
            kpi_frame.columnconfigure(i, weight=1)

            tk.Frame(card, bg=accent, width=5).pack(side="left", fill="y")

            inner = tk.Frame(card, bg="#111b2e")
            inner.pack(fill="both", expand=True, padx=16, pady=15)

            tk.Label(
                inner, text=title, bg="#111b2e", fg="#71849c",
                font=("Segoe UI", 9, "bold")
            ).pack(anchor="w")
            tk.Label(
                inner, text=value, bg="#111b2e", fg="white",
                font=("Segoe UI", 19, "bold")
            ).pack(anchor="w", pady=(8, 0))

        # Main chart + top consumers
        main = tk.Frame(self.page, bg="#0b1220")
        main.pack(fill="both", expand=True)

        chart_card = tk.Frame(main, bg="#111b2e")
        chart_card.pack(side="left", fill="both", expand=True, padx=(0, 8))

        tk.Label(
            chart_card, text="Energy Consumption by Appliance",
            bg="#111b2e", fg="white",
            font=("Segoe UI", 13, "bold")
        ).pack(anchor="w", padx=20, pady=(18, 2))

        tk.Label(
            chart_card, text="Estimated usage based on entered operating hours",
            bg="#111b2e", fg="#71849c",
            font=("Segoe UI", 9)
        ).pack(anchor="w", padx=20)

        self.chart = tk.Canvas(
            chart_card, bg="#111b2e", highlightthickness=0
        )
        self.chart.pack(fill="both", expand=True, padx=15, pady=15)
        self.chart.bind("<Configure>", lambda e: self.draw_chart(report))

        # Right panel
        right = tk.Frame(main, bg="#0b1220", width=355)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)

        top_card = tk.Frame(right, bg="#111b2e")
        top_card.pack(fill="both", expand=True, pady=(0, 8))

        tk.Label(
            top_card, text="Top Energy Consumers",
            bg="#111b2e", fg="white",
            font=("Segoe UI", 13, "bold")
        ).pack(anchor="w", padx=18, pady=(18, 3))

        tk.Label(
            top_card, text="Where your energy is going",
            bg="#111b2e", fg="#71849c",
            font=("Segoe UI", 9)
        ).pack(anchor="w", padx=18)

        top = report.top_consumers(5)
        if top:
            max_value = top[0][1]
            for idx, (name, value) in enumerate(top, 1):
                row = tk.Frame(top_card, bg="#111b2e")
                row.pack(fill="x", padx=18, pady=(13, 0))

                tk.Label(
                    row, text=f"{idx}. {name}",
                    bg="#111b2e", fg="#e7eef8",
                    font=("Segoe UI", 10, "bold"),
                    width=20, anchor="w"
                ).pack(side="left")

                tk.Label(
                    row, text=f"{value:.2f} kWh",
                    bg="#111b2e", fg="#41d39a",
                    font=("Segoe UI", 10, "bold")
                ).pack(side="right")

                bar_bg = tk.Frame(top_card, bg="#24344a", height=5)
                bar_bg.pack(fill="x", padx=18, pady=(5, 0))

                bar = tk.Frame(
                    bar_bg, bg="#41d39a",
                    width=max(2, int(270 * value / max_value)),
                    height=5
                )
                bar.place(x=0, y=0, relheight=1)

        else:
            tk.Label(
                top_card, text="No data available.",
                bg="#111b2e", fg="#71849c"
            ).pack(pady=30)

        rec_card = tk.Frame(right, bg="#111b2e")
        rec_card.pack(fill="both", expand=True)

        tk.Label(
            rec_card, text="Smart Recommendations",
            bg="#111b2e", fg="white",
            font=("Segoe UI", 13, "bold")
        ).pack(anchor="w", padx=18, pady=(16, 5))

        recommendations = build_recommendations(self.records)

        rec_text = tk.Text(
            rec_card, bg="#111b2e", fg="#b8c7d9",
            insertbackground="white", relief="flat",
            font=("Segoe UI", 9), wrap="word",
            height=8
        )
        rec_text.pack(fill="both", expand=True, padx=15, pady=(0, 12))
        rec_text.config(state="normal")

        for rec in recommendations:
            rec_text.insert("end", "• " + rec + "\n\n")

        rec_text.config(state="disabled")

        # Footer actions
        actions = tk.Frame(self.page, bg="#0b1220")
        actions.pack(fill="x", pady=(12, 0))

        self.make_button(
            actions, "+ Add Appliance", self.open_add_record,
            bg="#1fa774"
        ).pack(side="left")

        self.make_button(
            actions, "Generate Report", self.show_reports,
            bg="#285f9e"
        ).pack(side="left", padx=8)

        self.make_button(
            actions, "Export CSV", self.export_csv,
            bg="#39475b"
        ).pack(side="left")

        self.make_button(
            actions, "Load Sample Data", self.load_sample_and_refresh,
            bg="#39475b"
        ).pack(side="right")

    def draw_chart(self, report):
        if not hasattr(self, "chart"):
            return

        canvas = self.chart
        canvas.delete("all")

        width = max(canvas.winfo_width(), 500)
        height = max(canvas.winfo_height(), 300)

        totals = report.top_consumers(8)
        if not totals:
            canvas.create_text(
                width / 2, height / 2,
                text="Add appliance data to display the chart.",
                fill="#71849c",
                font=("Segoe UI", 11)
            )
            return

        max_value = max(v for _, v in totals) or 1
        left = 35
        bottom = height - 50
        chart_width = width - 70
        chart_height = height - 90

        # Grid lines
        for i in range(5):
            y = bottom - (chart_height * i / 4)
            canvas.create_line(
                left, y, width - 25, y,
                fill="#223149"
            )

        bar_space = chart_width / len(totals)
        bar_width = max(22, bar_space * 0.55)

        for i, (name, value) in enumerate(totals):
            x_center = left + bar_space * (i + 0.5)
            bar_h = chart_height * value / max_value
            x1 = x_center - bar_width / 2
            y1 = bottom - bar_h
            x2 = x_center + bar_width / 2
            y2 = bottom

            canvas.create_rectangle(
                x1, y1, x2, y2,
                fill="#41d39a", outline=""
            )

            canvas.create_text(
                x_center, y1 - 10,
                text=f"{value:.1f}",
                fill="#dbe8f5",
                font=("Segoe UI", 8, "bold")
            )

            short_name = name if len(name) <= 13 else name[:12] + "…"
            canvas.create_text(
                x_center, bottom + 17,
                text=short_name,
                fill="#8fa2b8",
                font=("Segoe UI", 8),
                angle=0
            )

        canvas.create_text(
            15, 15,
            text="kWh",
            anchor="w",
            fill="#71849c",
            font=("Segoe UI", 8)
        )

    # --------------------------------------------------------
    # Appliances page
    # --------------------------------------------------------

    def show_appliances(self):
        self.current_page = "Appliances"
        self.page_title.config(text="Appliances")
        self.page_subtitle.config(text="Manage energy usage records")
        self.set_active_nav("Appliances")
        self.clear_page()

        top = tk.Frame(self.page, bg="#0b1220")
        top.pack(fill="x", pady=(0, 12))

        self.make_button(
            top, "+ Add Appliance", self.open_add_record
        ).pack(side="left")

        self.make_button(
            top, "Delete Selected", self.delete_selected,
            bg="#9e3d4d"
        ).pack(side="left", padx=8)

        self.make_button(
            top, "Edit Selected", self.edit_selected,
            bg="#285f9e"
        ).pack(side="left")

        self.make_button(
            top, "Load Sample Data", self.load_sample_and_refresh,
            bg="#39475b"
        ).pack(side="right")

        card = tk.Frame(self.page, bg="#111b2e")
        card.pack(fill="both", expand=True)

        columns = ("name", "category", "power", "hours", "period", "energy", "date")
        self.tree = ttk.Treeview(card, columns=columns, show="headings")

        headings = {
            "name": "Appliance",
            "category": "Category",
            "power": "Power (W)",
            "hours": "Hours",
            "period": "Period",
            "energy": "Energy (kWh)",
            "date": "Date",
        }

        widths = {
            "name": 190, "category": 120, "power": 100,
            "hours": 80, "period": 90, "energy": 110, "date": 110
        }

        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], anchor="center")

        scrollbar = ttk.Scrollbar(card, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True, padx=(15, 0), pady=15)
        scrollbar.pack(side="right", fill="y", padx=(0, 15), pady=15)

        self.refresh_tree()

    def refresh_tree(self):
        if not hasattr(self, "tree"):
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        for i, record in enumerate(self.records):
            self.tree.insert(
                "",
                "end",
                iid=str(i),
                values=(
                    record.appliance.name,
                    record.appliance.category,
                    f"{record.appliance.power_watts:.0f}",
                    f"{record.usage_hours:.2f}",
                    record.period,
                    f"{record.energy_kwh:.2f}",
                    record.record_date,
                )
            )

    # --------------------------------------------------------
    # Add / Edit dialog
    # --------------------------------------------------------

    def open_add_record(self):
        self.open_record_dialog()

    def edit_selected(self):
        if not hasattr(self, "tree"):
            return

        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Edit Appliance", "Select a record first.")
            return

        index = int(selected[0])
        self.open_record_dialog(index)

    def open_record_dialog(self, index=None):
        editing = index is not None

        dialog = tk.Toplevel(self)
        dialog.title("Edit Appliance" if editing else "Add Appliance")
        dialog.geometry("470x510")
        dialog.resizable(False, False)
        dialog.configure(bg="#111b2e")
        dialog.transient(self)
        dialog.grab_set()

        record = self.records[index] if editing else None

        tk.Label(
            dialog,
            text="Edit Energy Record" if editing else "Add Energy Record",
            bg="#111b2e", fg="white",
            font=("Segoe UI", 18, "bold")
        ).pack(anchor="w", padx=30, pady=(25, 4))

        tk.Label(
            dialog,
            text="Enter appliance information and usage.",
            bg="#111b2e", fg="#71849c",
            font=("Segoe UI", 9)
        ).pack(anchor="w", padx=30, pady=(0, 20))

        form = tk.Frame(dialog, bg="#111b2e")
        form.pack(fill="x", padx=30)

        fields = {}

        def add_field(label, default="", choices=None):
            tk.Label(
                form, text=label, bg="#111b2e", fg="#aebdd0",
                font=("Segoe UI", 9, "bold")
            ).pack(anchor="w", pady=(7, 5))

            if choices:
                var = tk.StringVar(value=default)
                widget = ttk.Combobox(
                    form, textvariable=var,
                    values=choices, state="readonly"
                )
                widget.pack(fill="x", ipady=5)
            else:
                widget = tk.Entry(
                    form, bg="#17243a", fg="white",
                    insertbackground="white", relief="flat",
                    font=("Segoe UI", 10)
                )
                widget.pack(fill="x", ipady=7)
                widget.insert(0, default)

            fields[label] = widget

        add_field(
            "Appliance Name",
            record.appliance.name if record else ""
        )
        add_field(
            "Power Rating (Watts)",
            str(int(record.appliance.power_watts)) if record else ""
        )
        add_field(
            "Category",
            record.appliance.category if record else "Other",
            ["Cooling", "Heating", "Lighting", "Kitchen",
             "Laundry", "Entertainment", "Computing", "Other"]
        )
        add_field(
            "Usage Hours",
            str(record.usage_hours) if record else ""
        )
        add_field(
            "Period",
            record.period if record else "Daily",
            ["Daily", "Weekly", "Monthly"]
        )

        def save():
            try:
                name = fields["Appliance Name"].get().strip()
                power = float(fields["Power Rating (Watts)"].get())
                category = fields["Category"].get()
                hours = float(fields["Usage Hours"].get())
                period = fields["Period"].get()

                if hours < 0:
                    raise ValueError("Usage hours cannot be negative.")

                if period == "Daily" and hours > 24:
                    raise ValueError("Daily usage cannot exceed 24 hours.")

                appliance = Appliance(name, power, category)
                new_record = EnergyRecord(
                    appliance,
                    hours,
                    period,
                    record.record_date if record else date.today().isoformat()
                )

                if editing:
                    self.records[index] = new_record
                else:
                    self.records.append(new_record)

                self.save_data()
                dialog.destroy()
                self.show_appliances()
                messagebox.showinfo(
                    "Saved",
                    f"{name} uses approximately {new_record.energy_kwh:.2f} kWh per {period.lower()}."
                )

            except ValueError as exc:
                messagebox.showerror("Invalid Input", str(exc), parent=dialog)

        buttons = tk.Frame(dialog, bg="#111b2e")
        buttons.pack(fill="x", padx=30, pady=25)

        self.make_button(buttons, "Cancel", dialog.destroy,
                         bg="#39475b").pack(side="right")
        self.make_button(buttons, "Save Record", save).pack(side="right", padx=8)

    def delete_selected(self):
        if not hasattr(self, "tree"):
            return

        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Delete Appliance", "Select a record first.")
            return

        if not messagebox.askyesno(
            "Confirm Delete",
            "Delete the selected energy record?"
        ):
            return

        indexes = sorted([int(x) for x in selected], reverse=True)
        for index in indexes:
            if 0 <= index < len(self.records):
                self.records.pop(index)

        self.save_data()
        self.refresh_tree()

    # --------------------------------------------------------
    # Reports
    # --------------------------------------------------------

    def show_reports(self):
        self.current_page = "Reports"
        self.page_title.config(text="Energy Report")
        self.page_subtitle.config(text="Detailed energy, cost and carbon analysis")
        self.set_active_nav("Reports")
        self.clear_page()

        report = EnergyReport(self.records, self.tariff, self.emission_factor)

        # Summary
        summary = tk.Frame(self.page, bg="#0b1220")
        summary.pack(fill="x", pady=(0, 15))

        values = [
            ("Total Energy", f"{report.total_kwh:.2f} kWh"),
            ("Estimated Cost", f"₹{report.estimated_cost:,.2f}"),
            ("CO₂ Impact", f"{report.estimated_emissions_kg:.2f} kg"),
            ("Green Score", f"{report.efficiency_score():.0f}/100"),
        ]

        for i, (label, value) in enumerate(values):
            summary.columnconfigure(i, weight=1)
            card = tk.Frame(summary, bg="#111b2e")
            card.grid(row=0, column=i, sticky="nsew", padx=5)

            tk.Label(
                card, text=label, bg="#111b2e", fg="#71849c",
                font=("Segoe UI", 9, "bold")
            ).pack(anchor="w", padx=15, pady=(13, 2))
            tk.Label(
                card, text=value, bg="#111b2e", fg="white",
                font=("Segoe UI", 17, "bold")
            ).pack(anchor="w", padx=15, pady=(0, 13))

        # Detail
        body = tk.Frame(self.page, bg="#0b1220")
        body.pack(fill="both", expand=True)

        left = tk.Frame(body, bg="#111b2e")
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))

        tk.Label(
            left, text="Appliance Breakdown",
            bg="#111b2e", fg="white",
            font=("Segoe UI", 13, "bold")
        ).pack(anchor="w", padx=18, pady=(18, 10))

        report_text = tk.Text(
            left, bg="#111b2e", fg="#c9d5e3",
            relief="flat", font=("Consolas", 10),
            wrap="word"
        )
        report_text.pack(fill="both", expand=True, padx=18, pady=(0, 15))

        if not self.records:
            report_text.insert("end", "No records available.")
        else:
            report_text.insert("end", "GREEN GRID ENERGY REPORT\n")
            report_text.insert("end", "=" * 60 + "\n\n")
            report_text.insert("end", f"Generated: {date.today().isoformat()}\n")
            report_text.insert("end", f"Tariff: ₹{self.tariff:.2f}/kWh\n")
            report_text.insert("end", f"Carbon factor: {self.emission_factor:.2f} kg CO₂/kWh\n\n")

            for name, kwh in report.appliance_totals().items():
                share = (kwh / report.total_kwh * 100) if report.total_kwh else 0
                report_text.insert(
                    "end",
                    f"{name:<28} {kwh:>8.2f} kWh   {share:>5.1f}%\n"
                )

            report_text.insert("end", "\n")
            report_text.insert("end", f"TOTAL ENERGY       : {report.total_kwh:.2f} kWh\n")
            report_text.insert("end", f"ESTIMATED COST     : ₹{report.estimated_cost:,.2f}\n")
            report_text.insert("end", f"CO₂ EMISSIONS      : {report.estimated_emissions_kg:.2f} kg\n")
            report_text.insert("end", f"GREEN SCORE        : {report.efficiency_score():.0f}/100\n")

        report_text.config(state="disabled")

        right = tk.Frame(body, bg="#111b2e", width=340)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)

        tk.Label(
            right, text="Actions",
            bg="#111b2e", fg="white",
            font=("Segoe UI", 13, "bold")
        ).pack(anchor="w", padx=18, pady=(18, 12))

        self.make_button(
            right, "Export CSV", self.export_csv,
            bg="#285f9e"
        ).pack(fill="x", padx=18, pady=5)

        self.make_button(
            right, "Save JSON Data", self.save_data,
            bg="#39475b"
        ).pack(fill="x", padx=18, pady=5)

        tk.Label(
            right,
            text="How to reduce impact",
            bg="#111b2e", fg="#41d39a",
            font=("Segoe UI", 11, "bold")
        ).pack(anchor="w", padx=18, pady=(30, 8))

        tips = build_recommendations(self.records)
        tip_box = tk.Text(
            right, bg="#17243a", fg="#c9d5e3",
            relief="flat", font=("Segoe UI", 9),
            wrap="word", height=15
        )
        tip_box.pack(fill="both", expand=True, padx=18, pady=(0, 18))

        for tip in tips:
            tip_box.insert("end", "• " + tip + "\n\n")

        tip_box.config(state="disabled")

    # --------------------------------------------------------
    # Settings
    # --------------------------------------------------------

    def show_settings(self):
        self.current_page = "Settings"
        self.page_title.config(text="Settings")
        self.page_subtitle.config(text="Configure cost and carbon calculation factors")
        self.set_active_nav("Settings")
        self.clear_page()

        card = tk.Frame(self.page, bg="#111b2e")
        card.pack(fill="x", padx=10, pady=10)

        tk.Label(
            card, text="Calculation Settings",
            bg="#111b2e", fg="white",
            font=("Segoe UI", 16, "bold")
        ).pack(anchor="w", padx=25, pady=(25, 4))

        tk.Label(
            card,
            text="These configurable factors are used by the EnergyReport class.",
            bg="#111b2e", fg="#71849c",
            font=("Segoe UI", 9)
        ).pack(anchor="w", padx=25, pady=(0, 20))

        form = tk.Frame(card, bg="#111b2e")
        form.pack(fill="x", padx=25, pady=(0, 25))

        tariff_var = tk.StringVar(value=str(self.tariff))
        carbon_var = tk.StringVar(value=str(self.emission_factor))

        def field(label, variable, unit):
            row = tk.Frame(form, bg="#111b2e")
            row.pack(fill="x", pady=10)

            tk.Label(
                row, text=label, bg="#111b2e", fg="#c9d5e3",
                font=("Segoe UI", 10, "bold"), width=28, anchor="w"
            ).pack(side="left")

            entry = tk.Entry(
                row, textvariable=variable,
                bg="#17243a", fg="white",
                insertbackground="white", relief="flat",
                width=15, font=("Segoe UI", 10)
            )
            entry.pack(side="left", ipady=7)

            tk.Label(
                row, text=unit, bg="#111b2e", fg="#71849c",
                font=("Segoe UI", 9)
            ).pack(side="left", padx=10)

        field("Electricity Tariff", tariff_var, "₹ / kWh")
        field("Carbon Emission Factor", carbon_var, "kg CO₂ / kWh")

        def save_settings():
            try:
                tariff = float(tariff_var.get())
                carbon = float(carbon_var.get())

                if tariff < 0 or carbon < 0:
                    raise ValueError("Values cannot be negative.")

                self.tariff = tariff
                self.emission_factor = carbon
                self.save_data()

                messagebox.showinfo(
                    "Settings Saved",
                    "Calculation settings updated successfully."
                )
                self.show_dashboard()

            except ValueError as exc:
                messagebox.showerror("Invalid Settings", str(exc))

        self.make_button(
            card, "Save Settings", save_settings
        ).pack(anchor="w", padx=25, pady=(0, 25))

        # Explanation
        info = tk.Frame(self.page, bg="#111b2e")
        info.pack(fill="x", padx=10, pady=10)

        tk.Label(
            info, text="Calculation Logic",
            bg="#111b2e", fg="white",
            font=("Segoe UI", 13, "bold")
        ).pack(anchor="w", padx=20, pady=(18, 10))

        formulas = (
            "Energy (kWh) = Power (Watts) × Usage Hours ÷ 1000\n"
            "Estimated Cost = Total Energy × Tariff\n"
            "CO₂ Emissions = Total Energy × Carbon Emission Factor\n"
            "Top Consumers = Appliances ranked by calculated kWh"
        )

        tk.Label(
            info, text=formulas,
            bg="#111b2e", fg="#b8c7d9",
            justify="left", anchor="w",
            font=("Consolas", 10)
        ).pack(anchor="w", padx=20, pady=(0, 20))

    # --------------------------------------------------------
    # Data handling
    # --------------------------------------------------------

    def load_sample_data(self, silent=False):
        self.records = []

        for item in SAMPLE_RECORDS:
            try:
                appliance = Appliance(
                    item["name"],
                    item["power"],
                    item["category"]
                )
                self.records.append(
                    EnergyRecord(
                        appliance,
                        item["hours"],
                        "Daily"
                    )
                )
            except (KeyError, ValueError):
                continue

        if not silent:
            self.save_data()

    def load_sample_and_refresh(self):
        if self.records:
            if not messagebox.askyesno(
                "Load Sample Data",
                "This will replace the current records with sample data. Continue?"
            ):
                return

        self.load_sample_data()
        self.show_dashboard()

    def save_data(self):
        payload = {
            "tariff": self.tariff,
            "emission_factor": self.emission_factor,
            "records": [
                {
                    "name": r.appliance.name,
                    "power": r.appliance.power_watts,
                    "category": r.appliance.category,
                    "hours": r.usage_hours,
                    "period": r.period,
                    "date": r.record_date,
                }
                for r in self.records
            ]
        }

        try:
            with DATA_FILE.open("w", encoding="utf-8") as file:
                json.dump(payload, file, indent=4)
        except OSError:
            pass

    def load_data(self):
        if not DATA_FILE.exists():
            return

        try:
            with DATA_FILE.open("r", encoding="utf-8") as file:
                payload = json.load(file)

            self.tariff = float(payload.get("tariff", DEFAULT_TARIFF))
            self.emission_factor = float(
                payload.get("emission_factor", DEFAULT_EMISSION_FACTOR)
            )

            self.records = []

            for item in payload.get("records", []):
                appliance = Appliance(
                    item["name"],
                    item["power"],
                    item.get("category", "Other")
                )
                self.records.append(
                    EnergyRecord(
                        appliance,
                        item["hours"],
                        item.get("period", "Daily"),
                        item.get("date", date.today().isoformat())
                    )
                )

        except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError):
            self.records = []
            self.tariff = DEFAULT_TARIFF
            self.emission_factor = DEFAULT_EMISSION_FACTOR

    # --------------------------------------------------------
    # CSV export
    # --------------------------------------------------------

    def export_csv(self):
        if not self.records:
            messagebox.showinfo("Export CSV", "There are no records to export.")
            return

        path = filedialog.asksaveasfilename(
            title="Export GreenGrid Report",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )

        if not path:
            return

        report = EnergyReport(self.records, self.tariff, self.emission_factor)

        try:
            with open(path, "w", newline="", encoding="utf-8-sig") as file:
                writer = csv.writer(file)

                writer.writerow([
                    "Appliance", "Category", "Power (W)",
                    "Usage Hours", "Period", "Energy (kWh)", "Date"
                ])

                for r in self.records:
                    writer.writerow([
                        r.appliance.name,
                        r.appliance.category,
                        r.appliance.power_watts,
                        r.usage_hours,
                        r.period,
                        round(r.energy_kwh, 4),
                        r.record_date
                    ])

                writer.writerow([])
                writer.writerow(["TOTAL ENERGY (kWh)", round(report.total_kwh, 4)])
                writer.writerow(["ESTIMATED COST (INR)", round(report.estimated_cost, 2)])
                writer.writerow(["CO2 EMISSIONS (kg)", round(report.estimated_emissions_kg, 4)])
                writer.writerow(["GREEN SCORE", round(report.efficiency_score(), 2)])

            messagebox.showinfo(
                "Export Complete",
                f"Report exported successfully:\n{path}"
            )

        except OSError as exc:
            messagebox.showerror("Export Failed", str(exc))


# ============================================================
# 6. APPLICATION ENTRY POINT
# ============================================================

def main():
    app = GreenGridApp()
    app.mainloop()


if __name__ == "__main__":
    main()
