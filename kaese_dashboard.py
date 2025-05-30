
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
st.header("Alle Bewertungen – hochkant")

# Wrap long cheese names into two lines max 30 chars each
wrapped_names = [
    "<br>".join(textwrap.wrap(name, width=30)) for name in df["Käse"]
]

fig_rating = go.Figure()

# Person markers
for person in persons:
    fig_rating.add_trace(
        go.Scatter(
            x=df[person],
            y=wrapped_names,
            mode="markers",
            name=person,
            marker=dict(color=COLORS[person], size=10, line=dict(color="white", width=1)),
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
        marker=dict(color="red", symbol="diamond-wide", size=12, line=dict(color="black", width=1)),
        hovertemplate="%{y}<br>Mittel: %{x:.2f}<extra></extra>",
    )
)

fig_height = max(600, 35 * len(df))
fig_rating.update_layout(
    height=fig_height,
    yaxis=dict(showgrid=True, automargin=True),
    xaxis=dict(title="Bewertung (1–10)", range=[0.5, 10.5]),
    legend_title="Verkoster:in",
    margin=dict(l=0, r=0, b=10, t=10),
)
st.plotly_chart(fig_rating, use_container_width=True)

#############################################
# 2) BOX-PLOTS pro Person                   #
#############################################
st.header("Verteilungen der Bewertungen (Boxplots)")

fig_box = go.Figure()
for i, person in enumerate(persons, start=1):
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
# 5) Top‑3 je Person inkl. Bilder & Preis   #
#############################################
st.header("Top 3 Käse je Person")

CHEESE_INFO = {
    "Mammutkäse": {
        "img": "https://shop.hans-wagner.de/wp-content/uploads/2024/02/KASC1271-416x416.jpg",
        "url": "https://www.xn--mammutkse-12a.ch/onlineshop/",
        "price": "5,60 CHF / 250 g",
    },
    "Vorarlberger Bergkäse": {
        "img": "https://www.heumilch.com/wp-content/uploads/2020/06/vorarlberger.jpg",
        "url": "https://www.alpenkaese.at/online-verkauf/",
        "price": "4,30 € / 250 g",
    },
    "Pyramide mit Asche": {
        "img": "https://d2j6dbq0eux0bg.cloudfront.net/images/8984039/2106993261.jpg",
        "url": "https://store8984039.ecwid.com/Pyramide-de-ch%C3%A8vre-cendr%C3%A9-p180270327",
        "price": "13,50 CHF / 220 g",
    },
    "La Buchette Fleurs": {
        "img": "https://cheeseyard.co.uk/cdn/shop/products/Flower_Goat_Cheese_800x.jpg",
        "url": "https://www.bklynlarder.com/products/buchette-aux-fleurs",
        "price": "9,50 US$ / 100 g",
    },
    "Ziegengouda mit Trüffel": {
        "img": "https://www.tomandollie.com/cdn/shop/files/Truffle_goat_gouda.jpg",
        "url": "https://www.goudakaeseshop.de/ziegenkase-und-truffel-tartufo-exclusive.html",
        "price": "5,95 € / 200 g",
    },
    "Brie de Meaux mit Senf": {
        "img": "https://i.rewe-static.com/9107555/Brie-de-Meaux-Senf.jpg",
        "url": "https://shop.rewe.de/p/brie-de-meaux-senf/9107555",
        "price": "ca. 3,49 € / 100 g (standortabh.)",
    },
    "Frischkäse „Gärtnerin Art“": {
        "img": "https://www.globus.de/medias/Frischkaese-gaertnerin.jpg?context=bWFzdGVyfGltYWdlc3wxNDA4NHxpbWFnZS9qcGVnfGg1My9oNGMvODM5MDQ2OTMyNTI0Ni5qcGd8M2MwNTg5YmQ2ZmI4MTdiMTdmYjZhNjdiYmMzMzZlZTQwZGNkNDU0ZjY0ZTVmYjBiMzQ0MWU3OWRhZTI3MGE0Yw",
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
        # Display
        if info.get("img"):
            col.image(info["img"], caption=f"{cheese} – {info.get('price','')}", use_container_width=True)
        col.markdown(f"**{rank+1}. [{cheese}]({info.get('url','#')})** – {rating}/10  ")
        if not info:
            col.warning("Bild oder Link fehlt – bitte ergänzen.")

st.caption("Farben sind konsistent: Maxi ‑ Orange, Fabi ‑ Blau, Julian ‑ Grün.  |  ⚠️ Mittelwert‑Marker = rot")
