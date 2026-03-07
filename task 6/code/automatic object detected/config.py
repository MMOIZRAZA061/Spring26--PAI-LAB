"""
Configuration settings for Vehicle Detection System
"""

# YOLO Model settings
# Options: yolov8n.pt (fastest), yolov8s.pt, yolov8m.pt (balanced), yolov8l.pt, yolov8x.pt (most accurate)
MODEL_NAME = "yolov8n.pt"  # NANO = FASTEST ⚡
CONFIDENCE_THRESHOLD = 0.5

# SPEED OPTIMIZATION
SPEED_MODE = True  # Fast processing (recommended)
RESIZE_FRAME = True  # Resize frames for faster processing
FRAME_WIDTH = 640  # Lower = faster (640, 480, or 320)
SKIP_FRAMES = 0  # Process every frame (0=all, 1=skip 1, 2=skip 2, etc)

# DETECTION MODE
DETECT_ALL_OBJECTS = True  # Detect all objects instead of just vehicles

# All COCO dataset classes (80 classes)
ALL_CLASSES = {
    0: "person", 1: "bicycle", 2: "car", 3: "motorcycle", 4: "airplane", 5: "bus",
    6: "train", 7: "truck", 8: "boat", 9: "traffic light", 10: "fire hydrant",
    11: "stop sign", 12: "parking meter", 13: "bench", 14: "bird", 15: "cat",
    16: "dog", 17: "horse", 18: "sheep", 19: "cow", 20: "elephant", 21: "bear",
    22: "zebra", 23: "giraffe", 24: "backpack", 25: "umbrella", 26: "handbag",
    27: "tie", 28: "suitcase", 29: "frisbee", 30: "skis", 31: "snowboard",
    32: "sports ball", 33: "kite", 34: "baseball bat", 35: "baseball glove",
    36: "skateboard", 37: "surfboard", 38: "tennis racket", 39: "bottle",
    40: "wine glass", 41: "cup", 42: "fork", 43: "knife", 44: "spoon",
    45: "bowl", 46: "banana", 47: "apple", 48: "sandwich", 49: "orange",
    50: "broccoli", 51: "carrot", 52: "hot dog", 53: "pizza", 54: "donut",
    55: "cake", 56: "chair", 57: "couch", 58: "potted plant", 59: "bed",
    60: "dining table", 61: "toilet", 62: "tv", 63: "laptop", 64: "mouse",
    65: "remote", 66: "keyboard", 67: "cell phone", 68: "microwave", 69: "oven",
    70: "toaster", 71: "sink", 72: "refrigerator", 73: "book", 74: "clock",
    75: "vase", 76: "scissors", 77: "teddy bear", 78: "hair drier", 79: "toothbrush"
}

# Vehicle classes from COCO dataset (for backward compatibility)
VEHICLE_CLASSES = {
    2: "car",
    3: "motorcycle",
    5: "bus",
    7: "truck"
}

# Display settings
SHOW_CONFIDENCE = True
BOX_COLOR = (0, 255, 0)  # BGR format: Green
TEXT_COLOR = (255, 255, 255)  # White
LINE_THICKNESS = 2
FONT_SCALE = 0.6

# Video settings
OUTPUT_QUALITY = 'high'  # 'low', 'medium', 'high'
OUTPUT_FPS_REDUCTION = False  # Reduce FPS if processing is slow
TARGET_FPS = None  # None = keep original FPS
FRAME_RATE_MULTIPLIER = 1.0  # Speed up video (1.0 = normal, 2.0 = 2x speed, etc.)
PREVIEW_FPS = 15  # FPS for live preview (lower = smoother but slower processing)

# Input/Output paths
INPUT_FOLDER = "inputs"
OUTPUT_FOLDER = "outputs"
