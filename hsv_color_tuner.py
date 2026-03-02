#git clone https://github.com/Majdawad88/hsv_color_tuner.git

from picamera2 import Picamera2
import cv2, time
import numpy as np

def nothing(x): pass

# --- PiCamera2 setup ---
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

# Defaulting to your successful blue detection values
cv2.createTrackbar("Lo H", win, 95,  179, nothing)
cv2.createTrackbar("Lo S", win, 30,  255, nothing)
cv2.createTrackbar("Lo V", win, 30,  255, nothing)
cv2.createTrackbar("Hi H", win, 130, 179, nothing)
cv2.createTrackbar("Hi S", win, 255, 255, nothing)
cv2.createTrackbar("Hi V", win, 255, 255, nothing)

try:
    while True:
        frame_rgb = picam2.capture_array()
        
        # Display frame in BGR for natural on-screen colors
        frame_display = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
        
        # Using BGR2HSV on RGB frame swaps Red/Blue channels
        hsv = cv2.cvtColor(frame_rgb, cv2.COLOR_BGR2HSV)
        
        l_h = cv2.getTrackbarPos("Lo H", win)
        l_s = cv2.getTrackbarPos("Lo S", win)
        l_v = cv2.getTrackbarPos("Lo V", win)
        u_h = cv2.getTrackbarPos("Hi H", win)
        u_s = cv2.getTrackbarPos("Hi S", win)
        u_v = cv2.getTrackbarPos("Hi V", win)
        
        lower = np.array([l_h, l_s, l_v], dtype=np.uint8)
        upper = np.array([u_h, u_s, u_v], dtype=np.uint8)
        
        mask = cv2.inRange(hsv, lower, upper)
        mask_3ch = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
        result = cv2.bitwise_and(frame_display, frame_display, mask=mask)

        # --- Flipped Mapping Color Prediction ---
        avg_h = (l_h + u_h) / 2
        if 85 <= avg_h < 135:
            detected_color = "BLUE" # Matches your 95-130 success range
        elif 0 <= avg_h < 15 or 165 <= avg_h <= 179:
            detected_color = "CYAN/LIGHT BLUE"
        elif 15 <= avg_h < 35:
            detected_color = "PURPLE"
        elif 35 <= avg_h < 85:
            detected_color = "GREEN"
        elif 135 <= avg_h < 165:
            detected_color = "RED/ORANGE"
        else:
            detected_color = "UNKNOWN"

        # Stack and resize for display
        stacked = np.hstack((mask_3ch, result))
        view = cv2.resize(stacked, None, fx=0.5, fy=0.5)
        
        # --- Green Text Overlay (Updated with Detection Label) ---
        txt = f"Lo[{l_h},{l_s},{l_v}] Hi[{u_h},{u_s},{u_v}] | Detecting: {detected_color}"
        cv2.rectangle(view, (10, 10), (view.shape[1]-10, 40), (0,0,0), -1)
        cv2.putText(view, txt, (15, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
        
        cv2.imshow(win, view)
        
        if cv2.waitKey(1) & 0xFF == 27:
            print(f"Values: [[{l_h}, {l_s}, {l_v}], [{u_h}, {u_s}, {u_v}]] | Color: {detected_color}")
            break
finally:
    picam2.stop()
    cv2.destroyAllWindows()
