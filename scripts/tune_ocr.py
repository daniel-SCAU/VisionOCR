#!/usr/bin/env python3
"""Evaluate OCR tuning options on local image sets."""
import argparse
import os
import sys
from pathlib import Path
from typing import Any

import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.deps import get_settings
from app.core.exceptions import OCRExecutionError
from app.services import preprocess, validation
from app.services.ocr import get_ocr_backend


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare OCR preprocessing modes and calibrate confidence.")
    parser.add_argument("--samples-dir", required=True, help="Directory of representative OCR images.")
    parser.add_argument(
        "--modes",
        default="OTSU,ADAPTIVE,GLOBAL",
        help="Comma-separated threshold modes to evaluate.",
    )
    parser.add_argument(
        "--good-dir",
        help="Optional directory containing known-good label images for confidence calibration.",
    )
    parser.add_argument(
        "--bad-dir",
        help="Optional directory containing known-bad/noise images for confidence calibration.",
    )
    parser.add_argument(
        "--calibration-mode",
        default="OTSU",
        help="Mode to use for good/bad confidence calibration (default: OTSU).",
    )
    parser.add_argument("--roi-x", type=int, help="Override DEFAULT_ROI_X.")
    parser.add_argument("--roi-y", type=int, help="Override DEFAULT_ROI_Y.")
    parser.add_argument("--roi-w", type=int, help="Override DEFAULT_ROI_W.")
    parser.add_argument("--roi-h", type=int, help="Override DEFAULT_ROI_H.")
    parser.add_argument("--psm", type=int, help="Override OCR_PSM.")
    parser.add_argument("--whitelist", help="Override OCR_WHITELIST.")
    parser.add_argument("--language", help="Override OCR_LANGUAGE.")
    parser.add_argument("--min-confidence", type=float, help="Override MIN_CONFIDENCE for reporting.")
    parser.add_argument(
        "--full-rate-weight",
        type=float,
        default=1.0,
        help="Weight for full parse hit-rate when ranking modes.",
    )
    parser.add_argument(
        "--confidence-weight",
        type=float,
        default=1.0,
        help="Weight for average confidence when ranking modes.",
    )
    return parser.parse_args()


def list_images(path: str) -> list[Path]:
    exts = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}
    root = Path(path)
    files = [p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in exts]
    return sorted(files)


def build_settings_dict(args: argparse.Namespace) -> dict[str, Any]:
    settings = get_settings()
    data = settings.model_dump()
    if args.roi_x is not None:
        data["DEFAULT_ROI_X"] = args.roi_x
    if args.roi_y is not None:
        data["DEFAULT_ROI_Y"] = args.roi_y
    if args.roi_w is not None:
        data["DEFAULT_ROI_W"] = args.roi_w
    if args.roi_h is not None:
        data["DEFAULT_ROI_H"] = args.roi_h
    if args.psm is not None:
        data["OCR_PSM"] = args.psm
    if args.whitelist is not None:
        data["OCR_WHITELIST"] = args.whitelist
    if args.language is not None:
        data["OCR_LANGUAGE"] = args.language
    if args.min_confidence is not None:
        data["MIN_CONFIDENCE"] = args.min_confidence
    return data


def make_ocr_backend_from_dict(settings_dict: dict[str, Any]):
    settings = get_settings().model_copy(update=settings_dict)
    return get_ocr_backend(settings)


def evaluate_images(files: list[Path], settings_dict: dict[str, Any], mode: str) -> dict[str, float]:
    ocr = make_ocr_backend_from_dict(settings_dict)
    confidences: list[float] = []
    date_hits = 0
    batch_hits = 0
    full_hits = 0
    processed = 0
    failed = 0

    for image_path in files:
        img = cv2.imread(str(image_path))
        if img is None:
            continue
        local = dict(settings_dict)
        local["THRESHOLD_MODE"] = mode
        pre = preprocess.run_pipeline(img, local)
        try:
            res = ocr.recognize(pre)
        except OCRExecutionError:
            failed += 1
            continue
        date_text = validation.parse_date_text(res.raw_text, local["DATE_REGEX"])
        batch_text = validation.parse_batch_text(res.raw_text, local["BATCH_REGEX"])
        confidences.append(float(res.confidence))
        date_hits += int(bool(date_text))
        batch_hits += int(bool(batch_text))
        full_hits += int(bool(date_text and batch_text))
        processed += 1

    if processed == 0:
        return {
            "count": 0.0,
            "failed": float(failed),
            "avg_conf": 0.0,
            "p10_conf": 0.0,
            "p50_conf": 0.0,
            "p90_conf": 0.0,
            "date_rate": 0.0,
            "batch_rate": 0.0,
            "full_rate": 0.0,
        }

    conf_arr = np.array(confidences, dtype=np.float64)
    return {
        "count": float(processed),
        "failed": float(failed),
        "avg_conf": float(conf_arr.mean()),
        "p10_conf": float(np.percentile(conf_arr, 10)),
        "p50_conf": float(np.percentile(conf_arr, 50)),
        "p90_conf": float(np.percentile(conf_arr, 90)),
        "date_rate": date_hits / processed,
        "batch_rate": batch_hits / processed,
        "full_rate": full_hits / processed,
    }


def calibrate_min_confidence(
    good_files: list[Path],
    bad_files: list[Path],
    settings_dict: dict[str, Any],
    mode: str,
) -> float | None:
    if not good_files or not bad_files:
        return None
    good_stats = evaluate_images(good_files, settings_dict, mode)
    bad_stats = evaluate_images(bad_files, settings_dict, mode)
    if good_stats["count"] == 0 or bad_stats["count"] == 0:
        return None
    suggested = (good_stats["p10_conf"] + bad_stats["p90_conf"]) / 2.0
    return float(max(0.0, min(100.0, suggested)))


def main() -> None:
    args = parse_args()
    samples = list_images(args.samples_dir)
    if not samples:
        raise SystemExit(f"No supported image files found in: {args.samples_dir}")

    settings_dict = build_settings_dict(args)
    modes = [m.strip().upper() for m in args.modes.split(",") if m.strip()]
    if not modes:
        raise SystemExit("No valid threshold modes were provided.")

    print(f"Samples: {len(samples)} images")
    print(f"ROI: x={settings_dict['DEFAULT_ROI_X']} y={settings_dict['DEFAULT_ROI_Y']} "
          f"w={settings_dict['DEFAULT_ROI_W']} h={settings_dict['DEFAULT_ROI_H']}")
    print(f"OCR: lang={settings_dict['OCR_LANGUAGE']} psm={settings_dict['OCR_PSM']}")
    print("")
    print("Mode comparison:")
    print("mode      count fail  avg_conf   p10     p50     p90   date%  batch% full%")
    print("-" * 72)

    best_mode = None
    best_score = -1.0
    for mode in modes:
        stats = evaluate_images(samples, settings_dict, mode)
        print(
            f"{mode:<9} {int(stats['count']):>5} {int(stats['failed']):>4}  "
            f"{stats['avg_conf']:>7.2f}  {stats['p10_conf']:>6.2f}  {stats['p50_conf']:>6.2f}  {stats['p90_conf']:>6.2f}  "
            f"{stats['date_rate'] * 100:>5.1f}  {stats['batch_rate'] * 100:>6.1f} {stats['full_rate'] * 100:>5.1f}"
        )
        score = (
            args.full_rate_weight * (stats["full_rate"] * 100.0)
            + args.confidence_weight * stats["avg_conf"]
        )
        if score > best_score:
            best_score = score
            best_mode = mode

    print("")
    if best_mode:
        print(f"Suggested THRESHOLD_MODE: {best_mode}")

    if args.good_dir and args.bad_dir:
        good_files = list_images(args.good_dir)
        bad_files = list_images(args.bad_dir)
        calibration_mode = args.calibration_mode.upper()
        suggested = calibrate_min_confidence(good_files, bad_files, settings_dict, calibration_mode)
        if suggested is None:
            print("Could not compute MIN_CONFIDENCE suggestion (insufficient valid samples).")
        else:
            print(
                f"Suggested MIN_CONFIDENCE ({calibration_mode}, good={len(good_files)}, bad={len(bad_files)}): "
                f"{suggested:.2f}"
            )


if __name__ == "__main__":
    main()
