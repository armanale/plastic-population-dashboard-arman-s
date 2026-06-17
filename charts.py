"""charts.py — Sky-blue theme, compact figures, crystal-clear labels."""
import pandas as pd, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns
from filters import (get_plastic_type_totals, get_top_polluters,
                     get_country_totals, get_yearly_trend, get_plastic_by_year)

# ── DESIGN TOKENS ─────────────────────────────────────────────────
BG   = "#F0F8FF"
CARD = "#FFFFFF"
TX   = "#0A1628"
LB   = "#014F86"
TK   = "#2980B9"
GR   = "#DAEEF8"
BD   = "#90C4E4"

C = ["#0077B6","#E63946","#7B2FBE","#F57F17","#2196F3",
     "#00838F","#E65100","#AD1457","#023E8A","#0096C7","#00B4D8","#48CAE4"]

G1 = LinearSegmentedColormap.from_list("g1",["#0077B6","#00B4D8","#90E0EF"],N=256)
G2 = LinearSegmentedColormap.from_list("g2",["#023E8A","#0096C7","#ADE8F4"],N=256)
G3 = LinearSegmentedColormap.from_list("g3",["#7B2FBE","#48CAE4","#CAF0F8"],N=256)

plt.rcParams.update({
    "font.family":"DejaVu Sans","axes.facecolor":CARD,"figure.facecolor":BG,
    "axes.edgecolor":BD,"axes.linewidth":1.0,"axes.grid":True,
    "grid.color":GR,"grid.linestyle":"--","grid.linewidth":0.55,"grid.alpha":1.0,
    "xtick.color":TK,"ytick.color":TK,"xtick.labelsize":8.5,"ytick.labelsize":8.5,
    "text.color":TX,"axes.spines.top":False,"axes.spines.right":False,
    "axes.titlepad":10,
})

def _fig(w=6.5, h=3.8):
    fig, ax = plt.subplots(figsize=(w, h), constrained_layout=True)
    fig.patch.set_facecolor(BG); ax.set_facecolor(CARD)
    return fig, ax

def _T(ax, title, xl="", yl="", subtitle=""):
    ax.set_title(title, color=TX, fontsize=11, fontweight="bold", pad=10, loc="left")
    if subtitle:
        ax.annotate(subtitle, xy=(0,1.01), xycoords="axes fraction",
                    color=TK, fontsize=7.5, ha="left", va="bottom")
    if xl: ax.set_xlabel(xl, color=LB, fontsize=9, labelpad=5)
    if yl: ax.set_ylabel(yl, color=LB, fontsize=9, labelpad=5)

def _leg(ax, **kw):
    leg = ax.legend(facecolor="#E8F4FD", edgecolor=BD, labelcolor=TX,
                    fontsize=8, framealpha=0.97, **kw)
    for t in leg.get_texts(): t.set_color(TX)

def _fmtK(ax, which="y"):
    f = mticker.FuncFormatter(lambda x,_: f"{x/1e6:.1f}M" if x>=1e6 else
                               f"{x/1000:.0f}K" if x>=1000 else f"{int(x)}")
    if which=="y": ax.yaxis.set_major_formatter(f)
    else: ax.xaxis.set_major_formatter(f)

def _add_bar_labels(ax, bars, fmt="{:,.0f}", color=TX, fs=8, pad=0.012, orient="h"):
    for bar in bars:
        if orient=="h":
            w = bar.get_width()
            ax.text(w + w*pad, bar.get_y()+bar.get_height()/2,
                    fmt.format(w), va="center", color=color, fontsize=fs, fontweight="bold")
        else:
            h = bar.get_height()
            ax.text(bar.get_x()+bar.get_width()/2, h+h*pad,
                    fmt.format(h), ha="center", color=color, fontsize=fs, fontweight="bold")


# ── 1. PIE ── legend below, % inside, no overlap ──────────────────
def chart_pie(df):
    totals = get_plastic_type_totals(df)
    totals = totals[totals > 0]
    fig = plt.figure(figsize=(6.2, 6.0)); fig.patch.set_facecolor(BG)
    ax  = fig.add_axes([0.05, 0.28, 0.90, 0.66]); ax.set_facecolor(BG)
    wedges, _ = ax.pie(totals.values, labels=None, startangle=140,
                       colors=C[:len(totals)],
                       wedgeprops=dict(width=0.58, edgecolor="#FFFFFF", linewidth=2.5))
    for wedge, (name, val) in zip(wedges, totals.items()):
        pct = val/totals.sum()*100
        if pct >= 8:
            ang = (wedge.theta2+wedge.theta1)/2
            ax.text(0.70*np.cos(np.radians(ang)), 0.70*np.sin(np.radians(ang)),
                    f"{pct:.0f}%", ha="center", va="center",
                    fontsize=9.5, fontweight="bold", color="#FFFFFF", zorder=10)
    ax.text(0,0,"PLASTIC\nTYPES", ha="center", va="center",
            color=TX, fontsize=9.5, fontweight="bold")
    ax.set_title("Plastic Type Distribution", color=TX, fontsize=11, fontweight="bold", pad=8)
    lbls = [f"{n}  {v/totals.sum()*100:.1f}%  ({v:,.0f})" for n,v in totals.items()]
    ax.legend(wedges, lbls, loc="upper center", bbox_to_anchor=(0.5,-0.04),
              ncol=3, fontsize=8, facecolor="#E8F4FD", edgecolor=BD, labelcolor=TX,
              framealpha=0.97, handlelength=1.1, columnspacing=0.8, borderpad=0.7)
    return fig


# ── 2. HISTOGRAM ──────────────────────────────────────────────────
def chart_histogram(df):
    real = df[df["parent_company"]!="Grand Total"]
    data = real["grand_total"][real["grand_total"]>0].clip(upper=2000)
    fig, ax = _fig(6.5, 3.8)
    n, bins, patches = ax.hist(data, bins=45, log=True, edgecolor="none")
    for i,p in enumerate(patches):
        p.set_facecolor(G1(i/len(patches))); p.set_alpha(0.9)
    med, mn = data.median(), data.mean()
    ax.axvline(med, color="#E63946", lw=1.8, ls="--", label=f"Median: {med:,.0f}")
    ax.axvline(mn,  color="#F57F17", lw=1.8, ls=":",  label=f"Mean: {mn:,.0f}")
    _leg(ax)
    _T(ax,"Distribution of Plastic Counts","Items Collected (capped 2K)","Frequency (log)",
       "Right-skewed — most cleanups collect small amounts")
    return fig


# ── 3. LINE ───────────────────────────────────────────────────────
def chart_line(df):
    yd = get_yearly_trend(df)
    xs, ys = yd["year"].values, yd["Total_Plastic"].values
    fig, ax = _fig(6.2, 3.8)
    ax.fill_between(xs, ys, alpha=0.12, color="#0077B6")
    ax.plot(xs, ys, color="#0077B6", lw=2.5, zorder=5, marker="", label="Total Plastic")
    ax.scatter(xs, ys, color="#E63946", s=100, zorder=6,
               edgecolors="#FFFFFF", linewidths=2, label="Data point")
    for x,y in zip(xs, ys):
        ax.annotate(f"{y:,.0f}", (x,y), textcoords="offset points", xytext=(0,14),
                    ha="center", color=TX, fontsize=10, fontweight="bold",
                    bbox=dict(boxstyle="round,pad=0.3", fc="#E8F4FD",
                              ec="#0077B6", lw=1.4, alpha=0.97))
    ax.set_xticks(xs); ax.xaxis.set_major_formatter(mticker.FormatStrFormatter("%d"))
    ax.margins(x=0.25); _fmtK(ax,"y")
    _T(ax,"Total Plastic Collected — Year on Year","Year","Plastic Items",
       "2020 lower due to COVID-19 disruptions")
    _leg(ax)
    return fig


# ── 4. BAR (horizontal) ───────────────────────────────────────────
def chart_bar(df, n=10):
    cdf = get_country_totals(df).head(n)
    fig, ax = _fig(7.0, max(3.2, n*0.40))
    for i,(_,row) in enumerate(cdf[::-1].iterrows()):
        ax.barh(i, row["Total Plastic"], color=G1(i/max(len(cdf)-1,1)),
                edgecolor="none", height=0.58)
        ax.text(row["Total Plastic"]+row["Total Plastic"]*0.015, i,
                f"{row['Total Plastic']:,.0f}",
                va="center", color=TX, fontsize=8, fontweight="bold")
    ax.set_yticks(range(len(cdf)))
    ax.set_yticklabels(cdf["Country"][::-1], color=LB, fontsize=8.5)
    ax.set_xlim(0, cdf["Total Plastic"].max()*1.26)
    ax.grid(axis="y", alpha=0); _fmtK(ax,"x")
    _T(ax,f"Top {n} Countries by Plastic Collected","Total Plastic Items","",
       "Sorted by total brand-audit plastic collected")
    return fig


# ── 5. SCATTER ────────────────────────────────────────────────────
def chart_scatter(df):
    real = df[df["parent_company"]!="Grand Total"]
    by_c = real.groupby("country").agg(
        volunteers=("volunteers","sum"),
        grand_total=("grand_total","sum")).reset_index()
    fig, ax = _fig(6.5, 3.8)
    sc = ax.scatter(by_c["volunteers"], by_c["grand_total"],
                    c=by_c["grand_total"], cmap=G1,
                    s=by_c["grand_total"]/by_c["grand_total"].max()*360+25,
                    alpha=0.82, edgecolors=BD, linewidths=0.7, zorder=4)
    cbar = fig.colorbar(sc, ax=ax, pad=0.02, shrink=0.80)
    cbar.set_label("Plastic Items", color=LB, fontsize=8)
    cbar.ax.tick_params(colors=TK, labelsize=7.5)
    for _,r in by_c.nlargest(4,"grand_total").iterrows():
        ax.annotate(r["country"], (r["volunteers"],r["grand_total"]),
                    textcoords="offset points", xytext=(6,4),
                    color="#E63946", fontsize=7.5, fontweight="bold",
                    bbox=dict(boxstyle="round,pad=0.2",fc="#FFEBEE",ec="#E63946",lw=0.8,alpha=0.92))
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(
        lambda x,_: f"{x/1e6:.1f}M" if x>=1e6 else f"{x/1e3:.0f}K" if x>=1e3 else f"{x:.0f}"))
    _fmtK(ax,"y")
    _T(ax,"Volunteers vs. Plastic Collected","Total Volunteers","Plastic Items",
       "Bubble size = plastic volume · Top 4 labeled")
    return fig


# ── 6. BOX ────────────────────────────────────────────────────────
def chart_box(df):
    real = df[df["parent_company"]!="Grand Total"]
    years = sorted(real["year"].unique())
    data  = [real.loc[real["year"]==y,"grand_total"].clip(upper=3000).values for y in years]
    fig, ax = _fig(5.0, 3.8)
    bp = ax.boxplot(data, tick_labels=[str(y) for y in years], patch_artist=True, widths=0.40,
                    medianprops={"color":"#0096C7","linewidth":2.5},
                    whiskerprops={"color":TK,"linewidth":1.4,"linestyle":"--"},
                    capprops={"color":TK,"linewidth":1.8},
                    flierprops={"marker":"o","color":"#E63946","markersize":3,
                                "alpha":0.5,"markeredgewidth":0})
    colors = ["#0077B6","#E63946"]
    for i,patch in enumerate(bp["boxes"]):
        patch.set_facecolor(colors[i%2]); patch.set_alpha(0.20)
        patch.set_edgecolor(colors[i%2]); patch.set_linewidth(1.8)
    # Median value annotations
    for i,(d,yr) in enumerate(zip(data,years)):
        med = np.median(d)
        ax.text(i+1, med+60, f"Med:{med:.0f}", ha="center",
                color=TX, fontsize=7.5, fontweight="bold")
    _T(ax,"Spread by Year (capped 3K)","Year","Plastic Items",
       "Box=IQR · Line=Median · Dots=Outliers")
    return fig


# ── 7. HEATMAP ────────────────────────────────────────────────────
def chart_heatmap(df):
    real = df[df["parent_company"]!="Grand Total"]
    cols = ["hdpe","ldpe","o","pet","pp","ps","pvc","grand_total","num_events","volunteers"]
    labs = ["HDPE","LDPE","Other","PET","PP","PS","PVC","Grand Total","Events","Volunteers"]
    corr = real[cols].corr(); corr.index=corr.columns=labs
    hc   = LinearSegmentedColormap.from_list("hc",["#E63946","#FFFFFF","#0077B6"],N=256)
    fig, ax = plt.subplots(figsize=(7.5, 5.8), constrained_layout=True)
    fig.patch.set_facecolor(BG)
    sns.heatmap(corr, ax=ax, cmap=hc, annot=True, fmt=".2f",
                linewidths=1.2, linecolor=BG,
                annot_kws={"size":8,"color":TX,"weight":"bold"},
                cbar_kws={"shrink":0.70,"label":"Correlation"}, vmin=-1, vmax=1)
    ax.set_title("Feature Correlation Heatmap", color=TX, fontsize=11, fontweight="bold", pad=12)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=40, ha="right", color=LB, fontsize=8)
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0, color=LB, fontsize=8)
    cb = ax.collections[0].colorbar
    cb.ax.tick_params(colors=TK, labelsize=7.5)
    cb.set_label("Correlation", color=LB, fontsize=8)
    return fig


# ── 8. AREA ───────────────────────────────────────────────────────
def chart_area(df):
    yd = get_plastic_by_year(df)
    pt = [p for p in ["PET","HDPE","PP","LDPE","Other","PS","PVC","Empty"] if p in yd.columns]
    fig, ax = _fig(6.8, 3.8)
    ax.stackplot(yd["year"],[yd[p] for p in pt], labels=pt, colors=C[:len(pt)], alpha=0.80)
    ax.set_xticks(yd["year"]); ax.xaxis.set_major_formatter(mticker.FormatStrFormatter("%d"))
    _fmtK(ax,"y"); ax.margins(x=0)
    _leg(ax, loc="upper left", ncol=2)
    _T(ax,"Plastic Types — Stacked Over Time","Year","Total Plastic Items",
       "Shows how each type contributes to yearly totals")
    return fig


# ── 9. COUNT ──────────────────────────────────────────────────────
def chart_countplot(df):
    real   = df[df["parent_company"]!="Grand Total"]
    counts = real["year"].value_counts().sort_index()
    fig, ax = _fig(5.0, 3.8)
    bars = ax.bar(counts.index.astype(str), counts.values,
                  color=["#0077B6","#E63946"][:len(counts)], edgecolor="none", width=0.40)
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x()+bar.get_width()/2, h + counts.max()*0.02,
                f"{h:,}", ha="center", color=TX, fontsize=12, fontweight="bold")
    ax.set_ylim(0, counts.max()*1.20); ax.grid(axis="x", alpha=0)
    _T(ax,"Audit Records per Year","Year","Number of Records",
       "2020 drop reflects COVID-19 impact on campaigns")
    return fig


# ── 10. VIOLIN ────────────────────────────────────────────────────
def chart_violin(df):
    real = df[df["parent_company"]!="Grand Total"]
    c = real[real["pet"]>0].copy()
    c["pet"]  = c["pet"].clip(upper=600)
    c["year"] = c["year"].astype(str)
    fig, ax = _fig(5.0, 3.8)
    pal = {str(y):col for y,col in zip(sorted(c["year"].unique()),["#0077B6","#E63946"])}
    sns.violinplot(data=c, x="year", y="pet", ax=ax, hue="year",
                   palette=pal, inner="box", linewidth=1.5, saturation=0.88, legend=False)
    _T(ax,"PET Bottle Distribution by Year","Year","PET Items (capped 600)",
       "Shape shows probability density · Box inside = IQR")
    return fig


# ── TOP COMPANIES ─────────────────────────────────────────────────
def chart_top_companies(df, n=10):
    top = get_top_polluters(df, n=n)
    fig, ax = _fig(8.0, max(3.2, n*0.40))
    bars = []
    for i,(_,row) in enumerate(top[::-1].iterrows()):
        b = ax.barh(i, row["Total Plastic"],
                    color=G2(i/max(len(top)-1,1)),
                    edgecolor="none", height=0.58)
        bars.append(b)
        ax.text(row["Total Plastic"]+row["Total Plastic"]*0.012, i,
                f'{row["Total Plastic"]:,.0f}',
                va="center", color=TX, fontsize=8.5, fontweight="bold")
    ax.set_yticks(range(len(top)))
    ax.set_yticklabels(top["Company"][::-1], color=LB, fontsize=9)
    ax.set_xlim(0, top["Total Plastic"].max()*1.24)
    ax.grid(axis="y", alpha=0); _fmtK(ax,"x")
    _T(ax,f"Top {n} Corporate Polluters (brand-attributed)","Total Plastic Items","",
       "Excludes 'Unbranded' — only identified corporate sources")
    return fig


# ── VOLUNTEERS LINE ───────────────────────────────────────────────
def chart_volunteers(df):
    yd = get_yearly_trend(df)
    xs = yd["year"].values; ys = yd["Total_Volunteers"].values
    fig, ax = _fig(6.2, 3.8)
    ax.fill_between(xs, ys, alpha=0.12, color="#7B2FBE")
    ax.plot(xs, ys, color="#7B2FBE", lw=2.5, zorder=5)
    ax.scatter(xs, ys, color="#F57F17", s=100, zorder=6,
               edgecolors="#FFFFFF", linewidths=2)
    for x,y in zip(xs, ys):
        ax.annotate(f"{y:,.0f}", (x,y), textcoords="offset points", xytext=(0,14),
                    ha="center", color=TX, fontsize=10, fontweight="bold",
                    bbox=dict(boxstyle="round,pad=0.3",fc="#F3E5F5",ec="#7B2FBE",lw=1.3,alpha=0.97))
    ax.set_xticks(xs); ax.xaxis.set_major_formatter(mticker.FormatStrFormatter("%d"))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(
        lambda x,_: f"{x/1e6:.1f}M" if x>=1e6 else f"{x/1e3:.0f}K"))
    ax.margins(x=0.25)
    _T(ax,"Total Volunteers by Year","Year","Volunteer Count",
       "Volunteer participation across all audit campaigns")
    return fig


# ── 2019 vs 2020 GROUPED BAR ─────────────────────────────────────
def chart_plastic_compare(df):
    real = df[df["parent_company"]!="Grand Total"]
    cols  = {"HDPE":"hdpe","LDPE":"ldpe","Other":"o","PET":"pet",
             "PP":"pp","PS":"ps","PVC":"pvc","Empty":"empty"}
    years = sorted(real["year"].unique())
    x = np.arange(len(cols)); w = 0.34
    fig, ax = _fig(8.0, 3.8)
    for i,(yr,color) in enumerate(zip(years,["#0077B6","#E63946"])):
        vals = [real[real["year"]==yr][c].sum() for c in cols.values()]
        bars = ax.bar(x+i*w, vals, w, label=str(yr),
                      color=color, alpha=0.85, edgecolor="none")
    ax.set_xticks(x+w/2)
    ax.set_xticklabels(list(cols.keys()), color=LB, fontsize=9)
    _fmtK(ax,"y"); _leg(ax)
    _T(ax,"Plastic Type Comparison: 2019 vs 2020","Plastic Type","Total Items",
       "Grouped by plastic category for both audit years")
    return fig


# ── COUNTRY PIE ───────────────────────────────────────────────────
def chart_country_pie(df):
    cdf = get_country_totals(df).head(8)
    fig = plt.figure(figsize=(6.2, 6.0)); fig.patch.set_facecolor(BG)
    ax  = fig.add_axes([0.05, 0.28, 0.90, 0.66]); ax.set_facecolor(BG)
    wedges, _ = ax.pie(cdf["Total Plastic"], labels=None, startangle=140,
                       colors=C[:len(cdf)],
                       wedgeprops=dict(width=0.56, edgecolor="#FFFFFF", linewidth=2.5))
    for wedge,(_,row) in zip(wedges, cdf.iterrows()):
        pct = row["Total Plastic"]/cdf["Total Plastic"].sum()*100
        if pct >= 9:
            ang = (wedge.theta2+wedge.theta1)/2
            ax.text(0.67*np.cos(np.radians(ang)), 0.67*np.sin(np.radians(ang)),
                    f"{pct:.0f}%", ha="center", va="center",
                    fontsize=9.5, fontweight="bold", color="#FFFFFF")
    ax.text(0,0,"TOP 8\nCOUNTRIES", ha="center", va="center",
            color=TX, fontsize=8.5, fontweight="bold")
    ax.set_title("Country Share of Plastic", color=TX, fontsize=11, fontweight="bold", pad=8)
    lbls = [f"{row['Country']}  {row['Total Plastic']/cdf['Total Plastic'].sum()*100:.1f}%  ({row['Total Plastic']:,.0f})"
            for _,row in cdf.iterrows()]
    ax.legend(wedges, lbls, loc="upper center", bbox_to_anchor=(0.5,-0.04),
              ncol=2, fontsize=8, facecolor="#E8F4FD", edgecolor=BD, labelcolor=TX,
              framealpha=0.97, handlelength=1.1, borderpad=0.7)
    return fig


# ── EVENTS LINE ───────────────────────────────────────────────────
def chart_events(df):
    yd = get_yearly_trend(df)
    xs = yd["year"].values; ys = yd["Num_Events"].values
    fig, ax = _fig(6.2, 3.8)
    ax.fill_between(xs, ys, alpha=0.12, color="#2196F3")
    ax.plot(xs, ys, color="#2196F3", lw=2.5, zorder=5)
    ax.scatter(xs, ys, color="#F57F17", s=100, zorder=6,
               edgecolors="#FFFFFF", linewidths=2)
    for x,y in zip(xs, ys):
        ax.annotate(f"{y:,.0f}", (x,y), textcoords="offset points", xytext=(0,14),
                    ha="center", color=TX, fontsize=10, fontweight="bold",
                    bbox=dict(boxstyle="round,pad=0.3",fc="#E3F2FD",ec="#2196F3",lw=1.3,alpha=0.97))
    ax.set_xticks(xs); ax.xaxis.set_major_formatter(mticker.FormatStrFormatter("%d"))
    ax.margins(x=0.25)
    _T(ax,"Total Cleanup Events by Year","Year","Number of Events",
       "Each event = one brand audit cleanup campaign")
    return fig


# ── EFFICIENCY ────────────────────────────────────────────────────
def chart_efficiency(df):
    real = df[df["parent_company"]!="Grand Total"]
    by_c = real.groupby("country").agg(
        volunteers=("volunteers","sum"),
        grand_total=("grand_total","sum")).reset_index()
    by_c = by_c[by_c["volunteers"]>0]
    by_c["ratio"] = by_c["grand_total"]/by_c["volunteers"]
    top = by_c.nlargest(12,"ratio")
    fig, ax = _fig(7.5, 4.0)
    colors_bar = [G3(i/max(len(top)-1,1)) for i in range(len(top))]
    bars = ax.barh(range(len(top)), top["ratio"].values,
                   color=colors_bar, edgecolor="none", height=0.58)
    for i,v in enumerate(top["ratio"].values):
        ax.text(v+v*0.015, i, f"{v:.2f}", va="center",
                color=TX, fontsize=8, fontweight="bold")
    ax.set_yticks(range(len(top)))
    ax.set_yticklabels(top["country"].values, color=LB, fontsize=8.5)
    ax.set_xlim(0, top["ratio"].max()*1.25)
    ax.grid(axis="y", alpha=0)
    _T(ax,"Plastic Found per Volunteer (Top 12)","Items per Volunteer","",
       "Higher = fewer volunteers found more plastic")
    return fig


# ── NESTED DONUT ──────────────────────────────────────────────────
def chart_nested_donut(df):
    real = df[df["parent_company"]!="Grand Total"]
    plastic_cols = {"PET":"pet","PP":"pp","HDPE":"hdpe","Other":"o",
                    "LDPE":"ldpe","PS":"ps","PVC":"pvc","Empty":"empty"}
    years = sorted(real["year"].unique())
    fig = plt.figure(figsize=(6.2, 5.8)); fig.patch.set_facecolor(BG)
    ax  = fig.add_axes([0.05, 0.22, 0.90, 0.72]); ax.set_facecolor(BG)
    inner_c = ["#0077B6","#E63946"]
    outer_c = C[:len(plastic_cols)]
    yr_vals = [real[real["year"]==y]["grand_total"].sum() for y in years]
    ax.pie(yr_vals, radius=0.52, labels=None, colors=inner_c,
           wedgeprops=dict(width=0.26, edgecolor="#FFFFFF", linewidth=2.2))
    for yr,val,col,yoff in zip(years, yr_vals, inner_c, [0.18,-0.18]):
        ax.text(0, yoff, str(yr), ha="center", va="center",
                color="#FFFFFF", fontsize=8.5, fontweight="bold")
    outer_vals = [real[c].sum() for c in plastic_cols.values()]
    ax.pie(outer_vals, radius=0.92, labels=None, colors=outer_c,
           wedgeprops=dict(width=0.28, edgecolor="#FFFFFF", linewidth=1.5))
    ax.text(0,0,"YEAR\n×\nTYPE", ha="center", va="center",
            color=TX, fontsize=7.5, fontweight="bold")
    ax.set_title("Plastic Type × Year Overview", color=TX, fontsize=11, fontweight="bold", pad=8)
    inner_patches = [mpatches.Patch(color=c,label=str(y)) for c,y in zip(inner_c,years)]
    outer_patches = [mpatches.Patch(color=outer_c[i],label=n)
                     for i,n in enumerate(plastic_cols.keys())]
    ax.legend(handles=inner_patches+outer_patches,
              loc="upper center", bbox_to_anchor=(0.5,-0.04),
              ncol=5, fontsize=7.5, facecolor="#E8F4FD", edgecolor=BD,
              labelcolor=TX, framealpha=0.97, handlelength=1.0, columnspacing=0.6)
    return fig
