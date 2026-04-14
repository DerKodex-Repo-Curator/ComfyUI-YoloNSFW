"""
YOLO NSFW Detector Node
A ComfyUI custom node for detecting NSFW content in images using YOLO models.
"""

import os
import torch
import numpy as np
from PIL import Image, ImageFilter
import folder_paths
import cv2
import urllib.request


MODEL_URLS = {
    "erax_nsfw_yolo11m": "https://huggingface.co/erax-ai/EraX-NSFW-V1.0/resolve/main/erax_nsfw_yolo11m.pt",
    "erax_nsfw_yolo11n": "https://huggingface.co/erax-ai/EraX-NSFW-V1.0/resolve/main/erax_nsfw_yolo11n.pt",
    "erax_nsfw_yolo11s": "https://huggingface.co/erax-ai/EraX-NSFW-V1.0/resolve/main/erax_nsfw_yolo11s.pt",
}


def apply_blur_to_boxes(pil_img, boxes, blur_radius=30):
    """Apply blur to specific box regions in image."""
    result_img = pil_img.copy()
    for box in boxes:
        x1, y1, x2, y2 = map(int, box)
        # Ensure coordinates are within image bounds
        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(result_img.width, x2)
        y2 = min(result_img.height, y2)

        if x2 > x1 and y2 > y1:
            region = result_img.crop((x1, y1, x2, y2))
            blurred = region.filter(ImageFilter.GaussianBlur(blur_radius))
            result_img.paste(blurred, (x1, y1, x2, y2))
    return result_img


def apply_full_blur(pil_img, blur_radius=30):
    """Apply blur to entire image."""
    return pil_img.filter(ImageFilter.GaussianBlur(blur_radius))


class YoloNSFWNode:
    """
    Detect NSFW content in images using YOLO model.
    Returns boolean indicating if NSFW content was detected.
    """

    def __init__(self):
        self.model = None
        self.current_device = None
        self.current_model_name = None

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
                "model_name": (list(MODEL_URLS.keys()), {
                    "default": "erax_nsfw_yolo11n",
                }),
                "device": (["cpu", "cuda", "mps"], {
                    "default": "cpu",
                }),
                "conf": ("FLOAT", {
                    "default": 0.25,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                }),
                "iou": ("FLOAT", {
                    "default": 0.3,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                }),
                "blur": (["none", "full", "partial"], {
                    "default": "full",
                }),
            },
            "optional": {
                "blur_radius": ("INT", {
                    "default": 35,
                    "min": 1,
                    "max": 100,
                    "step": 1,
                }),
                "auto_release": ("BOOLEAN", {
                    "default": False,
                }),
            }
        }

    RETURN_TYPES = ("IMAGE", "BOOLEAN")
    RETURN_NAMES = ("image", "has_nsfw")
    FUNCTION = "detect"
    CATEGORY = "image/nsfw"
    OUTPUT_NODE = True

    def download_model(self, model_dir, model_name):
        """Download model if not exists."""
        model_filename = model_name + ".pt"
        model_path = os.path.join(model_dir, model_filename)

        if os.path.exists(model_path):
            return model_path

        os.makedirs(model_dir, exist_ok=True)

        url = MODEL_URLS.get(model_name)
        if not url:
            raise ValueError(f"Unknown model: {model_name}")

        print(f"Downloading model {model_name} from {url}...")

        # Download model
        temp_path = model_path + ".tmp"
        try:
            urllib.request.urlretrieve(url, temp_path)
            os.rename(temp_path, model_path)
            print(f"Model downloaded to {model_path}")
        except Exception as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise RuntimeError(f"Failed to download model: {e}")

        return model_path

    def load_model(self, model_name, device_str):
        """Load YOLO model."""
        try:
            from ultralytics import YOLO
        except ImportError:
            raise ImportError("Please install ultralytics: pip install ultralytics")

        # Download model if not exists
        model_dir = os.path.join(folder_paths.models_dir, "nsfw")
        model_path = self.download_model(model_dir, model_name)

        model = YOLO(model_path)

        # Set device
        if device_str == "cuda" and torch.cuda.is_available():
            device = torch.device("cuda")
        elif device_str == "mps" and torch.backends.mps.is_available():
            device = torch.device("mps")
        else:
            device = torch.device("cpu")

        model = model.to(device)
        return model, device

    def detect(self, images, model_name, device, conf, iou, blur="full", blur_radius=50, auto_release=False):
        """
        Detect NSFW content in images.

        Args:
            images: Input image tensor (B, H, W, C)
            model_name: Model name to use
            device: Device to run inference (cpu/cuda/mps)
            conf: Confidence threshold
            iou: IoU threshold for NMS
            blur: Blur mode (none/full/partial)
            blur_radius: Blur radius
            auto_release: Whether to release model after detection

        Returns:
            image: Processed image tensor
            has_nsfw: Whether NSFW content was detected
        """
        # Load model if not loaded or model/device changed
        if self.model is None or self.current_model_name != model_name or self.current_device != device:
            self.model, self.current_device = self.load_model(model_name, device)
            self.current_model_name = model_name

        has_nsfw = False
        processed_images = []

        # Process each image in batch
        for i in range(images.shape[0]):
            # Convert tensor to numpy (H, W, C) in RGB format, 0-255
            img_tensor = images[i]  # (H, W, C)
            img_np = (img_tensor.cpu().numpy() * 255).astype(np.uint8)

            # Convert RGB to BGR for OpenCV
            img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

            # Run prediction
            results = self.model.predict(
                img_bgr,
                conf=conf,
                iou=iou,
                device=self.current_device
            )

            result = results[0]

            # Convert BGR back to RGB for PIL
            img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(img_rgb)

            # Check if any detections
            boxes = []
            if result.boxes is not None and len(result.boxes) > 0:
                has_nsfw = True
                # Get all box coordinates
                for box in result.boxes:
                    xyxy = box.xyxy[0].cpu().numpy()
                    boxes.append(xyxy)
                    
            # Apply blur based on mode
            if blur == "none":
                # No blur, keep original
                output_img = pil_img
            elif blur == "full":
                # Full image blur
                output_img = apply_full_blur(pil_img, blur_radius)
            elif blur == "partial":
                # Partial blur on boxes only
                if boxes:
                    output_img = apply_blur_to_boxes(pil_img, boxes, blur_radius)
                else:
                    output_img = pil_img
            else:
                output_img = pil_img

            # Convert back to tensor (H, W, C) in 0-1 range
            output_np = np.array(output_img).astype(np.float32) / 255.0
            output_tensor = torch.from_numpy(output_np)
            processed_images.append(output_tensor)

        # Stack processed images
        output_batch = torch.stack(processed_images)

        # Release model if auto_release is enabled
        if auto_release:
            self.model = None
            self.current_device = None
            self.current_model_name = None
            import gc
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

        return (output_batch, has_nsfw)


# Node mappings for ComfyUI
NODE_CLASS_MAPPINGS = {
    "YoloNSFWNode": YoloNSFWNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "YoloNSFWNode": "YOLO NSFW Detector",
}
