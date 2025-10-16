import sys
import serial
import threading
import time
import winsound  # For Windows sound
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QVBoxLayout, QPushButton,
                             QHBoxLayout, QSlider, QLineEdit, QFrame, QGridLayout)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QPainter, QColor
from playsound import playsound  # Import playsound


# Uncomment the following if you have qt_material installed
# import qt_material


class InfusionPumpGUI(QWidget):
    update_signal = pyqtSignal(str, str, str)

    def __init__(self):
        super().__init__()
        self.serial_port = None
        self.monitoring = False
        self.battery_level = 100
        self.pump_running = False
        self.blood_detected = False
        self.alarm_active = False
        self.alarm_timer = None
        self.occlusion_detected = False  # Track occlusion state

        # GUI Setup
        self.setWindowTitle("Infusion Pump Monitor")
        self.setGeometry(100, 100, 800, 300)

        # Create main horizontal layout to split left and right panels
        main_layout = QHBoxLayout()

        # Create left panel for displays and alarms
        left_panel = QFrame()
        left_panel.setFrameShape(QFrame.Box)
        left_panel.setLineWidth(2)
        left_layout = QVBoxLayout()
        left_panel.setLayout(left_layout)

        # Create right panel for controls and buttons
        right_panel = QFrame()
        right_panel.setFrameShape(QFrame.Box)
        right_panel.setLineWidth(2)
        right_layout = QVBoxLayout()
        right_panel.setLayout(right_layout)

        # Battery section at top
        battery_layout = QHBoxLayout()
        self.battery_label = QLabel("Battery: 100%", self)
        self.battery_label.setFont(QFont("Arial", 14))
        self.battery_label.setAlignment(Qt.AlignRight)

        # Battery UI
        self.battery_display = QLabel(self)
        self.battery_display.setFixedSize(60, 20)
        self.update_battery_display(100)

        battery_layout.addStretch()
        battery_layout.addWidget(self.battery_label)
        battery_layout.addWidget(self.battery_display)

        # Connection Status
        self.connection_label = QLabel("Serial Connection: Disconnected", self)
        self.connection_label.setFont(QFont("Arial", 12))
        self.connection_label.setStyleSheet("color: red;")

        # LEFT PANEL COMPONENTS
        # Digital Flow Rate Display
        flow_label = QLabel("Flow Rate (mL/min):", self)
        flow_label.setFont(QFont("Arial", 15))
        self.flow_display = QLabel("00.0", self)
        self.flow_display.setFixedWidth(400)
        self.flow_display.setFixedHeight(200)
        self.flow_display.setFont(QFont("Arial", 80, QFont.Weight.Bold))
        self.flow_display.setStyleSheet("background-color: black; color: green; border: 3px solid gray; padding: 10px;")
        self.flow_display.setAlignment(Qt.AlignCenter)

        # Status Display
        status_label = QLabel("Status:", self)
        status_label.setFont(QFont("Arial", 18))
        self.status_display = QLabel("NORMAL", self)
        self.status_display.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        self.status_display.setAlignment(Qt.AlignCenter)
        self.status_display.setStyleSheet("color: green; border: 2px solid gray; padding: 5px;")

        # Pump Power Display
        self.power_display = QLabel("Pump Power: 0", self)
        self.power_display.setFont(QFont("Arial", 18))
        self.power_display.setAlignment(Qt.AlignCenter)

        # Mode Display
        self.mode_display = QLabel("Mode: AUTO", self)
        self.mode_display.setFont(QFont("Arial", 16))
        self.mode_display.setAlignment(Qt.AlignCenter)

        # Warning Label
        self.warning_label = QLabel("", self)
        self.warning_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.warning_label.setStyleSheet("color: red;")
        self.warning_label.setAlignment(Qt.AlignCenter)

        # Add components to left panel
        left_layout.addWidget(self.connection_label)
        left_layout.addWidget(flow_label)
        left_layout.addWidget(self.flow_display)
        left_layout.addWidget(status_label)
        left_layout.addWidget(self.status_display)
        left_layout.addWidget(self.power_display)
        left_layout.addWidget(self.mode_display)
        left_layout.addWidget(self.warning_label)
        left_layout.addStretch()

        # RIGHT PANEL COMPONENTS
        # Buttons
        right_layout.addLayout(battery_layout)
        right_layout.addSpacing(20)

        # Connection buttons
        self.start_button = QPushButton("Connect & Start Monitoring", self)
        self.start_button.setFont(QFont("Arial", 14))
        self.start_button.clicked.connect(self.start_monitoring)
        self.start_button.setMinimumHeight(50)

        self.stop_button = QPushButton("Stop Monitoring", self)
        self.stop_button.setFont(QFont("Arial", 14))
        self.stop_button.clicked.connect(self.stop_monitoring)
        self.stop_button.setEnabled(False)
        self.stop_button.setMinimumHeight(50)

        # Silence Alarm button
        self.silence_alarm_button = QPushButton("Silence Alarm", self)
        self.silence_alarm_button.setFont(QFont("Arial", 14))
        self.silence_alarm_button.clicked.connect(self.silence_alarm)
        self.silence_alarm_button.setEnabled(False)
        self.silence_alarm_button.setMinimumHeight(50)
        self.silence_alarm_button.setStyleSheet("background-color: #ffcccc;")

        # Pump control section
        control_section = QFrame()
        control_layout = QVBoxLayout()
        control_section.setLayout(control_layout)

        control_title = QLabel("Pump Control", self)
        control_title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        control_title.setAlignment(Qt.AlignCenter)

        # Pump Power Control
        slider_layout = QGridLayout()
        slider_label = QLabel("Power Level:", self)
        slider_label.setFont(QFont("Arial", 14))

        self.power_slider = QSlider(Qt.Horizontal)
        self.power_slider.setRange(0, 255)
        self.power_slider.setValue(180)  # Default value from Arduino code
        self.power_slider.setEnabled(False)
        self.power_slider.valueChanged.connect(self.set_pump_power)
        self.power_slider.setMinimumHeight(40)

        self.power_input = QLineEdit()
        self.power_input.setPlaceholderText("Power (0-255)")
        self.power_input.setEnabled(False)
        self.power_input.returnPressed.connect(self.set_pump_power_from_input)
        self.power_input.setMaximumWidth(150)

        slider_layout.addWidget(slider_label, 0, 0)
        slider_layout.addWidget(self.power_slider, 0, 1)
        slider_layout.addWidget(self.power_input, 1, 1, Qt.AlignRight)

        # Auto mode button
        self.auto_mode_button = QPushButton("Auto Mode", self)
        self.auto_mode_button.setFont(QFont("Arial", 14))
        self.auto_mode_button.clicked.connect(self.set_auto_mode)
        self.auto_mode_button.setEnabled(False)
        self.auto_mode_button.setMinimumHeight(50)

        # Add control components to the control section
        control_layout.addWidget(control_title)
        control_layout.addLayout(slider_layout)
        control_layout.addWidget(self.auto_mode_button)

        # Add components to right panel
        right_layout.addWidget(self.start_button)
        right_layout.addWidget(self.stop_button)
        right_layout.addWidget(self.silence_alarm_button)
        right_layout.addSpacing(20)
        right_layout.addWidget(control_section)
        right_layout.addStretch()

        # Add panels to main layout
        main_layout.addWidget(left_panel, 1)  # 1:1 ratio
        main_layout.addWidget(right_panel, 1)

        self.setLayout(main_layout)

        # Timer for battery simulation
        self.battery_timer = QTimer()
        self.battery_timer.timeout.connect(self.simulate_battery_drain)
        self.battery_timer.start(10000)  # Update every 10 seconds

        # Timer for LCD updates (similar to Arduino's LCD refresh)
        self.lcd_timer = QTimer()
        self.lcd_timer.timeout.connect(self.update_displays)
        self.lcd_timer.start(1000)  # Update every second

        # Timer for alarm sounds
        self.alarm_sound_timer = QTimer()
        self.alarm_sound_timer.timeout.connect(self.play_alarm_sound)

        # Signal connection
        self.update_signal.connect(self.update_display)

        # Preload the sound file
        self.blood_leakage_sound = "blood_leakage.mp3"  # Replace with your sound file

    def start_monitoring(self):
        try:
            # Try to connect to Arduino on COM ports
            ports = ['COM3', 'COM4', 'COM5', 'COM6', '/dev/ttyUSB0', '/dev/ttyACM0']
            for port in ports:
                try:
                    self.serial_port = serial.Serial(port, 9600, timeout=1)
                    self.connection_label.setText(f"Serial Connection: Connected to {port}")
                    self.connection_label.setStyleSheet("color: green;")
                    break
                except:
                    continue

            if self.serial_port is None:
                self.warning_label.setText("Failed to connect to Arduino. Check connections.")
                self.trigger_alarm("connection_failure")
                return

            self.monitoring = True
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.power_slider.setEnabled(True)
            self.power_input.setEnabled(True)
            self.auto_mode_button.setEnabled(True)

            # Start the monitoring thread
            self.monitor_thread = threading.Thread(target=self.read_serial_data)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()

        except Exception as e:
            self.warning_label.setText(f"Error: {str(e)}")
            self.trigger_alarm("connection_failure")

    def stop_monitoring(self):
        self.monitoring = False
        self.stop_alarm()
        if self.serial_port:
            self.serial_port.close()
            self.serial_port = None

        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.power_slider.setEnabled(False)
        self.power_input.setEnabled(False)
        self.auto_mode_button.setEnabled(False)
        self.silence_alarm_button.setEnabled(False)
        self.connection_label.setText("Serial Connection: Disconnected")
        self.connection_label.setStyleSheet("color: red;")
        self.occlusion_detected = False  # Reset occlusion state


    def read_serial_data(self):
        while self.monitoring and self.serial_port:
            try:
                if self.serial_port.in_waiting:
                    line = self.serial_port.readline().decode('utf-8').strip()
                    if line:
                        # Check if this is a status line with the expected format
                        if "Status:" in line and "|" in line:
                            parts = line.split('|')
                            if len(parts) >= 3:
                                status = parts[0].strip().replace("Status: ", "")
                                power = parts[1].strip().replace("Pump Speed: ", "")
                                flow = parts[2].strip().replace("Flow Rate: ", "").split(" ")[0]
                                self.update_signal.emit(status, power, flow)
                        # Check for blood leakage alert
                        elif "BLOOD LEAKAGE DETECTED" in line:
                            self.blood_detected = True
                            self.update_signal.emit("BLOOD LEAKAGE", "0", "0.0")
                            self.trigger_alarm("blood_leakage")
                        # Check for mode changes
                        elif "Switched to AUTO mode" in line:
                            self.update_mode_display("AUTO")
                        elif "Manual Mode: Speed Set To" in line:
                            self.update_mode_display("MANUAL")
            except Exception as e:
                self.warning_label.setText(f"Serial Error: {str(e)}")
                self.trigger_alarm("communication_error")
                break
            time.sleep(0.1)

    def update_mode_display(self, mode):
        # This function is called from the serial thread, so we need to be thread-safe
        self.mode_display.setText(f"Mode: {mode}")
        if mode == "AUTO":
            self.mode_display.setStyleSheet("color: blue;")
        else:
            self.mode_display.setStyleSheet("color: white;")

    def update_display(self, status, power, flow):
        try:
            # Update flow rate display
            try:
                flow_value = float(flow)
                if 0 <= flow_value < 500:  # Valid range check as in Arduino code
                    self.flow_display.setText(f"{flow_value:.1f}")
                else:
                    self.flow_display.setText("----")
            except ValueError:
                self.flow_display.setText("----")

            # Update status display
            if "BLOOD LEAKAGE" in status:
                self.status_display.setText("BLOOD LEAKAGE")
                self.status_display.setStyleSheet("color: red; border: 2px solid red; padding: 5px;")
                self.warning_label.setText("WARNING: Blood leakage detected!")
                self.blood_detected = True
                self.trigger_alarm("blood_leakage")
                self.silence_alarm_button.setEnabled(True)
            elif self.occlusion_detected: #added occlusin detection
                self.status_display.setText("OCCLUSION")
                self.status_display.setStyleSheet("color: red; border: 2px solid red; padding: 5px;")
                self.warning_label.setText("WARNING: Occlusion detected!")
            else:
                if not self.blood_detected:  # Only update if blood not detected (similar to Arduino logic)
                    self.status_display.setText(status)
                    self.status_display.setStyleSheet("color: green; border: 2px solid gray; padding: 5px;")
                    self.warning_label.setText("")


            # Update power display
            try:
                power_value = int(power)
                if 0 <= power_value <= 255:  # Valid range check
                    self.power_display.setText(f"Pump Power: {power_value}")
                else:
                    self.power_display.setText("Pump Power: ---")
            except ValueError:
                self.power_display.setText("Pump Power: ---")

            # Update slider if in manual mode
            if "MANUAL" in status and not self.power_slider.isSliderDown():
                try:
                    self.power_slider.setValue(int(power))
                except ValueError:
                    pass

             # Check for low flow rate / occlusion alert
            try:
                flow_value = float(flow)
                if flow_value <= 1.0 and int(power) > 50:
                    # Occlusion detected
                    self.occlusion_detected = True
                    self.warning_label.setText("WARNING: Occlusion detected!")
                    self.trigger_alarm("occlusion")
                    self.silence_alarm_button.setEnabled(True)
                elif flow_value > 1.0:
                    # Reset occlusion if flow is back to normal
                    self.occlusion_detected = False

            except ValueError:
                pass


        except Exception as e:
            self.warning_label.setText(f"Display Update Error: {str(e)}")

    def update_displays(self):
        """Simulates the Arduino's LCD refresh functionality"""
        if not self.monitoring:
            return

        # Check for low battery alert
        if self.battery_level < 10:
            self.trigger_alarm("low_battery")

        # Nothing specific to update here as our GUI refreshes when data arrives
        # But this mimics the LCD refresh cycle in the Arduino code

    def set_pump_power(self):
        if self.serial_port and self.serial_port.is_open:
            power = self.power_slider.value()
            self.serial_port.write(f"{power}\n".encode())
            self.power_display.setText(f"Pump Power: {power}")
            self.update_mode_display("MANUAL")
            # Reset occlusion when power is manually set
            self.occlusion_detected = False

    def set_pump_power_from_input(self):
        try:
            power = int(self.power_input.text())
            if 0 <= power <= 255:
                self.power_slider.setValue(power)
                if self.serial_port and self.serial_port.is_open:
                    self.serial_port.write(f"{power}\n".encode())
                    self.power_display.setText(f"Pump Power: {power}")
                    self.update_mode_display("MANUAL")
                    # Reset occlusion when power is manually set
                    self.occlusion_detected = False
            else:
                self.warning_label.setText("Power must be between 0 and 255")
                self.trigger_alarm("input_error")
        except ValueError:
            self.warning_label.setText("Invalid power value")
            self.trigger_alarm("input_error")

    def set_auto_mode(self):
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.write(b"AUTO\n")
            self.update_mode_display("AUTO")
            self.warning_label.setText("Switched to automatic mode")
            # Reset blood detection and occlusion when switching to auto mode
            self.blood_detected = False
            self.occlusion_detected = False  # Reset occlusion
            self.status_display.setText("NORMAL")
            self.status_display.setStyleSheet("color: green; border: 2px solid gray; padding: 5px;")
            self.stop_alarm()
            self.silence_alarm_button.setEnabled(False)

    def simulate_battery_drain(self):
        if self.monitoring:
            # Simulate battery drain when monitoring
            self.battery_level = max(0, self.battery_level - 1)
        else:
            # Simulate slow battery drain when idle
            self.battery_level = max(0, self.battery_level - 0.2)

        # Update battery display
        self.battery_label.setText(f"Battery: {int(self.battery_level)}%")
        self.update_battery_display(int(self.battery_level))

        # Low battery warning
        if self.battery_level < 20:
            self.battery_label.setStyleSheet("color: red;")
            if self.battery_level < 10:
                self.warning_label.setText("WARNING: Battery critically low!")
                self.trigger_alarm("low_battery")
                self.silence_alarm_button.setEnabled(True)
        else:
            self.battery_label.setStyleSheet("color: white;")

    def update_battery_display(self, level):
        """Draw battery level indicator."""
        pixmap = QPixmap(60, 20)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)

        # Draw battery outline
        painter.setPen(QColor(150, 150, 150))
        painter.drawRect(0, 0, 60, 20)

        # Draw battery level
        if level > 30:
            painter.setBrush(QColor(0, 255, 0))
        elif level > 10:
            painter.setBrush(QColor(255, 165, 0))
        else:
            painter.setBrush(QColor(255, 0, 0))

        painter.drawRect(2, 2, int(56 * (level / 100)), 16)
        painter.end()
        self.battery_display.setPixmap(pixmap)

    def trigger_alarm(self, alarm_type):
        """Start alarm sound based on the type of alarm"""
        if not self.alarm_active:
            self.alarm_active = True
            self.silence_alarm_button.setEnabled(True)

            # Flash UI element based on alarm type
            if alarm_type == "blood_leakage":
                self.status_display.setStyleSheet(
                    "color: white; background-color: red; border: 2px solid red; padding: 5px;")
                # Play sound for blood leakage immediately
                try:
                    playsound(self.blood_leakage_sound, block=False)  # Play asynchronously
                except Exception as e:
                    print(f"Error playing sound: {e}")

            elif alarm_type == "low_battery":
                self.battery_label.setStyleSheet("color: white; background-color: red;")
            elif alarm_type == "occlusion":  # Occlusion alarm
                self.status_display.setStyleSheet(
                    "color: white; background-color: red; border: 2px solid red; padding: 5px;")

            # Start sound timer (for beeps)
            self.alarm_sound_timer.start(500)  # Sound every 500ms

    def play_alarm_sound(self):
        """Play sound for active alarm"""
        try:
            # Different frequencies for different types of alarms
            if "BLOOD LEAKAGE" in self.status_display.text():
                # High priority alarm - blood leakage (higher pitch, longer)
                #winsound.Beep(1500, 200) #removed to avoid overlap
                pass # The blood leakage sound is already handled in trigger_alarm
            elif "OCCLUSION" in self.status_display.text():  # Occlusion alarm
                winsound.Beep(1350, 200) # Different frequency for occlusion
            elif "Low flow" in self.warning_label.text():
                # Medium priority - flow issue
                winsound.Beep(1200, 200)
            elif "Battery" in self.warning_label.text():
                # Lower priority - battery warning
                winsound.Beep(900, 200)
            else:
                # Generic alarm
                winsound.Beep(1000, 200)
        except Exception as e:
            print(f"Error in play_alarm_sound: {e}")
            # Fallback for platforms without winsound
            print("BEEP! Alarm activated")

    def stop_alarm(self):
        """Stop the alarm sound"""
        self.alarm_active = False
        self.alarm_sound_timer.stop()
        # Reset flashing elements
        if "BLOOD LEAKAGE" not in self.status_display.text() and not self.occlusion_detected:
             self.status_display.setStyleSheet("color: green; border: 2px solid gray; padding: 5px;")
        if self.battery_level < 20:
            self.battery_label.setStyleSheet("color: red;")
        else:
            self.battery_label.setStyleSheet("color: white;")

    def silence_alarm(self):
        """Silence the current alarm"""
        self.stop_alarm()
        self.silence_alarm_button.setEnabled(False)
        self.warning_label.setText(self.warning_label.text() + " (Alarm silenced)")

    def closeEvent(self, event):
        self.monitoring = False
        self.stop_alarm()
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        event.accept()


# Run the Application
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Uncomment if you have qt_material installed
    # qt_material.apply_stylesheet(app, theme="dark_blue.xml")

    window = InfusionPumpGUI()
    window.show()
    sys.exit(app.exec_())