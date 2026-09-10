import pytest
import numpy as np
from backend.app.geospatial.raster_ops import RasterOps

def test_ndvi_reference_values():
    nir = np.array([[0.6, 0.8], [0.5, 0.4]], dtype=np.float32)
    red = np.array([[0.2, 0.2], [0.1, 0.4]], dtype=np.float32)
    
    # Expected: (0.6-0.2)/0.8 = 0.5; (0.8-0.2)/1.0 = 0.6; (0.5-0.1)/0.6 = 0.6667; (0.4-0.4)/0.8 = 0.0
    ndvi = RasterOps.calculate_ndvi(nir, red)
    assert np.isclose(ndvi[0, 0], 0.5, atol=1e-3)
    assert np.isclose(ndvi[0, 1], 0.6, atol=1e-3)
    assert np.isclose(ndvi[1, 1], 0.0, atol=1e-3)

def test_spectral_indices_zero_denominator():
    zero_arr = np.zeros((10, 10), dtype=np.float32)
    ndvi = RasterOps.calculate_ndvi(zero_arr, zero_arr)
    assert not np.isnan(ndvi).any()
    assert not np.isinf(ndvi).any()
    assert (ndvi == 0.0).all()

def test_spectral_indices_nan_and_inf_inputs():
    nir = np.array([[0.5, np.nan], [np.inf, -np.inf]], dtype=np.float32)
    red = np.array([[0.1, 0.2], [0.3, 0.4]], dtype=np.float32)
    
    ndvi = RasterOps.calculate_ndvi(nir, red)
    assert not np.isnan(ndvi).any()
    assert not np.isinf(ndvi).any()

def test_integer_inputs():
    nir_int = np.array([[6000, 8000]], dtype=np.uint16)
    red_int = np.array([[2000, 2000]], dtype=np.uint16)
    
    ndvi = RasterOps.calculate_ndvi(nir_int, red_int)
    assert np.isclose(ndvi[0, 0], 0.5, atol=1e-3)
    assert np.isclose(ndvi[0, 1], 0.6, atol=1e-3)

def test_all_five_spectral_indices():
    green = np.array([0.4, 0.5], dtype=np.float32)
    nir = np.array([0.6, 0.2], dtype=np.float32)
    swir = np.array([0.2, 0.4], dtype=np.float32)
    red = np.array([0.1, 0.3], dtype=np.float32)

    ndvi = RasterOps.calculate_ndvi(nir, red)
    ndwi = RasterOps.calculate_ndwi(green, nir)
    mndwi = RasterOps.calculate_mndwi(green, swir)
    ndbi = RasterOps.calculate_ndbi(swir, nir)
    nbr = RasterOps.calculate_nbr(nir, swir)

    assert len(ndvi) == 2
    assert len(ndwi) == 2
    assert len(mndwi) == 2
    assert len(ndbi) == 2
    assert len(nbr) == 2
