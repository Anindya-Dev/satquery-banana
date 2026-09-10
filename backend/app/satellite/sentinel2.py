from __future__ import annotations

from datetime import datetime
import base64
from io import BytesIO
from typing import Any, Dict, List, Optional

import numpy as np
import requests
import rasterio
from PIL import Image
from rasterio.windows import from_bounds
from rasterio.warp import transform_bounds

from backend.app.satellite.base import SatelliteProvider
from backend.app.domain.models import ImageMetadata, SensorType
from backend.app.core.exceptions import SatelliteDataUnavailableError
from backend.app.core.config import settings

class Sentinel2Provider(SatelliteProvider):
    """Reads real Sentinel-2 L2A Cloud Optimized GeoTIFF windows from Planetary Computer."""

    def __init__(self, stac_api_url: Optional[str] = None):
        super().__init__(provider_name="Microsoft Planetary Computer Sentinel-2 L2A")
        self.stac_api_url = stac_api_url or settings.STAC_API_URL
        self._items: Dict[str, Dict[str, Any]] = {}
        self._band_cache: Dict[tuple[str, str], np.ndarray] = {}
        self._preview_cache: Dict[str, str] = {}

    def discover_scenes(
        self,
        bbox: List[float],
        start_date: str,
        end_date: str,
        max_cloud: float = 15.0
    ) -> List[ImageMetadata]:
        payload = {
            "collections": [settings.STAC_COLLECTION],
            "bbox": bbox,
            "datetime": f"{start_date}/{end_date}",
            "limit": settings.STAC_SEARCH_LIMIT,
            "query": {"eo:cloud_cover": {"lt": max_cloud}},
        }
        try:
            response = requests.post(f"{self.stac_api_url}/search", json=payload, timeout=30)
            response.raise_for_status()
        except requests.RequestException as exc:
            raise SatelliteDataUnavailableError(f"Unable to search the public Sentinel-2 catalog: {exc}") from exc

        features = response.json().get("features", [])
        features.sort(key=lambda item: (item.get("properties", {}).get("eo:cloud_cover", 100.0), item.get("properties", {}).get("datetime", "")))
        scenes = []
        for item in features:
            scene_id = item["id"]
            self._items[scene_id] = item
            props = item.get("properties", {})
            scenes.append(ImageMetadata(
                id=scene_id,
                sensor=SensorType.OPTICAL_SENTINEL2,
                date=props.get("datetime", "")[:10],
                spatial_resolution_m=10.0,
                cloud_cover_percent=float(props.get("eo:cloud_cover", 100.0)),
                bbox=item.get("bbox", bbox),
                bands_available=list(item.get("assets", {}).keys()),
                collection=item.get("collection"),
                source_uri=item.get("links", [{}])[0].get("href"),
            ))
        return scenes

    def fetch_metadata(self, scene_id: str) -> Optional[ImageMetadata]:
        item = self._items.get(scene_id)
        if not item:
            return None
        props = item.get("properties", {})
        return ImageMetadata(
            id=scene_id,
            sensor=SensorType.OPTICAL_SENTINEL2,
            date=props.get("datetime", "")[:10],
            cloud_cover_percent=float(props.get("eo:cloud_cover", 100.0)),
            bbox=item.get("bbox", []),
            bands_available=list(item.get("assets", {}).keys()),
            collection=item.get("collection"),
        )

    def get_band_data(self, scene_id: str, band_name: str) -> np.ndarray:
        cache_key = (scene_id, band_name)
        if cache_key in self._band_cache:
            return self._band_cache[cache_key]

        item = self._items.get(scene_id)
        if not item:
            raise SatelliteDataUnavailableError(f"Scene '{scene_id}' was not selected in this analysis request.")
        asset_name = self._resolve_asset_name(item.get("assets", {}), band_name)
        asset = item.get("assets", {}).get(asset_name)
        if not asset:
            raise SatelliteDataUnavailableError(f"Scene '{scene_id}' does not provide required Sentinel-2 band '{band_name}'.")

        href = self._sign_asset(asset["href"])
        bbox = item.get("bbox")
        try:
            with rasterio.open(href) as dataset:
                bounds = transform_bounds("EPSG:4326", dataset.crs, *bbox, densify_pts=21)
                window = from_bounds(*bounds, transform=dataset.transform).round_offsets().round_lengths()
                window = window.intersection(rasterio.windows.Window(0, 0, dataset.width, dataset.height))
                scale = min(1.0, settings.RASTER_MAX_DIMENSION / max(window.width, window.height))
                out_height = max(1, int(window.height * scale))
                out_width = max(1, int(window.width * scale))
                data = dataset.read(1, window=window, out_shape=(out_height, out_width), masked=True)
                data = data.astype(np.float32).filled(np.nan)
        except Exception as exc:
            raise SatelliteDataUnavailableError(f"Unable to read Sentinel-2 band '{band_name}' for scene '{scene_id}': {exc}") from exc

        # Sentinel-2 L2A reflectance is commonly stored as scaled integer DN in COGs.
        finite = data[np.isfinite(data)]
        if finite.size and np.nanmedian(finite) > 2:
            data *= 0.0001
        self._band_cache[cache_key] = data
        return data

    def get_valid_pixel_ratio(self, scene_id: str) -> float:
        band = self.get_band_data(scene_id, "B8")
        valid = np.isfinite(band) & (band > 0)
        return float(np.mean(valid)) if valid.size else 0.0

    def get_rgb_preview(self, scene_id: str) -> str:
        """Return a compact browser-ready RGB preview from the exact live scene used for analysis."""
        if scene_id in self._preview_cache:
            return self._preview_cache[scene_id]

        red = self.get_band_data(scene_id, "B4")
        green = self.get_band_data(scene_id, "B3")
        blue = self.get_band_data(scene_id, "B2")
        rgb = np.dstack([self._stretch(red), self._stretch(green), self._stretch(blue)])
        image = Image.fromarray(rgb, mode="RGB")
        image.thumbnail((512, 512))
        encoded = BytesIO()
        image.save(encoded, format="JPEG", quality=82, optimize=True)
        preview = "data:image/jpeg;base64," + base64.b64encode(encoded.getvalue()).decode("ascii")
        self._preview_cache[scene_id] = preview
        return preview

    @staticmethod
    def _resolve_asset_name(assets: Dict[str, Any], band_name: str) -> str:
        """Accept both project shorthand (B8/B4/B3) and STAC's B08/B04/B03 keys."""
        if band_name in assets:
            return band_name
        if band_name.startswith("B") and band_name[1:].isdigit():
            padded = f"B{int(band_name[1:]):02d}"
            if padded in assets:
                return padded
        return band_name

    @staticmethod
    def _stretch(data: np.ndarray) -> np.ndarray:
        valid = data[np.isfinite(data)]
        if valid.size == 0:
            return np.zeros(data.shape, dtype=np.uint8)
        low, high = np.percentile(valid, [2, 98])
        if high <= low:
            return np.zeros(data.shape, dtype=np.uint8)
        scaled = np.clip((data - low) / (high - low), 0, 1)
        return np.nan_to_num(scaled * 255, nan=0).astype(np.uint8)

    def _sign_asset(self, href: str) -> str:
        try:
            response = requests.get(
                "https://planetarycomputer.microsoft.com/api/sas/v1/sign",
                params={"href": href},
                timeout=30,
            )
            response.raise_for_status()
            return response.json()["href"]
        except (requests.RequestException, KeyError) as exc:
            raise SatelliteDataUnavailableError(f"Unable to authorize access to public Sentinel-2 asset: {exc}") from exc
