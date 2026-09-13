import folium

def create_tree_heatmap(center_lat, center_lon, df):
    """
    EcoSim GIS Tree Heatmap
    Creates colored grid around city center.
    """

    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=14,
        tiles="OpenStreetMap"
    )

    # 20 x 20 grid (matches raster_utils)
    cell = 0.00225
    start_lat = center_lat - (20 * cell) / 2
    start_lon = center_lon - (20 * cell) / 2

    for _, row in df.iterrows():

        lat = start_lat + row["row"] * cell
        lon = start_lon + row["col"] * cell

        if row["Priority"] == "Critical":
            color = "#ff0000"
        elif row["Priority"] == "High":
            color = "#ff8800"
        elif row["Priority"] == "Medium":
            color = "#ffd400"
        else:
            color = "#00cc44"

        popup = f"""
        <b>{row['Grid']}</b><br>
        NDVI: {row['NDVI']}<br>
        Vegetation: {row['Vegetation %']} %<br>
        ETDI: {row['ETDI']}<br>
        Trees Needed: {row['Trees Needed']}<br>
        Priority: {row['Priority']}
        """

        folium.Rectangle(
            bounds=[
                [lat, lon],
                [lat + cell, lon + cell]
            ],
            color="black",
            weight=0.5,
            fill=True,
            fill_color=color,
            fill_opacity=0.60,
            popup=popup
        ).add_to(m)

    return m