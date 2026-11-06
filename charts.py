import base64
import io

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter


MSRP = 30_000
ANNUAL_DROP = 3_000
VALUE_FLOOR = 10_000
SELECTED_MILEAGE = 33_000
SELECTED_PRICE = 24_000
PRICE_AT_ZERO_MILES = 30_000
DOLLARS_PER_MILE = 0.17


def depreciation_values(years: int = 5) -> list[int]:
    """Resale value after each year, dropping a fixed amount from MSRP."""
    return [MSRP - ANNUAL_DROP * year for year in range(years + 1)]


def comparable_prices(mileages: list[int]) -> list[int]:
    """Estimated asking price for a mileage, declining from a new-car price."""
    return [
        round(PRICE_AT_ZERO_MILES - DOLLARS_PER_MILE * mileage)
        for mileage in mileages
    ]


def _money_tick(value: float, _position: int) -> str:
    return f"${value / 1000:.0f}k"


def _miles_tick(value: float, _position: int) -> str:
    if value == 0:
        return "0"
    return f"{value / 1000:.0f}k"


def _png_data_uri(fig: plt.Figure) -> str:
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", bbox_inches="tight", facecolor="white")
    plt.close(fig)
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def _style(ax: plt.Axes) -> None:
    ax.set_facecolor("white")
    ax.yaxis.grid(True, color="#e5e7eb", linewidth=0.8)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#d1d5db")
    ax.spines["bottom"].set_color("#d1d5db")
    ax.tick_params(colors="#6b7280", labelsize=8, length=0)


def depreciation_chart() -> str:
    labels = ["MSRP", "1 yr", "2 yr", "3 yr", "4 yr", "5 yr"]
    values = depreciation_values()
    heights = [value - VALUE_FLOOR for value in values]

    fig, ax = plt.subplots(figsize=(5.56, 2.72), dpi=120)
    bars = ax.bar(
        labels,
        heights,
        bottom=VALUE_FLOOR,
        color="#334155",
        width=0.62,
    )
    ax.set_ylim(VALUE_FLOOR, 34_000)
    ax.yaxis.set_major_formatter(FuncFormatter(_money_tick))
    ax.bar_label(
        bars,
        labels=[f"${value / 1000:.0f}k" for value in values],
        padding=3,
        fontsize=8,
        color="#6b7280",
    )
    _style(ax)
    fig.tight_layout()
    return _png_data_uri(fig)


def price_mileage_chart() -> str:
    mileages = [8_000, 18_000, 28_000, 38_000, 48_000, 55_000, 68_000, 78_000, 88_000, 42_000]
    prices = comparable_prices(mileages)

    fig, ax = plt.subplots(figsize=(5.56, 2.55), dpi=120)
    ax.scatter(
        mileages,
        prices,
        s=28,
        color="#9ca3af",
        label="Comparable listings",
        zorder=3,
    )
    ax.scatter(
        [SELECTED_MILEAGE],
        [SELECTED_PRICE],
        s=42,
        color="#111827",
        label="Selected BRZ",
        zorder=4,
    )
    ax.annotate(
        "$24k · 33k mi",
        (SELECTED_MILEAGE, SELECTED_PRICE),
        textcoords="offset points",
        xytext=(8, 4),
        fontsize=8,
        color="#111827",
        fontweight="bold",
    )
    ax.set_xlim(0, 100_000)
    ax.set_ylim(12_000, 32_000)
    ax.xaxis.set_major_formatter(FuncFormatter(_miles_tick))
    ax.yaxis.set_major_formatter(FuncFormatter(_money_tick))
    ax.legend(frameon=False, fontsize=8, labelcolor="#6b7280")
    _style(ax)
    fig.tight_layout()
    return _png_data_uri(fig)
