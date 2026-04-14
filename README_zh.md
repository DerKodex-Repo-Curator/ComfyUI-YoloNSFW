# ComfyUI-YoloNSFW

[English](README_zh.md) | 中文

使用 YOLO 模型进行 NSFW（不适宜工作场所）内容检测的 ComfyUI 自定义节点。自动检测并可选择性地模糊图像中的成人内容。

本节点使用 Erax AI [erax-ai/EraX-NSFW-V1.0](https://huggingface.co/erax-ai/EraX-NSFW-V1.0) 模型。

## 特性

- **NSFW 检测**：使用 EraX YOLO11 NSFW 检测模型
- **自动下载**：首次使用时自动从 HuggingFace 下载模型
- **多模型选择**：3 种模型尺寸（n/s/m）供速度和精度权衡
- **灵活模糊**：模糊模式 - 全图模糊、仅检测区域模糊
- **可配置阈值**：调整置信度和 IoU 阈值
- **自动释放**：检测后卸载模型以释放内存

## 安装

### 前置要求

- Python 3.10+
- 已安装 ComfyUI
- CUDA 显卡（推荐）或 CPU

### 安装节点

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/er1cw00/ComfyUI-YoloNSFW.git
cd ComfyUI-YoloNSFW
pip install -r requirements.txt
```

重启 ComfyUI


## 模型设置

模型会在首次使用时自动下载并存储在：
```
ComfyUI/models/nsfw/
├── erax_nsfw_yolo11n.pt  # 轻量级，最快
├── erax_nsfw_yolo11s.pt  # 平衡型
└── erax_nsfw_yolo11m.pt  # 精度最高，较慢
```

来源：[erax-ai/EraX-NSFW-V1.0](https://huggingface.co/erax-ai/EraX-NSFW-V1.0)

也可以从上述链接手动下载并放入该目录。

## 使用说明

### 节点：YOLO NSFW Detector

单个节点处理模型加载、检测和图像处理。

#### 输入参数

| 参数 | 类型 | 默认值 | 说明 |
|-----------|------|---------|-------------|
| `images` | IMAGE | - | 待检测的输入图像 |
| `model_name` | STRING | erax_nsfw_yolo11n | 模型选择：`erax_nsfw_yolo11n` (快), `erax_nsfw_yolo11s` (平衡), `erax_nsfw_yolo11m` (精确) |
| `device` | STRING | cpu | 推理设备：`cpu`, `cuda`, 或 `mps` (Apple Silicon) |
| `conf` | FLOAT | 0.25 | 置信度阈值 (0.0 - 1.0)，越高越严格 |
| `iou` | FLOAT | 0.3 | NMS IoU 阈值 (0.0 - 1.0) |
| `blur` | STRING | full | 模糊模式：`none` (无模糊), `full` (全图模糊), `partial` (仅检测区域模糊) |
| `blur_radius` | INT | 35 | 高斯模糊半径 (1 - 100)，仅在 blur 不为 `none` 时有效 |
| `auto_release` | BOOLEAN | false | 检测后卸载模型释放内存 |

#### 输出

| 输出 | 类型 | 说明 |
|--------|------|-------------|
| `image` | IMAGE | 处理后的图像（如启用模糊则包含模糊效果） |
| `has_nsfw` | BOOLEAN | 检测到 NSFW 内容为 True，否则为 False |

### 模糊模式

- **none**：返回原图，不做任何模糊处理
- **full**：对整个图像应用高斯模糊
- **partial**：仅对检测到的 NSFW 区域应用高斯模糊

![节点截图](docs/screenshot.png)

## 许可证

MIT License

## 免责声明

本工具仅用于内容审核目的。用户需自行遵守适用的法律法规。
