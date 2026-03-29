from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
from matplotlib.patches import Patch
import pandas as pd
import seaborn as sns

DATA_DIR = Path(__file__).parent / "Whoop Data Mar 29 2026"
OUT_DIR = Path(__file__).parent / "graphs" / "vansh"

WEEK_LOW = ("2026-03-09", "2026-03-15")
WEEK_HIGH = ("2026-03-16", "2026-03-22")

LOW_LABEL = "Low Exercise\n(Mar 9 – 15)"
HIGH_LABEL = "High Exercise\n(Mar 16 – 22)"
ORDER = [LOW_LABEL, HIGH_LABEL]

PALETTE = {LOW_LABEL: "#5B9BD5", HIGH_LABEL: "#FF6B35"}
BG = "#0D1117"
CARD = "#161B22"
TEXT = "#E6EDF3"
GRID = "#30363D"
ACCENT_BLUE = "#5B9BD5"
ACCENT_ORANGE = "#FF6B35"


def setup_style():
    plt.rcParams.update({
        "figure.facecolor": BG,
        "axes.facecolor": CARD,
        "axes.edgecolor": GRID,
        "axes.labelcolor": TEXT,
        "axes.titlecolor": TEXT,
        "text.color": TEXT,
        "xtick.color": TEXT,
        "ytick.color": TEXT,
        "grid.color": GRID,
        "grid.alpha": 0.4,
        "figure.dpi": 150,
        "axes.titleweight": "bold",
        "axes.titlesize": 13,
        "axes.titlepad": 12,
        "axes.labelsize": 11,
        "axes.labelpad": 8,
        "font.family": "sans-serif",
        "legend.facecolor": CARD,
        "legend.edgecolor": GRID,
        "legend.labelcolor": TEXT,
    })
    sns.set_theme(style="darkgrid", rc=plt.rcParams)


def load_data():
    sleeps = pd.read_csv(DATA_DIR / "sleeps.csv", parse_dates=["Sleep onset", "Wake onset"])
    physio = pd.read_csv(
        DATA_DIR / "physiological_cycles.csv",
        parse_dates=["Cycle start time", "Cycle end time"],
    )
    workouts = pd.read_csv(DATA_DIR / "workouts.csv", parse_dates=["Workout start time", "Workout end time"])
    return sleeps, physio, workouts


def assign_date(df, date_col):
    df = df.copy()
    df["date"] = pd.to_datetime(df[date_col]).dt.normalize()
    return df


def tag_week(df):
    df = df.copy()
    low_mask = (df["date"] >= WEEK_LOW[0]) & (df["date"] <= WEEK_LOW[1])
    high_mask = (df["date"] >= WEEK_HIGH[0]) & (df["date"] <= WEEK_HIGH[1])
    df.loc[low_mask, "week"] = LOW_LABEL
    df.loc[high_mask, "week"] = HIGH_LABEL
    return df.dropna(subset=["week"])


def prepare_sleep(sleeps):
    df = sleeps[sleeps["Nap"] == False].copy()
    df = assign_date(df, "Wake onset")
    df = tag_week(df)
    df["Asleep duration (hr)"] = df["Asleep duration (min)"] / 60
    df["Deep (SWS) duration (hr)"] = df["Deep (SWS) duration (min)"] / 60
    df["REM duration (hr)"] = df["REM duration (min)"] / 60
    return df


def prepare_physio(physio):
    return tag_week(assign_date(physio, "Cycle start time"))


def prepare_workouts(workouts):
    return tag_week(assign_date(workouts, "Workout start time"))


def _style_ax(ax, title, ylabel):
    ax.set(title=title, xlabel="", ylabel=ylabel)
    ax.title.set_fontsize(13)
    ax.title.set_fontweight("bold")
    ax.tick_params(axis="both", which="both", length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)


def _add_mean_line(ax, data, col, order):
    for i, week in enumerate(order):
        subset = data[data["week"] == week][col].dropna()
        if len(subset):
            ax.hlines(subset.mean(), i - 0.25, i + 0.25, colors="white", linewidths=2, zorder=10)


def plot_workout_overview(workouts_tagged):
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    daily = workouts_tagged.groupby(["week", "date"]).agg(
        total_duration=("Duration (min)", "sum"),
        total_strain=("Activity Strain", "sum"),
    ).reset_index()

    for ax, col, title, ylabel in [
        (axes[0], "total_duration", "Total Workout Duration", "Minutes"),
        (axes[1], "total_strain", "Total Activity Strain", "Strain"),
    ]:
        bars = sns.barplot(
            data=daily, x="week", y=col, hue="week", estimator="sum", errorbar=None,
            palette=PALETTE, hue_order=ORDER, order=ORDER, ax=ax, edgecolor="none", width=0.55, legend=False,
        )
        _style_ax(ax, title, ylabel)
        for container in ax.containers:
            ax.bar_label(container, fmt="%.0f", fontweight="bold", padding=4, color=TEXT, fontsize=14)

    fig.suptitle("Exercise Volume Comparison", fontsize=17, fontweight="bold", color=TEXT, y=1.03)
    fig.tight_layout()
    return fig


def plot_sleep_comparison(sleep_tagged):
    fig, axes = plt.subplots(2, 2, figsize=(13, 9.5))

    metrics = [
        ("Sleep performance %", "Sleep Performance", "%", axes[0, 0]),
        ("Asleep duration (hr)", "Total Sleep Duration", "Hours", axes[0, 1]),
        ("Deep (SWS) duration (hr)", "Deep Sleep Duration", "Hours", axes[1, 0]),
        ("Sleep efficiency %", "Sleep Efficiency", "%", axes[1, 1]),
    ]

    for col, title, ylabel, ax in metrics:
        bp = sns.boxplot(
            data=sleep_tagged, x="week", y=col, hue="week", palette=PALETTE,
            hue_order=ORDER, order=ORDER, ax=ax, width=0.45, linewidth=1.5, fliersize=0,
            boxprops=dict(alpha=0.7), medianprops=dict(color="white", linewidth=2), legend=False,
        )
        sns.stripplot(
            data=sleep_tagged, x="week", y=col, hue="week", palette=PALETTE,
            hue_order=ORDER, order=ORDER, ax=ax, size=7, alpha=0.8,
            edgecolor="white", linewidth=0.5, jitter=0.15, legend=False,
        )
        _add_mean_line(ax, sleep_tagged, col, ORDER)
        _style_ax(ax, title, ylabel)

    fig.suptitle("Sleep Quality: Low vs High Exercise Week", fontsize=17, fontweight="bold", color=TEXT, y=1.01)
    fig.tight_layout()
    return fig


def plot_recovery_stress(physio_tagged):
    fig, axes = plt.subplots(2, 2, figsize=(13, 9.5))

    metrics = [
        ("Recovery score %", "Recovery Score", "%", axes[0, 0]),
        ("Heart rate variability (ms)", "Heart Rate Variability", "ms", axes[0, 1]),
        ("Resting heart rate (bpm)", "Resting Heart Rate", "bpm", axes[1, 0]),
        ("Day Strain", "Daily Strain", "Strain", axes[1, 1]),
    ]

    for col, title, ylabel, ax in metrics:
        sns.boxplot(
            data=physio_tagged, x="week", y=col, hue="week", palette=PALETTE,
            hue_order=ORDER, order=ORDER, ax=ax, width=0.45, linewidth=1.5, fliersize=0,
            boxprops=dict(alpha=0.7), medianprops=dict(color="white", linewidth=2), legend=False,
        )
        sns.stripplot(
            data=physio_tagged, x="week", y=col, hue="week", palette=PALETTE,
            hue_order=ORDER, order=ORDER, ax=ax, size=7, alpha=0.8,
            edgecolor="white", linewidth=0.5, jitter=0.15, legend=False,
        )
        _add_mean_line(ax, physio_tagged, col, ORDER)
        _style_ax(ax, title, ylabel)

    fig.suptitle("Stress & Recovery: Low vs High Exercise Week", fontsize=17, fontweight="bold", color=TEXT, y=1.01)
    fig.tight_layout()
    return fig


def plot_daily_timeline(sleep_tagged, physio_tagged):
    both = sleep_tagged.merge(
        physio_tagged[["date", "Recovery score %", "Heart rate variability (ms)", "Day Strain", "week"]],
        on=["date", "week"],
        how="inner",
    ).sort_values("date")

    fig, axes = plt.subplots(4, 1, figsize=(14, 13), sharex=True)
    color_map = {LOW_LABEL: ACCENT_BLUE, HIGH_LABEL: ACCENT_ORANGE}
    colors = both["week"].map(color_map)

    plots = [
        ("Sleep performance %", "Sleep Perf (%)", axes[0]),
        ("Recovery score %", "Recovery (%)", axes[1]),
        ("Heart rate variability (ms)", "HRV (ms)", axes[2]),
        ("Day Strain", "Day Strain", axes[3]),
    ]

    for col, ylabel, ax in plots:
        bars = ax.bar(both["date"], both[col], color=colors, alpha=0.9, width=0.65,
                      edgecolor="none")
        ax.set_ylabel(ylabel, fontsize=11, fontweight="bold")
        ax.axvline(pd.Timestamp("2026-03-16"), color="#8B949E", linestyle="--", linewidth=1.2, alpha=0.8)
        ax.tick_params(axis="both", length=0)
        for spine in ax.spines.values():
            spine.set_visible(False)

        for bar, val in zip(bars, both[col]):
            if pd.notna(val):
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                        f"{val:.0f}", ha="center", va="bottom", fontsize=7.5,
                        color=TEXT, alpha=0.7)

    axes[0].set_title("Daily Timeline Across Both Weeks", fontsize=17, fontweight="bold", color=TEXT, pad=15)
    axes[-1].xaxis.set_major_formatter(mdates.DateFormatter("%a\n%b %d"))
    axes[-1].xaxis.set_major_locator(mdates.DayLocator())
    plt.setp(axes[-1].xaxis.get_majorticklabels(), fontsize=8.5)

    legend_elements = [Patch(facecolor=ACCENT_BLUE, label="Low Exercise (Mar 9–15)", edgecolor="none"),
                       Patch(facecolor=ACCENT_ORANGE, label="High Exercise (Mar 16–22)", edgecolor="none")]
    axes[0].legend(handles=legend_elements, loc="upper right", framealpha=0.9, fontsize=10)

    fig.tight_layout(h_pad=1.5)
    return fig


def run():
    setup_style()
    sleeps, physio, workouts = load_data()

    sleep_tagged = prepare_sleep(sleeps)
    physio_tagged = prepare_physio(physio)
    workouts_tagged = prepare_workouts(workouts)

    print(f"[vansh] Sleep: {len(sleep_tagged)} | Physio: {len(physio_tagged)} | Workouts: {len(workouts_tagged)}")

    figs = {
        "workout_overview": plot_workout_overview(workouts_tagged),
        "sleep_comparison": plot_sleep_comparison(sleep_tagged),
        "recovery_stress": plot_recovery_stress(physio_tagged),
        "daily_timeline": plot_daily_timeline(sleep_tagged, physio_tagged),
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, fig in figs.items():
        fig.savefig(OUT_DIR / f"{name}.png", bbox_inches="tight", facecolor=fig.get_facecolor())

    print(f"[vansh] Saved {len(figs)} graphs to {OUT_DIR}")
    plt.show()