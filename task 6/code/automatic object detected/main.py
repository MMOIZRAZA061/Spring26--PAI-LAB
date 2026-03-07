"""
Main script for automatic object detection from videos and images
Usage: python main.py <input_path> [output_path]
"""
import sys
import os
from pathlib import Path
import cv2
from vehicle_detector import VehicleDetector
import config


def create_output_filename(input_path, output_folder=config.OUTPUT_FOLDER):
    """
    Create output filename based on input file
    
    Args:
        input_path (str): Path to input file
        output_folder (str): Output folder path
        
    Returns:
        str: Full output path
    """
    Path(output_folder).mkdir(exist_ok=True)
    
    input_file = Path(input_path)
    name_without_ext = input_file.stem
    suffix = input_file.suffix
    
    # For videos, ensure mp4 format
    if suffix.lower() in ['.mp4', '.avi', '.mov', '.mkv']:
        output_name = f"{name_without_ext}_detected.mp4"
    else:
        output_name = f"{name_without_ext}_detected{suffix}"
    
    return os.path.join(output_folder, output_name)


def process_file(detector, input_path, output_path=None):
    """
    Process a file (image or video)
    
    Args:
        detector: VehicleDetector instance
        input_path (str): Path to input file
        output_path (str): Path to save output (optional)
    """
    input_path = Path(input_path)
    
    if not input_path.exists():
        print(f"Error: File not found: {input_path}")
        return
    
    file_type = input_path.suffix.lower()
    
    # Image processing
    if file_type in ['.jpg', '.jpeg', '.png', '.bmp', '.gif']:
        print(f"\nProcessing image: {input_path}")
        
        if output_path is None:
            output_path = create_output_filename(input_path)
        
        try:
            frame, vehicles = detector.process_image(input_path, output_path)
            print(f"✓ Successfully detected {len(vehicles)} vehicle(s) in image")
        except Exception as e:
            print(f"✗ Error processing image: {e}")
    
    # Video processing
    elif file_type in ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv']:
        print(f"\nProcessing video: {input_path}")
        
        if output_path is None:
            output_path = create_output_filename(input_path)
        
        def progress_callback(current, total, vehicles_in_frame):
            percent = (current / total) * 100
            bar_length = 40
            filled = int(bar_length * current / total)
            bar = '█' * filled + '░' * (bar_length - filled)
            print(f"\r[{bar}] {percent:.1f}% ({current}/{total}) - Vehicles: {vehicles_in_frame}", end='', flush=True)
        
        try:
            output_file, total = detector.process_video(input_path, output_path, progress_callback)
            print(f"\n✓ Successfully detected {total} vehicle(s) in video")
        except Exception as e:
            print(f"✗ Error processing video: {e}")
    
    else:
        print(f"Error: Unsupported file type: {file_type}")
        print("Supported formats: .jpg, .jpeg, .png, .bmp, .gif (images), .mp4, .avi, .mov, .mkv (videos)")


def process_folder(detector, input_folder, output_folder=None):
    """
    Process all files in a folder
    
    Args:
        detector: VehicleDetector instance
        input_folder (str): Path to input folder
        output_folder (str): Path to output folder (optional)
    """
    input_folder = Path(input_folder)
    
    if not input_folder.is_dir():
        print(f"Error: Folder not found: {input_folder}")
        return
    
    if output_folder is None:
        output_folder = config.OUTPUT_FOLDER
    
    Path(output_folder).mkdir(exist_ok=True)
    
    # Get all image and video files
    supported_formats = ('*.jpg', '*.jpeg', '*.png', '*.bmp', '*.gif', 
                        '*.mp4', '*.avi', '*.mov', '*.mkv', '*.flv', '*.wmv')
    
    files = []
    for pattern in supported_formats:
        files.extend(input_folder.glob(pattern))
        files.extend(input_folder.glob(pattern.upper()))
    
    if not files:
        print(f"No supported files found in: {input_folder}")
        return
    
    print(f"Found {len(files)} file(s) to process\n")
    
    for i, file_path in enumerate(files, 1):
        print(f"\n[{i}/{len(files)}]", end=" ")
        output_path = os.path.join(output_folder, f"{file_path.stem}_detected{file_path.suffix}")
        process_file(detector, file_path, output_path)


def main():
    """Main execution function"""
    
    print("=" * 60)
    print("AUTOMATIC OBJECT DETECTION SYSTEM")
    print("=" * 60)
    
    # Initialize detector
    print("\nInitializing detector...")
    detector = VehicleDetector(config.MODEL_NAME, config.CONFIDENCE_THRESHOLD)
    
    # Parse command line arguments
    if len(sys.argv) < 2:
        print("\nUsage: python main.py <input_path> [output_path]")
        print("\nExamples:")
        print("  python main.py video.mp4")
        print("  python main.py image.jpg output_image.jpg")
        print("  python main.py input_folder/")
        print("  python main.py video.mp4 output.mp4")
        print("\nSupported formats:")
        print("  Images: .jpg, .jpeg, .png, .bmp, .gif")
        print("  Videos: .mp4, .avi, .mov, .mkv, .flv, .wmv")
        print("\nOutput files will be saved in 'outputs' folder by default")
        return
    
    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    input_path_obj = Path(input_path)
    
    # Process folder
    if input_path_obj.is_dir():
        process_folder(detector, input_path, output_path)
    else:
        process_file(detector, input_path, output_path)
    
    print("\n" + "=" * 60)
    print("Processing complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
