"""
Vehicle Detection Module using YOLOv8
"""
import cv2
import torch
from ultralytics import YOLO
from pathlib import Path
import config


class VehicleDetector:
    """Vehicle detection class using YOLOv8"""
    
    def __init__(self, model_name=config.MODEL_NAME, confidence=config.CONFIDENCE_THRESHOLD):
        """
        Initialize the detector with YOLOv8 model
        
        Args:
            model_name (str): Model weights to use
            confidence (float): Confidence threshold for detections
        """
        self.confidence = confidence
        
        # Determine device with fallback
        try:
            if torch.cuda.is_available():
                self.device = 'cuda'
                print(f"✓ CUDA available - Using GPU")
            else:
                self.device = 'cpu'
                print(f"ℹ CUDA not available - Using CPU (slower)")
        except Exception as e:
            print(f"⚠ Warning: {str(e)}")
            self.device = 'cpu'
            print(f"✓ Fallback to CPU")
        
        try:
            # Load YOLO model
            print(f"Loading model: {model_name}...")
            self.model = YOLO(model_name)
            
            # Try to move to device
            try:
                self.model.to(self.device)
                print(f"✓ Model loaded on {self.device.upper()}")
            except Exception as e:
                print(f"⚠ Could not move model to {self.device}: {str(e)}")
                print(f"Using CPU instead...")
                self.device = 'cpu'
                self.model.to(self.device)
                print(f"✓ Model loaded on CPU")
        
        except Exception as e:
            print(f"✗ Error loading model: {str(e)}")
            raise Exception(f"Failed to load YOLOv8 model: {str(e)}\n\nTry: pip install --upgrade ultralytics torch")
        
    def detect_objects(self, frame):
        """
        Detect vehicles in a frame
        
        Args:
            frame (np.ndarray): Input frame/image
            
        Returns:
            list: Detection results with boxes and class info
        """
        try:
            results = self.model(frame, conf=self.confidence, verbose=False)
            return results
        except Exception as e:
            print(f"⚠ Detection error (will retry): {str(e)}")
            # Try with CPU device as fallback
            if self.device == 'cuda':
                print("Switching to CPU...")
                self.device = 'cpu'
                self.model.to(self.device)
            results = self.model(frame, conf=self.confidence, verbose=False)
            return results
    
    def filter_detections(self, results):
        """
        Filter detections based on configuration
        
        Args:
            results: YOLOv8 detection results
            
        Returns:
            list: Filtered detections
        """
        detections = []
        
        if len(results) > 0:
            boxes = results[0].boxes
            for box in boxes:
                cls = int(box.cls[0])
                
                # Choose class mapping based on detection mode
                if config.DETECT_ALL_OBJECTS:
                    class_name = config.ALL_CLASSES.get(cls, f"class_{cls}")
                else:
                    # Only keep vehicle classes
                    if cls not in config.VEHICLE_CLASSES:
                        continue
                    class_name = config.VEHICLE_CLASSES[cls]
                
                detections.append({
                    'box': box.xyxy[0].cpu().numpy(),
                    'class': cls,
                    'class_name': class_name,
                    'confidence': float(box.conf[0])
                })
        
        return detections
    
    def draw_boxes(self, frame, vehicles):
        """
        Draw bounding boxes on detected vehicles
        
        Args:
            frame (np.ndarray): Input frame
            vehicles (list): List of detected vehicles
            
        Returns:
            np.ndarray: Frame with drawn boxes
        """
        for vehicle in vehicles:
            box = vehicle['box'].astype(int)
            x1, y1, x2, y2 = box
            
            # Draw rectangle
            cv2.rectangle(frame, (x1, y1), (x2, y2), config.BOX_COLOR, config.LINE_THICKNESS)
            
            # Prepare label
            label = vehicle['class_name'].upper()
            if config.SHOW_CONFIDENCE:
                label += f" {vehicle['confidence']:.2f}"
            
            # Draw label background and text
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_thickness = 1
            text_size = cv2.getTextSize(label, font, config.FONT_SCALE, font_thickness)[0]
            
            # Background rectangle for text
            cv2.rectangle(frame, (x1, y1 - text_size[1] - 5), 
                         (x1 + text_size[0] + 5, y1), config.BOX_COLOR, -1)
            
            # Text
            cv2.putText(frame, label, (x1 + 2, y1 - 5),
                       font, config.FONT_SCALE, config.TEXT_COLOR, font_thickness)
        
        return frame
    
    def process_image(self, image_path, save_path=None):
        """
        Process a single image
        
        Args:
            image_path (str): Path to input image
            save_path (str): Path to save output image (optional)
            
        Returns:
            tuple: (processed_frame, vehicles_detected)
        """
        frame = cv2.imread(str(image_path))
        if frame is None:
            raise ValueError(f"Could not load image: {image_path}")
        
        results = self.detect_objects(frame)
        detections = self.filter_detections(results)
        
        print(f"Detected {len(vehicles)} vehicle(s) in image")
        
        # Draw boxes on frame
        frame = self.draw_boxes(frame, vehicles)
        
        # Save if path provided
        if save_path:
            cv2.imwrite(str(save_path), frame)
            print(f"Saved to: {save_path}")
        
        return frame, vehicles
    
    def process_video(self, video_path, save_path=None, callback=None):
        """
        Process a video file
        
        Args:
            video_path (str): Path to input video
            save_path (str): Path to save output video (optional)
            callback (function): Callback for progress updates (frame_number, total_frames)
            
        Returns:
            tuple: (output_path, total_vehicles_count)
        """
        # Open video
        cap = cv2.VideoCapture(str(video_path))
        
        if not cap.isOpened():
            raise ValueError(f"Could not open video: {video_path}")
        
        # Get video properties
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Speed optimization: resize frames if enabled
        if config.SPEED_MODE and config.RESIZE_FRAME:
            aspect_ratio = height / width
            width = config.FRAME_WIDTH
            height = int(width * aspect_ratio)
            print(f"⚡ Speed Mode: Resizing to {width}x{height}")
        
        print(f"Video properties - Frames: {total_frames}, FPS: {fps}, Resolution: {width}x{height}")
        
        # Reduce FPS if needed
        if config.TARGET_FPS and config.TARGET_FPS < fps:
            fps = config.TARGET_FPS
        
        # Apply frame rate multiplier for output speed
        output_fps = fps * config.FRAME_RATE_MULTIPLIER
        print(f"Output FPS: {output_fps:.1f} (multiplier: {config.FRAME_RATE_MULTIPLIER}x)")
        
        # Setup video writer if save_path provided
        writer = None
        if save_path:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            writer = cv2.VideoWriter(str(save_path), fourcc, output_fps, (width, height))
            print(f"Video writer initialized for: {save_path}")
        
        frame_count = 0
        total_vehicles = 0
        frame_vehicles_count = {}
        skip_count = 0
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame_count += 1
                
                # Skip frames if configured
                if config.SKIP_FRAMES > 0:
                    skip_count += 1
                    if skip_count < config.SKIP_FRAMES:
                        if writer:
                            writer.write(frame)
                        continue
                    skip_count = 0
                
                # Resize frame for speed
                if config.SPEED_MODE and config.RESIZE_FRAME:
                    frame_resized = cv2.resize(frame, (width, height), interpolation=cv2.INTER_LINEAR)
                else:
                    frame_resized = frame
                
                # Detect and draw
                results = self.detect_objects(frame_resized)
                detections = self.filter_detections(results)
                frame_resized = self.draw_boxes(frame_resized, detections)
                
                # Resize back to original if needed
                if config.SPEED_MODE and config.RESIZE_FRAME:
                    frame_resized = cv2.resize(frame_resized, (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))), interpolation=cv2.INTER_LINEAR)
                
                total_vehicles += len(detections)
                frame_vehicles_count[frame_count] = len(detections)
                
                # Write frame
                if writer:
                    writer.write(frame_resized)
                
                # Progress callback
                if callback:
                    callback(frame_count, total_frames, len(detections))
                elif frame_count % 30 == 0:  # Print every 30 frames
                    print(f"Processed {frame_count}/{total_frames} frames - {len(detections)} detections in current frame")
        
        finally:
            cap.release()
            if writer:
                writer.release()
            
            if save_path:
                print(f"\nVideo saved to: {save_path}")
        
        print(f"Total vehicles detected: {total_vehicles} across {frame_count} frames")
        
        return save_path, total_vehicles
