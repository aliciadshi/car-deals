import base64
import io

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter


ANNUAL_DROP = 3_000


def depreciation_values(msrp: int, years: int = 5) -> list[int]:
    """Resale value after each year, dropping a fixed amount from MSRP."""
    return [max(msrp - ANNUAL_DROP * year, 0) for year in range(years + 1)]


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


def depreciation_chart(msrp: int) -> str:
    labels = ["MSRP", "1 yr", "2 yr", "3 yr", "4 yr", "5 yr"]
    values = depreciation_values(msrp)

    fig, ax = plt.subplots(figsize=(5.56, 2.72), dpi=120)
    bars = ax.bar(labels, values, color="#334155", width=0.62)
    ax.set_ylim(0, max(values) * 1.15)
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


def price_mileage_chart(
    mileage: int,
    price: int,
    listings: list[dict],
) -> str:
    comparable = [
        (int(item["mileage"]), int(item["price"]))
        for item in listings
        if item.get("mileage") is not None and item.get("price") is not None
    ]
    mileages = [point[0] for point in comparable]
    prices = [point[1] for point in comparable]

    fig, ax = plt.subplots(figsize=(5.56, 2.55), dpi=120)
    if mileages:
        ax.scatter(
            mileages,
            prices,
            s=28,
            color="#9ca3af",
            label="Comparable listings",
            zorder=3,
        )
    ax.scatter(
        [mileage],
        [price],
        s=42,
        color="#111827",
        label="Selected car",
        zorder=4,
    )
    ax.annotate(
        f"${price / 1000:.0f}k · {mileage / 1000:.0f}k mi",
        (mileage, price),
        textcoords="offset points",
        xytext=(8, 4),
        fontsize=8,
        color="#111827",
        fontweight="bold",
    )
    xs = mileages + [mileage]
    ys = prices + [price]
    ax.set_xlim(0, max(xs) * 1.15)
    ax.set_ylim(0, max(ys) * 1.2)
    ax.xaxis.set_major_formatter(FuncFormatter(_miles_tick))
    ax.yaxis.set_major_formatter(FuncFormatter(_money_tick))
    ax.legend(frameon=False, fontsize=8, labelcolor="#6b7280")
    _style(ax)
    fig.tight_layout()
    return _png_data_uri(fig)
