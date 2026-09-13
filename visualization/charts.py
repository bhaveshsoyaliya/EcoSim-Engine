import plotly.graph_objects as go
import plotly.express as px

# Pollution Bar Chart
def pollution_chart(pm25, pm10, no2, o3):

    fig = go.Figure()

    fig.add_bar(
        x=["PM 2.5", "PM10", "NO₂", "O₃"],
        y=[pm25, pm10, no2, o3],
        marker_color=["red", "orange", "blue", "green"]
    )

    fig.update_layout(
        title="Live Pollution Levels",
        template="plotly_dark",
        height=400
    )

    return fig


# 24-Hour Forecast Chart
def forecast_chart(df):

    fig = px.line(
        df,
        x="Hour",
        y="PM 2.5",          # <-- FIXED
        markers=True,
        title="24-Hour PM 2.5 Forecast"
    )

    fig.update_layout(
        template="plotly_dark",
        height=420,
        xaxis_title="Hour",
        yaxis_title="PM 2.5 (µg/m³)"
    )

    return fig

import plotly.graph_objects as go

def plume_heatmap(X, Y, C):

    fig = go.Figure(
        data=go.Heatmap(
            z=C,
            x=X[0],
            y=Y[:,0],
            colorscale="Turbo"
        )
    )

    fig.update_layout(
        title="Gaussian PM 2.5 Dispersion",
        template="plotly_dark",
        xaxis_title="Distance (m)",
        yaxis_title="Cross Wind (m)",
        height=500
    )

    return fig

import plotly.graph_objects as go

def carbon_gauge(score):

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={"text":"Sustainability Score"},
        gauge={
            "axis":{"range":[0,100]},
            "bar":{"color":"green"},
            "steps":[
                {"range":[0,40],"color":"red"},
                {"range":[40,70],"color":"orange"},
                {"range":[70,100],"color":"green"}
            ]
        }
    ))

    fig.update_layout(
        template="plotly_dark",
        height=300
    )

    return fig
