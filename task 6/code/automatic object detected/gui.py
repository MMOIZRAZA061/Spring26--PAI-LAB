"""
GUI application for Vehicle Detection
Run this file to open the graphical interface
"""
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
import threading
import cv2
from PIL import Image, ImageTk
from vehicle_detector import VehicleDetector
import config


class VehicleDetectorGUI:
    """GUI Application for Vehicle Detection"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🚗 Automatic Object Detector")
        self.root.geometry("1400x950")
        self.root.minsize(1200, 850)
        
        self.detector = None
        self.is_processing = False
        self.input_file = None
        self.output_file = None
        self.preview_running = False
        self.preview_thread = None
        
        # Create menu bar
        self.create_menu()
        
        # Setup UI
        self.setup_ui()
    
    def create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open File", command=self.select_input)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
    
    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo("About", "Automatic Object Detection System\n\nUses YOLOv8 for real-time object detection\n\nSupports: MP4, AVI, MOV, JPG, PNG\n\nCan detect all 80 COCO dataset objects or vehicles only")
    
    def setup_ui(self):
        """Setup UI components"""
        
        # Top frame - Title and Info
        top_frame = tk.Frame(self.root, bg="lightblue", height=60)
        top_frame.pack(fill="x", padx=0, pady=0)
        top_frame.pack_propagate(False)
        
        title_label = tk.Label(top_frame, text="🚗 AUTOMATIC OBJECT DETECTOR 🚗", 
                              font=("Arial", 18, "bold"), bg="lightblue", fg="darkblue")
        title_label.pack(pady=10)
        
        # Main container
        main_container = tk.Frame(self.root)
        main_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Left side - Video/Image preview
        left_frame = tk.LabelFrame(main_container, text="📹 VIDEO/IMAGE PREVIEW", 
                                   font=("Arial", 12, "bold"), padx=5, pady=5)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 3))
        
        # Video preview canvas
        self.canvas = tk.Canvas(left_frame, bg="black", width=600, height=500)
        self.canvas.pack(fill="both", expand=True)
        
        self.preview_label = tk.Label(left_frame, text="No video/image selected", 
                                      font=("Arial", 10), fg="gray")
        self.preview_label.pack(pady=5)
        
        # Right side - Controls
        right_frame = tk.Frame(main_container)
        right_frame.pack(side="right", fill="both", padx=(3, 0))
        
        # Create scrollable frame for controls
        self.controls_canvas = tk.Canvas(right_frame, bg=self.root.cget('bg'))
        self.controls_scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=self.controls_canvas.yview)
        self.controls_scrollable_frame = tk.Frame(self.controls_canvas, bg=self.root.cget('bg'))
        
        self.controls_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.controls_canvas.configure(scrollregion=self.controls_canvas.bbox("all"))
        )
        
        self.controls_canvas.create_window((0, 0), window=self.controls_scrollable_frame, anchor="nw")
        self.controls_canvas.configure(yscrollcommand=self.controls_scrollbar.set)
        
        # Bind mouse wheel to scrolling
        def _on_mousewheel(event):
            self.controls_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        self.controls_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        self.controls_canvas.pack(side="left", fill="both", expand=True)
        self.controls_scrollbar.pack(side="right", fill="y")
        
        # Use scrollable frame for all controls
        controls_container = self.controls_scrollable_frame
        
        # File selection
        file_frame = tk.LabelFrame(controls_container, text="📁 FILE SELECTION", 
                                   font=("Arial", 11, "bold"), padx=5, pady=5)
        file_frame.pack(fill="x", pady=2)
        
        self.file_label = tk.Label(file_frame, text="No file selected", 
                                   font=("Arial", 9), fg="red", wraplength=300)
        self.file_label.pack(anchor="w", pady=2)
        
        tk.Button(file_frame, text="📂 UPLOAD VIDEO/IMAGE", command=self.select_input,
                 bg="#4CAF50", fg="white", font=("Arial", 9, "bold"), 
                 width=22, height=1).pack(pady=2)
        
        # Settings
        settings_frame = tk.LabelFrame(controls_container, text="⚙️ SETTINGS", 
                                      font=("Arial", 11, "bold"), padx=5, pady=5)
        settings_frame.pack(fill="x", pady=2)
        
        tk.Label(settings_frame, text="Confidence Threshold:", font=("Arial", 9)).pack(anchor="w")
        self.confidence = tk.Scale(settings_frame, from_=0, to=1, resolution=0.05,
                                   orient="horizontal", bg="lightgray")
        self.confidence.set(config.CONFIDENCE_THRESHOLD)
        self.confidence.pack(fill="x", pady=2)
        
        self.show_conf = tk.BooleanVar(value=config.SHOW_CONFIDENCE)
        tk.Checkbutton(settings_frame, text="✓ Show confidence scores", 
                      variable=self.show_conf, font=("Arial", 9)).pack(anchor="w")
        
        # Detection Mode
        self.detect_all = tk.BooleanVar(value=config.DETECT_ALL_OBJECTS)
        tk.Checkbutton(settings_frame, text="🎯 Detect ALL objects (not just vehicles)", 
                      variable=self.detect_all, font=("Arial", 9, "bold"), fg="blue").pack(anchor="w")
        
        # Speed Mode
        self.speed_mode = tk.BooleanVar(value=True)
        tk.Checkbutton(settings_frame, text="⚡ Speed Mode (RECOMMENDED)", 
                      variable=self.speed_mode, font=("Arial", 9, "bold"), fg="red").pack(anchor="w")
        
        tk.Label(settings_frame, text="Frame Quality:", font=("Arial", 9)).pack(anchor="w", pady=(2, 0))
        self.frame_quality = tk.StringVar(value="640")
        for quality in ["320 (Fastest)", "480 (Fast)", "640 (Balanced)", "800 (Quality)"]:
            tk.Radiobutton(settings_frame, text=quality, variable=self.frame_quality,
                          value=quality.split()[0], font=("Arial", 8)).pack(anchor="w")
        
        tk.Label(settings_frame, text="Preview FPS:", font=("Arial", 9)).pack(anchor="w", pady=(2, 0))
        self.preview_fps = tk.Scale(settings_frame, from_=5, to=30, resolution=5,
                                   orient="horizontal", bg="lightgray")
        self.preview_fps.set(config.PREVIEW_FPS)
        self.preview_fps.pack(fill="x", pady=2)
        
        tk.Label(settings_frame, text="Output Speed:", font=("Arial", 9)).pack(anchor="w", pady=(2, 0))
        self.frame_rate_multiplier = tk.Scale(settings_frame, from_=0.5, to=3.0, resolution=0.5,
                                             orient="horizontal", bg="lightgray")
        self.frame_rate_multiplier.set(config.FRAME_RATE_MULTIPLIER)
        self.frame_rate_multiplier.pack(fill="x", pady=2)
        control_frame = tk.LabelFrame(controls_container, text="🎮 CONTROLS", 
                                     font=("Arial", 11, "bold"), padx=5, pady=5)
        control_frame.pack(fill="x", pady=2)
        
        tk.Button(control_frame, text="👁️ LIVE PREVIEW", command=self.start_live_preview,
                 bg="#9C27B0", fg="white", font=("Arial", 9, "bold"), 
                 width=22, height=1).pack(pady=2)
        
        tk.Button(control_frame, text="⏹️ STOP PREVIEW", command=self.stop_live_preview,
                 bg="#f44336", fg="white", font=("Arial", 9, "bold"), 
                 width=22, height=1).pack(pady=2)
        
        tk.Button(control_frame, text="▶️ DETECT OBJECTS", command=self.process_file,
                 bg="#2196F3", fg="white", font=("Arial", 9, "bold"), 
                 width=22, height=1).pack(pady=2)
        
        tk.Button(control_frame, text="💾 SAVE OUTPUT", command=self.save_output,
                 bg="#FF9800", fg="white", font=("Arial", 9, "bold"), 
                 width=22, height=1).pack(pady=2)
        
        tk.Button(control_frame, text="⬇️ DOWNLOAD VIDEO", command=self.download_video,
                 bg="#4CAF50", fg="white", font=("Arial", 9, "bold"), 
                 width=22, height=1).pack(pady=2)
        
        # Progress
        progress_frame = tk.LabelFrame(controls_container, text="📊 PROGRESS", 
                                      font=("Arial", 11, "bold"), padx=5, pady=5)
        progress_frame.pack(fill="x", pady=2)
        
        self.progress_bar = ttk.Progressbar(progress_frame, length=300, mode='determinate')
        self.progress_bar.pack(fill="x", pady=2)
        
        self.progress_label = tk.Label(progress_frame, text="0%", font=("Arial", 9))
        self.progress_label.pack()
        
        # Status/Log
        status_frame = tk.LabelFrame(controls_container, text="📝 STATUS LOG", 
                                    font=("Arial", 11, "bold"), padx=5, pady=5)
        status_frame.pack(fill="both", expand=True, pady=2)
        
        self.status_text = tk.Text(status_frame, height=6, width=38, 
                                   font=("Courier", 8), state="disabled")
        self.status_text.pack(fill="both", expand=True)
        
        # Scrollbar for status
        scrollbar = ttk.Scrollbar(status_frame, command=self.status_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.status_text.config(yscrollcommand=scrollbar.set)
        
        # Bottom frame - Exit
        bottom_frame = tk.Frame(self.root, bg="lightgray", height=40)
        bottom_frame.pack(fill="x", padx=0, pady=0)
        bottom_frame.pack_propagate(False)
        
        tk.Button(bottom_frame, text="❌ EXIT", command=self.root.quit,
                 bg="#f44336", fg="white", font=("Arial", 10, "bold"), width=20).pack(pady=8)
    
    def log_message(self, message):
        """Add message to status text"""
        self.status_text.config(state="normal")
        self.status_text.insert("end", message + "\n")
        self.status_text.see("end")
        self.status_text.config(state="disabled")
        self.root.update()
    
    def select_input(self):
        """Select input file"""
        file_type = [("All Files", "*.*"),
                    ("Video Files", "*.mp4 *.avi *.mov *.mkv *.flv"),
                    ("Image Files", "*.jpg *.png *.jpeg *.bmp")]
        
        filename = filedialog.askopenfilename(filetypes=file_type)
        if filename:
            self.input_file = filename
            self.file_label.config(text=f"✓ {Path(filename).name}", fg="green")
            self.log_message(f"File selected: {Path(filename).name}")
            self.show_preview()
    
    def show_preview(self):
        """Show video/image preview on canvas"""
        if not self.input_file:
            return
        
        try:
            file_ext = Path(self.input_file).suffix.lower()
            
            if file_ext in ['.jpg', '.jpeg', '.png', '.bmp']:
                # Show image
                img = Image.open(self.input_file)
                img.thumbnail((500, 400), Image.Resampling.LANCZOS)
                self.photo = ImageTk.PhotoImage(img)
                self.canvas.create_image(250, 200, image=self.photo)
                self.preview_label.config(text="Image Preview")
            
            elif file_ext in ['.mp4', '.avi', '.mov', '.mkv', '.flv']:
                # Show first frame of video
                cap = cv2.VideoCapture(self.input_file)
                ret, frame = cap.read()
                cap.release()
                
                if ret:
                    # Convert BGR to RGB
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame = cv2.resize(frame, (500, 400))
                    
                    img = Image.fromarray(frame)
                    self.photo = ImageTk.PhotoImage(img)
                    self.canvas.create_image(250, 200, image=self.photo)
                    
                    # Get video info
                    cap = cv2.VideoCapture(self.input_file)
                    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                    fps = cap.get(cv2.CAP_PROP_FPS)
                    cap.release()
                    
                    duration = total_frames / fps if fps > 0 else 0
                    self.preview_label.config(text=f"Video Preview | Frames: {total_frames} | FPS: {fps:.1f}")
        
        except Exception as e:
            self.log_message(f"Preview error: {str(e)}")
    
    def start_live_preview(self):
        """Start live preview with detection highlighting"""
        if not self.input_file:
            messagebox.showerror("Error", "Please select a video or image first!")
            return
        
        if self.preview_running:
            messagebox.showinfo("Info", "Preview already running!")
            return
        
        self.preview_running = True
        self.log_message("\n▶️ Starting live preview with detection...")
        
        self.preview_thread = threading.Thread(target=self._live_preview_thread)
        self.preview_thread.daemon = True
        self.preview_thread.start()
    
    def stop_live_preview(self):
        """Stop live preview"""
        self.preview_running = False
        self.log_message("⏹️ Preview stopped")
    
    def _live_preview_thread(self):
        """Live preview thread with detection"""
        try:
            # Initialize detector if needed
            if self.detector is None:
                self.log_message("⏳ Initializing detector...")
                self.detector = VehicleDetector(config.MODEL_NAME, self.confidence.get())
                self.log_message("✓ Detector ready!\n")
            
            file_ext = Path(self.input_file).suffix.lower()
            
            if file_ext in ['.jpg', '.jpeg', '.png', '.bmp']:
                # Static image preview with detection
                self.log_message("📷 Loading image with detection...")
                
                frame = cv2.imread(self.input_file)
                if frame is None:
                    raise ValueError("Could not load image")
                
                # Detect
                results = self.detector.detect_objects(frame)
                detections = self.detector.filter_detections(results)
                frame = self.detector.draw_boxes(frame, detections)
                
                # Resize for display
                display_frame = cv2.resize(frame, (500, 400))
                display_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
                
                img = Image.fromarray(display_frame)
                self.photo = ImageTk.PhotoImage(img)
                self.canvas.create_image(250, 200, image=self.photo)
                
                object_type = "object" if config.DETECT_ALL_OBJECTS else "vehicle"
                plural = "s" if len(detections) != 1 else ""
                self.log_message(f"✓ Found {len(detections)} {object_type}{plural}")
                self.preview_label.config(text=f"Live Detection - {len(detections)} {object_type}{plural} found")
            
            else:
                # Video preview with live detection
                self.log_message("🎬 Loading video with live detection...")
                self.log_message("Processing first 30 frames for preview...")
                
                cap = cv2.VideoCapture(self.input_file)
                frame_count = 0
                detections_found = 0
                
                while self.preview_running and frame_count < 30:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    frame_count += 1
                    
                    # Detect
                    results = self.detector.detect_objects(frame)
                    detections = self.detector.filter_detections(results)
                    frame = self.detector.draw_boxes(frame, detections)
                    detections_found += len(detections)
                    
                    # Resize for display
                    display_frame = cv2.resize(frame, (500, 400))
                    display_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
                    
                    img = Image.fromarray(display_frame)
                    self.photo = ImageTk.PhotoImage(img)
                    self.canvas.create_image(250, 200, image=self.photo)
                    
                    object_type = "object" if config.DETECT_ALL_OBJECTS else "vehicle"
                    plural = "s" if len(detections) != 1 else ""
                    self.preview_label.config(text=f"Live Detection - Frame {frame_count} | {len(detections)} {object_type}{plural}")
                    self.root.update()
                    
                    # Small delay for smooth preview
                    threading.Event().wait(1.0 / self.preview_fps.get())
                
                cap.release()
                
                if self.preview_running:
                    object_type = "object" if config.DETECT_ALL_OBJECTS else "vehicle"
                    plural = "s" if detections_found != 1 else ""
                    self.log_message(f"✓ Preview complete - {detections_found} {object_type}{plural} in first {frame_count} frames")
                    self.preview_label.config(text=f"Preview Complete - {detections_found} {object_type}{plural} detected")
        
        except Exception as e:
            self.log_message(f"✗ Preview error: {str(e)}")
            messagebox.showerror("Error", f"Preview failed: {str(e)}")
        
        finally:
            self.preview_running = False
    
    def process_file(self):
        """Process file in separate thread"""
        if not self.input_file:
            messagebox.showerror("Error", "Please select a video or image first!")
            return
        
        # Generate output path
        input_path = Path(self.input_file)
        self.output_file = f"outputs/{input_path.stem}_detected{input_path.suffix}"
        
        self.log_message(f"\n{'='*40}")
        self.log_message("🔄 STARTING DETECTION...")
        self.log_message(f"{'='*40}")
        
        thread = threading.Thread(target=self._process_thread)
        thread.daemon = True
        thread.start()
    
    def _process_thread(self):
        """Processing thread"""
        try:
            # Update settings
            config.SPEED_MODE = self.speed_mode.get()
            config.FRAME_WIDTH = int(self.frame_quality.get())
            config.DETECT_ALL_OBJECTS = self.detect_all.get()
            config.FRAME_RATE_MULTIPLIER = self.frame_rate_multiplier.get()
            config.PREVIEW_FPS = self.preview_fps.get()
            
            # Initialize detector if needed
            if self.detector is None:
                self.log_message("⏳ Initializing detector...")
                self.detector = VehicleDetector(config.MODEL_NAME, self.confidence.get())
                self.log_message("✓ Detector ready!\n")
            
            input_file = self.input_file
            output_file = self.output_file
            
            self.log_message(f"📁 Processing: {Path(input_file).name}")
            detection_mode = "ALL OBJECTS" if config.DETECT_ALL_OBJECTS else "VEHICLES ONLY"
            self.log_message(f"🎯 Detection Mode: {detection_mode}")
            if config.SPEED_MODE:
                self.log_message(f"⚡ Speed Mode: ON (Resolution: {config.FRAME_WIDTH}px)")
            if config.FRAME_RATE_MULTIPLIER != 1.0:
                self.log_message(f"⏱️  Speed Multiplier: {config.FRAME_RATE_MULTIPLIER}x")
            
            file_type = Path(input_file).suffix.lower()
            
            if file_type in ['.jpg', '.jpeg', '.png', '.bmp']:
                self.log_message("📷 Type: IMAGE\n")
                frame, detections = self.detector.process_image(input_file, output_file)
                object_type = "object" if config.DETECT_ALL_OBJECTS else "vehicle"
                plural = "s" if len(detections) != 1 else ""
                self.log_message(f"\n✓ DETECTION COMPLETE!")
                self.log_message(f"🎯 Found {len(detections)} {object_type}{plural}")
                self.progress_bar['value'] = 100
                self.progress_label.config(text="100% - COMPLETE")
                messagebox.showinfo("Success", f"✓ Image processed!\n\n{len(detections)} {object_type}{plural} detected\n\nOutput saved to:\n{output_file}")
            
            else:
                self.log_message(f"🎬 Type: VIDEO\n")
                
                def callback(current, total, detections_count):
                    percent = (current / total) * 100
                    self.progress_bar['value'] = percent
                    self.progress_label.config(text=f"{percent:.0f}%")
                    object_type = "objects" if config.DETECT_ALL_OBJECTS else "vehicles"
                    if current % 30 == 0:
                        self.log_message(f"Frame {current}/{total} - {detections_count} {object_type}")
                    self.root.update()
                
                output_file, total = self.detector.process_video(input_file, output_file, callback)
                object_type = "object" if config.DETECT_ALL_OBJECTS else "vehicle"
                plural = "s" if total != 1 else ""
                self.log_message(f"\n✓ DETECTION COMPLETE!")
                self.log_message(f"🎯 Total {object_type}{plural}: {total}")
                self.progress_bar['value'] = 100
                self.progress_label.config(text="100% - COMPLETE")
                messagebox.showinfo("Success", f"✓ Video processed!\n\n{total} {object_type}{plural} detected\n\nOutput saved to:\n{output_file}")
        
        except Exception as e:
            error_msg = str(e)
            self.log_message(f"\n✗ ERROR: {error_msg}")
            self.log_message("\n📋 TROUBLESHOOTING:")
            self.log_message("1. Update PyTorch: pip install --upgrade torch")
            self.log_message("2. Reinstall YOLOv8: pip install --upgrade ultralytics")
            self.log_message("3. Try smaller model: yolov8n.pt")
            self.log_message("4. Try different video file")
            messagebox.showerror("Processing Error", f"❌ Error: {error_msg}\n\nTroubleshooting:\n1. pip install --upgrade torch\n2. pip install --upgrade ultralytics\n3. Try smaller model (edit config.py)")
            self.progress_bar['value'] = 0
    
    def save_output(self):
        """Save/export the output file"""
        if not self.output_file or not Path(self.output_file).exists():
            messagebox.showwarning("Warning", "No processed output available yet.\n\nPlease process a file first!")
            return
        
        file_type = [("Video Files", "*.mp4"), ("All Files", "*.*")]
        save_path = filedialog.asksaveasfilename(
            defaultextension=".mp4",
            filetypes=file_type,
            initialfile=Path(self.output_file).name
        )
        
        if save_path:
            try:
                import shutil
                shutil.copy(self.output_file, save_path)
                messagebox.showinfo("Success", f"✓ File saved to:\n{save_path}")
                self.log_message(f"✓ Saved to: {save_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Save failed: {str(e)}")
    
    def download_video(self):
        """Download/save the processed video with custom options"""
        if not self.output_file or not Path(self.output_file).exists():
            messagebox.showwarning("Warning", "No processed video available yet.\n\nPlease process a video file first!")
            return
        
        # Check if it's a video file
        if not Path(self.output_file).suffix.lower() in ['.mp4', '.avi', '.mov', '.mkv']:
            messagebox.showwarning("Warning", "Download is only available for video files.\n\nFor images, use 'Save Output' instead.")
            return
        
        # Get video info
        cap = cv2.VideoCapture(self.output_file)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap.release()
        
        # Show download dialog with info
        info_msg = f"Video Details:\n"
        info_msg += f"• Resolution: {width}x{height}\n"
        info_msg += f"• FPS: {fps:.1f}\n"
        info_msg += f"• Frames: {total_frames}\n"
        info_msg += f"• Duration: {total_frames/fps:.1f} seconds\n\n"
        info_msg += "Choose where to save the detected video:"
        
        messagebox.showinfo("Download Video", info_msg)
        
        file_type = [("MP4 Video", "*.mp4"), ("AVI Video", "*.avi"), ("All Files", "*.*")]
        save_path = filedialog.asksaveasfilename(
            defaultextension=".mp4",
            filetypes=file_type,
            initialfile=f"detected_{Path(self.output_file).name}"
        )
        
        if save_path:
            try:
                import shutil
                shutil.copy(self.output_file, save_path)
                messagebox.showinfo("Success", f"✓ Video downloaded successfully!\n\nSaved to:\n{save_path}")
                self.log_message(f"⬇️ Downloaded to: {save_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Download failed: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = VehicleDetectorGUI(root)
    root.mainloop()
