
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="Cheese Tasting Dashboard", layout="wide")

st.title("🧀 Cheese‑Tasting Dashboard")

# ---- 1. File upload ----
uploaded_file = st.file_uploader("Lade die Bewertungs‑Excel hoch (rawDaten‑ & Skala‑Sheets müssen enthalten sein)", type=["xlsx"])

colors = {"Maxi": "#FF7F0E", "Fabi": "#1F77B4", "Julian": "#2CA02C"}  # konsistente Farbpalette

if uploaded_file:
    df = pd.read_excel(uploaded_file, sheet_name="rawDaten", engine="openpyxl")

    persons = list(colors.keys())
    df["Mittelwert"] = df[persons].mean(axis=1)

    # ---- 2. Scatter & mean‑line ----
    st.subheader("Bewertungen aller Käsevarianten")
    import numpy as np
    from itertools import cycle

    fig_scatter = go.Figure()
    jitters = cycle([-0.20, 0, 0.20])  # gleichmäßige Versätze

    for person in persons:
        jitter = next(jitters)
        fig_scatter.add_trace(
            go.Scatter(
                x=[i + jitter for i in range(len(df))],
                y=df[person],
                mode="markers",
                name=person,
                marker=dict(color=colors[person], size=10, line=dict(width=1, color="white")),
                hovertemplate="<b>%{text}</b><br>" + person + ": %{y}<extra></extra>",
                text=df["Käse"],
            )
        )

    fig_scatter.add_trace(
        go.Scatter(
            x=list(range(len(df))),
            y=df["Mittelwert"],
            mode="lines+markers",
            name="Mittelwert",
            line=dict(color="black", width=2),
            marker=dict(symbol="diamond", size=8),
            hovertemplate="<b>%{text}</b><br>Mittelwert: %{y:.2f}<extra></extra>",
            text=df["Käse"],
        )
    )

    fig_scatter.update_layout(
        height=650,
        xaxis=dict(
            tickmode="array",
            tickvals=list(range(len(df))),
            ticktext=df["Käse"],
            tickangle=45,
        ),
        yaxis_title="Bewertung (1 = schlecht, 10 = gut)",
        margin=dict(l=0, r=0, b=150),
        legend_title="Verkoster:in",
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    # ---- 3. Violin plots ----
    st.subheader("Verteilung der Bewertungen pro Person")
    fig_violin = go.Figure()
    for person in persons:
        fig_violin.add_trace(
            go.Violin(
                y=df[person],
                name=person,
                box_visible=True,
                meanline_visible=True,
                line_color=colors[person],
                fillcolor=colors[person],
                opacity=0.6,
                spanmode="hard",
                points="all",
                pointpos=0,
            )
        )
    fig_violin.update_layout(
        yaxis_title="Bewertung",
        height=500,
        legend_title="Verkoster:in",
        violingap=0.2,
    )
    st.plotly_chart(fig_violin, use_container_width=True)

    # ---- 4. Korrelationsanalyse ----
    st.subheader("Korrelation der Bewerter:innen")
    corr = df[persons].corr()
    fig_corr = px.imshow(
        corr,
        text_auto=".2f",
        aspect="auto",
        color_continuous_scale="RdBu",
        range_color=(-1, 1),
    )
    fig_corr.update_coloraxes(colorbar_title="ρ")
    fig_corr.update_layout(height=350, margin=dict(t=40, l=0, r=0, b=0))
    st.plotly_chart(fig_corr, use_container_width=True)

    # ---- 5. Radarplot nach Käsekategorie ----
    st.subheader("Radar‑Plot – Durchschnittsbewertungen je Kategorie")
    cat_means = (
        df.groupby("Kategorie")[persons]
        .mean()
        .sort_index()  # zur reproduzierbaren Reihenfolge
    )
    categories = list(cat_means.index)

    fig_radar = go.Figure()
    for person in persons:
        values = cat_means[person].tolist()
        values += values[:1]  # Radar schließt Kreis
        fig_radar.add_trace(
            go.Scatterpolar(
                r=values,
                theta=categories + categories[:1],
                name=person,
                line=dict(color=colors[person]),
                marker=dict(color=colors[person]),
            )
        )
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
        showlegend=True,
        height=600,
        legend_title="Verkoster:in",
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    # ---- 6. Top‑3 Ranking pro Person ----
    st.subheader("Top 3 Käse je Person")
    import streamlit as st
    from PIL import Image
    import requests
    from io import BytesIO

    cols = st.columns(len(persons))
    for idx, person in enumerate(persons):
        col = cols[idx]
        col.markdown(f"### {person}")
        top3 = df.nlargest(3, person)[["Käse", person]].reset_index(drop=True)
        for i in range(3):
            cheese_name = top3.loc[i, "Käse"]
            rating = top3.loc[i, person]
            col.markdown(f"**{i+1}. {cheese_name}** – {rating}/10")

    st.markdown("—")
    st.caption("Farben sind konsistent: Maxi ‑ Orange, Fabi ‑ Blau, Julian ‑ Grün.")

else:
    st.info("⬆️ Bitte lade zuerst die Bewertungs‑Datei hoch, um die Visualisierung zu starten.")
