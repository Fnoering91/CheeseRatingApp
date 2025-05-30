
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

import textwrap, pathlib
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

##########################
# ---- CONFIG & COLORS ---
##########################
st.set_page_config(page_title="🧀 Cheese‑Tasting Dashboard", layout="wide")
COLORS = {"Maxi": "#FF7F0E", "Fabi": "#1F77B4", "Julian": "#2CA02C"}  # feste Zuordnung
JITTER_X = {"Maxi": -0.15, "Fabi": 0.0, "Julian": 0.15}  # für Plot 1
DATA_FILE = pathlib.Path(__file__).parent / "ECC_Kaese_Rating_05152025.xlsx"

st.title("🧀 Cheese‑Tasting Dashboard")

##########################
# ---- LOAD DATA ---------
##########################
if not DATA_FILE.exists():
    st.error(f"Die Datei {DATA_FILE.name} konnte nicht gefunden werden. Bitte ins Repo legen.")
    st.stop()

df = pd.read_excel(DATA_FILE, sheet_name="rawDaten", engine="openpyxl")
persons = list(COLORS.keys())
df["Mittelwert"] = df[persons].mean(axis=1)

#############################################
# 1) RATING PLOT  (Hochkant / Smartphone)   #
#############################################
st.header("Alle Bewertungen")

# Wrap long cheese names into two lines max 30 chars each
wrapped_names = ["<br>".join(textwrap.wrap(name, width=30)) for name in df["Käse"]]

fig_rating = go.Figure()

# Person markers
for person in persons:
    jitter = JITTER_X[person]
    fig_rating.add_trace(
        go.Scatter(
            x=df[person] + jitter,
            y=wrapped_names,
            mode="markers",
            name=person,
            marker=dict(color=COLORS[person], size=11, line=dict(color="white", width=1), opacity=0.85),
            hovertemplate=f"%{{y}}<br>{person}: %{{x}}<extra></extra>",
        )
    )

# Mean marker in RED
fig_rating.add_trace(
    go.Scatter(
        x=df["Mittelwert"],
        y=wrapped_names,
        mode="markers",
        name="Mittelwert",
        marker=dict(color="red", symbol="diamond-wide", size=14, line=dict(color="black", width=1)),
        hovertemplate="%{y}<br>Mittel: %{x:.2f}<extra></extra>",
    )
)

fig_height = max(650, 35 * len(df))
fig_rating.update_layout(
    height=fig_height,
    yaxis=dict(showgrid=True, automargin=True),
    xaxis=dict(title="Bewertung (1–10)", range=[0.5, 10.5]),
    legend_title="Verkoster:in",
    legend=dict(orientation="h", yanchor="bottom", y=1.03, xanchor="left", x=0),
    margin=dict(l=0, r=0, b=10, t=40),
)
st.plotly_chart(fig_rating, use_container_width=True)

#############################################
# 2) BOX-PLOTS pro Person                   #
#############################################
st.header("Verteilungen der Bewertungen (Boxplots)")

fig_box = go.Figure()
for person in persons:
    fig_box.add_trace(
        go.Box(
            x=df[person],
            name=person,
            marker=dict(color=COLORS[person]),
            boxmean="sd",
            orientation="h",
        )
    )

fig_box.update_layout(
    height=400,
    xaxis=dict(title="Bewertung"),
    legend_title="Verkoster:in",
)
st.plotly_chart(fig_box, use_container_width=True)

#############################################
# 3) Korrelation                            #
#############################################
st.header("Korrelation der Bewerter:innen")
corr = df[persons].corr()
fig_corr = px.imshow(
    corr,
    text_auto=".2f",
    aspect="auto",
    color_continuous_scale="RdBu",
    range_color=(-1, 1),
)
fig_corr.update_coloraxes(colorbar_title="ρ")
st.plotly_chart(fig_corr, use_container_width=True)

#############################################
# 4) Radarplot Kategorien                   #
#############################################
st.header("Radar‑Plot – Durchschnittsbewertungen je Kategorie")
cat_means = df.groupby("Kategorie")[persons].mean().sort_index()
categories = cat_means.index.tolist()

fig_radar = go.Figure()
for person in persons:
    values = cat_means[person].tolist()
    values += values[:1]
    fig_radar.add_trace(
        go.Scatterpolar(
            r=values,
            theta=categories + [categories[0]],
            name=person,
            line=dict(color=COLORS[person]),
        )
    )

fig_radar.update_layout(
    polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
    showlegend=True,
    height=600,
    legend_title="Verkoster:in",
)
st.plotly_chart(fig_radar, use_container_width=True)

#############################################
# 5) Top‑3 je Person (Link & Preis)         #
#############################################
st.header("Top 3 Käse je Person")

CHEESE_INFO = {
    "Mammutkäse": {
        "url": "https://www.xn--mammutkse-12a.ch/onlineshop/",
        "price": "5,60 CHF / 250 g",
    },
    "Vorarlberger Bergkäse": {
        "url": "https://www.alpenkaese.at/online-verkauf/",
        "price": "4,30 € / 250 g",
    },
    "Pyramide mit Asche": {
        "url": "https://store8984039.ecwid.com/Pyramide-de-ch%C3%A8vre-cendr%C3%A9-p180270327",
        "price": "13,50 CHF / 220 g",
    },
    "La Buchette Fleurs": {
        "url": "https://www.bklynlarder.com/products/buchette-aux-fleurs",
        "price": "9,50 US$ / 100 g",
    },
    "Ziegengouda mit Trüffel": {
        "url": "https://www.goudakaeseshop.de/ziegenkase-und-truffel-tartufo-exclusive.html",
        "price": "5,95 € / 200 g",
    },
    "Brie de Meaux mit Senf": {
        "url": "https://shop.rewe.de/p/brie-de-meaux-senf/9107555",
        "price": "ca. 3,49 € / 100 g (standortabh.)",
    },
    "Frischkäse „Gärtnerin Art“": {
        "url": "https://produkte.globus.de/wurst-kaese/kaesetheke/frischkaese/291465/frischkaese-gaertnerin",
        "price": "1,80 € / Portion",
    },
}

cols = st.columns(len(persons))
for idx, person in enumerate(persons):
    col = cols[idx]
    col.subheader(person)
    top3 = df.nlargest(3, person)[["Käse", person]].reset_index(drop=True)
    for rank in range(3):
        cheese = top3.loc[rank, "Käse"]
        rating = top3.loc[rank, person]
        info = CHEESE_INFO.get(cheese, {})
        link = info.get("url", "#")
        price = info.get("price", "k. A.")
        col.markdown(f"**{rank+1}. [{cheese}]({link})** – {rating}/10  Preis: {price}")

#############################################
# 6) Fazit                                  #
#############################################
st.header("Fazit & Auffälligkeiten")

overall_best = df.sort_values("Mittelwert", ascending=False).iloc[0]["Käse"]
overall_worst = df.sort_values("Mittelwert").iloc[0]["Käse"]

best_cat = cat_means.mean(axis=1).idxmax()
worst_cat = cat_means.mean(axis=1).idxmin()

stds = df[persons].std()
min_std_person = stds.idxmin()
max_std_person = stds.idxmax()

corr = df[persons].corr()
corr_values = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))
max_corr_val = corr_values.max().max()
max_corr_pair = corr_values.stack().idxmax()

st.markdown(
    f"""
* **Gesamtsieger:** **{overall_best}** – höchste Durchschnittsbewertung aller drei Verkoster.  
* **Schlusslicht:** **{overall_worst}** – kam bei keinem so richtig gut an.  

* **Beliebteste Kategorie:** **{best_cat}**  
* **Schwächste Kategorie:** **{worst_cat}**

* **Konsistentestes Bewertungsverhalten:** *{min_std_person}* (geringste σ ≈ {stds[min_std_person]:.2f})  
  **Variabelstes:** *{max_std_person}* (höchste σ ≈ {stds[max_std_person]:.2f})  

* **Stärkste Geschmacks‑Übereinstimmung:** **{max_corr_pair[0]} & {max_corr_pair[1]}** (ρ ≈ {max_corr_val:.2f})
"""
)

st.caption("Farben sind konsistent: Maxi ‑ Orange, Fabi ‑ Blau, Julian ‑ Grün.  |  Mittelwert‑Marker = rot")
