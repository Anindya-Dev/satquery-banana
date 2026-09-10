import numpy as np
from backend.app.geospatial.raster_ops import RasterOps

def test_ndvi_calculation():
    nir = np.array([0.8, 0.6, 0.4])
    red = np.array([0.2, 0.2, 0.2])
    ndvi = RasterOps.calculate_ndvi(nir, red)
    # expected: (0.8-0.2)/(0.8+0.2) = 0.6 / 1.0 = 0.6
    assert np.isclose(ndvi[0], 0.6)
    assert np.isclose(ndvi[1], 0.5)

def test_ndwi_calculation():
    green = np.array([0.5, 0.4])
    nir = np.array([0.1, 0.2])
    ndwi = RasterOps.calculate_ndwi(green, nir)
    # expected: (0.5-0.1)/(0.5+0.1) = 0.4 / 0.6 = 0.6667
    assert np.isclose(ndwi[0], 0.6666667)

def test_index_stats():
    arr = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
    stats = RasterOps.get_index_stats(arr)
    assert stats["mean"] == 0.3
    assert stats["min"] == 0.1
    assert stats["max"] == 0.5

def test_bitemporal_diff():
    t1 = np.ones((10, 10)) * 0.2
    t2 = np.ones((10, 10)) * 0.6
    diff, mask, pct = RasterOps.compute_bitemporal_diff(t1, t2, threshold=0.3)
    assert pct == 100.0
    assert np.all(mask == 1)
