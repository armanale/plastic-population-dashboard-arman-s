"""Generate base64-encoded info cards using matplotlib — no internet needed."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np, io, base64

BG   = "#F0F8FF"
CARD = "#FFFFFF"

def _card_b64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=110, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close(fig)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()

def make_info_cards():
    cards = []

    # ── Card 1: Ocean Crisis ─────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(3.5, 2.0))
    fig.patch.set_facecolor("#012A4A"); ax.set_facecolor("#012A4A")
    ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis("off")
    # wave shapes
    x = np.linspace(0,1,200)
    for i, (amp, yoff, alpha, color) in enumerate([
        (0.06,0.35,0.5,"#00B4D8"),(0.05,0.28,0.6,"#48CAE4"),
        (0.04,0.20,0.4,"#90E0EF"),(0.07,0.42,0.3,"#0077B6")]):
        y = yoff + amp*np.sin(2*np.pi*(x+i*0.2)*3)
        ax.fill_between(x, 0, y, alpha=alpha, color=color)
    ax.text(0.5,0.82,"~ ~ ~", ha="center", va="center", fontsize=22,
            transform=ax.transAxes)
    ax.text(0.5,0.65,"Ocean Plastic Crisis", ha="center", va="center",
            color="#FFFFFF", fontsize=9, fontweight="bold",
            transform=ax.transAxes)
    ax.text(0.5,0.50,"8M tons enter oceans yearly", ha="center",
            color="#90E0EF", fontsize=7.5, transform=ax.transAxes)
    ax.text(0.5,0.15,"affecting 700+ marine species",
            ha="center", color="#ADE8F4", fontsize=7,
            transform=ax.transAxes)
    cards.append(_card_b64(fig))

    # ── Card 2: Brand Audit ──────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(3.5, 2.0))
    fig.patch.set_facecolor("#E1F5FE"); ax.set_facecolor("#E1F5FE")
    ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis("off")
    for i,(x0,y0,w,h,c) in enumerate([
        (0.08,0.30,0.38,0.48,"#0077B6"),
        (0.54,0.18,0.38,0.60,"#0096C7"),
        (0.08,0.82,0.18,0.12,"#48CAE4"),
        (0.54,0.82,0.38,0.12,"#ADE8F4"),
    ]):
        ax.add_patch(FancyBboxPatch((x0,y0),w,h,
                     boxstyle="round,pad=0.01",
                     facecolor=c, edgecolor="white", linewidth=1.5, alpha=0.85))
    ax.text(0.5,0.92,"📋  Brand Audit Process", ha="center",
            color="#012A4A", fontsize=8.5, fontweight="bold", transform=ax.transAxes)
    ax.text(0.5,0.55,"Volunteers identify &\ntag each plastic piece\nto a corporate brand",
            ha="center", color="#FFFFFF", fontsize=7.5,
            fontweight="bold", transform=ax.transAxes)
    cards.append(_card_b64(fig))

    # ── Card 3: PET Bottles ──────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(3.5, 2.0))
    fig.patch.set_facecolor("#FFF3E0"); ax.set_facecolor("#FFF3E0")
    ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis("off")
    plastic_types = [("PET","#E65100",0.72),("PP","#F57F17",0.35),
                     ("HDPE","#FFA000",0.28),("Other","#FFCA28",0.22)]
    for i,(name,color,frac) in enumerate(plastic_types):
        yb = 0.15 + i*0.16
        ax.add_patch(FancyBboxPatch((0.08,yb),frac*0.80,0.12,
                     boxstyle="round,pad=0.005",
                     facecolor=color, edgecolor="none", alpha=0.88))
        ax.text(0.10,yb+0.06, name, va="center", color="#FFFFFF",
                fontsize=7.5, fontweight="bold", transform=ax.transAxes)
        ax.text(0.08+frac*0.80+0.03, yb+0.06, f"{int(frac*100)}%",
                va="center", color="#3E2800", fontsize=7, transform=ax.transAxes)
    ax.text(0.5,0.92,"PET — #1 Plastic Type", ha="center",
            color="#3E2800", fontsize=8.5, fontweight="bold", transform=ax.transAxes)
    cards.append(_card_b64(fig))

    # ── Card 4: Volunteers ───────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(3.5, 2.0))
    fig.patch.set_facecolor("#F3E5F5"); ax.set_facecolor("#F3E5F5")
    ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis("off")
    # people icons
    for i, (x0, size, color) in enumerate([
        (0.15,0.18,"#7B2FBE"),(0.30,0.15,"#0077B6"),(0.45,0.20,"#7B2FBE"),
        (0.60,0.14,"#00B4D8"),(0.75,0.17,"#7B2FBE"),
    ]):
        # body circle
        ax.add_patch(plt.Circle((x0, 0.62), size*0.28,
                     facecolor=color, alpha=0.85, zorder=3))
        # head circle
        ax.add_patch(plt.Circle((x0, 0.62+size*0.42), size*0.15,
                     facecolor=color, alpha=0.9, zorder=3))
    ax.text(0.5,0.92,"Volunteers", ha="center",
            color="#4A0080", fontsize=9, fontweight="bold", transform=ax.transAxes)
    ax.text(0.5,0.25,"Thousands of people power\ncleanup campaigns globally",
            ha="center", color="#4A0080", fontsize=7.5, transform=ax.transAxes)
    ax.text(0.5,0.10,"69 countries · 2019–2020",
            ha="center", color="#7B2FBE", fontsize=7, transform=ax.transAxes)
    cards.append(_card_b64(fig))

    return cards
