"""
Example usage of the Vehicle Detection System
This script demonstrates how to use the detector in your own code
"""

from vehicle_detector import VehicleDetector
from pathlib import Path
import config


def example_1_single_image():
    """Example 1: Process a single image"""
    print("=" * 60)
    print("Example 1: Process a Single Image")
    print("=" * 60)
    
    # Initialize detector
    detector = VehicleDetector(config.MODEL_NAME, config.CONFIDENCE_THRESHOLD)
    
    # Process image (place your image in inputs/ folder)
    input_image = "inputs/sample_image.jpg"  # Change to your image path
    output_image = "outputs/sample_image_detected.jpg"
    
    try:
        frame, vehicles = detector.process_image(input_image, output_image)
        print(f"✓ Found {len(vehicles)} vehicle(s)")
        
        # Print vehicle details
        for i, vehicle in enumerate(vehicles, 1):
            print(f"  Vehicle {i}: {vehicle['class_name'].upper()} (confidence: {vehicle['confidence']:.2f})")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        print(f"  Make sure {input_image} exists")


def example_2_single_video():
    """Example 2: Process a single video"""
    print("\n" + "=" * 60)
    print("Example 2: Process a Single Video")
    print("=" * 60)
    
    # Initialize detector
    detector = VehicleDetector(config.MODEL_NAME, config.CONFIDENCE_THRESHOLD)
    
    # Process video (place your video in inputs/ folder)
    input_video = "inputs/sample_video.mp4"  # Change to your video path
    output_video = "outputs/sample_video_detected.mp4"
    
    try:
        def progress_callback(current, total, vehicles_in_frame):
            percent = (current / total) * 100
            print(f"\r  Progress: {percent:.1f}% ({current}/{total}) - "
                  f"Current frame: {vehicles_in_frame} vehicles", end='', flush=True)
        
        output_file, total_vehicles = detector.process_video(
            input_video, 
            output_video, 
            callback=progress_callback
        )
        print(f"\n✓ Total vehicles detected: {total_vehicles}")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        print(f"  Make sure {input_video} exists")


def example_3_batch_processing():
    """Example 3: Process multiple files in a folder"""
    print("\n" + "=" * 60)
    print("Example 3: Batch Process Multiple Files")
    print("=" * 60)
    
    # Initialize detector
    detector = VehicleDetector(config.MODEL_NAME, config.CONFIDENCE_THRESHOLD)
    
    input_folder = Path("inputs")
    
    if not input_folder.exists():
        print(f"✗ Error: {input_folder} folder not found")
        return
    
    # Find all image and video files
    supported_formats = ('*.jpg', '*.jpeg', '*.png', '*.mp4', '*.avi')
    files = []
    
    for pattern in supported_formats:
        files.extend(input_folder.glob(pattern))
    
    if not files:
        print(f"No supported files found in {input_folder}")
        return
    
    print(f"Found {len(files)} file(s) to process\n")
    
    total_vehicles = 0
    
    for file_path in files:
        print(f"Processing: {file_path.name}")
        
        output_path = f"outputs/{file_path.stem}_detected{file_path.suffix}"
        
        try:
            if file_path.suffix.lower() in ['.mp4', '.avi']:
                _, vehicles = detector.process_video(file_path, output_path)
                print(f"  ✓ Video: {vehicles} vehicles detected")
                total_vehicles += vehicles
            else:
                _, vehicles = detector.process_image(file_path, output_path)
                print(f"  ✓ Image: {len(vehicles)} vehicles detected")
                total_vehicles += len(vehicles)
        
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    print(f"\n✓ Total vehicles across all files: {total_vehicles}")


def example_4_custom_processing():
    """Example 4: Custom processing with detection filtering"""
    print("\n" + "=" * 60)
    print("Example 4: Custom Processing - Get Vehicle Coordinates")
    print("=" * 60)
    
    import cv2
    
    # Initialize detector
    detector = VehicleDetector(config.MODEL_NAME, config.CONFIDENCE_THRESHOLD)
    
    # Load image
    input_image = "inputs/sample_image.jpg"
    
    try:
        frame = cv2.imread(input_image)
        if frame is None:
            raise ValueError(f"Could not load {input_image}")
        
        # Detect
        results = detector.detect_objects(frame)
        detections = detector.filter_detections(results)
        
        print(f"Found {len(detections)} object(s):\n")
        
        for i, detection in enumerate(detections, 1):
            x1, y1, x2, y2 = detection['box']
            width = x2 - x1
            height = y2 - y1
            
            print(f"Object {i}:")
            print(f"  Type: {detection['class_name'].upper()}")
            print(f"  Confidence: {detection['confidence']:.2%}")
            print(f"  Position: x={x1:.0f}, y={y1:.0f}")
            print(f"  Size: {width:.0f}x{height:.0f} pixels")
            print()
        
    except Exception as e:
        print(f"✗ Error: {e}")


def example_5_real_time_camera():
    """Example 5: Real-time detection from webcam"""
    print("\n" + "=" * 60)
    print("Example 5: Real-Time Webcam Detection")
    print("=" * 60)
    
    import cv2
    
    # Initialize detector
    print("Initializing detector...")
    detector = VehicleDetector(config.MODEL_NAME, config.CONFIDENCE_THRESHOLD)
    
    # Open webcam
    print("Opening webcam... (Press 'q' to quit)")
    cap = cv2.VideoCapture(0)  # 0 for default webcam
    
    if not cap.isOpened():
        print("✗ Error: Could not open webcam")
        return
    
    frame_count = 0
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # Detect every 5 frames for performance
            if frame_count % 5 == 0:
                results = detector.detect_objects(frame)
                detections = detector.filter_detections(results)
                frame = detector.draw_boxes(frame, detections)
            
            # Display
            cv2.imshow('Vehicle Detection', frame)
            
            # Check for quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    print("\nVEHICLE DETECTION - USAGE EXAMPLES")
    print("\nThese examples show different ways to use the detector")
    print("Copy the code snippets to your own projects\n")
    
    print("Note: Place sample images/videos in the 'inputs/' folder")
    print("Example files should be named: sample_image.jpg, sample_video.mp4\n")
    
    # Uncomment the example you want to run:
    
    # example_1_single_image()           # Process single image
    # example_2_single_video()           # Process single video
    # example_3_batch_processing()       # Process multiple files
    # example_4_custom_processing()      # Get detailed vehicle info
    # example_5_real_time_camera()       # Webcam detection
    
    print("\n" + "=" * 60)
    print("Examples are commented out to prevent errors")
    print("Uncomment the examples you want to run at the bottom")
    print("=" * 60)
