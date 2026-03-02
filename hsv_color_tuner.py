from picamera2 import Picamera2
import cv2, time
import numpy as np

def nothing(x): pass

# --- PiCamera2 setup ---
print("Initializing Pi Camera...")
picam2 = Picamera2()
picam2.preview_configuration.main.size = (1280, 720)
picam2.preview_configuration.main.format = "RGB888" 
picam2.configure("preview")
picam2.start()
time.sleep(0.3) 

# --- Trackbars window ---
win = "Trackbars"
cv2.namedWindow(win, cv2.WINDOW_NORMAL)
cv2.resizeWindow(win, 900, 400)

# Default Blue values: Hue 95-130
cv2.createTrackbar("Lo H", win, 95,  179, nothing)
cv2.createTrackbar("Lo S", win, 30,  255, nothing)
cv2.createTrackbar("Lo V", win, 30,  255, nothing)
cv2.createTrackbar("Hi H", win, 130, 179, nothing)
cv2.createTrackbar("Hi S", win, 255, 255, nothing)
cv2.createTrackbar("Hi V", win, 255, 255, nothing)

try:
    while True:
        # Capture frame
        frame_rgb = picam2.capture_array()
        
        # Display frame in BGR so colors look natural on screen
        frame_display = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)

        # Convert to HSV for processing (Matching your mapping)
        hsv = cv2.cvtColor(frame_rgb, cv2.COLOR_BGR2HSV)

        # Get trackbar positions
        l_h = cv2.getTrackbarPos("Lo H", win)
        l_s = cv2.getTrackbarPos("Lo S", win)
        l_v = cv2.getTrackbarPos("Lo V", win)
        u_h = cv2.getTrackbarPos("Hi H", win)
        u_s = cv2.getTrackbarPos("Hi S", win)
        u_v = cv2.getTrackbarPos("Hi V", win)

        lower = np.array([l_h, l_s, l_v], dtype=np.uint8)
        upper = np.array([u_h, u_s, u_v], dtype=np.uint8)

        # Create binary mask
        mask = cv2.inRange(hsv, lower, upper)

        # Prepare for display
        mask_3ch = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
        result = cv2.bitwise_and(frame_display, frame_display, mask=mask)

        # --- Dynamic Color Detection Logic ---
        # OpenCV Hue ranges: Blue (~120), Green (~60), Red (0 or 179)
        color_name = "Custom"
        if 90 <= l_h <= 130:
            color_name = "BLUE"
        elif 40 <= l_h <= 85:
            color_name = "GREEN"
        elif 20 <= l_h <= 35:
            color_name = "YELLOW"
        elif (0 <= l_h <= 10) or (160 <= l_h <= 179):
            color_name = "RED"
        elif 11 <= l_h <= 25:
            color_name = "ORANGE"

        # --- Top Right Label ---
        # Draw the detected color name in the top right corner of the result frame
        cv2.putText(result, color_name, (result.shape[1] - 200, 60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)

        # Stack mask and result horizontally and resize for the screen
        stacked = np.hstack((mask_3ch, result))
        view = cv2.resize(stacked, None, fx=0.5, fy=0.5)

        # --- HUD Overlay ---
        txt = f"Lo[{l_h},{l_s},{l_v}] Hi[{u_h},{u_s},{u_v}] (ESC to quit)"
        cv2.rectangle(view, (10, 10), (460, 45), (0,0,0), -1)
        cv2.putText(view, txt, (15, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)

        # Show the final window
        cv2.imshow(win, view)

        # ESC to quit
        if cv2.waitKey(1) & 0xFF == 27:
            print(f"{color_name} Detected: [[{l_h}, {l_s}, {l_v}], [{u_h}, {u_s}, {u_v}]]")
            break

finally:
    # Always stop camera and close windows
    print("\nCleaning up...")
    picam2.stop()
    cv2.destroyAllWindows()
