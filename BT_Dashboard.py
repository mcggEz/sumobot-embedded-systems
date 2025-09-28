"""
Windows dashboard: reads PS5 DualSense (pygame) or keyboard and sends
throttle/turn/brake/rotate/gear over Bluetooth Serial to ESP32.

Protocol (ASCII, newline-terminated):
  F <throttle> <turn> <brake> <rotate> <gear_boost>

Usage:
  python BT_Dashboard.py --com COM7 --baud 115200 --dashboard
  python BT_Dashboard.py --com COM7 --keyboard --dashboard
  python BT_Dashboard.py --com COM7 --baud 115200 --pins 5,6,9,10 --dashboard
"""

import argparse
import logging
import threading
import time
from typing import Optional
import os
import platform
import threading

# Pygame for controller
try:
    import pygame  # type: ignore
    HAS_PYGAME = True
except Exception:
    HAS_PYGAME = False

# Tkinter for dashboard
try:
    import tkinter as tk  # type: ignore
except Exception:
    tk = None  # type: ignore

# PySerial for Bluetooth COM
try:
    import serial  # type: ignore
    from serial.tools import list_ports  # type: ignore
    HAS_SERIAL = True
except Exception:
    HAS_SERIAL = False


def setup_logging(level: str = "INFO") -> None:
    logging.basicConfig(level=getattr(logging, level.upper(), logging.INFO),
                        format="%(asctime)s %(levelname)s %(message)s")


class ControllerState:
    def __init__(self) -> None:
        self.throttle: float = 0.0
        self.turn: float = 0.0
        self.deadman_pressed: bool = False
        self.brake_pressed: bool = False  # R2 button for brake
        self.rotate_pressed: bool = False  # X button for rotate
        self.gear_boost: bool = False  # Square button for speed boost
        self.last_event_time: float = time.time()


class RuntimeStatus:
    def __init__(self, com: str, baud: int) -> None:
        self.controller_connected: bool = False
        self.serial_connected: bool = False
        self.com: str = com
        self.baud: int = baud
        self._lock = threading.Lock()
        self.available_ports: list[str] = []

    def set_controller(self, connected: bool) -> None:
        with self._lock:
            self.controller_connected = connected

    def set_serial(self, connected: bool) -> None:
        with self._lock:
            self.serial_connected = connected

    def snapshot(self) -> tuple[bool, bool, str, int]:
        with self._lock:
            return self.controller_connected, self.serial_connected, self.com, self.baud

    def update_ports(self) -> list[str]:
        ports: list[str] = []
        try:
            if HAS_SERIAL:
                ports = [p.device for p in list_ports.comports()]
        except Exception:
            ports = []
        with self._lock:
            self.available_ports = ports
        return ports

    def find_esp32_port(self) -> Optional[str]:
        """Auto-detect ESP32 Bluetooth COM port"""
        try:
            if not HAS_SERIAL:
                return None
            for port in list_ports.comports():
                # Look for ESP32 in description or try to connect
                if "ESP32" in str(port.description).upper() or "SUMOBOT" in str(port.description).upper():
                    return port.device
                # Also try to connect and test
                try:
                    test_ser = serial.Serial(port.device, 115200, timeout=0.5)
                    time.sleep(0.2)
                    test_ser.write(b"TEST\n")
                    time.sleep(0.1)
                    if test_ser.in_waiting > 0:
                        response = test_ser.read(test_ser.in_waiting).decode('utf-8', errors='ignore')
                        if "ESP32" in response or "Bluetooth" in response:
                            test_ser.close()
                            return port.device
                    test_ser.close()
                except Exception:
                    continue
        except Exception:
            pass
        return None

    def get_ports(self) -> list[str]:
        with self._lock:
            return list(self.available_ports)


def _apply_deadzone(value: float, dz: float) -> float:
    return 0.0 if abs(value) < dz else value


def _expo(value: float, factor: float) -> float:
    if factor <= 0:
        return value
    return (1 - factor) * value + factor * (value * abs(value))


class KeyboardReader(threading.Thread):
    def __init__(self, on_state, status: RuntimeStatus) -> None:
        super().__init__(daemon=True)
        self.on_state = on_state
        self.state = ControllerState()
        self._stop = threading.Event()
        self.status = status

    def stop(self) -> None:
        self._stop.set()

    def run(self) -> None:
        if tk is None:
            logging.error("Tkinter not available for keyboard fallback")
            return
        root = tk.Tk()
        root.title("Keyboard (W/S throttle, A/D turn, Space deadman, B brake, X rotate, Q quit)")
        root.geometry("400x100")
        root.bind("<KeyPress>", self._on_press)
        root.bind("<KeyRelease>", self._on_release)

        def tick():
            if self._stop.is_set():
                root.quit()
                return
            self.state.last_event_time = time.time()
            self.on_state(self.state)
            root.after(20, tick)

        root.after(20, tick)
        root.mainloop()

    def _on_press(self, event):
        key = event.keysym.lower()
        if key == "w":
            self.state.throttle = 1.0
        elif key == "s":
            self.state.throttle = -1.0
        elif key == "a":
            self.state.turn = -1.0
        elif key == "d":
            self.state.turn = 1.0
        elif key == "space":
            self.state.deadman_pressed = True
        elif key == "b":
            self.state.brake_pressed = True
        elif key == "x":
            self.state.rotate_pressed = True
        elif key == "q":
            self._stop.set()

    def _on_release(self, event):
        key = event.keysym.lower()
        if key in ("w", "s"):
            self.state.throttle = 0.0
        elif key in ("a", "d"):
            self.state.turn = 0.0
        elif key == "space":
            self.state.deadman_pressed = False
        elif key == "b":
            self.state.brake_pressed = False
        elif key == "x":
            self.state.rotate_pressed = False


class PygameReader(threading.Thread):
    def __init__(self, on_state, status: RuntimeStatus, axis_throttle: int = 1, axis_turn: int = 0, deadzone: float = 0.08, expo: float = 0.3) -> None:
        super().__init__(daemon=True)
        self.on_state = on_state
        self.state = ControllerState()
        self._stop = threading.Event()
        self.joy = None
        self.axis_throttle = axis_throttle
        self.axis_turn = axis_turn
        self.deadzone = deadzone
        self.expo = expo
        self.status = status

    def stop(self) -> None:
        self._stop.set()

    def _connect(self) -> bool:
        pygame.joystick.quit()
        pygame.joystick.init()
        n = pygame.joystick.get_count()
        
        logging.info("Found %d joystick(s)", n)
        if n == 0:
            logging.warning("No joysticks found via pygame; is the controller connected?")
            logging.warning("Try: 1) Reconnect PS5 controller 2) Use --keyboard flag 3) Check Windows Game Controllers")
            return False
        
        # List all available controllers
        for i in range(n):
            try:
                joy = pygame.joystick.Joystick(i)
                name = joy.get_name()
                logging.info("Found joystick %d: '%s'", i, name)
            except Exception as e:
                logging.info("Found joystick %d: <error: %s>", i, e)
        
        # Try to find DualSense or any controller
        chosen = 0
        for i in range(n):
            try:
                joy = pygame.joystick.Joystick(i)
                name = joy.get_name()
                if "DualSense" in name or "Wireless Controller" in name or "Controller" in name:
                    chosen = i
                    logging.info("Selected controller: '%s'", name)
                    break
            except Exception:
                continue
        
        # If no specific controller found, use the first one
        if chosen == 0 and n > 0:
            logging.info("Using first available controller")
        
        try:
            self.joy = pygame.joystick.Joystick(chosen)
            self.joy.init()
            logging.info("Connected: '%s' axes=%d buttons=%d hats=%d", 
                       self.joy.get_name(), 
                       self.joy.get_numaxes(), 
                       self.joy.get_numbuttons(), 
                       self.joy.get_numhats())
            self.status.set_controller(True)
            return True
        except Exception as e:
            logging.error("Failed to initialize controller: %s", e)
            return False

    def run(self) -> None:
        if not HAS_PYGAME:
            logging.error("pygame not available. pip install pygame")
            return
        if platform.system() == 'Linux' and not os.environ.get('DISPLAY'):
            os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
        pygame.init()
        try:
            pygame.display.init()
            try:
                pygame.display.set_mode((1, 1))
            except Exception:
                pass
        except Exception:
            pass
        
        logging.info("Pygame initialized. Looking for controllers...")
        while not self._stop.is_set():
            if self.joy is None or not self.joy.get_init():
                if not self._connect():
                    time.sleep(1.0)
                    continue
            for event in pygame.event.get():
                pass
            try:
                ax_th = self.axis_throttle
                ax_tr = self.axis_turn
                raw_throttle = -float(self.joy.get_axis(ax_th)) if self.joy.get_numaxes() > ax_th else 0.0
                raw_turn = float(self.joy.get_axis(ax_tr)) if self.joy.get_numaxes() > ax_tr else 0.0
                throttle = _expo(_apply_deadzone(raw_throttle, self.deadzone), self.expo)
                turn = _expo(_apply_deadzone(raw_turn, self.deadzone), self.expo)
                btn0 = self.joy.get_button(0) if self.joy.get_numbuttons() > 0 else 0  # X button
                btn1 = self.joy.get_button(1) if self.joy.get_numbuttons() > 1 else 0  # Circle button
                btn2 = self.joy.get_button(2) if self.joy.get_numbuttons() > 2 else 0  # Square button
                btn3 = self.joy.get_button(3) if self.joy.get_numbuttons() > 3 else 0  # Triangle button
                # R2 trigger (axis 5, value > 0.5 means pressed)
                r2_trigger = self.joy.get_axis(5) if self.joy.get_numaxes() > 5 else 0.0
                
                # Map buttons: X=deadman, Square=gear boost, R2=brake, X=rotate
                deadman = bool(btn0)
                brake = r2_trigger > 0.5
                gear_boost = bool(btn2)  # Square button for gear boost
                rotate = bool(btn0)  # X button for rotate
                
                self.state.throttle = throttle
                self.state.turn = turn
                self.state.deadman_pressed = deadman
                self.state.brake_pressed = brake
                self.state.rotate_pressed = rotate
                self.state.gear_boost = gear_boost
                self.state.last_event_time = time.time()
                self.on_state(self.state)
            except Exception as e:
                logging.warning("pygame read error: %s", e)
                self.joy = None
                self.status.set_controller(False)
            # No delay for maximum responsiveness


class SerialSender(threading.Thread):
    def __init__(self, port: str, baud: int, get_state_callable, status: RuntimeStatus) -> None:
        super().__init__(daemon=True)
        self.port = port
        self.baud = baud
        self.get_state = get_state_callable
        self._stop = threading.Event()
        self.ser: Optional[serial.Serial] = None if HAS_SERIAL else None  # type: ignore
        self.status = status

    def stop(self) -> None:
        self._stop.set()
        try:
            if self.ser and self.ser.is_open:
                self.ser.close()
        except Exception:
            pass

    def run(self) -> None:
        if not HAS_SERIAL:
            logging.error("pyserial not installed. pip install pyserial")
            return
        while not self._stop.is_set():
            try:
                if self.ser is None or not self.ser.is_open:
                    self.ser = serial.Serial(self.port, self.baud, timeout=0.1)
                    logging.info("Serial opened: %s @ %d", self.port, self.baud)
                    self.status.set_serial(True)
                state = self.get_state()
                if state:
                    line = f"F {state.throttle:.3f} {state.turn:.3f} {int(state.brake_pressed)} {int(state.rotate_pressed)} {int(state.gear_boost)}\n"
                    self.ser.write(line.encode('ascii'))
            except Exception as e:
                logging.warning("Serial error: %s", e)
                try:
                    if self.ser:
                        self.ser.close()
                except Exception:
                    pass
                self.ser = None
                self.status.set_serial(False)
                time.sleep(1.0)
            # No delay for maximum responsiveness


class Dashboard:
    def __init__(self, status: RuntimeStatus, pins: tuple[int, int, int, int]) -> None:
        if tk is None:
            raise RuntimeError("Tkinter not available for dashboard")
        self.root = tk.Tk()
        self.root.title("ESP32 Sumobot Dashboard")
        self.root.geometry("700x420")
        self.root.configure(bg="#1e3a8a")
        from tkinter import ttk
        self.ttk = ttk
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except Exception:
            pass
        style.configure('TFrame', background='#1e3a8a')
        style.configure('TLabel', background='#1e3a8a', foreground='#ffffff', font=('Segoe UI', 10))
        style.configure('Header.TLabel', font=('Segoe UI Semibold', 12), foreground='#60a5fa')
        style.configure('StatusGood.TLabel', foreground='#10b981')
        style.configure('StatusBad.TLabel', foreground='#ef4444')
        style.configure('StatusWarn.TLabel', foreground='#f59e0b')
        self.status = status
        self.pins = pins
        self._build_ui()
        self._queue = []
        self._lock = threading.Lock()

    def _build_ui(self) -> None:
        main = self.ttk.Frame(self.root, padding=16, style='TFrame')
        main.pack(fill=tk.BOTH, expand=True)
        self.ttk.Label(main, text="Connections", style='Header.TLabel').pack(anchor=tk.W)
        conn = self.ttk.Frame(main, padding=(0, 8, 0, 8))
        conn.pack(fill=tk.X)
        self.controller_lbl = self.ttk.Label(conn, text="Controller: Waiting", style='StatusWarn.TLabel')
        self.controller_lbl.pack(anchor=tk.W)
        self.serial_lbl = self.ttk.Label(conn, text="ESP32: Disconnected", style='StatusBad.TLabel')
        self.serial_lbl.pack(anchor=tk.W)
        self.port_lbl = self.ttk.Label(conn, text="Port: N/A")
        self.port_lbl.pack(anchor=tk.W)
        self.ports_avail_lbl = self.ttk.Label(conn, text="Available COM ports: -")
        self.ports_avail_lbl.pack(anchor=tk.W)

        self.ttk.Label(main, text="Inputs", style='Header.TLabel').pack(anchor=tk.W)
        self.age_var = tk.StringVar(value="Last event: N/A")
        self.ttk.Label(main, textvariable=self.age_var).pack(anchor=tk.W)
        self.ttk.Label(main, text="Throttle").pack(anchor=tk.W, pady=(12, 0))
        self.throttle_bar = self.ttk.Progressbar(main, orient="horizontal", length=400, mode="determinate", maximum=100)
        self.throttle_bar.pack(anchor=tk.W)
        self.ttk.Label(main, text="Turn").pack(anchor=tk.W, pady=(12, 0))
        self.turn_bar = self.ttk.Progressbar(main, orient="horizontal", length=400, mode="determinate", maximum=100)
        self.turn_bar.pack(anchor=tk.W)
        self.gear_var = tk.StringVar(value="Gear: Normal")
        self.movement_var = tk.StringVar(value="Movement: Stopped")
        self.brake_var = tk.StringVar(value="Brake: Off")
        self.rotate_var = tk.StringVar(value="Rotate: Off")
        self.ttk.Label(main, textvariable=self.gear_var).pack(anchor=tk.W, pady=(12, 0))
        self.ttk.Label(main, textvariable=self.movement_var).pack(anchor=tk.W)
        self.ttk.Label(main, textvariable=self.brake_var).pack(anchor=tk.W)
        self.ttk.Label(main, textvariable=self.rotate_var).pack(anchor=tk.W)
        self.ttk.Label(main, text="Motors", style='Header.TLabel').pack(anchor=tk.W, pady=(12, 0))
        self.canvas = tk.Canvas(main, width=640, height=80, bg='#1e3a8a', highlightthickness=0)
        self.canvas.pack(anchor=tk.W)
        # Bars for left/right speed
        self.left_rect = self.canvas.create_rectangle(20, 20, 20, 50, fill='#2e7d32', outline='')
        self.right_rect = self.canvas.create_rectangle(20, 55, 20, 85, fill='#2e7d32', outline='')
        self.canvas.create_text(10, 35, text='L', anchor='w', fill='#ffffff', font=('Segoe UI', 10))
        self.canvas.create_text(10, 70, text='R', anchor='w', fill='#ffffff', font=('Segoe UI', 10))

        pins_text = f"ESP32 Pins L({self.pins[0]},{self.pins[1]}) R({self.pins[2]},{self.pins[3]})"
        self.ttk.Label(main, text=pins_text).pack(anchor=tk.W, pady=(8, 0))

        self.ttk.Label(main, text="Logs", style='Header.TLabel').pack(anchor=tk.W, pady=(12, 0))
        self.log_text = tk.Text(main, height=8, width=80, state=tk.DISABLED, bg='#111111', fg='#e0e0e0')
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def push(self, state: ControllerState) -> None:
        with self._lock:
            self._queue.append(state)

    def log(self, message: str) -> None:
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)

    def _tick(self) -> None:
        with self._lock:
            state = self._queue[-1] if self._queue else None
            self._queue.clear()
        # Update connection statuses
        ctrl_ok, ser_ok, com, baud = self.status.snapshot()
        # Periodically refresh available ports
        ports = self.status.update_ports()
        self.controller_lbl.configure(text=f"Controller: {'Connected' if ctrl_ok else 'Waiting'}",
                                      style='StatusGood.TLabel' if ctrl_ok else 'StatusWarn.TLabel')
        self.serial_lbl.configure(text=f"ESP32: {'Connected' if ser_ok else 'Disconnected'}",
                                  style='StatusGood.TLabel' if ser_ok else 'StatusBad.TLabel')
        self.port_lbl.configure(text=f"Port: {com} @ {baud}")
        self.ports_avail_lbl.configure(text=f"Available COM ports: {', '.join(ports) if ports else '-'}")

        if state is not None:
            age_ms = int((time.time() - state.last_event_time) * 1000)
            self.age_var.set(f"Last event: {age_ms} ms")
            self.throttle_bar['value'] = int((state.throttle + 1.0) * 50)
            self.turn_bar['value'] = int((state.turn + 1.0) * 50)
            self.gear_var.set(f"Gear: {'BOOST' if state.gear_boost else 'Normal'}")
            self.brake_var.set(f"Brake: {'ON' if state.brake_pressed else 'Off'}")
            self.rotate_var.set(f"Rotate: {'ON' if state.rotate_pressed else 'Off'}")
            
            # Determine movement state
            if state.brake_pressed:
                movement = "Braking"
            elif state.rotate_pressed:
                movement = "Rotating"
            elif abs(state.throttle) > 0.1 or abs(state.turn) > 0.1:
                if state.throttle > 0.1:
                    if abs(state.turn) > 0.1:
                        if state.turn > 0:
                            movement = "Forward Right"
                        else:
                            movement = "Forward Left"
                    else:
                        movement = "Forward"
                elif state.throttle < -0.1:
                    if abs(state.turn) > 0.1:
                        if state.turn > 0:
                            movement = "Backward Right"
                        else:
                            movement = "Backward Left"
                    else:
                        movement = "Backward"
                else:
                    movement = "Turning"
            else:
                movement = "Stopped"
            
            self.movement_var.set(f"Movement: {movement}")

            # Update colored speed bars: brake -> red, boost -> orange, normal -> blue
            def color_for(state):
                if state.brake_pressed:
                    return '#ef4444'  # Red for brake
                return '#f59e0b' if state.gear_boost else '#3b82f6'

            bar_color = color_for(state)
            # Map speed [-1,1] to width [20, 620]
            def set_bar(rect, value):
                min_x, max_x = 20, 620
                mid_x = (min_x + max_x) // 2
                width = int(mid_x + value * (max_x - min_x) / 2)
                y1, y2 = (20, 50) if rect == self.left_rect else (55, 85)
                self.canvas.coords(rect, 20, y1, width, y2)
                self.canvas.itemconfig(rect, fill=bar_color)

            # Approximate left/right from throttle/turn
            left = max(-1.0, min(1.0, state.throttle + state.turn))
            right = max(-1.0, min(1.0, state.throttle - state.turn))
            set_bar(self.left_rect, left)
            set_bar(self.right_rect, right)
        self.root.after(1, self._tick)

    def run(self) -> None:
        self.root.after(1, self._tick)
        self.root.mainloop()


def main() -> None:
    parser = argparse.ArgumentParser(description="ESP32 Dashboard Sender")
    parser.add_argument("--com", help="ESP32 Bluetooth/USB COM port, e.g., COM7 (auto-detect if not specified)")
    parser.add_argument("--baud", type=int, default=115200, help="Baud rate")
    parser.add_argument("--keyboard", action="store_true", help="Use keyboard instead of controller")
    parser.add_argument("--dashboard", action="store_true", help="Show dashboard UI")
    parser.add_argument("--pins", type=str, default="5,6,9,10", help="ESP32 pins as L1,L2,R1,R2")
    args = parser.parse_args()

    setup_logging()
    logging.info("Starting ESP32 Dashboard")

    # Parse pins
    try:
        p = tuple(int(x.strip()) for x in args.pins.split(','))
        pins: tuple[int, int, int, int] = (p[0], p[1], p[2], p[3])  # type: ignore[index]
    except Exception:
        pins = (5, 6, 9, 10)

    last_state: Optional[ControllerState] = None

    def on_state(state: ControllerState) -> None:
        nonlocal last_state
        last_state = state

    # Auto-detect ESP32 port if not specified
    com_port = args.com
    if not com_port:
        logging.info("No COM port specified, auto-detecting ESP32...")
        status_temp = RuntimeStatus("", args.baud)
        com_port = status_temp.find_esp32_port()
        if com_port:
            logging.info(f"Auto-detected ESP32 on {com_port}")
        else:
            logging.error("Could not auto-detect ESP32. Please specify --com manually.")
            logging.info("Available ports:")
            for port in status_temp.update_ports():
                logging.info(f"  {port}")
            return
    else:
        logging.info(f"Using specified COM port: {com_port}")

    status = RuntimeStatus(com_port, args.baud)

    # Choose input source
    if args.keyboard:
        logging.info("Using keyboard controls")
        status.set_controller(True)
        reader = KeyboardReader(on_state, status)
    elif not HAS_PYGAME:
        logging.info("Pygame not available, using keyboard controls")
        status.set_controller(True)
        reader = KeyboardReader(on_state, status)
    else:
        logging.info("Attempting to use PS5 controller")
        reader = PygameReader(on_state, status)
    
    reader.start()
    
    # If pygame reader fails to connect, fallback to keyboard
    if not args.keyboard and HAS_PYGAME:
        time.sleep(2)  # Give pygame time to connect
        if not status.controller_connected:
            logging.warning("Controller not detected, switching to keyboard mode")
            reader.stop()
            status.set_controller(True)
            reader = KeyboardReader(on_state, status)
            reader.start()

    # Serial sender thread
    sender = SerialSender(args.com, args.baud, lambda: last_state, status)
    sender.start()

    # Optional dashboard
    if args.dashboard:
        dash = Dashboard(status, pins)

        def push_loop():
            while reader.is_alive():
                if last_state is not None:
                    dash.push(last_state)
                time.sleep(0.05)

        t = threading.Thread(target=push_loop, daemon=True)
        t.start()
        try:
            dash.run()
        finally:
            sender.stop()
            reader.stop()
    else:
        try:
            while reader.is_alive():
                time.sleep(0.1)
        finally:
            sender.stop()
            reader.stop()


if __name__ == "__main__":
    main()


