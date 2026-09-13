import plotly.express as px

def microclimate_heatmap(df):

    fig = px.density_heatmap(
        df,
        x="Col",
        y="Row",
        z="Surface Temp",
        color_continuous_scale="Turbo",
        title="Urban Surface Temperature (°C)"
    )

    fig.update_layout(
        height=650,
        xaxis_title="Grid X",
        yaxis_title="Grid Y"
    )

    fig.update_yaxes(autorange="reversed")

    return fig