import cv2
import mediapipe as mp
import sys
import os
import customtkinter as ctk
from PIL import Image, ImageTk
import threading
import time
import tkinter as tk  # For Canvas
import math  # For angle calculations

# Set CustomTkinter appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Initialize MediaPipe modules (lightweight)
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
HAND_CONNECTIONS = mp_hands.HAND_CONNECTIONS

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Hand Gesture Monitor")
        self.iconbitmap('icon.ico')  # Set custom icon
        self.lift()  # Bring to foreground
        self.focus_force()  # Force focus
        self.attributes("-fullscreen", True)
        self.resizable(True, True)  # Allow resizing for full-screen toggle
        self.bind("<F11>", self.toggle_fullscreen)
        self.bind("<Escape>", lambda e: self.attributes("-fullscreen", False))

        # Header
        self.header_label = ctk.CTkLabel(self, text="Real-Time Hand Gesture Monitor", font=ctk.CTkFont(size=28, weight="bold"), text_color="#ef4444")
        self.header_label.pack(pady=20)

        # Safety note
        self.safety_label = ctk.CTkLabel(self, text="System monitoring active. All features are safety-enabled.", font=ctk.CTkFont(size=12), text_color="#fbbf24")
        self.safety_label.pack(pady=(0, 20))

        # Main frame
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Video frame
        self.video_frame = ctk.CTkFrame(self.main_frame, width=500, height=600, fg_color="#1f2937", border_width=2, border_color="#374151")
        self.video_frame.pack(side="left", padx=5, pady=10)
        self.video_frame.pack_propagate(False)
        self.video_label = ctk.CTkLabel(self.video_frame, text="Camera Feed Loading...")
        self.video_label.pack(expand=True)

        # Virtual hand frame
        self.virtual_frame = ctk.CTkFrame(self.main_frame, width=400, height=600, fg_color="#000000", border_width=2, border_color="#00FFFF")
        self.virtual_frame.pack(side="left", padx=5, pady=10)
        self.virtual_frame.pack_propagate(False)
        self.virtual_canvas = tk.Canvas(self.virtual_frame, width=380, height=580, bg="#000000", highlightthickness=0)
        self.virtual_canvas.pack(expand=True, padx=10, pady=10)
        self.virtual_label = ctk.CTkLabel(self.virtual_frame, text="Holographic Wireframe Model", font=ctk.CTkFont(size=14, weight="bold"), text_color="#00FFFF")
        self.virtual_label.pack(pady=(0, 10))

        # Right panel
        self.right_frame = ctk.CTkFrame(self.main_frame)
        self.right_frame.pack(side="right", fill="both", expand=True, padx=5, pady=10)

        # Status frame
        self.status_frame = ctk.CTkFrame(self.right_frame, fg_color="#1f2937", border_width=2, border_color="#3b82f6")
        self.status_frame.pack(fill="x", pady=10)
        
        # Status icon
        self.status_icon = ctk.CTkLabel(self.status_frame, text="●", font=ctk.CTkFont(size=24, weight="bold"), text_color="#3b82f6")
        self.status_icon.pack(pady=10)
        
        self.status_label = ctk.CTkLabel(self.status_frame, text="Loading AI Model...", font=ctk.CTkFont(size=20, weight="bold"), text_color="#3b82f6")
        self.status_label.pack(pady=5)
        self.fps_label = ctk.CTkLabel(self.status_frame, text="0 FPS", font=ctk.CTkFont(size=14), text_color="#6b7280")
        self.fps_label.pack(pady=(0, 10))

        # Log frame
        self.log_frame = ctk.CTkFrame(self.right_frame, border_width=1, border_color="#374151")
        self.log_frame.pack(fill="both", expand=True, pady=10)
        self.log_label = ctk.CTkLabel(self.log_frame, text="Event Log", font=ctk.CTkFont(size=18, weight="bold"))
        self.log_label.pack(pady=10)
        self.log_textbox = ctk.CTkTextbox(self.log_frame, wrap="word", height=300)
        self.log_textbox.pack(fill="both", expand=True, padx=10, pady=5)
        self.log_textbox.insert("0.0", "[Starting] Waiting for AI model and camera to initialize...\n")

        # Variables
        self.running = True
        self.last_fps_time = time.time()
        self.frame_count = 0
        self.gesture_detected = False
        self.last_virtual_update = 0
        self.hands = None
        self.cap = None

        # Status note (repurposed from countdown)
        self.countdown_label = ctk.CTkLabel(self.status_frame, text="Instant Mode: Middle Finger = Immediate Shutdown", font=ctk.CTkFont(size=12), text_color="#ff4444")
        self.countdown_label.pack(pady=5)

        # Delay init and start video thread after GUI shows
        self.after(500, self.init_hands_and_camera)

        # Bind close event
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Initial log
        self.log("Application started successfully.")

    def log(self, message):
        timestamp = time.strftime("%H:%M:%S")
        self.log_textbox.insert("end", f"[{timestamp}] {message}\n")
        self.log_textbox.see("end")

    def update_status(self, text, color="#3b82f6"):
        self.status_label.configure(text=text, text_color=color)

    def toggle_fullscreen(self, event=None):
        self.attributes("-fullscreen", not self.attributes("-fullscreen"))

    def init_hands_and_camera(self):
        # Heavy init after GUI shows
        self.hands = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.8,  # Higher for sensitivity
            min_tracking_confidence=0.6
        )
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            self.log("ERROR: Could not open camera.")
            self.update_status("Camera Error", "#FF0000")
            return

        # Start video thread after init
        self.video_thread = threading.Thread(target=self.update_video)
        self.video_thread.daemon = True
        self.video_thread.start()

        self.log("AI Model and Camera Initialized - Instant Monitoring Active")
        self.update_status("Instant Monitoring...", "#3b82f6")

    # --- UPDATED DRAWING LOGIC FOR HOLOGRAPHIC EFFECT ---
    def draw_virtual_hand(self, landmarks):
        self.virtual_canvas.delete("all")
        canvas_width, canvas_height = 380, 580
        offset_x, offset_y = canvas_width / 2, canvas_height / 2
        scale = 350

        # Target: Deep blue/cyan holographic wireframe palette
        COLORS = {
            "glow_high": "#00FFFF",     # Bright Cyan for major lines/joints
            "glow_medium": "#00AAFF",   # Slightly darker blue for secondary mesh
            "mesh_base": "#0055AA",     # Deep Blue for subtle background wireframe
            "mesh_high": "#0099FF",     # Brighter blue for dense mesh structure
        }

        # --- Define connections for maximum density ---
        
        # 1. Standard connections (Bones)
        SKELETAL_CONNECTIONS = list(mp_hands.HAND_CONNECTIONS)

        # 2. Palm and Wrist Cross-Links (Base structure)
        PALM_LINKS = [
            (0, 5), (0, 9), (0, 13), (0, 17),  # Wrist to MCPs
            (5, 9), (9, 13), (13, 17),        # Across MCPs
            (1, 5), (2, 5), (1, 17), (2, 9),  # Diagonal links
            (0, 8), (0, 12), (0, 16), (0, 20) # Wrist to finger tips (to create longitudinal lines)
        ]

        # 3. Dense Cross-Segment and Volumetric Links (Creating the mesh)
        DENSE_MESH_LINKS = []
        
        # Cross-segment links (skipping one joint, e.g. PIP to DIP)
        for finger_start_idx in [1, 5, 9, 13, 17]:
            if finger_start_idx + 2 < 21: DENSE_MESH_LINKS.append((finger_start_idx, finger_start_idx + 2))
            if finger_start_idx + 3 < 21: DENSE_MESH_LINKS.append((finger_start_idx + 1, finger_start_idx + 3))

        # Horizontal/Webbing Links (Connecting adjacent fingers at the same level)
        for i in range(1, 4): # Thumb to Index MCP/Wrist area links
            if i + 4 < 21: DENSE_MESH_LINKS.append((i, i + 4))

        # Links across all finger segments (MCP, PIP, DIP, TIP to next finger)
        for i in range(5, 17, 4): 
            for j in range(4): # 0=MCP, 1=PIP, 2=DIP, 3=TIP
                DENSE_MESH_LINKS.append((i + j, i + j + 4)) # E.g., MCP 5 to MCP 9
                
        # Deep Palm Triangulation (Filling the wrist/palm area)
        DEEP_PALM_TRIANGULATION = [
            (0, 1), (0, 2), (0, 3), (0, 4), 
            (1, 9), (5, 13), (9, 17), 
            (2, 13), (3, 17), (1, 13), (5, 17),
            (0, 6), (0, 10), (0, 14), (0, 18), # Wrist to mid-finger joints
            (5, 10), (9, 14), (13, 18), # Extra palm diagonals
        ]

        # Combine all mesh lines
        ALL_MESH_CONNECTIONS = SKELETAL_CONNECTIONS + PALM_LINKS + DENSE_MESH_LINKS + DEEP_PALM_TRIANGULATION
        
        # Ensure all connection pairs are consistently converted to tuples with sorted indices 
        # before putting them into a set to eliminate duplicates.
        ALL_MESH_CONNECTIONS = list(set(tuple(sorted(c)) for c in ALL_MESH_CONNECTIONS))

        # --- PURE 2D COORDINATE MAPPING (NO Z-AXIS EFFECT) ---
        def get_coords(idx):
            lm = landmarks[idx]
            mirrored_x = 1 - lm.x # Mirror X-axis for natural perspective
            
            # Simple 2D projection
            x = offset_x + (mirrored_x - 0.5) * scale
            y = offset_y + (lm.y - 0.5) * scale
            
            # Clamp to canvas boundaries
            x = max(10, min(canvas_width - 10, int(x)))
            y = max(10, min(canvas_height - 10, int(y)))
            
            return x, y, lm.z

        # --- 1. Draw Mesh/Wireframe (Background, Thinner lines) ---
        for start_idx, end_idx in ALL_MESH_CONNECTIONS:
            sx, sy, sz = get_coords(start_idx)
            ex, ey, ez = get_coords(end_idx)
            
            # Use a slightly brighter color for the bulk of the dense mesh
            fill_color = COLORS["mesh_high"]
            
            self.virtual_canvas.create_line(
                sx, sy, ex, ey, 
                fill=fill_color, 
                width=1, 
                tags="mesh_line"
            )
        
        # --- 2. Draw Standard Bones (Foreground, High Glow) ---
        # This reinforces the main skeletal structure over the mesh
        for start_idx, end_idx in SKELETAL_CONNECTIONS:
            sx, sy, _ = get_coords(start_idx)
            ex, ey, _ = get_coords(end_idx)
            
            # Draw High Glow Layer (soft, wider line)
            self.virtual_canvas.create_line(
                sx, sy, ex, ey, 
                fill=COLORS["glow_high"], 
                width=5, 
                capstyle=tk.ROUND,
                tags="bone_glow"
            )
            
            # The white core line has been removed entirely per user request.

        # --- 3. Draw Joints with Glow (Uniform size) ---
        # Draw joints last to ensure they sit on top of all lines
        for idx in range(21):
            x, y, _ = get_coords(idx)
            base_size = 6
            size = base_size # Uniform size for clean look
            
            # Outer glow (soft) - This is now the only indicator for the joint point
            self.virtual_canvas.create_oval(
                x - size, y - size, x + size, y + size, 
                fill=COLORS["glow_high"], outline="", 
                tags=f"joint_glow_{idx}"
            )
            
            # Removed the code section that drew the inner core point.
            
            # Extra pulsating effect for fingertips
            if idx in [4, 8, 12, 16, 20]:
                ring_size = size + 4
                self.virtual_canvas.create_oval(
                    x - ring_size, y - ring_size, x + ring_size, y + ring_size,
                    outline=COLORS["glow_medium"], width=1, 
                    tags=f"fingertip_ring_{idx}"
                )
        
        # --- 4. Animated Energy Arc (Placeholder for animation loop) ---
        t = time.time() * 2
        for i in range(5): # Create arcs around the MCPs
            px, py, _ = get_coords(i * 4) 
            self.virtual_canvas.create_arc(px-30, py-30, px+30, py+30,
                                            start=(t*50+i*60) % 360, extent=40,
                                            outline=COLORS["glow_high"], style="arc", width=2)

    def update_video(self):
        if self.hands is None or not self.cap.isOpened():
            time.sleep(0.1)
            return

        while self.running:
            success, image = self.cap.read()
            if not success:
                time.sleep(0.1)
                continue

            # Flip the image horizontally for a mirror effect
            image = cv2.flip(image, 1)
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # Process the image with MediaPipe
            results = self.hands.process(rgb_image)

            landmarks = None
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Draw landmarks on the live feed
                    mp_drawing.draw_landmarks(
                        rgb_image, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                        mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2, circle_radius=4),
                        mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2)
                    )

                    landmarks = hand_landmarks.landmark

                    # --- INSTANT GESTURE CHECK: Middle finger only triggers immediate shutdown ---
                    # Get hand label for thumb detection
                    hand_label = None
                    if results.multi_handedness:
                        hand_label = results.multi_handedness[0].classification[0].label  # 'Left' or 'Right'

                    def fingers_up(lm, hand_label):
                        """
                        Return [thumb, index, middle, ring, pinky] booleans for whether finger is 'up'.
                        Combines angle-based with y-coordinate for robustness.
                        """
                        tips_ids = [4, 8, 12, 16, 20]
                        pip_ids = [2, 6, 10, 14, 18]  # Thumb uses 2 (MCP)

                        fingers = []

                        # Thumb: Use x-position comparison based on hand chirality
                        if hand_label:
                            thumb_tip_x = lm[4].x
                            thumb_ip_x = lm[3].x
                            if hand_label == 'Right':
                                thumb_up = thumb_tip_x < thumb_ip_x  # Thumb to left (mirrored)
                            else:
                                thumb_up = thumb_tip_x > thumb_ip_x
                        else:
                            # Fallback to angle
                            thumb_up = angle_between_three_points(lm[1], lm[2], lm[4]) > 140
                        fingers.append(not thumb_up)  # Curled if not up

                        # Other fingers: Use angle at PIP > 140 for extended (up)
                        for i, (tip, pip, mcp) in enumerate(zip([8,12,16,20], [6,10,14,18], [5,9,13,17])):
                            angle = angle_between_three_points(lm[mcp], lm[pip], lm[tip])
                            fingers.append(not (angle > 140))  # Curled if angle < 140

                        return fingers  # All curled except middle

                    def is_middle_only_gesture(lm, hand_label):
                        fingers = fingers_up(lm, hand_label)
                        # Middle extended (not curled), others curled
                        return fingers[0] and fingers[1] and not fingers[2] and fingers[3] and fingers[4]  # thumb curled, index curled, middle extended, ring curled, pinky curled

                    def angle_between_three_points(p1, p2, p3):
                        v1 = (p1.x - p2.x, p1.y - p2.y, p1.z - p2.z)
                        v2 = (p3.x - p2.x, p3.y - p2.y, p3.z - p2.z)
                        dot = v1[0]*v2[0] + v1[1]*v2[1] + v1[2]*v2[2]
                        mag1 = math.sqrt(v1[0]**2 + v1[1]**2 + v1[2]**2)
                        mag2 = math.sqrt(v2[0]**2 + v2[1]**2 + v2[2]**2)
                        if mag1 == 0 or mag2 == 0:
                            return 0
                        cos_angle = max(min(dot / (mag1 * mag2), 1.0), -1.0)
                        return math.degrees(math.acos(cos_angle))

                    gesture_active = is_middle_only_gesture(landmarks, hand_label)

                    if gesture_active:
                        self.log("MIDDLE FINGER GESTURE DETECTED: Initiating immediate shutdown!")
                        self.update_status("SHUTDOWN TRIGGERED", "#ff0000")
                        self.after(0, self.initiate_shutdown)
                        break  # Stop processing further frames
                    else:
                        self.gesture_detected = False

                    # Update virtual hand periodically
                    current_time = time.time()
                    if current_time - self.last_virtual_update > 0.05:  # ~20 FPS for virtual hand updates
                        # Call drawing on the main thread
                        self.after(0, self.draw_virtual_hand, landmarks)
                        self.last_virtual_update = current_time

                    # Log hand detection periodically
                    if current_time - getattr(self, 'last_hand_log', 0) > 2:
                        self.log("Hand detected, tracking landmarks.")
                        self.last_hand_log = current_time
            else:
                # Clear virtual hand when no hand detected
                current_time = time.time()
                if current_time - self.last_virtual_update > 0.1:
                    self.after(0, lambda: self.virtual_canvas.delete("all"))
                    self.last_virtual_update = current_time

                # Log no hand periodically
                if current_time - getattr(self, 'last_no_hand_log', 0) > 2:
                    self.log("No hand detected.")
                    self.last_no_hand_log = current_time


            # Convert to PIL Image
            pil_image = Image.fromarray(rgb_image)
            # Resize image to fit the frame if necessary, maintaining aspect ratio is best practice but keeping it simple for Tkinter
            video_frame_width = 500
            video_frame_height = 600
            pil_image = pil_image.resize((video_frame_width, video_frame_height))
            
            tk_image = ImageTk.PhotoImage(pil_image)

            # Update label
            self.video_label.configure(image=tk_image)
            self.video_label.image = tk_image

            # Update status to Monitoring after first frame
            if self.status_label.cget("text") == "Loading AI Model...":
                self.update_status("Monitoring...", "#3b82f6")
                self.status_icon.configure(text_color="#3b82f6", text="●")

            # Update FPS
            self.frame_count += 1
            current_time = time.time()
            if current_time - self.last_fps_time >= 1:
                fps = self.frame_count / (current_time - self.last_fps_time)
                self.fps_label.configure(text=f"{int(fps)} FPS")
                self.frame_count = 0
                self.last_fps_time = current_time

            time.sleep(0.01) # Faster loop for smoother video, relying on sleep to cap FPS if possible

        # Final state if not running (either closed by user or due to shutdown)
        if not self.running:
            self.update_status("Closed/Shutdown Initiated", "#FF00FF")

    def check_cancel_gesture(self):
        # Removed: No countdown, instant trigger only
        pass

    def initiate_shutdown(self):
        def get_shutdown_command():
            platform = sys.platform
            if platform.startswith("win"):
                return 'shutdown /s /t 1'
            elif platform.startswith("linux"):
                return 'shutdown -h now'
            elif platform == "darwin":
                return 'osascript -e \'tell app "System Events" to shut down\''
            else:
                return None

        shutdown_cmd = get_shutdown_command()
        if shutdown_cmd:
            self.log("EXECUTING SHUTDOWN: " + shutdown_cmd)
            try:
                os.system(shutdown_cmd)
            except Exception as e:
                self.log(f"ERROR: Could not execute shutdown: {e}")
        else:
            self.log("ERROR: Unsupported platform for shutdown.")
        self.update_status("SHUTDOWN INITIATED", "#ff0000")
        self.running = False


    def on_closing(self):
        self.running = False
        if self.cap and self.cap.isOpened():
             self.cap.release()
        if self.hands:
            self.hands.close() 
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()
