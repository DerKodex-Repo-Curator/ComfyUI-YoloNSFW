"""
ComfyUI-YoloNSFW
A ComfyUI custom node for NSFW content detection using YOLO models.
"""

from .nodes.yolo_nsfw_node import YoloNSFWNode

NODE_CLASS_MAPPINGS = {
    "YoloNSFWNode": YoloNSFWNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "YoloNSFWNode": "YOLO NSFW Detector",
}

#WEB_DIRECTORY = "./web"

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
