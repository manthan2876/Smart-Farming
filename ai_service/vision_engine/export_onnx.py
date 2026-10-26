#!/usr/bin/env python3
"""
export_onnx.py — Export PyTorch EfficientNet Models to ONNX & Dynamic int8 Quantization
=======================================================================================

Converts trained PyTorch (.pth) models to ONNX format with optional dynamic int8
quantization, reducing model file size by ~75% and accelerating CPU inference on
free-tier Hugging Face Spaces by 2-3x.

Usage:
    python ai_service/vision_engine/export_onnx.py \\
        --checkpoint models/crop_identifier_v1.pth \\
        --output models/crop_identifier_v1.onnx \\
        --arch efficientnet_b0 \\
        --num-classes 5 \\
        --quantize-int8
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

import torch
import torch.nn as nn
from torchvision import models

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("export_onnx")


def build_model_arch(arch: str, num_classes: int) -> nn.Module:
    """Instantiate model architecture matching project weights."""
    try:
        import timm
        return timm.create_model(arch, pretrained=False, num_classes=num_classes)
    except Exception:
        pass

    # Fallback to torchvision
    if hasattr(models, arch):
        model_fn = getattr(models, arch)
        model = model_fn(weights=None)
        in_features = model.classifier[1].in_features
        model.classifier = nn.Sequential(
            nn.Dropout(p=0.4, inplace=True),
            nn.Linear(in_features, num_classes),
        )
        return model
    raise ValueError(f"Unknown architecture: {arch}")


def export_to_onnx(
    checkpoint_path: Path,
    output_path: Path,
    arch: str,
    num_classes: int,
    img_size: int = 224,
    quantize_int8: bool = False,
) -> Path:
    logger.info("Loading PyTorch checkpoint from %s...", checkpoint_path)
    model = build_model_arch(arch, num_classes)

    ckpt = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
    state = ckpt.get("model_state_dict", ckpt)
    model.load_state_dict(state, strict=False)
    model.eval()

    dummy_input = torch.randn(1, 3, img_size, img_size, dtype=torch.float32)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fp32_onnx_path = output_path.with_suffix(".onnx") if quantize_int8 else output_path

    logger.info("Exporting FP32 ONNX model to %s...", fp32_onnx_path)
    torch.onnx.export(
        model,
        dummy_input,
        str(fp32_onnx_path),
        export_params=True,
        opset_version=14,
        do_constant_folding=True,
        input_names=["input"],
        output_names=["output"],
        dynamic_axes={"input": {0: "batch_size"}, "output": {0: "batch_size"}},
    )
    logger.info("FP32 ONNX exported successfully (size: %.2f MB)", fp32_onnx_path.stat().st_size / (1024 * 1024))

    if not quantize_int8:
        return fp32_onnx_path

    # Dynamic INT8 Quantization
    int8_onnx_path = output_path.parent / f"{output_path.stem}_int8.onnx"
    try:
        from onnxruntime.quantization import quantize_dynamic, QuantType

        logger.info("Applying dynamic int8 quantization to %s...", int8_onnx_path)
        quantize_dynamic(
            model_input=str(fp32_onnx_path),
            model_output=str(int8_onnx_path),
            weight_type=QuantType.QInt8,
        )
        logger.info(
            "INT8 ONNX model generated successfully (size: %.2f MB, reduction: %.1f%%)",
            int8_onnx_path.stat().st_size / (1024 * 1024),
            (1.0 - int8_onnx_path.stat().st_size / fp32_onnx_path.stat().st_size) * 100,
        )
        return int8_onnx_path
    except ImportError:
        logger.warning(
            "onnxruntime.quantization is not installed; returning FP32 ONNX model. "
            "Install onnxruntime via 'pip install onnxruntime' to enable int8 quantization."
        )
        return fp32_onnx_path


def main():
    parser = argparse.ArgumentParser(description="Export PyTorch model to ONNX / int8")
    parser.add_argument("--checkpoint", required=True, type=Path, help="Path to PyTorch .pth checkpoint")
    parser.add_argument("--output", required=True, type=Path, help="Output path for ONNX model")
    parser.add_argument("--arch", default="efficientnet_b0", help="Architecture name (e.g. efficientnet_b0, efficientnet_b2)")
    parser.add_argument("--num-classes", type=int, required=True, help="Number of target classes")
    parser.add_argument("--img-size", type=int, default=224, help="Input image dimension")
    parser.add_argument("--quantize-int8", action="store_true", help="Apply dynamic int8 quantization")

    args = parser.parse_args()
    export_to_onnx(
        checkpoint_path=args.checkpoint,
        output_path=args.output,
        arch=args.arch,
        num_classes=args.num_classes,
        img_size=args.img_size,
        quantize_int8=args.quantize_int8,
    )


if __name__ == "__main__":
    main()

