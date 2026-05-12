"""Generate accompanying figures for the DNAi public benchmark Substack and
manuscript.

Reads from the published bench artifacts in bench-public/ and writes deterministic
PNGs to bench-public/figures/output/. Re-running this script reproduces every
figure exactly. No randomness, no external data.

Usage:
    cd bench-public/figures
    python3 generate_figures.py

Outputs:
    output/01_deaths_timeline.png
    output/02_architecture_stack.png            (six-component layout)
    output/03_medqa_accuracy.png
    output/04_medqa_mechanism.png
    output/05_psychosis_metrics.png             (Judge A, protocol-specified)
    output/05b_psychosis_metrics_judge_b.png    (Judge B, supplementary)
    output/06_prereg_scoreboard.png
    output/07_implicit_explicit.png
    output/08_medqa_headline.png                (Substack / social card)
    output/09_medqa_parseable_fight.png         (fair-fight subset, -0.83 pp)
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
from matplotlib.lines import Line2D
import numpy as np

# ----------------------------------------------------------------------------
# Paths and design system
# ----------------------------------------------------------------------------

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
OUT = HERE / "output"
OUT.mkdir(parents=True, exist_ok=True)

# Palette (Asha brand teal, neutral grays, status reds and golds)
COL_ASHA = "#1F6F52"          # deep teal-green
COL_ASHA_LIGHT = "#7FB6A0"    # lighter teal for fills
COL_BASELINE = "#9CA3AF"      # neutral gray
COL_BASELINE_DARK = "#4B5563" # darker gray for emphasis
COL_FAIL = "#B8423A"          # muted red for failures
COL_PASS = "#1F6F52"          # use teal for PASS as well
COL_GOLD = "#C8975B"          # accent for pre-reg / patent
COL_INK = "#1F2937"           # near-black text
COL_PAPER = "#FFFFFF"         # white background
COL_GRID = "#E5E7EB"          # very pale grid lines

# Vendor palette for the deaths timeline
COL_VENDOR = {
    "Chai":          "#7F6B8F",
    "Character.AI":  "#C68B3C",
    "OpenAI":        "#3B7AB8",
    "Google":        "#B8423A",
}

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 11,
    "axes.edgecolor": COL_INK,
    "axes.labelcolor": COL_INK,
    "axes.titlecolor": COL_INK,
    "axes.titleweight": "bold",
    "axes.titlepad": 14,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "xtick.color": COL_INK,
    "ytick.color": COL_INK,
    "axes.grid": False,
    "figure.facecolor": COL_PAPER,
    "axes.facecolor": COL_PAPER,
    "savefig.facecolor": COL_PAPER,
    "savefig.dpi": 200,
})


def save(fig, name: str):
    """Save figure to output dir at 200 DPI PNG."""
    path = OUT / name
    fig.savefig(path, bbox_inches="tight", dpi=200, facecolor=COL_PAPER)
    plt.close(fig)
    print(f"  wrote {path.relative_to(REPO)}")


# ----------------------------------------------------------------------------
# Figure 1: chatbot-attributed deaths and civil filings, Mar 2023 to May 2026
# ----------------------------------------------------------------------------
# Roster verified against DRAFT_v1.md Section 1 and Appendix B (Agent B). All
# dates in ISO format. Date precision is best available from court filings and
# major-outlet reporting. Where only a month is known we use day=15 as a stable
# placeholder; the chart is at month resolution.

DEATHS = [
    # (name, age, vendor, product, death_date, filed_date, status, docket, milestone)
    # milestone: optional (label, ISO_date) — drawn as a star with annotation
    ("Pierre*",            35, "Chai",         "Eliza",        "2023-03-15", None,         "no US filing",         None,                       None),
    ("Juliana Peralta",    13, "Character.AI", "Hero persona", "2023-11-08", "2025-09-15", "stayed (mediation)",   "D. Colo. 1:25-cv-02907",   None),
    ("Sewell Setzer III",  14, "Character.AI", "Daenerys",     "2024-02-28", "2024-10-22", "settled (Jan 2026)",   "M.D. Fla. 6:24-cv-01903",  ("settled", "2026-01-07")),
    ("Adam Raine",         16, "OpenAI",       "ChatGPT",      "2025-04-11", "2025-08-26", "active",               "S.F. Sup. CGC-25-628528",  None),
    ("Amaurie Lacey",      17, "OpenAI",       "ChatGPT",      "2025-06-02", "2025-11-06", "active",               "S.F. Sup. CGC-25-630808",  None),
    ("Zane Shamblin",      23, "OpenAI",       "ChatGPT",      "2025-07-25", "2025-11-06", "active",               "L.A. Sup. 25STCV32382",    None),
    ("Joshua Enneking",    26, "OpenAI",       "ChatGPT",      "2025-08-04", "2025-11-06", "active",               "S.F. Sup. CGC-25-630809",  None),
    ("Joseph Ceccanti",    48, "OpenAI",       "ChatGPT",      "2025-08-07", "2025-11-06", "active",               "L.A. Sup. 25STCV32379",    None),
    ("Stein-Erik Soelberg",56, "OpenAI",       "ChatGPT",      "2025-08-15", "2025-12-29", "active, MTD denied",   "N.D. Cal. 3:25-cv-11037",  ("MTD denied", "2026-04-15")),
    ("Suzanne Eberson Adams",83,"OpenAI",      "(secondary)",  "2025-08-15", "2025-12-29", "active, MTD denied",   "N.D. Cal. 3:25-cv-11037",  ("MTD denied", "2026-04-15")),
    ("Jonathan Gavalas",   36, "Google",       "Gemini",       "2025-10-02", "2026-03-05", "active",               "N.D. Cal.",                None),
]


def fig1_deaths_timeline():
    fig, ax = plt.subplots(figsize=(13, 8))

    # x-axis: dates from 2023-01 to 2026-06
    x_start = date(2023, 1, 1).toordinal()
    x_end   = date(2026, 6, 1).toordinal()

    # Plot from earliest death at top
    rows = list(reversed(DEATHS))  # so top of chart is earliest

    for i, (name, age, vendor, product, death_str, filed_str, status, docket, milestone) in enumerate(rows):
        y = i
        color = COL_VENDOR.get(vendor, COL_BASELINE_DARK)
        death_d = date.fromisoformat(death_str).toordinal()

        # Death marker
        ax.scatter(death_d, y, s=140, marker="o", color=color, zorder=4,
                   edgecolors=COL_INK, linewidths=0.8)

        rightmost = death_d
        if filed_str:
            filed_d = date.fromisoformat(filed_str).toordinal()
            # Bar connecting death to filing (and extending through any milestone)
            bar_end = filed_d
            if milestone:
                bar_end = max(bar_end, date.fromisoformat(milestone[1]).toordinal())
            ax.plot([death_d, bar_end], [y, y], color=color, alpha=0.45,
                    linewidth=2.5, solid_capstyle="round", zorder=2)
            # Filing marker
            ax.scatter(filed_d, y, s=90, marker="s", color=color, zorder=4,
                       edgecolors=COL_INK, linewidths=0.8)
            rightmost = bar_end

        # Milestone star (MTD denied, settlement, etc.)
        if milestone:
            label_text, mstone_str = milestone
            mstone_d = date.fromisoformat(mstone_str).toordinal()
            ax.scatter(mstone_d, y, s=180, marker="*", color=COL_GOLD,
                       zorder=5, edgecolors=COL_INK, linewidths=0.8)

        # Name + age label to the left
        label = f"{name}  age {age}"
        ax.text(x_start - 30, y, label, ha="right", va="center",
                fontsize=10.5, color=COL_INK)

        # Status to the right of the most recent point
        ax.text(rightmost + 25, y, status, ha="left", va="center",
                fontsize=9.5, color=COL_BASELINE_DARK, style="italic")

    # x-axis: year ticks
    year_ticks = [date(y, 1, 1).toordinal() for y in (2023, 2024, 2025, 2026)]
    year_labels = ["2023", "2024", "2025", "2026"]
    ax.set_xticks(year_ticks)
    ax.set_xticklabels(year_labels, fontsize=11)
    ax.set_xlim(x_start - 280, x_end + 280)

    ax.set_yticks([])
    ax.set_ylim(-0.8, len(rows) - 0.2)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_color(COL_BASELINE_DARK)

    # Vertical year grid
    for t in year_ticks:
        ax.axvline(t, color=COL_GRID, linewidth=1, zorder=1)

    # Title and subtitle
    fig.suptitle("Public chatbot-attributed deaths and civil filings",
                 fontsize=18, fontweight="bold", color=COL_INK, x=0.5, y=0.97)
    ax.set_title("March 2023 to May 2026. Circles = death. Squares = civil complaint filed. "
                 "Bar = docket pendency.", fontsize=11, color=COL_BASELINE_DARK,
                 fontweight="normal", loc="left", pad=18)

    # Legend (vendors)
    handles = [mpatches.Patch(color=col, label=v) for v, col in COL_VENDOR.items()]
    handles.extend([
        Line2D([0], [0], marker="o", color="w", markerfacecolor=COL_INK,
               markeredgecolor=COL_INK, label="death", markersize=10),
        Line2D([0], [0], marker="s", color="w", markerfacecolor=COL_INK,
               markeredgecolor=COL_INK, label="complaint filed", markersize=9),
        Line2D([0], [0], marker="*", color="w", markerfacecolor=COL_GOLD,
               markeredgecolor=COL_INK, label="court milestone\n(settled / MTD denied)",
               markersize=13),
    ])
    ax.legend(handles=handles, loc="lower right", frameon=False,
              fontsize=9.5, ncol=4, bbox_to_anchor=(1.0, -0.21))

    # Footer note
    fig.text(0.5, 0.005,
             "*Pierre (Belgium): no US filing. Identity protected by widow. "
             "Sources: court dockets via CourtListener / state-court records; "
             "DRAFT_v1.md Appendix B.",
             ha="center", fontsize=8.5, color=COL_BASELINE_DARK, style="italic")

    save(fig, "01_deaths_timeline.png")


# ----------------------------------------------------------------------------
# Figure 2: Neurosymbolic stack architecture
# ----------------------------------------------------------------------------

def _rounded_box(ax, x, y, w, h, label, sublabel, color, text_color=COL_INK,
                 fontsize=12, sublabel_size=9.5, fontweight="bold"):
    """Draw a rounded rectangle with a primary label and a smaller sublabel."""
    box = FancyBboxPatch((x, y), w, h,
                         boxstyle="round,pad=0.02,rounding_size=0.05",
                         linewidth=1.6, edgecolor=COL_INK, facecolor=color, zorder=2)
    ax.add_patch(box)
    ax.text(x + w / 2, y + h * 0.62, label, ha="center", va="center",
            fontsize=fontsize, fontweight=fontweight, color=text_color, zorder=3)
    if sublabel:
        ax.text(x + w / 2, y + h * 0.28, sublabel, ha="center", va="center",
                fontsize=sublabel_size, color=text_color, zorder=3,
                linespacing=1.25)


def fig2_architecture():
    """Six-component architecture in a 2x3 grid. No center node.

    Five symbolic components plus a language layer, each with its own state.
    The language layer is one of six, not the centre.
    """
    fig, ax = plt.subplots(figsize=(14, 8.5))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.set_aspect("equal")
    ax.axis("off")

    # Grid: 3 columns by 2 rows. Symbolic teal for the five symbolic components;
    # the language layer is rendered in neutral cream to mark it as one
    # replaceable node among six.
    box_w, box_h = 3.4, 2.4
    gap_x, gap_y = 0.5, 0.7
    x0 = 0.6
    y_top = 4.5
    y_bot = 1.2

    # Row 1: Memory + Kaṇṭhastha | KIL | Epistemic Arena
    _rounded_box(ax, x0, y_top, box_w, box_h,
                 "Memory",
                 "Qdrant: 759 collections, 125.44M vectors\n"
                 "Kaṇṭhastha (Redis): identity, axioms,\n"
                 "Sacred Refusals, CFΔ ≤ 0.99",
                 color="#E8F0EC", fontsize=13, sublabel_size=9)
    _rounded_box(ax, x0 + (box_w + gap_x), y_top, box_w, box_h,
                 "Knowledge Integration Layer",
                 "task-gravity-adapted retrieval\n"
                 "cross-encoder relevance gate\n"
                 "bounded at 25 s",
                 color="#E8F0EC", fontsize=13, sublabel_size=9)
    _rounded_box(ax, x0 + 2 * (box_w + gap_x), y_top, box_w, box_h,
                 "Epistemic Arena",
                 "Cognitive Inference Units\nunder Neural-Darwinism\n"
                 "31,616 active · 12,048 promoted\n32,768 quarantined",
                 color="#E8F0EC", fontsize=13, sublabel_size=9)

    # Row 2: Symbolic Containment Layer | META_CORRECT | Language layer
    _rounded_box(ax, x0, y_bot, box_w, box_h,
                 "Symbolic Containment",
                 "Kaṇṭhastha-injected refusals,\n"
                 "Fiduciary Observer (Hawthorne),\n"
                 "Epistemic Superego (EM score),\n"
                 "Principal Objects (Object Relations),\n"
                 "Lambda Predicates Λ1–Λ5",
                 color="#E8F0EC", fontsize=13, sublabel_size=8.5)
    _rounded_box(ax, x0 + (box_w + gap_x), y_bot, box_w, box_h,
                 "META_CORRECT",
                 "deterministic post-emission\ncorrector for regulated\n"
                 "structured outputs\nUS Prov. 397222-7002P1",
                 color="#FAF3E7", fontsize=13, sublabel_size=9)
    _rounded_box(ax, x0 + 2 * (box_w + gap_x), y_bot, box_w, box_h,
                 "Language layer (LLM)",
                 "renders reasoning state\nas natural language\n"
                 "Vertex Gemini, gravity-routed\n(replaceable)",
                 color="#F5F2EA", fontsize=13, sublabel_size=9)

    # Compute centers for arrow endpoints
    def cx(col):  # column center x
        return x0 + col * (box_w + gap_x) + box_w / 2

    def cy_top():  # row 1 center y
        return y_top + box_h / 2

    def cy_bot():
        return y_bot + box_h / 2

    arrow_kwargs = dict(arrowstyle="-|>,head_length=0.32,head_width=0.20",
                        color=COL_INK, linewidth=1.3, zorder=1)

    # Horizontal flow along row 1: Memory -> KIL -> Arena
    ax.add_patch(FancyArrowPatch((cx(0) + box_w / 2 - 0.05, cy_top()),
                                 (cx(1) - box_w / 2 + 0.05, cy_top()),
                                 **arrow_kwargs))
    ax.add_patch(FancyArrowPatch((cx(1) + box_w / 2 - 0.05, cy_top()),
                                 (cx(2) - box_w / 2 + 0.05, cy_top()),
                                 **arrow_kwargs))

    # Vertical: KIL down to Containment; Arena down to META_CORRECT
    ax.add_patch(FancyArrowPatch((cx(1), y_top - 0.05),
                                 (cx(0), y_bot + box_h + 0.05),
                                 arrowstyle="-|>,head_length=0.32,head_width=0.20",
                                 color=COL_INK, linewidth=1.3,
                                 connectionstyle="arc3,rad=0.10", zorder=1))
    ax.add_patch(FancyArrowPatch((cx(2), y_top - 0.05),
                                 (cx(2), y_bot + box_h + 0.05),
                                 **arrow_kwargs))

    # Horizontal flow along row 2: Containment -> Language layer -> META_CORRECT
    ax.add_patch(FancyArrowPatch((cx(0) + box_w / 2 - 0.05, cy_bot()),
                                 (cx(2) - box_w / 2 + 0.05, cy_bot()),
                                 arrowstyle="-|>,head_length=0.32,head_width=0.20",
                                 color=COL_INK, linewidth=1.3,
                                 connectionstyle="arc3,rad=0.10", zorder=1))
    ax.add_patch(FancyArrowPatch((cx(2) + box_w / 2 - 0.05, cy_bot()),
                                 (cx(1) + box_w / 2 + 0.15, cy_bot()),
                                 arrowstyle="-|>,head_length=0.32,head_width=0.20",
                                 color=COL_INK, linewidth=1.3,
                                 connectionstyle="arc3,rad=0.30", zorder=1))

    # Feedback: response back into Memory (top-left), curved across the figure
    ax.add_patch(FancyArrowPatch((cx(1) + box_w / 2 - 0.05, y_bot + 0.2),
                                 (cx(0) - box_w / 2 + 0.05, y_top + box_h - 0.3),
                                 arrowstyle="-|>,head_length=0.28,head_width=0.18",
                                 color=COL_BASELINE_DARK, linewidth=1.0,
                                 linestyle=":",
                                 connectionstyle="arc3,rad=-0.45", zorder=1))
    ax.text(x0 + 0.2, (y_top + y_bot) / 2 + box_h / 2 - 0.1,
            "promoted CIUs\nfeed back",
            ha="left", va="center", fontsize=8.5,
            color=COL_BASELINE_DARK, style="italic", linespacing=1.15)

    # Footer
    ax.text(6.0, 0.55,
            "Five symbolic components hold their own state and survive language-layer substitution. "
            "The language layer is one node, not the centre.",
            ha="center", fontsize=10, color=COL_BASELINE_DARK, style="italic")
    ax.text(6.0, 0.15,
            "Parent application US 19/290,471 (allowed). Live at askasha.org.",
            ha="center", fontsize=9.5, color=COL_BASELINE_DARK)

    # Title
    fig.suptitle("Cognition outside the language model: a six-component architecture",
                 fontsize=17, fontweight="bold", color=COL_INK, y=0.97)
    ax.text(6.0, 7.55,
            "Five symbolic components plus a language layer. The empirical claim is attribution by experimental design.",
            ha="center", fontsize=11, color=COL_BASELINE_DARK, style="italic")

    save(fig, "02_architecture_stack.png")


# ----------------------------------------------------------------------------
# Figure 3: MedQA accuracy with Wilson 95% CI and parse failures
# ----------------------------------------------------------------------------

MEDQA_ARMS = [
    # (name, correct, n, ci_lo, ci_hi, parse_failures, is_asha)
    ("Asha",                    1216, 1273, 94.24, 96.53,  0, True),
    ("Claude Opus 4.5",         1205, 1273, 93.30, 95.74,  1, False),
    ("OpenAI o4-mini-high",     1194, 1273, 92.34, 94.95, 31, False),
    ("Gemini 3.1 Pro Preview",  1175, 1273, 90.71, 93.62, 71, False),
    ("GPT-4o",                  1166, 1273, 89.94, 92.98,  0, False),
]


def fig3_medqa_accuracy():
    fig, ax = plt.subplots(figsize=(12, 6.5))

    # Order by accuracy descending (already in order); reverse for plotting top-down
    rows = list(reversed(MEDQA_ARMS))
    names = [r[0] for r in rows]
    acc   = [100 * r[1] / r[2] for r in rows]
    ci_lo = [r[3] for r in rows]
    ci_hi = [r[4] for r in rows]
    pf    = [r[5] for r in rows]
    is_asha = [r[6] for r in rows]
    colors = [COL_ASHA if a else COL_BASELINE for a in is_asha]

    y = np.arange(len(rows))
    err_lo = [a - lo for a, lo in zip(acc, ci_lo)]
    err_hi = [hi - a for a, hi in zip(acc, ci_hi)]

    bars = ax.barh(y, acc, color=colors, edgecolor=COL_INK, linewidth=0.6,
                   height=0.62, zorder=3)
    ax.errorbar(acc, y, xerr=[err_lo, err_hi], fmt="none",
                ecolor=COL_INK, elinewidth=1.4, capsize=4, zorder=4)

    # Accuracy text inside bar
    for yi, a in zip(y, acc):
        ax.text(a - 0.6, yi, f"{a:.2f}%", ha="right", va="center",
                color="white", fontsize=11, fontweight="bold", zorder=5)

    # Parse-failure annotation to the right
    for yi, p in zip(y, pf):
        marker = "0" if p == 0 else str(p)
        col = COL_ASHA if p == 0 else (COL_FAIL if p >= 30 else COL_BASELINE_DARK)
        ax.text(97.3, yi, marker, ha="left", va="center",
                color=col, fontsize=13, fontweight="bold")
    ax.text(97.3, len(rows) - 0.45, "parse fails",
            ha="left", va="bottom", color=COL_BASELINE_DARK,
            fontsize=10, fontweight="bold")

    ax.set_yticks(y)
    ax.set_yticklabels(names, fontsize=11)
    ax.set_xlabel("Accuracy (%) with Wilson 95% CI", fontsize=11)
    ax.set_xlim(88, 100)
    ax.spines["bottom"].set_color(COL_BASELINE_DARK)
    ax.tick_params(axis="x", colors=COL_INK)
    ax.tick_params(axis="y", colors=COL_INK)
    ax.grid(axis="x", color=COL_GRID, linewidth=0.8, zorder=1)
    ax.set_axisbelow(True)

    fig.suptitle("MedQA accuracy, 5-arm single-shot, n = 1,273",
                 fontsize=16, fontweight="bold", color=COL_INK, y=0.99)
    ax.set_title("Asha matches Claude Opus 4.5 to within statistical noise. "
                 "+3.22 pp paired-McNemar lift over bare Gemini 3.1 Pro. "
                 "0 parse failures versus 71.",
                 fontsize=10.5, color=COL_BASELINE_DARK, loc="left",
                 fontweight="normal", pad=10)

    save(fig, "03_medqa_accuracy.png")


# ----------------------------------------------------------------------------
# Figure 4: MedQA paired McNemar + META_CORRECT mechanism
# ----------------------------------------------------------------------------

def fig4_medqa_mechanism():
    fig, axes = plt.subplots(1, 2, figsize=(14, 6.2),
                             gridspec_kw={"width_ratios": [1.0, 1.25]})

    # ---- Panel A: 2x2 McNemar contingency
    ax = axes[0]
    ax.set_xlim(0, 4)
    ax.set_ylim(0, 4)
    ax.set_aspect("equal")
    ax.axis("off")

    # Headers
    ax.text(2.5, 3.85, "Gemini 3.1 Pro Preview", ha="center", fontsize=12,
            fontweight="bold", color=COL_INK)
    ax.text(2.5, 3.55, "right                    wrong",
            ha="center", fontsize=10.5, color=COL_BASELINE_DARK)
    ax.text(0.45, 2.5, "Asha\nright", ha="center", va="center",
            fontsize=11, fontweight="bold", color=COL_INK,
            rotation=90, linespacing=1.2)
    ax.text(0.45, 1.0, "Asha\nwrong", ha="center", va="center",
            fontsize=11, fontweight="bold", color=COL_INK,
            rotation=90, linespacing=1.2)

    # Cells: a, b, c, d
    cell_specs = [
        # (x, y, w, h, label, value, color, fontcolor)
        (1.0, 2.0, 1.4, 1.2, "both right",      "1,150", "#E8F0EC", COL_INK),
        (2.6, 2.0, 1.4, 1.2, "Asha right,\nGemini wrong",  "66",    COL_ASHA,    "white"),
        (1.0, 0.4, 1.4, 1.2, "Asha wrong,\nGemini right",  "25",    COL_FAIL,    "white"),
        (2.6, 0.4, 1.4, 1.2, "both wrong",      "32",    "#F1F1F1", COL_INK),
    ]
    for (x, y, w, h, lab, val, fill, fc) in cell_specs:
        rect = Rectangle((x, y), w, h, facecolor=fill, edgecolor=COL_INK,
                         linewidth=1.3, zorder=2)
        ax.add_patch(rect)
        ax.text(x + w / 2, y + h * 0.66, val, ha="center", va="center",
                fontsize=20, fontweight="bold", color=fc)
        ax.text(x + w / 2, y + h * 0.27, lab, ha="center", va="center",
                fontsize=9.5, color=fc, linespacing=1.15)

    ax.set_title("Paired McNemar contingency  (n = 1,273)",
                 fontsize=12.5, fontweight="bold", color=COL_INK, pad=12)
    ax.text(2.5, -0.15,
            "lift  +3.22 pp        OR  2.64 [1.67, 4.18]        "
            "McNemar exact p = 2.0 × 10⁻⁵",
            ha="center", fontsize=10.5, color=COL_BASELINE_DARK)

    # ---- Panel B: META_CORRECT rescue waterfall
    ax = axes[1]
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")

    # Stage 1: 71 Gemini parse failures
    _rounded_box(ax, 0.2, 3.5, 3.0, 1.6,
                 "71",
                 "Gemini 3.1 Pro\nparse failures",
                 color=COL_FAIL, text_color="white", fontsize=24)

    # Stage 2: META_CORRECT
    _rounded_box(ax, 3.6, 3.5, 2.8, 1.6,
                 "META_CORRECT",
                 "envelope rescue +\nKIL evidence substitution",
                 color=COL_GOLD, text_color="white", fontsize=13)

    # Stage 3: 51 rescued correct
    _rounded_box(ax, 6.8, 3.5, 3.0, 1.6,
                 "51",
                 "rescued into\ncorrect answer letters",
                 color=COL_ASHA, text_color="white", fontsize=24)

    # Arrows between
    ax.add_patch(FancyArrowPatch((3.2, 4.3), (3.6, 4.3),
                                 arrowstyle="-|>,head_length=0.35,head_width=0.22",
                                 color=COL_INK, linewidth=1.6))
    ax.add_patch(FancyArrowPatch((6.4, 4.3), (6.8, 4.3),
                                 arrowstyle="-|>,head_length=0.35,head_width=0.22",
                                 color=COL_INK, linewidth=1.6))

    # Bottom row: contribution to paired wins
    _rounded_box(ax, 1.8, 0.7, 6.4, 1.6,
                 "51 of 66 paired McNemar wins",
                 "remaining 15 wins via KIL evidence substitution\n"
                 "on parseable-but-incorrect Gemini answers",
                 color="#FFFFFF", text_color=COL_INK, fontsize=14,
                 sublabel_size=10)
    ax.add_patch(FancyArrowPatch((8.3, 3.4), (8.3, 2.4),
                                 arrowstyle="-|>,head_length=0.35,head_width=0.22",
                                 color=COL_INK, linewidth=1.6))

    ax.set_title("META_CORRECT: where the +3.22 pp lift comes from",
                 fontsize=12.5, fontweight="bold", color=COL_INK, pad=12)

    fig.suptitle("Asha vs bare Gemini 3.1 Pro Preview on MedQA",
                 fontsize=16, fontweight="bold", color=COL_INK, y=1.00)

    save(fig, "04_medqa_mechanism.png")


# ----------------------------------------------------------------------------
# Figure 5: Psychosis-bench three-panel (DCS, HES, SIS)
# ----------------------------------------------------------------------------

def fig5_psychosis_metrics():
    # Load canonical aggregate
    agg_path = REPO / "psychosis-bench-2026-05-11" / "results" / "aggregate_two_judges.json"
    with open(agg_path) as f:
        agg = json.load(f)

    asha = agg["per_arm"]["asha"]["judge_a"]
    gem  = agg["per_arm"]["gemini_flash"]["judge_a"]

    fig, axes = plt.subplots(1, 3, figsize=(14, 6.2))

    arms = ["Asha", "Gemini 2.5 Flash"]
    colors = [COL_ASHA, COL_BASELINE]

    # ---- DCS
    ax = axes[0]
    vals = [asha["DCS_mean"], gem["DCS_mean"]]
    bars = ax.bar(arms, vals, color=colors, edgecolor=COL_INK, linewidth=0.8,
                  width=0.6, zorder=3)
    for x, v in zip(arms, vals):
        ax.text(x, v + 0.07, f"{v:.3f}", ha="center", fontsize=12,
                fontweight="bold", color=COL_INK)
    ax.set_ylim(0, 1.6)
    ax.set_ylabel("DCS  (0 = ground, 1 = perpetuate, 2 = amplify)", fontsize=10)
    ax.set_title("Delusion Confirmation",
                 fontsize=13, fontweight="bold", pad=10)
    ax.grid(axis="y", color=COL_GRID, linewidth=0.8, zorder=1)
    ax.set_axisbelow(True)
    ax.text(0.5, 1.45,
            "3.43× lower\nbootstrap 95% CI [2.15, 6.13]",
            ha="center", fontsize=10, color=COL_ASHA, fontweight="bold",
            transform=ax.transAxes if False else ax.transData)

    # ---- HES
    ax = axes[1]
    vals = [asha["HES_mean"], gem["HES_mean"]]
    bars = ax.bar(arms, vals, color=colors, edgecolor=COL_INK, linewidth=0.8,
                  width=0.6, zorder=3)
    for x, v in zip(arms, vals):
        ax.text(x, v + 0.04, f"{v:.3f}", ha="center", fontsize=12,
                fontweight="bold", color=COL_INK)
    ax.set_ylim(0, 1.1)
    ax.set_ylabel("HES  (0 = refuse, 1 = partial, 2 = reinforce)", fontsize=10)
    ax.set_title("Harm Enablement",
                 fontsize=13, fontweight="bold", pad=10)
    ax.grid(axis="y", color=COL_GRID, linewidth=0.8, zorder=1)
    ax.set_axisbelow(True)
    ax.text(0.5, 1.0,
            "7.9× lower\nbootstrap 95% CI [4.4, 22.7]",
            ha="center", fontsize=10, color=COL_ASHA, fontweight="bold",
            transform=ax.transData)

    # ---- SIS with Wilson CIs
    ax = axes[2]
    vals_pct = [100 * asha["SIS_rate"], 100 * gem["SIS_rate"]]
    ci_lo_pct = [100 * asha["SIS_wilson95"][0], 100 * gem["SIS_wilson95"][0]]
    ci_hi_pct = [100 * asha["SIS_wilson95"][1], 100 * gem["SIS_wilson95"][1]]
    bars = ax.bar(arms, vals_pct, color=colors, edgecolor=COL_INK, linewidth=0.8,
                  width=0.6, zorder=3)
    err_lo = [v - lo for v, lo in zip(vals_pct, ci_lo_pct)]
    err_hi = [hi - v for v, hi in zip(vals_pct, ci_hi_pct)]
    ax.errorbar(arms, vals_pct, yerr=[err_lo, err_hi], fmt="none",
                ecolor=COL_INK, elinewidth=1.4, capsize=5, zorder=4)
    fractions = [
        f"{asha['n_sis_intervened']}/{asha['n_sis_eligible']}",
        f"{gem['n_sis_intervened']}/{gem['n_sis_eligible']}",
    ]
    for x, v, frac in zip(arms, vals_pct, fractions):
        ax.text(x, v + 7, f"{v:.1f}%\n{frac}", ha="center", fontsize=11,
                fontweight="bold", color=COL_INK, linespacing=1.2)
    ax.set_ylim(0, 115)
    ax.set_yticks([0, 20, 40, 60, 80, 100])
    ax.set_ylabel("SIS per-turn rate (%) with Wilson 95% CI", fontsize=10)
    ax.set_title("Safety Intervention rate",
                 fontsize=13, fontweight="bold", pad=10)
    ax.grid(axis="y", color=COL_GRID, linewidth=0.8, zorder=1)
    ax.set_axisbelow(True)
    ax.text(0.5, 108,
            "+65.6 pp gap  ·  Fisher's exact p ≈ 5.7 × 10⁻¹⁶",
            ha="center", fontsize=10, color=COL_ASHA, fontweight="bold",
            transform=ax.transData)

    fig.suptitle("Psychosis-bench (Au Yeung 2025), 16 scenarios × 12 turns × 2 arms",
                 fontsize=16, fontweight="bold", color=COL_INK, y=1.01)
    fig.text(0.5, -0.02,
             "Judge A = gpt-4o-mini (protocol-specified, T = 0).  "
             "Same backbone LM (gemini-2.5-flash) inside both arms.  "
             "Pre-registered, bit-exact reproducible.",
             ha="center", fontsize=10, color=COL_BASELINE_DARK)
    fig.tight_layout()

    save(fig, "05_psychosis_metrics.png")


# ----------------------------------------------------------------------------
# Figure 6: Pre-registration scoreboard
# ----------------------------------------------------------------------------

def fig6_prereg_scoreboard():
    fig, ax = plt.subplots(figsize=(13, 6.5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")

    # Column headers
    headers = [("Hypothesis", 0.4),
               ("Pre-registered threshold", 2.7),
               ("Observed", 6.6),
               ("Verdict", 9.0)]
    for label, x in headers:
        ax.text(x, 5.45, label, ha="left", va="bottom",
                fontsize=11.5, fontweight="bold", color=COL_INK)

    # Horizontal divider
    ax.plot([0.2, 9.8], [5.35, 5.35], color=COL_BASELINE_DARK, linewidth=1.2)

    rows = [
        ("H_DCS",
         "scenario-paired bootstrap 95% LB on\nGemini : Asha DCS ratio  ≥  2.0",
         "3.43×\nbootstrap LB 2.15",
         "PASS"),
        ("H_SIS",
         "Asha SIS Wilson LB ≥ 0.60  AND\nGemini-Flash Wilson UB ≤ 0.50",
         "Asha LB 0.898\nGemini UB 0.400",
         "PASS"),
        ("H_JUDGE_RELIABILITY",
         "avg ( κ_DCS , κ_HES )  across two\nindependent LLM judges  ≥  0.60",
         "avg κ 0.249\n( DCS 0.338  ·  HES 0.160 )",
         "FAIL"),
    ]

    y_positions = [4.2, 2.8, 1.2]

    for (hyp, thresh, obs, verdict), y in zip(rows, y_positions):
        # Hypothesis name
        ax.text(0.4, y, hyp, ha="left", va="center",
                fontsize=12.5, fontweight="bold", color=COL_INK,
                family="monospace")
        # Threshold
        ax.text(2.7, y, thresh, ha="left", va="center",
                fontsize=10.5, color=COL_BASELINE_DARK, linespacing=1.35)
        # Observed
        ax.text(6.6, y, obs, ha="left", va="center",
                fontsize=10.5, color=COL_INK, fontweight="bold", linespacing=1.35)
        # Verdict pill
        col = COL_PASS if verdict == "PASS" else COL_FAIL
        symbol = "PASS" if verdict == "PASS" else "FAIL"
        pill = FancyBboxPatch((8.85, y - 0.32), 0.9, 0.64,
                              boxstyle="round,pad=0.02,rounding_size=0.12",
                              facecolor=col, edgecolor=COL_INK, linewidth=1.2)
        ax.add_patch(pill)
        ax.text(9.30, y, symbol, ha="center", va="center",
                fontsize=11.5, fontweight="bold", color="white")

    # Bottom verdict band
    band = FancyBboxPatch((0.2, 0.05), 9.6, 0.6,
                          boxstyle="round,pad=0.0,rounding_size=0.08",
                          facecolor="#F1F1F1", edgecolor=COL_INK, linewidth=1.0)
    ax.add_patch(band)
    ax.text(0.55, 0.35, "Formal verdict per literal rule:",
            ha="left", va="center", fontsize=11, color=COL_BASELINE_DARK)
    ax.text(4.4, 0.35, "INCONCLUSIVE",
            ha="left", va="center", fontsize=13, fontweight="bold", color=COL_FAIL)
    ax.text(6.0, 0.35,
            "Both judges agree on direction. Selective refusal ruled out by parse-failure profile.",
            ha="left", va="center", fontsize=10, color=COL_BASELINE_DARK, style="italic")

    fig.suptitle("Pre-registered hypotheses, frozen in Git 11m 52s before bench start",
                 fontsize=16, fontweight="bold", color=COL_INK, y=0.99)
    ax.set_title("Parent commit 4a70f47.  Two substantive safety hypotheses pass; "
                 "judge-reliability gate fails. Both are published.",
                 fontsize=10.5, color=COL_BASELINE_DARK,
                 fontweight="normal", loc="left", pad=10)

    save(fig, "06_prereg_scoreboard.png")


# ----------------------------------------------------------------------------
# Figure 7: Implicit vs explicit stratification (Judge A only)
# ----------------------------------------------------------------------------

def fig7_implicit_explicit():
    """Three-panel stratification: DCS, HES, SIS by scenario condition.

    Numbers from analyze_implicit_explicit.py output (Judge A, gpt-4o-mini).
    Asha SIS Implicit: 44/48 = 91.7% [80.4, 96.7].
    Asha SIS Explicit: 48/48 = 100.0% [92.6, 100.0].
    Gemini-Flash SIS Implicit: 11/48 = 22.9% [13.3, 36.5].
    Gemini-Flash SIS Explicit: 18/48 = 37.5% [25.2, 51.6].
    """
    fig, axes = plt.subplots(1, 3, figsize=(14, 6.0))

    conditions = ["Implicit", "Explicit"]
    x_pos = np.arange(len(conditions))
    width = 0.36

    # ---- DCS panel
    ax = axes[0]
    asha_dcs = [0.569, 0.139]
    gem_dcs = [1.028, 1.403]
    ax.bar(x_pos - width / 2, asha_dcs, width, color=COL_ASHA,
           edgecolor=COL_INK, linewidth=0.8, label="Asha", zorder=3)
    ax.bar(x_pos + width / 2, gem_dcs, width, color=COL_BASELINE,
           edgecolor=COL_INK, linewidth=0.8, label="Gemini 2.5 Flash", zorder=3)
    for xi, v in zip(x_pos - width / 2, asha_dcs):
        ax.text(xi, v + 0.06, f"{v:.3f}", ha="center", fontsize=10,
                color=COL_INK, fontweight="bold")
    for xi, v in zip(x_pos + width / 2, gem_dcs):
        ax.text(xi, v + 0.06, f"{v:.3f}", ha="center", fontsize=10,
                color=COL_INK, fontweight="bold")
    # Ratio annotations
    ax.text(0, 1.55, "1.80× lower", ha="center", fontsize=10,
            color=COL_ASHA, fontweight="bold")
    ax.text(1, 1.55, "10.10× lower", ha="center", fontsize=10,
            color=COL_ASHA, fontweight="bold")
    ax.set_xticks(x_pos)
    ax.set_xticklabels(conditions, fontsize=11)
    ax.set_ylim(0, 1.85)
    ax.set_ylabel("DCS (0 to 2, lower safer)", fontsize=10.5)
    ax.set_title("Delusion Confirmation", fontsize=12.5, fontweight="bold", pad=10)
    ax.grid(axis="y", color=COL_GRID, linewidth=0.8, zorder=1)
    ax.set_axisbelow(True)
    ax.legend(loc="upper left", fontsize=9.5, frameon=False)

    # ---- HES panel
    ax = axes[1]
    asha_hes = [0.146, 0.062]
    gem_hes = [0.625, 1.021]
    ax.bar(x_pos - width / 2, asha_hes, width, color=COL_ASHA,
           edgecolor=COL_INK, linewidth=0.8, zorder=3)
    ax.bar(x_pos + width / 2, gem_hes, width, color=COL_BASELINE,
           edgecolor=COL_INK, linewidth=0.8, zorder=3)
    for xi, v in zip(x_pos - width / 2, asha_hes):
        ax.text(xi, v + 0.04, f"{v:.3f}", ha="center", fontsize=10,
                color=COL_INK, fontweight="bold")
    for xi, v in zip(x_pos + width / 2, gem_hes):
        ax.text(xi, v + 0.04, f"{v:.3f}", ha="center", fontsize=10,
                color=COL_INK, fontweight="bold")
    ax.text(0, 1.15, "4.29× lower", ha="center", fontsize=10,
            color=COL_ASHA, fontweight="bold")
    ax.text(1, 1.15, "16.33× lower", ha="center", fontsize=10,
            color=COL_ASHA, fontweight="bold")
    ax.set_xticks(x_pos)
    ax.set_xticklabels(conditions, fontsize=11)
    ax.set_ylim(0, 1.35)
    ax.set_ylabel("HES (0 to 2, lower safer)", fontsize=10.5)
    ax.set_title("Harm Enablement", fontsize=12.5, fontweight="bold", pad=10)
    ax.grid(axis="y", color=COL_GRID, linewidth=0.8, zorder=1)
    ax.set_axisbelow(True)

    # ---- SIS panel
    ax = axes[2]
    asha_sis = [91.7, 100.0]
    asha_sis_lo = [80.4, 92.6]
    asha_sis_hi = [96.7, 100.0]
    gem_sis = [22.9, 37.5]
    gem_sis_lo = [13.3, 25.2]
    gem_sis_hi = [36.5, 51.6]
    ax.bar(x_pos - width / 2, asha_sis, width, color=COL_ASHA,
           edgecolor=COL_INK, linewidth=0.8, zorder=3)
    ax.bar(x_pos + width / 2, gem_sis, width, color=COL_BASELINE,
           edgecolor=COL_INK, linewidth=0.8, zorder=3)
    a_err_lo = [v - lo for v, lo in zip(asha_sis, asha_sis_lo)]
    a_err_hi = [hi - v for v, hi in zip(asha_sis, asha_sis_hi)]
    g_err_lo = [v - lo for v, lo in zip(gem_sis, gem_sis_lo)]
    g_err_hi = [hi - v for v, hi in zip(gem_sis, gem_sis_hi)]
    ax.errorbar(x_pos - width / 2, asha_sis, yerr=[a_err_lo, a_err_hi],
                fmt="none", ecolor=COL_INK, elinewidth=1.4, capsize=4, zorder=4)
    ax.errorbar(x_pos + width / 2, gem_sis, yerr=[g_err_lo, g_err_hi],
                fmt="none", ecolor=COL_INK, elinewidth=1.4, capsize=4, zorder=4)
    fractions = [("44/48", "11/48"), ("48/48", "18/48")]
    for i, ci in enumerate(x_pos):
        ax.text(ci - width / 2, asha_sis[i] + 6, f"{asha_sis[i]:.1f}%\n{fractions[i][0]}",
                ha="center", fontsize=9.5, color=COL_INK, fontweight="bold",
                linespacing=1.2)
        ax.text(ci + width / 2, gem_sis[i] + 6, f"{gem_sis[i]:.1f}%\n{fractions[i][1]}",
                ha="center", fontsize=9.5, color=COL_INK, fontweight="bold",
                linespacing=1.2)
    ax.text(0, 118, "+68.8 pp gap", ha="center", fontsize=10,
            color=COL_ASHA, fontweight="bold")
    ax.text(1, 118, "+62.5 pp gap", ha="center", fontsize=10,
            color=COL_ASHA, fontweight="bold")
    ax.set_xticks(x_pos)
    ax.set_xticklabels(conditions, fontsize=11)
    ax.set_ylim(0, 128)
    ax.set_yticks([0, 20, 40, 60, 80, 100])
    ax.set_ylabel("SIS per-turn rate (%) with Wilson 95% CI", fontsize=10.5)
    ax.set_title("Safety Intervention rate", fontsize=12.5, fontweight="bold", pad=10)
    ax.grid(axis="y", color=COL_GRID, linewidth=0.8, zorder=1)
    ax.set_axisbelow(True)

    fig.suptitle("Psychosis-bench stratified by scenario condition (Judge A)",
                 fontsize=15.5, fontweight="bold", color=COL_INK, y=1.02)
    fig.text(0.5, -0.02,
             "All four Asha SIS misses live in implicit scenarios "
             "(turing_test_implicit turns 7-9, ai_sweetheart_implicit turn 9). "
             "The lift holds on both halves of the bench.",
             ha="center", fontsize=10, color=COL_BASELINE_DARK, style="italic")
    fig.tight_layout()

    save(fig, "07_implicit_explicit.png")


# ----------------------------------------------------------------------------
# Figure 8: MedQA standalone headline chart (social-shareable)
# ----------------------------------------------------------------------------

def fig8_medqa_headline():
    """Standalone bar chart for the MedQA accuracy table.

    Use: Substack inline header card, LinkedIn graphic, X attachment.
    Larger fonts, stronger visual hierarchy for Asha, prominent parse-failure
    column. Honest framing: top-of-table accuracy + reliability + cost. The
    1.72-2.20 pp gap to Opus is shown with non-overlapping but adjacent CIs;
    the chart does not claim accuracy supremacy over Opus.
    """
    fig = plt.figure(figsize=(14, 8.5))
    ax = fig.add_axes([0.30, 0.15, 0.62, 0.66])

    rows = list(reversed(MEDQA_ARMS))
    names = [r[0] for r in rows]
    acc = [100 * r[1] / r[2] for r in rows]
    ci_lo = [r[3] for r in rows]
    ci_hi = [r[4] for r in rows]
    pf = [r[5] for r in rows]
    is_asha = [r[6] for r in rows]
    colors = [COL_ASHA if a else COL_BASELINE for a in is_asha]

    y = np.arange(len(rows))
    err_lo = [a - lo for a, lo in zip(acc, ci_lo)]
    err_hi = [hi - a for a, hi in zip(acc, ci_hi)]

    bars = ax.barh(y, acc, color=colors, edgecolor=COL_INK, linewidth=0.8,
                   height=0.68, zorder=3)
    # Thicker border on the Asha bar to draw the eye
    for bar, is_a in zip(bars, is_asha):
        if is_a:
            bar.set_linewidth(2.2)

    ax.errorbar(acc, y, xerr=[err_lo, err_hi], fmt="none",
                ecolor=COL_INK, elinewidth=1.6, capsize=5, zorder=4)

    # Accuracy text inside bar, large
    for yi, a in zip(y, acc):
        ax.text(a - 0.55, yi, f"{a:.2f}%", ha="right", va="center",
                color="white", fontsize=15, fontweight="bold", zorder=5)

    # Parse-failure column on the right
    ax.text(97.8, len(rows) - 0.4, "parse\nfailures",
            ha="left", va="bottom", color=COL_BASELINE_DARK,
            fontsize=11.5, fontweight="bold", linespacing=1.1)
    for yi, p in zip(y, pf):
        marker = "0" if p == 0 else str(p)
        col = COL_ASHA if p == 0 else (COL_FAIL if p >= 30 else COL_BASELINE_DARK)
        ax.text(97.95, yi, marker, ha="left", va="center",
                color=col, fontsize=18, fontweight="bold")

    # Side note "out of 1,273" at the bottom right of the parse-failure column
    ax.text(97.95, -0.85, "(out of 1,273)",
            ha="left", va="center", color=COL_BASELINE_DARK, fontsize=9.5,
            style="italic")

    ax.set_yticks(y)
    ax.set_yticklabels(names, fontsize=13)
    ax.set_xlabel("Accuracy (%) with Wilson 95% CI", fontsize=12)
    ax.set_xlim(88, 100)
    ax.spines["bottom"].set_color(COL_BASELINE_DARK)
    ax.tick_params(axis="x", colors=COL_INK, labelsize=11)
    ax.tick_params(axis="y", colors=COL_INK)
    ax.grid(axis="x", color=COL_GRID, linewidth=0.8, zorder=1)
    ax.set_axisbelow(True)

    # Title strip at top
    fig.text(0.06, 0.92, "MedQA, n = 1,273  (Jin et al. 2020, USMLE-style)",
             fontsize=20, fontweight="bold", color=COL_INK)
    fig.text(0.06, 0.875,
             "Single-shot, no Medprompt / k-shot scaffolding. "
             "Lenient parser applied uniformly across all arms. "
             "SHA-256 locked input.",
             fontsize=10.5, color=COL_BASELINE_DARK, style="italic")

    # Bottom callout strip
    fig.text(0.06, 0.085,
             "Asha matches Claude Opus 4.5 to statistical parity   "
             "(paired McNemar exact p = 0.228)   at roughly one-quarter "
             "of the marginal per-query cost.",
             fontsize=11.5, color=COL_INK, fontweight="bold")
    fig.text(0.06, 0.045,
             "0 parse failures across 1,273 questions.   "
             "Bare Gemini 3.1 Pro Preview: 71 parse failures (5.58%).   "
             "META_CORRECT envelope rescue accounts for the entire "
             "+3.22 pp paired McNemar advantage.",
             fontsize=10, color=COL_BASELINE_DARK)
    fig.text(0.06, 0.013,
             "Reproduce: github.com/EndlessRay/asha-bench-public",
             fontsize=9.5, color=COL_BASELINE_DARK, style="italic")

    save(fig, "08_medqa_headline.png")


# ----------------------------------------------------------------------------
# Figure 5b: Psychosis-bench under Judge B (supplementary)
# ----------------------------------------------------------------------------

def fig5b_psychosis_metrics_judge_b():
    """Judge B (claude-haiku-4-5) parallel of Figure 5.

    Same panel layout, same arms, same metrics. Reads the canonical aggregate.
    Honest range framing: Judge A is the protocol-specified judge, but the
    pre-registered κ gate failed, so the manuscript reports both.
    """
    agg_path = REPO / "psychosis-bench-2026-05-11" / "results" / "aggregate_two_judges.json"
    with open(agg_path) as f:
        agg = json.load(f)

    asha = agg["per_arm"]["asha"]["judge_b"]
    gem = agg["per_arm"]["gemini_flash"]["judge_b"]

    fig, axes = plt.subplots(1, 3, figsize=(14, 6.2))
    arms = ["Asha", "Gemini 2.5 Flash"]
    colors = [COL_ASHA, COL_BASELINE]

    # ---- DCS
    ax = axes[0]
    vals = [asha["DCS_mean"], gem["DCS_mean"]]
    ax.bar(arms, vals, color=colors, edgecolor=COL_INK, linewidth=0.8,
           width=0.6, zorder=3)
    for x, v in zip(arms, vals):
        ax.text(x, v + 0.06, f"{v:.3f}", ha="center", fontsize=12,
                fontweight="bold", color=COL_INK)
    ax.set_ylim(0, 2.0)
    ax.set_ylabel("DCS  (0 = ground, 1 = perpetuate, 2 = amplify)", fontsize=10)
    ax.set_title("Delusion Confirmation",
                 fontsize=13, fontweight="bold", pad=10)
    ax.grid(axis="y", color=COL_GRID, linewidth=0.8, zorder=1)
    ax.set_axisbelow(True)
    ratio_dcs = gem["DCS_mean"] / asha["DCS_mean"] if asha["DCS_mean"] > 0 else float("inf")
    ax.text(0.5, 1.85,
            f"{ratio_dcs:.2f}× lower under Judge B\n(harsher on Asha, lenient on Gemini Flash)",
            ha="center", fontsize=10, color=COL_ASHA, fontweight="bold")

    # ---- HES
    ax = axes[1]
    vals = [asha["HES_mean"], gem["HES_mean"]]
    ax.bar(arms, vals, color=colors, edgecolor=COL_INK, linewidth=0.8,
           width=0.6, zorder=3)
    for x, v in zip(arms, vals):
        ax.text(x, v + 0.05, f"{v:.3f}", ha="center", fontsize=12,
                fontweight="bold", color=COL_INK)
    ax.set_ylim(0, 2.0)
    ax.set_ylabel("HES  (0 = refuse, 1 = partial, 2 = reinforce)", fontsize=10)
    ax.set_title("Harm Enablement",
                 fontsize=13, fontweight="bold", pad=10)
    ax.grid(axis="y", color=COL_GRID, linewidth=0.8, zorder=1)
    ax.set_axisbelow(True)
    ratio_hes = gem["HES_mean"] / asha["HES_mean"] if asha["HES_mean"] > 0 else float("inf")
    ax.text(0.5, 1.85,
            f"{ratio_hes:.2f}× lower under Judge B",
            ha="center", fontsize=10, color=COL_ASHA, fontweight="bold")

    # ---- SIS
    ax = axes[2]
    vals_pct = [100 * asha["SIS_rate"], 100 * gem["SIS_rate"]]
    ci_lo_pct = [100 * asha["SIS_wilson95"][0], 100 * gem["SIS_wilson95"][0]]
    ci_hi_pct = [100 * asha["SIS_wilson95"][1], 100 * gem["SIS_wilson95"][1]]
    ax.bar(arms, vals_pct, color=colors, edgecolor=COL_INK, linewidth=0.8,
           width=0.6, zorder=3)
    err_lo = [v - lo for v, lo in zip(vals_pct, ci_lo_pct)]
    err_hi = [hi - v for v, hi in zip(vals_pct, ci_hi_pct)]
    ax.errorbar(arms, vals_pct, yerr=[err_lo, err_hi], fmt="none",
                ecolor=COL_INK, elinewidth=1.4, capsize=5, zorder=4)
    fractions = [
        f"{asha['n_sis_intervened']}/{asha['n_sis_eligible']}",
        f"{gem['n_sis_intervened']}/{gem['n_sis_eligible']}",
    ]
    for x, v, frac in zip(arms, vals_pct, fractions):
        ax.text(x, v + 7, f"{v:.1f}%\n{frac}", ha="center", fontsize=11,
                fontweight="bold", color=COL_INK, linespacing=1.2)
    ax.set_ylim(0, 115)
    ax.set_yticks([0, 20, 40, 60, 80, 100])
    ax.set_ylabel("SIS per-turn rate (%) with Wilson 95% CI", fontsize=10)
    ax.set_title("Safety Intervention rate",
                 fontsize=13, fontweight="bold", pad=10)
    ax.grid(axis="y", color=COL_GRID, linewidth=0.8, zorder=1)
    ax.set_axisbelow(True)
    gap_pp = 100 * (asha["SIS_rate"] - gem["SIS_rate"])
    ax.text(0.5, 108,
            f"+{gap_pp:.1f} pp gap under Judge B",
            ha="center", fontsize=10, color=COL_ASHA, fontweight="bold")

    fig.suptitle("Psychosis-bench under Judge B  (claude-haiku-4-5)",
                 fontsize=15.5, fontweight="bold", color=COL_INK, y=1.01)
    fig.text(0.5, -0.02,
             "Supplementary to Figure 5. Direction agrees with Judge A on every metric; "
             "magnitude shrinks. Pre-registered κ gate failed; both judges are published.",
             ha="center", fontsize=10, color=COL_BASELINE_DARK, style="italic")
    fig.tight_layout()

    save(fig, "05b_psychosis_metrics_judge_b.png")


# ----------------------------------------------------------------------------
# Figure 9: MedQA parseable-only "fair fight" McNemar
# ----------------------------------------------------------------------------

def fig9_medqa_parseable_fight():
    """Parseable-only subset of the MedQA McNemar table (the "fair fight").

    Reviewer asked for the 25-loss decomposition. Conditioning on the 1,202
    questions where both arms emitted a parseable letter:
        both right:  1,150
        Asha right, Gemini wrong:  15
        Asha wrong, Gemini right:  25
        both wrong:  12
    Net delta: -10 (-0.83 pp), Asha behind on the head-to-head subset.
    The +3.22 pp full-bench lift is therefore attributable to META_CORRECT
    rescue on Gemini's 71 parse failures, not to retrieval-or-arena reasoning.
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 6.2),
                             gridspec_kw={"width_ratios": [1.0, 1.15]})

    # ---- Panel A: parseable-only 2x2
    ax = axes[0]
    ax.set_xlim(0, 4)
    ax.set_ylim(0, 4)
    ax.set_aspect("equal")
    ax.axis("off")

    ax.text(2.5, 3.85, "Gemini 3.1 Pro Preview", ha="center", fontsize=12,
            fontweight="bold", color=COL_INK)
    ax.text(2.5, 3.55, "right                    wrong",
            ha="center", fontsize=10.5, color=COL_BASELINE_DARK)
    ax.text(0.45, 2.5, "Asha\nright", ha="center", va="center",
            fontsize=11, fontweight="bold", color=COL_INK,
            rotation=90, linespacing=1.2)
    ax.text(0.45, 1.0, "Asha\nwrong", ha="center", va="center",
            fontsize=11, fontweight="bold", color=COL_INK,
            rotation=90, linespacing=1.2)

    cell_specs = [
        (1.0, 2.0, 1.4, 1.2, "both right",      "1,150", "#E8F0EC", COL_INK),
        (2.6, 2.0, 1.4, 1.2, "Asha right,\nGemini wrong", "15", COL_ASHA, "white"),
        (1.0, 0.4, 1.4, 1.2, "Asha wrong,\nGemini right", "25", COL_FAIL, "white"),
        (2.6, 0.4, 1.4, 1.2, "both wrong",      "12",    "#F1F1F1", COL_INK),
    ]
    for (x, y, w, h, lab, val, fill, fc) in cell_specs:
        rect = Rectangle((x, y), w, h, facecolor=fill, edgecolor=COL_INK,
                         linewidth=1.3, zorder=2)
        ax.add_patch(rect)
        ax.text(x + w / 2, y + h * 0.66, val, ha="center", va="center",
                fontsize=20, fontweight="bold", color=fc)
        ax.text(x + w / 2, y + h * 0.27, lab, ha="center", va="center",
                fontsize=9.5, color=fc, linespacing=1.15)

    ax.set_title("Parseable-only subset  (n = 1,202)",
                 fontsize=12.5, fontweight="bold", color=COL_INK, pad=12)
    ax.text(2.5, -0.15,
            "Net delta  −10 questions  (−0.83 pp).  "
            "On head-to-head answer letters, Asha runs slightly behind bare Gemini.",
            ha="center", fontsize=10.5, color=COL_FAIL, fontweight="bold")

    # ---- Panel B: lift attribution
    ax = axes[1]
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")

    _rounded_box(ax, 0.4, 3.8, 4.4, 1.6,
                 "+3.22 pp",
                 "Full 1,273 paired McNemar lift\n"
                 "Asha 95.52% vs Gemini 92.30%",
                 color=COL_ASHA, text_color="white", fontsize=22,
                 sublabel_size=9.5)

    _rounded_box(ax, 5.2, 3.8, 4.4, 1.6,
                 "−0.83 pp",
                 "Parseable-only 1,202 subset\n"
                 "head-to-head, Asha lags",
                 color=COL_FAIL, text_color="white", fontsize=22,
                 sublabel_size=9.5)

    ax.add_patch(FancyArrowPatch((5.0, 3.7), (5.0, 2.5),
                                 arrowstyle="-|>,head_length=0.32,head_width=0.20",
                                 color=COL_INK, linewidth=1.4))
    ax.text(5.0, 3.05, "subtract", ha="center", fontsize=9.5,
            color=COL_BASELINE_DARK, style="italic")

    _rounded_box(ax, 1.0, 0.4, 8.0, 1.9,
                 "The lift is META_CORRECT envelope rescue",
                 "The full-bench +3.22 pp advantage is attributable to META_CORRECT recovering\n"
                 "51 correct answer letters from bare Gemini's 71 parse failures.\n"
                 "On the head-to-head parseable subset, retrieval and arena components\n"
                 "do not produce a statistically meaningful lift over the bare backbone LM.",
                 color="#FAF3E7", text_color=COL_INK, fontsize=13,
                 sublabel_size=9.5)

    ax.set_title("Where the lift comes from and where it does not",
                 fontsize=12.5, fontweight="bold", color=COL_INK, pad=12)

    fig.suptitle("MedQA fair-fight subset: the architectural claim, tightened",
                 fontsize=16, fontweight="bold", color=COL_INK, y=1.00)

    save(fig, "09_medqa_parseable_fight.png")


# ----------------------------------------------------------------------------
# Figure 10: Psychosis-bench standalone headline chart (social-shareable)
# ----------------------------------------------------------------------------

def fig10_psychosis_headline():
    """Standalone three-panel headline chart for the Psychosis-bench
    (DCS / HES / SIS), Judge A only, with a Judge-B robustness footer so the
    κ failure is not invisible when this image travels alone.

    Use: Substack inline header card for Chapter 3, LinkedIn graphic, X
    attachment. Parallel design to fig8_medqa_headline().
    """
    agg_path = REPO / "psychosis-bench-2026-05-11" / "results" / "aggregate_two_judges.json"
    with open(agg_path) as f:
        agg = json.load(f)
    a = agg["per_arm"]["asha"]["judge_a"]
    g = agg["per_arm"]["gemini_flash"]["judge_a"]

    fig = plt.figure(figsize=(14, 8.5))
    panel_w = 0.26
    panel_h = 0.50
    panel_y = 0.20
    gap = 0.04
    total = 3 * panel_w + 2 * gap
    panel_x0 = (1 - total) / 2

    arms = ["Asha", "Gemini 2.5 Flash"]
    colors = [COL_ASHA, COL_BASELINE]

    # ---- DCS panel
    ax = fig.add_axes([panel_x0, panel_y, panel_w, panel_h])
    vals = [a["DCS_mean"], g["DCS_mean"]]
    bars = ax.bar(arms, vals, color=colors, edgecolor=COL_INK, linewidth=0.8,
                  width=0.62, zorder=3)
    bars[0].set_linewidth(2.0)
    for x, v in zip(arms, vals):
        ax.text(x, v + 0.06, f"{v:.3f}", ha="center", fontsize=14,
                color=COL_INK, fontweight="bold")
    ax.set_ylim(0, 1.65)
    ax.set_ylabel("DCS  (0 to 2, lower safer)", fontsize=11)
    ax.set_title("Delusion Confirmation", fontsize=14, fontweight="bold", pad=8)
    ax.tick_params(axis="x", labelsize=11)
    ax.grid(axis="y", color=COL_GRID, linewidth=0.8, zorder=1)
    ax.set_axisbelow(True)
    ax.text(0.5, 1.50, "3.43× lower\nbootstrap 95% CI [2.15, 6.13]",
            ha="center", fontsize=11, color=COL_ASHA, fontweight="bold",
            transform=ax.transData, linespacing=1.3)

    # ---- HES panel
    ax = fig.add_axes([panel_x0 + panel_w + gap, panel_y, panel_w, panel_h])
    vals = [a["HES_mean"], g["HES_mean"]]
    bars = ax.bar(arms, vals, color=colors, edgecolor=COL_INK, linewidth=0.8,
                  width=0.62, zorder=3)
    bars[0].set_linewidth(2.0)
    for x, v in zip(arms, vals):
        ax.text(x, v + 0.04, f"{v:.3f}", ha="center", fontsize=14,
                color=COL_INK, fontweight="bold")
    ax.set_ylim(0, 1.15)
    ax.set_ylabel("HES  (0 to 2, lower safer)", fontsize=11)
    ax.set_title("Harm Enablement", fontsize=14, fontweight="bold", pad=8)
    ax.tick_params(axis="x", labelsize=11)
    ax.grid(axis="y", color=COL_GRID, linewidth=0.8, zorder=1)
    ax.set_axisbelow(True)
    ax.text(0.5, 1.04, "7.9× lower\nbootstrap 95% CI [4.4, 22.7]",
            ha="center", fontsize=11, color=COL_ASHA, fontweight="bold",
            transform=ax.transData, linespacing=1.3)

    # ---- SIS panel
    ax = fig.add_axes([panel_x0 + 2 * (panel_w + gap), panel_y, panel_w, panel_h])
    vals_pct = [100 * a["SIS_rate"], 100 * g["SIS_rate"]]
    ci_lo_pct = [100 * a["SIS_wilson95"][0], 100 * g["SIS_wilson95"][0]]
    ci_hi_pct = [100 * a["SIS_wilson95"][1], 100 * g["SIS_wilson95"][1]]
    bars = ax.bar(arms, vals_pct, color=colors, edgecolor=COL_INK, linewidth=0.8,
                  width=0.62, zorder=3)
    bars[0].set_linewidth(2.0)
    err_lo = [v - lo for v, lo in zip(vals_pct, ci_lo_pct)]
    err_hi = [hi - v for v, hi in zip(vals_pct, ci_hi_pct)]
    ax.errorbar(arms, vals_pct, yerr=[err_lo, err_hi], fmt="none",
                ecolor=COL_INK, elinewidth=1.6, capsize=5, zorder=4)
    fractions = [
        f"{a['n_sis_intervened']}/{a['n_sis_eligible']}",
        f"{g['n_sis_intervened']}/{g['n_sis_eligible']}",
    ]
    for x, v, frac in zip(arms, vals_pct, fractions):
        ax.text(x, v + 7, f"{v:.1f}%\n{frac}", ha="center", fontsize=12.5,
                fontweight="bold", color=COL_INK, linespacing=1.2)
    ax.set_ylim(0, 118)
    ax.set_yticks([0, 20, 40, 60, 80, 100])
    ax.set_ylabel("SIS per-turn rate (%)  with Wilson 95% CI", fontsize=11)
    ax.set_title("Safety Intervention rate", fontsize=14, fontweight="bold", pad=8)
    ax.tick_params(axis="x", labelsize=11)
    ax.grid(axis="y", color=COL_GRID, linewidth=0.8, zorder=1)
    ax.set_axisbelow(True)
    ax.text(0.5, 111,
            "+65.6 pp gap\nFisher's exact p ≈ 5.7 × 10⁻¹⁶",
            ha="center", fontsize=11, color=COL_ASHA, fontweight="bold",
            transform=ax.transData, linespacing=1.3)

    # ---- Title strip at top
    fig.text(0.5, 0.92,
             "Psychosis-bench  (Au Yeung 2025), 16 scenarios × 12 turns × 2 arms",
             ha="center", fontsize=20, fontweight="bold", color=COL_INK)
    fig.text(0.5, 0.875,
             "Judge A (gpt-4o-mini, T = 0, protocol-specified).  "
             "Same backbone LM (gemini-2.5-flash) inside both arms.  "
             "Pre-registered, bit-exact reproducible.",
             ha="center", fontsize=11, color=COL_BASELINE_DARK, style="italic")

    # ---- Bottom callout strip
    fig.text(0.5, 0.115,
             "Asha and Gemini Wilson 95% CIs on SIS do not overlap.  "
             "Both Cohen's d on DCS and HES exceed 1.3 (large effect).",
             ha="center", fontsize=11.5, color=COL_INK, fontweight="bold")
    fig.text(0.5, 0.075,
             "Pre-registered judge-reliability gate FAILED  (avg κ across two LLM judges = 0.249).  "
             "Under Judge B (claude-haiku-4-5) the direction of every metric holds; "
             "magnitudes shrink to 1.72× DCS, 1.76× HES, +22.9 pp SIS.",
             ha="center", fontsize=10, color=COL_BASELINE_DARK)
    fig.text(0.5, 0.035,
             "Formal verdict per literal pre-registration rule: INCONCLUSIVE.  "
             "Reproduce: github.com/EndlessRay/asha-bench-public",
             ha="center", fontsize=10, color=COL_BASELINE_DARK, style="italic")

    save(fig, "10_psychosis_headline.png")


# Figure 11: Tier-attribution chart — bare Flash / bare Pro / Asha (Chapter 4)
# ----------------------------------------------------------------------------

def fig11_tier_attribution():
    """Three-arm bar chart: bare Gemini-2.5-Flash, bare Gemini-2.5-Pro, Asha.

    Visual story: bare Pro and bare Flash are nearly identical; Asha towers
    over both.  Same design system as fig10_psychosis_headline().

    Data: Chapter 4 aggregate_bench6.json (psychosis-attribution-2026-05-12/).
    Controls (Flash + Asha) come from the Chapter 3 REDO, matched to the
    public Chapter 3 numbers exactly.
    """
    agg_path = REPO / "psychosis-attribution-2026-05-12" / "results" / "aggregate_bench6.json"
    with open(agg_path) as f:
        agg = json.load(f)

    flash = agg["arms"]["gemini_flash"]
    pro   = agg["arms"]["raw_gemini_pro"]
    asha  = agg["arms"]["asha"]

    arm_labels = ["Gemini 2.5\nFlash (bare)", "Gemini 2.5\nPro (bare)", "Asha"]
    colors     = [COL_BASELINE, COL_BASELINE_DARK, COL_ASHA]
    arm_data   = [flash, pro, asha]
    bar_w = 0.60

    fig = plt.figure(figsize=(15, 8.5))
    panel_w = 0.25
    panel_h = 0.50
    panel_y = 0.22
    gap = 0.045
    total = 3 * panel_w + 2 * gap
    panel_x0 = (1 - total) / 2

    # ---- DCS panel
    ax = fig.add_axes([panel_x0, panel_y, panel_w, panel_h])
    dcs_vals = [d["DCS_mean"] for d in arm_data]
    bars = ax.bar(arm_labels, dcs_vals, color=colors, edgecolor=COL_INK,
                  linewidth=0.8, width=bar_w, zorder=3)
    bars[2].set_linewidth(2.0)
    for lbl, v in zip(arm_labels, dcs_vals):
        ax.text(lbl, v + 0.06, f"{v:.3f}", ha="center", fontsize=13,
                color=COL_INK, fontweight="bold")
    ax.set_ylim(0, 1.70)
    ax.set_ylabel("DCS  (0 to 2, lower safer)", fontsize=11)
    ax.set_title("Delusion Confirmation", fontsize=14, fontweight="bold", pad=8)
    ax.tick_params(axis="x", labelsize=10)
    ax.grid(axis="y", color=COL_GRID, linewidth=0.8, zorder=1)
    ax.set_axisbelow(True)
    ax.annotate("", xy=(1, 1.30), xytext=(0, 1.30),
                arrowprops=dict(arrowstyle="<->", color=COL_BASELINE_DARK, lw=1.5))
    ax.text(0.5, 1.36, "ratio CI [0.86, 1.21]", ha="center", fontsize=9,
            color=COL_BASELINE_DARK, style="italic")
    ax.text(2, 1.57, "3.35×\nlower\n(Asha)", ha="center", fontsize=10,
            color=COL_ASHA, fontweight="bold", linespacing=1.2)

    # ---- HES panel
    ax = fig.add_axes([panel_x0 + panel_w + gap, panel_y, panel_w, panel_h])
    hes_vals = [d["HES_mean"] for d in arm_data]
    bars = ax.bar(arm_labels, hes_vals, color=colors, edgecolor=COL_INK,
                  linewidth=0.8, width=bar_w, zorder=3)
    bars[2].set_linewidth(2.0)
    for lbl, v in zip(arm_labels, hes_vals):
        ax.text(lbl, v + 0.04, f"{v:.3f}", ha="center", fontsize=13,
                color=COL_INK, fontweight="bold")
    ax.set_ylim(0, 1.20)
    ax.set_ylabel("HES  (0 to 2, lower safer)", fontsize=11)
    ax.set_title("Harm Enablement", fontsize=14, fontweight="bold", pad=8)
    ax.tick_params(axis="x", labelsize=10)
    ax.grid(axis="y", color=COL_GRID, linewidth=0.8, zorder=1)
    ax.set_axisbelow(True)

    # ---- SIS panel
    ax = fig.add_axes([panel_x0 + 2 * (panel_w + gap), panel_y, panel_w, panel_h])
    sis_pct = [100 * d["SIS_rate"] for d in arm_data]
    ci_lo   = [100 * d["SIS_wilson95"][0] for d in arm_data]
    ci_hi   = [100 * d["SIS_wilson95"][1] for d in arm_data]
    bars = ax.bar(arm_labels, sis_pct, color=colors, edgecolor=COL_INK,
                  linewidth=0.8, width=bar_w, zorder=3)
    bars[2].set_linewidth(2.0)
    err_lo = [v - lo for v, lo in zip(sis_pct, ci_lo)]
    err_hi = [hi - v for v, hi in zip(sis_pct, ci_hi)]
    ax.errorbar(arm_labels, sis_pct, yerr=[err_lo, err_hi], fmt="none",
                ecolor=COL_INK, elinewidth=1.6, capsize=5, zorder=4)
    fracs = [f"{d['SIS_x']}/{d['SIS_n']}" for d in arm_data]
    for lbl, v, frac in zip(arm_labels, sis_pct, fracs):
        offset = 3.5 if v < 90 else -9.0
        va = "bottom" if v < 90 else "top"
        ax.text(lbl, v + offset, f"{v:.1f}%\n({frac})", ha="center",
                fontsize=11, color=COL_INK, fontweight="bold", va=va)
    ax.set_ylim(0, 115)
    ax.set_ylabel("SIS rate  (%, higher safer)", fontsize=11)
    ax.set_title("Safety Intervention Rate", fontsize=14, fontweight="bold", pad=8)
    ax.tick_params(axis="x", labelsize=10)
    ax.grid(axis="y", color=COL_GRID, linewidth=0.8, zorder=1)
    ax.set_axisbelow(True)

    # ---- Supertitle and footnotes
    fig.text(0.5, 0.95, "Tier-attribution: Bare Flash ≈ Bare Pro  ≪  Asha",
             ha="center", fontsize=18, fontweight="bold", color=COL_INK)
    fig.text(0.5, 0.90,
             "16 scenarios × 12 turns × 3 arms  |  Judge: gpt-4o-mini  |"
             "  Chapter 4 · psychosis-attribution-2026-05-12",
             ha="center", fontsize=11, color=COL_BASELINE_DARK)
    fig.text(0.5, 0.14,
             "Flash + Asha controls from Chapter 3 dual-judge REDO (0 empty responses)."
             "  Bare Pro run 2026-05-12 v2; v1 retracted — forensic/v1_truncation_bug/RETRACTED.md.",
             ha="center", fontsize=9, color=COL_BASELINE_DARK, style="italic")
    fig.text(0.5, 0.10,
             "Flash/Pro DCS ratio bootstrap 95% CI [0.86, 1.21]  —  tier jump provides zero measurable safety lift.",
             ha="center", fontsize=10, color=COL_BASELINE_DARK, fontweight="bold")

    save(fig, "11_tier_attribution.png")


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------

def main():
    print("Generating DNAi bench-public figures...")
    fig1_deaths_timeline()
    fig2_architecture()
    fig3_medqa_accuracy()
    fig4_medqa_mechanism()
    fig5_psychosis_metrics()
    fig5b_psychosis_metrics_judge_b()
    fig6_prereg_scoreboard()
    fig7_implicit_explicit()
    fig8_medqa_headline()
    fig9_medqa_parseable_fight()
    fig10_psychosis_headline()
    fig11_tier_attribution()
    print("Done. Outputs in bench-public/figures/output/.")


if __name__ == "__main__":
    main()
