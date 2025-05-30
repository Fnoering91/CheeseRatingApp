
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from itertools import cycle

# ---- CONFIG ----
st.set_page_config(page_title="Cheese‑Tasting Dashboard", layout="wide")
DATA_FILE = "ECC_Kaese_Rating_05152025.xlsx"  # liegt im Repo

# Farbpalette
COLORS = {
    "Maxi": "#FF7F0E",   # orange
    "Fabi": "#1F77B4",   # blau
    "Julian": "#2CA02C"  # grün
}
MEAN_COLOR = "#000000"  # schwarz

# Bilder, Links & Preise (vereinfachtes Mapping; ggf. anpassen)
CHEESE_INFO = {
    "Mammutkäse": {
        "img": "https://worldofcheese.ch/wp-content/uploads/2022/04/DSC5901-scaled-2-400x365.jpg",
        "url": "https://www.xn--mammutkse-12a.ch/onlineshop/",
        "price": "CHF 22.50 / kg"
    },
    "Voralberger Bergkäse": {
        "img": "https://better-eat-better.shop/media/25/2b/7d/1637486256/Benutzerdefiniertes%20Format%20%E2%80%93%2046.jpg?ts=1637486256",
        "url": "https://www.alpenkaese.at/online-verkauf/",
        "price": "18,20 € / kg"
    },
    "Pyramide mit Asche": {
        "img": "https://www.waltmann.de/media/images/org/tmp/0ff3c8bdf8e2e5692e8b335b30f1eab170a9c20e.jpg",
        "url": "https://www.waltmann.de/artikel_detail.html?a=97",
        "price": "12,15 € / 300 g"
    },
    "La Buchette Fleurs": {
        "img": "https://shop.rewe.de/product-image/7035272/standard/la-buchette-fleurs-100g.png",
        "url": "https://shop.rewe.de/p/la-buchette-fleurs-100g/7035272",
        "price": "3,49 € / 100 g"
    },
    "Ziegengouda mit Trueffel": {
        "img": "https://www.goudakaeseshop.de/media/catalog/product/cache/0/image/9df78eab33525d08d6e5fb8d27136e95/b/o/boer_n_trots_truffel_geit_honing.png",
        "url": "https://www.goudakaeseshop.de/boer-n-trots-honig-ziege-trueffel.html",
        "price": "ca. 26,95 € / kg"
    },
    "Brie de Meaux mit Senf": {
        "img": "https://shop.rewe.de/product-image/9107555/standard/brie-de-meaux-senf.png",
        "url": "https://shop.rewe.de/p/brie-de-meaux-senf/9107555",
        "price": "2,99 € / 100 g"
    },
    "Frischkäse Gärtnerin Art": {
        "img": "https://produkte.globus.de/images/2/9/1/4/6/5/291465/291465_m.jpg",
        "url": "https://produkte.globus.de/wurst-kaese/kaesetheke/frischkaese/291465/frischkaese-gaertnerin",
        "price": "ca. 1,99 € / 100 g"
    }
}

# ---- LOAD DATA ----
@st.cache_data
def load_data():
    df = pd.read_excel(DATA_FILE, sheet_name="rawDaten", engine="openpyxl")
    persons = ["Maxi", "Fabi", "Julian"]
    df["Mittelwert"] = df[persons].mean(axis=1)
    return df, persons

df, persons = load_data()

st.title("🧀 Cheese‑Tasting Dashboard")

# ----------------------------------------------------------------------------------------------------------------------
# 1) Horizontale Scatter‑Charts mit Mittelwertlinie (y = Käse; x = Bewertung)
# ----------------------------------------------------------------------------------------------------------------------
st.subheader("Bewertungen aller Käsevarianten")

fig_scatter = go.Figure()
jitters = cycle([-0.15, 0, 0.15])  # kleine Versätze, damit Punkte nicht exakt übereinanderliegen

for person in persons:
    jitter = next(jitters)
    fig_scatter.add_trace(
        go.Scatter(
            x=df[person] + jitter,
            y=df["Käse"],
            mode="markers",
            name=person,
            marker=dict(color=COLORS[person], size=10, line=dict(width=1, color="white")),
            hovertemplate=f"<b>%{{y}}</b><br>{person}: %{{x}}<extra></extra>",
        )
    )

# Mittelwert als Linie
fig_scatter.add_trace(
    go.Scatter(
        x=df["Mittelwert"],
        y=df["Käse"],
        mode="lines+markers",
        name="Mittelwert",
        line=dict(color=MEAN_COLOR, width=3, dash="dash"),
        marker=dict(symbol="diamond", size=9, color=MEAN_COLOR),
        hovertemplate="<b>%{y}</b><br>Mittelwert: %{x:.2f}<extra></extra>",
    )
)

fig_scatter.update_layout(
    height=max(800, 25 * len(df)),  # passt Höhe an Länge der Liste an
    yaxis=dict(autorange="reversed", title="Käse"),
    xaxis=dict(title="Bewertung (1 = schlecht, 10 = gut)", range=[0.5, 10.5]),
    margin=dict(l=150, r=50, t=10, b=10),
    legend_title="Verkoster:in",
)
st.plotly_chart(fig_scatter, use_container_width=True)

# ----------------------------------------------------------------------------------------------------------------------
# 2) Boxplots
# ----------------------------------------------------------------------------------------------------------------------
st.subheader("Boxplots der Bewertungen pro Person")

fig_box = go.Figure()
for person in persons:
    fig_box.add_trace(
        go.Box(
            y=df[person],
            name=person,
            marker_color=COLORS[person],
            boxmean="sd",
            boxpoints="all",
            jitter=0.3,
            pointpos=-1.8,
        )
    )
fig_box.update_layout(
    yaxis_title="Bewertung",
    height=500,
    legend_title="Verkoster:in",
    violingap=0.25,
)
st.plotly_chart(fig_box, use_container_width=True)

# ----------------------------------------------------------------------------------------------------------------------
# 3) Korrelationsmatrix
# ----------------------------------------------------------------------------------------------------------------------
st.subheader("Korrelation der Bewerter:innen")
corr = df[persons].corr()
fig_corr = go.Figure(
    data=go.Heatmap(
        z=corr.values,
        x=persons,
        y=persons,
        colorscale="RdBu",
        zmin=-1,
        zmax=1,
        text=np.round(corr.values, 2),
        texttemplate="%{text}",
        hovertemplate="ρ = %{z:.2f}<extra></extra>",
    )
)
fig_corr.update_layout(
    height=350,
    coloraxis_colorbar=dict(title="ρ"),
)
st.plotly_chart(fig_corr, use_container_width=True)

# ----------------------------------------------------------------------------------------------------------------------
# 4) Radarplot Kategorie‑Durchschnitt
# ----------------------------------------------------------------------------------------------------------------------
st.subheader("Radar‑Plot – Durchschnittsbewertungen je Kategorie")
cat_means = df.groupby("Kategorie")[persons].mean().sort_index()
categories = list(cat_means.index)

fig_radar = go.Figure()
for person in persons:
    values = cat_means[person].tolist()
    values += values[:1]
    fig_radar.add_trace(
        go.Scatterpolar(
            r=values,
            theta=categories + categories[:1],
            name=person,
            line=dict(color=COLORS[person]),
            marker=dict(color=COLORS[person]),
        )
    )
fig_radar.update_layout(
    polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
    showlegend=True,
    height=600,
    legend_title="Verkoster:in",
)
st.plotly_chart(fig_radar, use_container_width=True)

# ----------------------------------------------------------------------------------------------------------------------
# 5) Top‑3 Käse pro Person inkl. Bild, Preis & Link
# ----------------------------------------------------------------------------------------------------------------------
st.subheader("Top 3 Käse je Person")

cols = st.columns(len(persons))
for idx, person in enumerate(persons):
    col = cols[idx]
    col.markdown(f"### {person}")
    top3 = df.nlargest(3, person)[["Käse", person]].reset_index(drop=True)
    for i in range(3):
        cheese = top3.loc[i, "Käse"]
        rating = top3.loc[i, person]
        info = CHEESE_INFO.get(cheese, {})
        img = info.get("img")
        url = info.get("url")
        price = info.get("price", "Preis n. a.")
        if img:
            col.image(img, use_column_width=True)
        col.markdown(f"**{i+1}. [{cheese}]({url if url else '#'})** – {rating}/10  Preis: {price}")

st.caption("Farben sind konsistent: Maxi ‑ Orange, Fabi ‑ Blau, Julian ‑ Grün.")
