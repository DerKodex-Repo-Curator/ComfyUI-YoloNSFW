# ComfyUI-YoloNSFW

English | [中文](README_zh.md)

A ComfyUI custom node for NSFW (Not Safe For Work) content detection using YOLO models. Automatically detect and optionally blur adult content in images.

This node uses the Erax AI [erax-ai/EraX-NSFW-V1.0](https://huggingface.co/erax-ai/EraX-NSFW-V1.0) model.

## Features

- **NSFW Detection**: Detect adult content using EraX YOLO11 NSFW detection models
- **Auto Download**: Automatically download models from HuggingFace on first use
- **Multiple Models**: Choose from 3 model sizes (n/s/m) for speed/accuracy trade-off
- **Flexible Blur**: Blur modes - full image blur, or partial blur on detected regions
- **Configurable Thresholds**: Adjust confidence and IoU thresholds
- **Auto Release**: Option to unload model after detection to free memory

## Installation

### Prerequisites

- Python 3.10+
- ComfyUI installed
- CUDA-capable GPU (recommended) or CPU

### Install the Node

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/er1cw00/ComfyUI-YoloNSFW.git
cd ComfyUI-YoloNSFW
pip install -r requirements.txt
```

Restart ComfyUI

## Model Setup

Models are automatically downloaded on first use and stored in:
```
ComfyUI/models/nsfw/
├── erax_nsfw_yolo11n.pt  # Lightweight, fastest
├── erax_nsfw_yolo11s.pt  # Balanced
└── erax_nsfw_yolo11m.pt  # Best accuracy, slower
```

Source: [erax-ai/EraX-NSFW-V1.0](https://huggingface.co/erax-ai/EraX-NSFW-V1.0)

Or you can manually download from the link above and place them in the directory.

## Usage

### Node: YOLO NSFW Detector

A single node that handles model loading, detection, and image processing.

#### Inputs

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `images` | IMAGE | - | Input image(s) to detect |
| `model_name` | STRING | erax_nsfw_yolo11n | Model to use: `erax_nsfw_yolo11n` (fast), `erax_nsfw_yolo11s` (balanced), `erax_nsfw_yolo11m` (accurate) |
| `device` | STRING | cpu | Device for inference: `cpu`, `cuda`, or `mps` (Apple Silicon) |
| `conf` | FLOAT | 0.25 | Confidence threshold (0.0 - 1.0), higher = stricter |
| `iou` | FLOAT | 0.3 | IoU threshold for NMS (0.0 - 1.0) |
| `blur` | STRING | full | Blur mode: `none` (no blur), `full` (blur entire image), `partial` (blur detected regions only) |
| `blur_radius` | INT | 35 | Gaussian blur radius (1 - 100), only used when blur is not `none` |
| `auto_release` | BOOLEAN | false | Unload model after detection to free memory |

#### Outputs

| Output | Type | Description |
|--------|------|-------------|
| `image` | IMAGE | Processed image (with blur applied if enabled) |
| `has_nsfw` | BOOLEAN | True if NSFW content was detected, False otherwise |

### Blur Modes

- **none**: Returns original image without any blur
- **full**: Applies Gaussian blur to the entire image
- **partial**: Applies Gaussian blur only to detected NSFW regions (if any)

![Screenshot](docs/screenshot.png)

## License

MIT License

## Disclaimer

This tool is for content moderation purposes only. Users are responsible for complying with applicable laws and regulations.
