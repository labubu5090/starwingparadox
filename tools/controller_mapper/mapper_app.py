"""Starwing Controller Mapper - main application."""
import os
import sys
import threading
import time
import tkinter as tk
from tkinter import ttk

sys.path.insert(0, os.path.dirname(__file__))

from joystick import enumerate_devices, is_button_pressed, normalize_axis, read_joystick
from keyboard_output import KeyboardOutput
from process_guard import is_starwing_foreground

from config import AxisMapping, ButtonMapping, load_config, save_config

DEFAULT_ACTIONS = {
    "forward": {"label": "Forward", "default_axis": "lx_pos", "default_key": "W"},
    "left": {"label": "Left", "default_axis": "lx_neg", "default_key": "A"},
    "right": {"label": "Right", "default_axis": "rx_pos", "default_key": "D"},
    "foot_pedal": {"label": "Foot Pedal", "default_button": 0, "default_key": "Space"},
    "start": {"label": "Start", "default_button": 7, "default_key": "Enter"},
    "shot_left": {"label": "Shot Left", "default_button": 4, "default_key": "LMB"},
    "shot_right": {"label": "Shot Right", "default_button": 5, "default_key": "RMB"},
    "dash": {"label": "Dash", "default_button": 6, "default_key": "Shift"},
    "left_button": {"label": "Left Button", "default_button": 8, "default_key": "Q"},
    "right_button": {"label": "Right Button", "default_button": 9, "default_key": "E"},
    "weapon_change": {"label": "Weapon Change", "default_button": 3, "default_key": "MMB"},
    "step": {"label": "Step", "default_button": 10, "default_key": "LCtrl"},
    "ar_skill": {"label": "AR Skill", "default_button": 1, "default_key": "F"},
}

CREDIT_ACTION = "credit"


class ControllerMapper:
    def __init__(self):
        self.config = load_config()
        self.output = KeyboardOutput()
        self.running = False
        self.test_mode = False
        self.adapter_enabled = False
        self._thread: threading.Thread | None = None
        self._capturing: str | None = None
        self._capture_prev_state = None
        self._credit_count = 0
        self._last_credit_time = 0.0
        self._prev_buttons = 0
        self._prev_pov = 0xFFFFFFFF
        self._prev_axes = {}
        self._root: tk.Tk | None = None
        self._labels = {}
        self._live_axis_labels = {}
        self._live_button_labels = {}
        self._status_label = None
        self._fg_label = None
        self._output_label = None
        self._capture_label = None
        self._adapter_btn = None
        self._credit_count_label = None
        self._credit_arm_var = None
        self._device_var = None
        self._deadzone_var = None

    def start(self):
        self._root = tk.Tk()
        self._root.title("Starwing Controller Mapper")
        self._root.geometry("520x780")
        self._root.resizable(False, False)
        self._build_ui()
        self.running = True
        self._poll_loop()
        self._root.protocol("WM_DELETE_WINDOW", self._on_close)
        self._root.mainloop()

    def _build_ui(self):
        root = self._root

        top = ttk.Frame(root)
        top.pack(fill=tk.X, padx=8, pady=4)

        ttk.Label(top, text="Controller:").pack(side=tk.LEFT)
        self._device_var = tk.StringVar(value=str(self.config.device_id))
        devs = enumerate_devices()
        dev_names = [f"Device {d['id']}" for d in devs] if devs else ["No devices"]
        self._device_combo = ttk.Combobox(top, values=dev_names, width=12, state="readonly",
                                          textvariable=self._device_var)
        self._device_combo.pack(side=tk.LEFT, padx=4)

        ttk.Label(top, text="Deadzone:").pack(side=tk.LEFT, padx=(12, 0))
        self._deadzone_var = tk.StringVar(value=f"{self.config.deadzone:.2f}")
        dz_spin = ttk.Spinbox(top, from_=0.0, to=0.5, increment=0.05, width=5,
                               textvariable=self._deadzone_var)
        dz_spin.pack(side=tk.LEFT, padx=4)

        self._status_label = ttk.Label(top, text="Disconnected", foreground="red")
        self._status_label.pack(side=tk.RIGHT)

        sep = ttk.Separator(root, orient=tk.HORIZONTAL)
        sep.pack(fill=tk.X, padx=8, pady=2)

        ttk.Label(root, text="Live Input", font=("", 10, "bold")).pack(anchor=tk.W, padx=8)
        live_frame = ttk.Frame(root)
        live_frame.pack(fill=tk.X, padx=8)

        axis_frame = ttk.LabelFrame(live_frame, text="Axes")
        axis_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 4))
        for i, name in enumerate(["LX", "LY", "RX", "RY"]):
            row = ttk.Frame(axis_frame)
            row.pack(fill=tk.X, padx=2, pady=1)
            ttk.Label(row, text=f"{name}:", width=4).pack(side=tk.LEFT)
            bar = ttk.Progressbar(row, length=120, mode="determinate", maximum=100)
            bar.pack(side=tk.LEFT, padx=2)
            val_label = ttk.Label(row, text="0.00", width=6)
            val_label.pack(side=tk.LEFT)
            self._live_axis_labels[name] = (bar, val_label)

        btn_frame = ttk.LabelFrame(live_frame, text="Buttons")
        btn_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._live_button_grid = ttk.Frame(btn_frame)
        self._live_button_grid.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        sep2 = ttk.Separator(root, orient=tk.HORIZONTAL)
        sep2.pack(fill=tk.X, padx=8, pady=4)

        ttk.Label(root, text="Mappings", font=("", 10, "bold")).pack(anchor=tk.W, padx=8)
        canvas = tk.Canvas(root, borderwidth=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(root, orient=tk.VERTICAL, command=canvas.yview)
        self._map_frame = ttk.Frame(canvas)
        self._map_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self._map_frame, anchor=tk.NW)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(8, 0))
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        for action, info in DEFAULT_ACTIONS.items():
            self._add_mapping_row(action, info["label"])

        credit_frame = ttk.LabelFrame(self._map_frame, text="Credit (Safety)")
        credit_frame.pack(fill=tk.X, padx=4, pady=4)
        row = ttk.Frame(credit_frame)
        row.pack(fill=tk.X, padx=4, pady=2)
        self._credit_arm_var = tk.BooleanVar(value=self.config.credit.armed)
        ttk.Checkbutton(row, text="Arm Credit Input", variable=self._credit_arm_var,
                         command=self._toggle_credit_arm).pack(side=tk.LEFT)
        self._credit_count_label = ttk.Label(row, text=f"Count: 0/{self.config.credit.max_per_arm}")
        self._credit_count_label.pack(side=tk.RIGHT)
        self._add_mapping_row(CREDIT_ACTION, "Credit (Z)")

        sep3 = ttk.Separator(root, orient=tk.HORIZONTAL)
        sep3.pack(fill=tk.X, padx=8, pady=4)

        btn_bar = ttk.Frame(root)
        btn_bar.pack(fill=tk.X, padx=8, pady=4)

        self._test_btn = ttk.Button(btn_bar, text="Test Input", command=self._toggle_test)
        self._test_btn.pack(side=tk.LEFT, padx=2)

        ttk.Button(btn_bar, text="Save", command=self._save).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_bar, text="Reset", command=self._reset).pack(side=tk.LEFT, padx=2)

        self._adapter_btn = ttk.Button(btn_bar, text="Enable Adapter", command=self._toggle_adapter)
        self._adapter_btn.pack(side=tk.RIGHT, padx=2)

        ttk.Button(btn_bar, text="Emergency Stop", command=self._emergency_stop).pack(side=tk.RIGHT, padx=2)

        bottom = ttk.Frame(root)
        bottom.pack(fill=tk.X, padx=8, pady=2)
        self._fg_label = ttk.Label(bottom, text="Game: Not found")
        self._fg_label.pack(side=tk.LEFT)
        self._output_label = ttk.Label(bottom, text="Output: None")
        self._output_label.pack(side=tk.RIGHT)

        self._capture_label = ttk.Label(root, text="", foreground="blue")
        self._capture_label.pack(fill=tk.X, padx=8)

        self._build_button_grid()

    def _build_button_grid(self):
        grid = self._live_button_grid
        for child in grid.winfo_children():
            child.destroy()
        cols = 6
        for i in range(16):
            row_idx = i // cols
            col_idx = i % cols
            lbl = ttk.Label(grid, text=f"B{i}:0", width=5, relief=tk.SUNKEN, anchor=tk.CENTER)
            lbl.grid(row=row_idx, column=col_idx, padx=1, pady=1, sticky=tk.EW)
            self._live_button_labels[i] = lbl
        for c in range(cols):
            grid.columnconfigure(c, weight=1)

    def _add_mapping_row(self, action: str, label: str):
        row = ttk.Frame(self._map_frame)
        row.pack(fill=tk.X, padx=4, pady=2)
        ttk.Label(row, text=f"{label}:", width=14, anchor=tk.W).pack(side=tk.LEFT)
        key_var = tk.StringVar()
        btn = ttk.Button(row, text="Assign", width=8,
                         command=lambda a=action: self._start_capture(a))
        btn.pack(side=tk.RIGHT, padx=2)
        clear_btn = ttk.Button(row, text="Clear", width=5,
                               command=lambda a=action: self._clear_mapping(a))
        clear_btn.pack(side=tk.RIGHT, padx=2)
        key_label = ttk.Label(row, textvariable=key_var, width=8, relief=tk.SUNKEN, anchor=tk.CENTER)
        key_label.pack(side=tk.RIGHT, padx=2)
        mapping = self._get_current_mapping(action)
        if mapping:
            key_var.set(mapping)
        self._labels[action] = key_var

    def _get_current_mapping(self, action: str) -> str:
        if action in self.config.button_mappings:
            return self.config.button_mappings[action].key
        if action in self.config.axis_mappings:
            return self.config.axis_mappings[action].key
        if action == CREDIT_ACTION:
            return self.config.credit.key
        return ""

    def _start_capture(self, action: str):
        if self._capturing:
            return
        self._capturing = action
        self._capture_label.config(text=f"Capture: Move/press {action} on controller...")
        self._capture_prev_state = read_joystick(self.config.device_id)

    def _clear_mapping(self, action: str):
        self.config.button_mappings.pop(action, None)
        self.config.axis_mappings.pop(action, None)
        if action == CREDIT_ACTION:
            self.config.credit.key = "Z"
        if action in self._labels:
            self._labels[action].set("")
        save_config(self.config)

    def _toggle_test(self):
        self.test_mode = not self.test_mode
        self._test_btn.config(text="Test Input ON" if self.test_mode else "Test Input")
        if self.test_mode:
            self.output.release_all()

    def _toggle_adapter(self):
        self.adapter_enabled = not self.adapter_enabled
        self._adapter_btn.config(
            text="Disable Adapter" if self.adapter_enabled else "Enable Adapter"
        )
        if not self.adapter_enabled:
            self.output.release_all()

    def _emergency_stop(self):
        self.output.release_all()
        self.adapter_enabled = False
        self._adapter_btn.config(text="Enable Adapter")

    def _toggle_credit_arm(self):
        self.config.credit.armed = self._credit_arm_var.get()
        if not self.config.credit.armed:
            self._credit_count = 0
        self._update_credit_display()
        save_config(self.config)

    def _update_credit_display(self):
        if self._credit_count_label:
            self._credit_count_label.config(
                text=f"Count: {self._credit_count}/{self.config.credit.max_per_arm}"
            )

    def _save(self):
        try:
            self.config.deadzone = float(self._deadzone_var.get())
        except ValueError:
            pass
        save_config(self.config)

    def _reset(self):
        from config import _create_default
        self.config = _create_default()
        for action in DEFAULT_ACTIONS:
            if action in self._labels:
                mapping = self._get_current_mapping(action)
                self._labels[action].set(mapping if mapping else "")
        if CREDIT_ACTION in self._labels:
            self._labels[CREDIT_ACTION].set(self.config.credit.key)
        self._deadzone_var.set(f"{self.config.deadzone:.2f}")
        self._credit_arm_var.set(self.config.credit.armed)
        self._update_credit_display()

    def _poll_loop(self):
        if not self.running:
            return
        try:
            state = read_joystick(self.config.device_id)
            self._update_live_display(state)
            if self._capturing:
                self._process_capture(state)
            elif self.adapter_enabled:
                self._process_output(state)
            self._update_fg_status()
        except (OSError, ValueError, TypeError):
            pass
        self._root.after(16, self._poll_loop)

    def _update_live_display(self, state):
        if not state.valid:
            self._status_label.config(text="Disconnected", foreground="red")
            return
        self._status_label.config(text="Connected", foreground="green")

        axes = {
            "LX": normalize_axis(state.x),
            "LY": normalize_axis(state.y),
            "RX": normalize_axis(state.r),
            "RY": normalize_axis(state.u),
        }
        for name, val in axes.items():
            if name in self._live_axis_labels:
                bar, lbl = self._live_axis_labels[name]
                bar["value"] = abs(val) * 100
                lbl.config(text=f"{val:+.2f}")

        for i in range(16):
            pressed = is_button_pressed(state.buttons, i)
            if i in self._live_button_labels:
                self._live_button_labels[i].config(
                    text=f"B{i}:{'1' if pressed else '0'}",
                    foreground="red" if pressed else "black"
                )

    def _process_capture(self, state):
        if self._capture_prev_state is None:
            self._capture_prev_state = state
            return
        prev = self._capture_prev_state
        action = self._capturing

        for bit in range(16):
            was = is_button_pressed(prev.buttons, bit)
            now = is_button_pressed(state.buttons, bit)
            if now and not was:
                self._finalize_capture(action, "button", bit)
                return

        dz = self.config.deadzone
        axes_check = [
            ("lx_pos", normalize_axis(state.x) > dz),
            ("lx_neg", normalize_axis(state.x) < -dz),
            ("ly_pos", normalize_axis(state.y) > dz),
            ("ly_neg", normalize_axis(state.y) < -dz),
            ("rx_pos", normalize_axis(state.r) > dz),
            ("rx_neg", normalize_axis(state.r) < -dz),
            ("ry_pos", normalize_axis(state.u) > dz),
            ("ry_neg", normalize_axis(state.u) < -dz),
        ]
        prev_axes = [
            ("lx_pos", normalize_axis(prev.x) > dz),
            ("lx_neg", normalize_axis(prev.x) < -dz),
            ("ly_pos", normalize_axis(prev.y) > dz),
            ("ly_neg", normalize_axis(prev.y) < -dz),
            ("rx_pos", normalize_axis(prev.r) > dz),
            ("rx_neg", normalize_axis(prev.r) < -dz),
            ("ry_pos", normalize_axis(prev.u) > dz),
            ("ry_neg", normalize_axis(prev.u) < -dz),
        ]
        for (aname, is_now), (_, was) in zip(axes_check, prev_axes):
            if is_now and not was:
                self._finalize_capture(action, "axis", aname)
                return

        self._capture_prev_state = state

    def _finalize_capture(self, action: str, input_type: str, value):
        if action == CREDIT_ACTION:
            self.config.credit.key = "Z"
        elif input_type == "button":
            self.config.button_mappings[action] = ButtonMapping(button=value, key=DEFAULT_ACTIONS.get(action, {}).get("default_key", ""))
            self.config.axis_mappings.pop(action, None)
        elif input_type == "axis":
            self.config.axis_mappings[action] = AxisMapping(axis=value, key=DEFAULT_ACTIONS.get(action, {}).get("default_key", ""))
            self.config.button_mappings.pop(action, None)

        if action in self._labels:
            key = DEFAULT_ACTIONS.get(action, {}).get("default_key", "Z") if action != CREDIT_ACTION else "Z"
            self._labels[action].set(key)

        self._capturing = None
        self._capture_prev_state = None
        self._capture_label.config(text=f"Captured: {action} -> {input_type}={value}")
        save_config(self.config)

    def _process_output(self, state):
        if not is_starwing_foreground():
            self.output.release_all()
            return

        active_keys = set()
        dz = self.config.deadzone

        for action, mapping in self.config.axis_mappings.items():
            if action == CREDIT_ACTION:
                continue
            ax_val = self._get_axis_value(state, mapping.axis)
            if ax_val > dz:
                active_keys.add(mapping.key)

        for action, mapping in self.config.button_mappings.items():
            if action == CREDIT_ACTION:
                continue
            if is_button_pressed(state.buttons, mapping.button):
                active_keys.add(mapping.key)

        for key in list(self.output.held):
            if key not in active_keys:
                self.output.release(key)
        for key in active_keys:
            self.output.press(key)

        self._process_credit(state)
        self._prev_buttons = state.buttons
        self._output_label.config(text=f"Output: {','.join(sorted(active_keys)) or 'None'}")

    def _process_credit(self, state):
        if not self.config.credit.armed:
            return
        if self._credit_count >= self.config.credit.max_per_arm:
            return
        now = time.time()
        if now - self._last_credit_time < self.config.credit.cooldown:
            return
        credit_mapping = self.config.button_mappings.get(CREDIT_ACTION)
        if credit_mapping is None:
            return
        was_pressed = is_button_pressed(self._prev_buttons, credit_mapping.button)
        now_pressed = is_button_pressed(state.buttons, credit_mapping.button)
        if now_pressed and not was_pressed:
            self.output.tap(self.config.credit.key, duration=0.03)
            self._credit_count += 1
            self._last_credit_time = now
            self._update_credit_display()

    def _get_axis_value(self, state, axis_name: str) -> float:
        mapping = {
            "lx_pos": normalize_axis(state.x),
            "lx_neg": -normalize_axis(state.x),
            "ly_pos": normalize_axis(state.y),
            "ly_neg": -normalize_axis(state.y),
            "rx_pos": normalize_axis(state.r),
            "rx_neg": -normalize_axis(state.r),
            "ry_pos": normalize_axis(state.u),
            "ry_neg": -normalize_axis(state.u),
        }
        return max(0.0, mapping.get(axis_name, 0.0))

    def _update_fg_status(self):
        if self._fg_label:
            fg = is_starwing_foreground()
            self._fg_label.config(
                text=f"Game: {'FOREGROUND' if fg else 'Not focused'}",
                foreground="green" if fg else "gray"
            )

    def _on_close(self):
        self.running = False
        self.output.release_all()
        self._root.destroy()


def main():
    mapper = ControllerMapper()
    mapper.start()


if __name__ == "__main__":
    main()
