"""
Live Webcam Vehicle Detection
Real-time detection from your camera with live highlighting
Press 'q' to quit, 's' to save screenshot, 'p' to pause/resume
"""
import cv2
import config
from vehicle_detector import VehicleDetector


def run_webcam_detection():
    """Run real-time vehicle detection from webcam"""
    
    print("=" * 60)
    print("LIVE WEBCAM VEHICLE DETECTION")
    print("=" * 60)
    print("\nInitializing detector...")
    detector = VehicleDetector(config.MODEL_NAME, config.CONFIDENCE_THRESHOLD)
    
    print("Opening webcam...")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("✗ Error: Could not open webcam")
        return
    
    # Set resolution for speed
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    print(f"✓ Webcam opened!")
    print(f"\nControls:")
    print(f"  'q' - Quit")
    print(f"  's' - Save screenshot")
    print(f"  'p' - Pause/Resume")
    print(f"  'c' - Clear vehicle count")
    print(f"\n{'='*60}")
    
    frame_count = 0
    total_vehicles = 0
    paused = False
    screenshot_count = 0
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # Detect (skip every other frame for speed)
            if frame_count % 2 == 0 and not paused:
                results = detector.detect_objects(frame)
                detections = detector.filter_detections(results)
                frame = detector.draw_boxes(frame, detections)
                total_vehicles += len(detections)
            
            # Add info text
            info_text = f"Frame: {frame_count} | Total Vehicles: {total_vehicles}"
            if paused:
                info_text += " | PAUSED"
            
            cv2.putText(frame, info_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                       0.6, (0, 255, 0), 2)
            cv2.putText(frame, "Press 'q' to quit, 'h' for help", (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Display
            cv2.imshow("Live Vehicle Detection", frame)
            
            # Key handling
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                print("\nQuitting...")
                break
            elif key == ord('s'):
                filename = f"screenshot_{screenshot_count}.jpg"
                cv2.imwrite(filename, frame)
                screenshot_count += 1
                print(f"✓ Screenshot saved: {filename}")
            elif key == ord('p'):
                paused = not paused
                status = "PAUSED ⏸️" if paused else "RUNNING ▶️"
                print(f"Detection {status}")
            elif key == ord('c'):
                total_vehicles = 0
                print("✓ Vehicle count cleared")
            elif key == ord('h'):
                print("\nControls:")
                print("  'q' - Quit")
                print("  's' - Save screenshot")
                print("  'p' - Pause/Resume")
                print("  'c' - Clear count")
                print("  'h' - Show this help")
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
        
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Total frames: {frame_count}")
        print(f"Total vehicles detected: {total_vehicles}")
        print(f"Average vehicles per frame: {total_vehicles/frame_count:.2f}")
        print("=" * 60)


if __name__ == "__main__":
    try:
        run_webcam_detection()
    except KeyboardInterrupt:
        print("\n✓ Stopped by user")
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
