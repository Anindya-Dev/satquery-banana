import sqlite3
import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from backend.app.core.config import settings
from backend.app.core.exceptions import StorageError

class MetadataDB:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or settings.DB_PATH
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        try:
            conn = sqlite3.connect(self.db_path, timeout=10.0)
            conn.row_factory = sqlite3.Row
            return conn
        except Exception as e:
            conn = sqlite3.connect(":memory:", timeout=10.0)
            conn.row_factory = sqlite3.Row
            return conn

    def _init_db(self):
        """Initializes database schema tables if they do not exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Scenes Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scenes (
                    scene_id TEXT PRIMARY KEY,
                    provider TEXT NOT NULL,
                    sensor TEXT NOT NULL,
                    acquisition_time TEXT NOT NULL,
                    bbox_json TEXT NOT NULL,
                    cloud_cover REAL NOT NULL,
                    bands_json TEXT NOT NULL,
                    source_uri TEXT
                )
            """)

            # Tiles Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tiles (
                    tile_id TEXT PRIMARY KEY,
                    scene_id TEXT NOT NULL,
                    bbox_json TEXT NOT NULL,
                    cloud_cover REAL NOT NULL,
                    valid_pixel_ratio REAL NOT NULL,
                    stats_json TEXT,
                    embedding_id TEXT,
                    FOREIGN KEY(scene_id) REFERENCES scenes(scene_id)
                )
            """)

            # Observations Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS observations (
                    observation_id TEXT PRIMARY KEY,
                    tile_id TEXT NOT NULL,
                    metric TEXT NOT NULL,
                    value REAL NOT NULL,
                    formula TEXT,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY(tile_id) REFERENCES tiles(tile_id)
                )
            """)

            # Background Jobs Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS jobs (
                    job_id TEXT PRIMARY KEY,
                    task_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    progress_pct REAL DEFAULT 0.0,
                    result_json TEXT,
                    error_msg TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)

            # Conversational Sessions Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    history_json TEXT NOT NULL,
                    last_intent_json TEXT,
                    updated_at TEXT NOT NULL
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS response_cache (
                    cache_key TEXT PRIMARY KEY,
                    result_json TEXT NOT NULL,
                    expires_at REAL NOT NULL
                )
            """)

            # Seed default demo tiles if empty
            cursor.execute("SELECT COUNT(*) FROM tiles")
            if cursor.fetchone()[0] == 0:
                default_scenes = [
                    ("SCENE-KOLKATA-2024", "Copernicus", "Sentinel-2 MSI", "2024-05-20", json.dumps([88.214, 22.451, 88.482, 22.689]), 3.2, json.dumps(["B2","B3","B4","B8"]), ""),
                    ("SCENE-BHUBANESWAR-2023", "USGS", "Landsat-9 OLI", "2023-11-14", json.dumps([85.780, 20.240, 85.880, 20.350]), 1.1, json.dumps(["B2","B3","B4","B5"]), ""),
                    ("SCENE-ASSAM-SAR-2024", "Copernicus", "Sentinel-1 SAR", "2024-07-02", json.dumps([93.100, 26.500, 93.300, 26.700]), 0.0, json.dumps(["VV","VH"]), ""),
                    ("SCENE-DELHI-AIRPORT-2024", "DigitalGlobe", "WorldView-3", "2024-02-10", json.dumps([77.080, 28.540, 77.120, 28.580]), 0.5, json.dumps(["RGB"]), "")
                ]
                cursor.executemany("INSERT INTO scenes VALUES (?, ?, ?, ?, ?, ?, ?, ?)", default_scenes)

                default_tiles = [
                    ("TILE-KOLKATA-001", "SCENE-KOLKATA-2024", json.dumps([88.214, 22.451, 88.482, 22.689]), 3.2, 0.98, json.dumps({"NDVI_mean": 0.42, "NDWI_mean": 0.18}), "EMB-KOL-01"),
                    ("TILE-BHUBANESWAR-001", "SCENE-BHUBANESWAR-2023", json.dumps([85.780, 20.240, 85.880, 20.350]), 1.1, 0.99, json.dumps({"NDVI_mean": 0.55}), "EMB-BHU-01"),
                    ("TILE-ASSAM-SAR-001", "SCENE-ASSAM-SAR-2024", json.dumps([93.100, 26.500, 93.300, 26.700]), 0.0, 1.00, json.dumps({"Sigma0_dB": -14.2}), "EMB-ASM-01"),
                    ("TILE-DELHI-001", "SCENE-DELHI-AIRPORT-2024", json.dumps([77.080, 28.540, 77.120, 28.580]), 0.5, 0.97, json.dumps({"BuildingCount": 42}), "EMB-DEL-01")
                ]
                cursor.executemany("INSERT INTO tiles VALUES (?, ?, ?, ?, ?, ?, ?)", default_tiles)

            conn.commit()

    def insert_scene(self, scene_id: str, provider: str, sensor: str, acquisition_time: str, bbox: List[float], cloud_cover: float, bands: List[str], source_uri: str = ""):
        with self._get_connection() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO scenes VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (scene_id, provider, sensor, acquisition_time, json.dumps(bbox), cloud_cover, json.dumps(bands), source_uri)
            )
            conn.commit()

    def insert_tile(self, tile_id: str, scene_id: str, bbox: List[float], cloud_cover: float, valid_pixel_ratio: float, stats: Dict[str, Any], embedding_id: Optional[str] = None):
        with self._get_connection() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO tiles VALUES (?, ?, ?, ?, ?, ?, ?)",
                (tile_id, scene_id, json.dumps(bbox), cloud_cover, valid_pixel_ratio, json.dumps(stats), embedding_id)
            )
            conn.commit()

    def get_tiles(self, max_cloud: float = 15.0, min_valid_pixels: float = 0.75) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM tiles WHERE cloud_cover <= ? AND valid_pixel_ratio >= ?",
                (max_cloud, min_valid_pixels)
            )
            rows = cursor.fetchall()
            results = []
            for row in rows:
                r = dict(row)
                r["bbox"] = json.loads(r["bbox_json"])
                r["stats"] = json.loads(r["stats_json"]) if r["stats_json"] else {}
                results.append(r)
            return results

    # Jobs persistence
    def create_job(self, job_id: str, task_type: str) -> Dict[str, Any]:
        now = datetime.utcnow().isoformat()
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO jobs VALUES (?, ?, 'PENDING', 0.0, NULL, NULL, ?, ?)",
                (job_id, task_type, now, now)
            )
            conn.commit()
        return {"job_id": job_id, "status": "PENDING", "progress_pct": 0.0, "created_at": now}

    def update_job(self, job_id: str, status: str, progress_pct: float = 0.0, result: Optional[Dict[str, Any]] = None, error_msg: Optional[str] = None):
        now = datetime.utcnow().isoformat()
        res_json = json.dumps(result) if result else None
        with self._get_connection() as conn:
            conn.execute(
                "UPDATE jobs SET status = ?, progress_pct = ?, result_json = ?, error_msg = ?, updated_at = ? WHERE job_id = ?",
                (status, progress_pct, res_json, error_msg, now, job_id)
            )
            conn.commit()

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,))
            row = cursor.fetchone()
            if not row:
                return None
            res = dict(row)
            if res["result_json"]:
                res["result"] = json.loads(res["result_json"])
            return res

    def get_cached_response(self, cache_key: str, now: float) -> Optional[Dict[str, Any]]:
        try:
            with self._get_connection() as conn:
                row = conn.execute("SELECT result_json FROM response_cache WHERE cache_key = ? AND expires_at > ?", (cache_key, now)).fetchone()
                if row:
                    return json.loads(row["result_json"])
                conn.execute("DELETE FROM response_cache WHERE expires_at <= ?", (now,))
                conn.commit()
        except Exception:
            pass
        return None

    def cache_response(self, cache_key: str, result: Dict[str, Any], expires_at: float):
        try:
            with self._get_connection() as conn:
                conn.execute("INSERT OR REPLACE INTO response_cache VALUES (?, ?, ?)", (cache_key, json.dumps(result), expires_at))
                conn.commit()
        except Exception:
            pass

metadata_db = MetadataDB()
