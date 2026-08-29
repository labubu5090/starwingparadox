"""G34 Controller Interface Diagnostic - enumerates all interfaces for VID_2DC8 PID_301C."""
import json
import ctypes
import ctypes.wintypes as wt
import hashlib
import subprocess
import sys
import time
import os

result = {
    "device_name": "8BitDo Ultimate 2C Wireless Controller",
    "vid": "2DC8",
    "pid": "301C",
    "transport": "",
    "joy_cpl_present": True,
    "joy_cpl_live_events": None,
    "raw_input_visible": None,
    "hid_visible": None,
    "directinput_visible": None,
    "xinput_slots": {"0": "", "1": "", "2": "", "3": ""},
    "final_api_classification": ""
}

# === PnP ===
print("=== PnP Devices ===")
pnp = subprocess.run(
    ["powershell", "-Command",
     r"Get-PnpDevice -Status OK -ErrorAction SilentlyContinue | "
     r"Where-Object { $_.InstanceId -match '2DC8' } | "
     r"ForEach-Object { Write-Output ($_.FriendlyName + ' | ' + $_.Class + ' | ' + $_.Status) }"],
    capture_output=True, text=True, timeout=10
)
pnp_lines = [l.strip() for l in pnp.stdout.strip().split("\n") if l.strip()]
for line in pnp_lines:
    print(f"  {line}")
if not pnp_lines:
    print("  No 8BitDo PnP devices found")

# === HID ===
print()
print("=== HID Interfaces ===")
try:
    import hid
    hid_devices = []
    for d in hid.enumerate():
        if d["vendor_id"] == 0x2DC8:
            hid_devices.append(d)
            path_hash = hashlib.md5(d["path"]).hexdigest()[:12]
            usage_page = d["usage_page"]
            usage = d["usage"]
            print(f"  path_hash={path_hash} usage_page=0x{usage_page:04X} usage=0x{usage:04X} iface={d['interface_number']}")
            print(f"    product={d['product_string']}")
            print(f"    manufacturer={d['manufacturer_string']}")
            print(f"    serial={d['serial_number']}")
            print(f"    input_report_length={d['input_report_length']} output_report_length={d['output_report_length']} feature_report_length={d['feature_report_length']}")

    result["hid_visible"] = len(hid_devices) > 0
    print(f"  Total HID devices: {len(hid_devices)}")

    # Test each HID device for live input
    print()
    print("=== HID Live Input Test ===")
    for d in hid_devices:
        path_hash = hashlib.md5(d["path"]).hexdigest()[:12]
        print(f"  Testing path_hash={path_hash}...")
        try:
            dev = hid.device()
            dev.open_path(d["path"])
            dev.set_nonblocking(True)
            count = 0
            start = time.time()
            while time.time() - start < 3:
                try:
                    data = dev.read(64)
                    if data:
                        count += 1
                        hex_str = " ".join(f"{b:02X}" for b in data[:16])
                        if count <= 5:
                            print(f"    [{count}] {len(data)}B: {hex_str}")
                except Exception as e:
                    print(f"    read error: {e}")
                    break
                time.sleep(0.005)
            dev.close()
            print(f"    Total: {count} reports in 3s")
            if count > 0:
                result["hid_visible"] = True
        except Exception as e:
            print(f"    Open error: {e}")

except ImportError:
    print("  hid module not available")
    result["hid_visible"] = "hid module not available"
except Exception as e:
    print(f"  HID error: {e}")
    result["hid_visible"] = str(e)

# === XInput ===
print()
print("=== XInput Slots ===")

class XINPUT_GAMEPAD(ctypes.Structure):
    _fields_ = [
        ("wButtons", wt.WORD),
        ("bLeftTrigger", ctypes.c_ubyte),
        ("bRightTrigger", ctypes.c_ubyte),
        ("sThumbLX", ctypes.c_short),
        ("sThumbLY", ctypes.c_short),
        ("sThumbRX", ctypes.c_short),
        ("sThumbRY", ctypes.c_short),
    ]

class XINPUT_STATE(ctypes.Structure):
    _fields_ = [
        ("dwPacketNumber", wt.DWORD),
        ("Gamepad", XINPUT_GAMEPAD),
    ]

xinput_dll = None
xinput_name = ""
for dll_name in ["xinput1_4", "xinput1_3", "xinput9_1_0"]:
    try:
        xinput_dll = ctypes.windll.LoadLibrary(dll_name)
        xinput_name = dll_name
        print(f"  Loaded {dll_name}.dll")
        break
    except Exception:
        print(f"  {dll_name}.dll not available")

if xinput_dll:
    for slot in range(4):
        state = XINPUT_STATE()
        try:
            rc = xinput_dll.XInputGetState(slot, ctypes.byref(state))
        except Exception as e:
            result["xinput_slots"][str(slot)] = f"CALL_FAILED: {e}"
            print(f"  Slot {slot}: call failed: {e}")
            continue
        if rc == 0:
            btns = state.Gamepad.wButtons
            lx, ly = state.Gamepad.sThumbLX, state.Gamepad.sThumbLY
            rx, ry = state.Gamepad.sThumbRX, state.Gamepad.sThumbRY
            lt, rt = state.Gamepad.bLeftTrigger, state.Gamepad.bRightTrigger
            result["xinput_slots"][str(slot)] = f"CONNECTED {xinput_name} buttons=0x{btns:04X} LX={lx} LY={ly} RX={rx} RY={ry} LT={lt} RT={rt}"
            print(f"  Slot {slot}: CONNECTED buttons=0x{btns:04X} LX={lx} LY={ly} RX={rx} RY={ry} LT={lt} RT={rt}")
        elif rc == 1167:
            result["xinput_slots"][str(slot)] = f"{xinput_name}:ERROR_DEVICE_NOT_CONNECTED"
            print(f"  Slot {slot}: ERROR_DEVICE_NOT_CONNECTED")
        else:
            result["xinput_slots"][str(slot)] = f"{xinput_name}:ERROR_{rc}"
            print(f"  Slot {slot}: ERROR_{rc}")
else:
    print("  No XInput DLL available")

# === Raw Input ===
print()
print("=== Raw Input ===")
try:
    user32 = ctypes.windll.user32

    # First get device count
    device_count = wt.UINT(0)
    rc = user32.GetRawInputDeviceList(None, ctypes.byref(device_count), ctypes.sizeof(wt.UINT))
    print(f"  Raw Input device count: {device_count.value}")

    if device_count.value > 0:
        class RAWINPUTDEVICELIST(ctypes.Structure):
            _fields_ = [("hDevice", wt.HANDLE), ("dwType", wt.DWORD)]

        devices = (RAWINPUTDEVICELIST * device_count.value)()
        actual = user32.GetRawInputDeviceList(devices, ctypes.byref(device_count), ctypes.sizeof(RAWINPUTDEVICELIST))
        found_8bitdo = False
        for i in range(actual):
            dev = devices[i]
            # Get device info
            cbSize = wt.UINT(0)
            user32.GetRawInputDeviceInfoW(dev.hDevice, 0x20000000, None, ctypes.byref(cbSize))
            if cbSize.value > 0:
                buf = ctypes.create_unicode_buffer(cbSize.value)
                user32.GetRawInputDeviceInfoW(dev.hDevice, 0x20000000, buf, ctypes.byref(cbSize))
                name = buf.value
                if "2DC8" in name or "301C" in name:
                    found_8bitdo = True
                    type_names = {0x11: "MOUSE", 0x12: "KEYBOARD", 0x13: "HID"}
                    type_name = type_names.get(dev.dwType, f"UNKNOWN(0x{dev.dwType:X})")
                    print(f"  FOUND: hDevice={dev.hDevice} type={type_name} name={name}")

                    # For HID devices, try to read preparsed data
                    if dev.dwType == 0x13:
                        # RIDI_PREPARSEDDATA
                        cbSize2 = wt.UINT(0)
                        user32.GetRawInputDeviceInfoW(dev.hDevice, 0x20000001, None, ctypes.byref(cbSize2))
                        print(f"    Preparsed data size: {cbSize2.value} bytes")

        result["raw_input_visible"] = found_8bitdo
        if not found_8bitdo:
            print(f"  No 8BitDo found in {actual} Raw Input devices")
    else:
        result["raw_input_visible"] = False
        print("  No Raw Input devices")
except Exception as e:
    print(f"  Raw Input error: {e}")
    result["raw_input_visible"] = str(e)

# === DirectInput ===
print()
print("=== DirectInput ===")
try:
    dinput8 = ctypes.windll.dinput8
    result["directinput_visible"] = "dinput8.dll LOADABLE"
    print("  dinput8.dll loaded")
except Exception as e:
    try:
        dinput = ctypes.windll.dinput
        result["directinput_visible"] = "dinput.dll LOADABLE"
        print("  dinput.dll loaded (legacy)")
    except Exception as e2:
        result["directinput_visible"] = f"NOT_AVAILABLE: {e}"
        print(f"  DirectInput not available: {e}")

# === joy.cpl information ===
print()
print("=== joy.cpl Registry ===")
try:
    import winreg
    reg_path = r"SYSTEM\CurrentControlSet\Control\MediaProperties\PrivateProperties\Joystick\OEM"
    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
    i = 0
    found = False
    while True:
        try:
            subkey_name = winreg.EnumKey(key, i)
            subkey = winreg.OpenKey(key, subkey_name)
            try:
                oem_name, _ = winreg.QueryValueEx(subkey, "OEMName")
                if "2DC8" in subkey_name or "301C" in subkey_name or "8BitDo" in str(oem_name):
                    found = True
                    print(f"  OEM key: {subkey_name} -> {oem_name}")
            except FileNotFoundError:
                pass
            winreg.CloseKey(subkey)
            i += 1
        except OSError:
            break
    winreg.CloseKey(key)
    if not found:
        print("  No 8BitDo in joystick OEM registry")
except Exception as e:
    print(f"  Registry check error: {e}")

# === Summary ===
print()
print("=== SUMMARY ===")
print(json.dumps(result, indent=2))

# Save result
os.makedirs("artifacts/phase_2a_g34", exist_ok=True)
with open("artifacts/phase_2a_g34/controller_windows_inventory.json", "w") as f:
    json.dump(result, f, indent=2)
print()
print("Saved to artifacts/phase_2a_g34/controller_windows_inventory.json")
