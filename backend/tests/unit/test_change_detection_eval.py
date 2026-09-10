import pytest
import numpy as np
from backend.app.geospatial.raster_ops import RasterOps

def calculate_change_metrics(gt_mask: np.ndarray, pred_mask: np.ndarray):
    tp = np.sum((gt_mask == 1) & (pred_mask == 1))
    fp = np.sum((gt_mask == 0) & (pred_mask == 1))
    fn = np.sum((gt_mask == 1) & (pred_mask == 0))
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 1.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 1.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 1.0
    iou = tp / (tp + fp + fn) if (tp + fp + fn) > 0 else 1.0
    
    return precision, recall, f1, iou

def test_change_detection_no_change():
    t1 = np.ones((100, 100), dtype=np.float32) * 0.5
    t2 = t1.copy()
    gt_mask = np.zeros((100, 100), dtype=np.uint8)

    diff, pred_mask, pct = RasterOps.compute_bitemporal_diff(t1, t2, threshold=0.2)
    precision, recall, f1, iou = calculate_change_metrics(gt_mask, pred_mask)
    
    assert pct == 0.0
    assert iou == 1.0
    assert f1 == 1.0

def test_change_detection_known_large_change():
    t1 = np.ones((100, 100), dtype=np.float32) * 0.2
    t2 = t1.copy()
    # Insert 20x20 change block in top left
    t2[:20, :20] = 0.8
    
    gt_mask = np.zeros((100, 100), dtype=np.uint8)
    gt_mask[:20, :20] = 1

    diff, pred_mask, pct = RasterOps.compute_bitemporal_diff(t1, t2, threshold=0.25)
    precision, recall, f1, iou = calculate_change_metrics(gt_mask, pred_mask)
    
    assert pct == 4.0 # 400 pixels out of 10000 = 4%
    assert precision == 1.0
    assert recall == 1.0
    assert f1 == 1.0
    assert iou == 1.0

def test_change_detection_noisy_scene():
    np.random.seed(42)
    t1 = np.random.uniform(0.3, 0.4, (100, 100)).astype(np.float32)
    t2 = t1 + np.random.normal(0, 0.02, (100, 100)).astype(np.float32)
    gt_mask = np.zeros((100, 100), dtype=np.uint8)

    # Threshold set above noise level (0.2) suppresses noise false positives
    diff, pred_mask, pct = RasterOps.compute_bitemporal_diff(t1, t2, threshold=0.20)
    precision, recall, f1, iou = calculate_change_metrics(gt_mask, pred_mask)
    
    assert pct == 0.0
    assert f1 == 1.0
