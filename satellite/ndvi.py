import numpy as np

def calculate_ndvi(ds):

    red = ds.red.isel(time=0).values.astype("float32")
    nir = ds.nir.isel(time=0).values.astype("float32")

    ndvi = (nir-red)/(nir+red+1e-6)

    return ndvi


def green_cover(ndvi):

    vegetation = ndvi > 0.35

    percent = vegetation.mean()*100

    return round(percent,2)