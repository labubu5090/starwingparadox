"""G34 HID Deep Diagnostic - enumerate all HID collections, read each."""
import hid
import hashlib
import time
import json
import os
import ctypes

VID = 0x2DC8
PID = 0x301C

print("=== G34 HID DEEP DIAGNOSTIC ===")
print(f"Target: VID=0x{VID:04X} PID=0x{PID:04X}")
print()

# Enumerate all HID devices for this VID/PID
all_devices = []
for d in hid.enumerate():
    if d["vendor_id"] == VID:
        all_devices.append(d)

print(f"Found {len(all_devices)} HID device(s) for VID 0x{VID:04X}")
print()

results = []
for idx, d in enumerate(all_devices):
    path_hash = hashlib.md5(d["path"]).hexdigest()[:12]
    print(f"--- Device {idx}: path_hash={path_hash} ---")
    print(f"  product_string: {d['product_string']}")
    print(f"  manufacturer_string: {d['manufacturer_string']}")
    print(f"  serial_number: {d['serial_number']}")
    print(f"  usage_page: 0x{d['usage_page']:04X}")
    print(f"  usage: 0x{d['usage']:04X}")
    print(f"  interface_number: {d['interface_number']}")
    print(f"  path: {d['path']}")
    print(f"  input_report_length (from enumerate): {d.get('input_report_length', 'N/A')}")
    print(f"  output_report_length (from enumerate): {d.get('output_report_length', 'N/A')}")
    print(f"  feature_report_length (from enumerate): {d.get('feature_report_length', 'N/A')}")

    dev_result = {
        "path_hash": path_hash,
        "usage_page": d["usage_page"],
        "usage": d["usage"],
        "interface_number": d["interface_number"],
        "input_report_length": d.get("input_report_length", 0),
        "output_report_length": d.get("output_report_length", 0),
        "feature_report_length": d.get("feature_report_length", 0),
        "open_result": None,
        "read_result": None,
        "read_error_code": None,
        "report_count": 0,
        "reports": []
    }

    # Try to open and read
    print(f"  Opening...")
    try:
        dev = hid.device()
        dev.open_path(d["path"])
        print(f"  Opened successfully!")
        dev_result["open_result"] = "SUCCESS"

        # Try to get product info
        try:
            print(f"  Product: {dev.product}")
        except:
            pass
        try:
            print(f"  Manufacturer: {dev.manufacturer}")
        except:
            pass

        # Set non-blocking
        dev.set_nonblocking(True)
        print(f"  Non-blocking mode set")

        # Try feature reports first
        print(f"  Attempting feature report queries...")
        try:
            feat = dev.get_feature_report(0, 64)
            if feat:
                print(f"  Feature report 0x00: {len(feat)}B: {' '.join(f'{b:02X}' for b in feat[:16])}")
        except Exception as e:
            print(f"  Feature report 0x00 failed: {e}")

        try:
            feat = dev.get_feature_report(0x01, 64)
            if feat:
                print(f"  Feature report 0x01: {len(feat)}B: {' '.join(f'{b:02X}' for b in feat[:16])}")
        except Exception as e:
            print(f"  Feature report 0x01 failed: {e}")

        # Read loop
        print(f"  Reading input reports for 5s...")
        start = time.time()
        count = 0
        timeout_sec = 5
        while time.time() - start < timeout_sec:
            try:
                data = dev.read(64)
                if data:
                    count += 1
                    hex_str = " ".join(f"{b:02X}" for b in data[:20])
                    if count <= 10:
                        print(f"    [{count}] {len(data)}B: {hex_str}")
                    dev_result["reports"].append({"length": len(data), "hex_preview": hex_str})
            except Exception as e:
                err = ctypes.get_last_error()
                print(f"    Read error: {e} (WinErr={err})")
                dev_result["read_error_code"] = err
                break
            time.sleep(0.002)

        dev_result["report_count"] = count
        dev_result["read_result"] = f"{count} reports in {timeout_sec}s"
        print(f"  Total: {count} reports")

        dev.close()
    except Exception as e:
        err = ctypes.get_last_error()
        print(f"  Open failed: {e} (WinErr={err})")
        dev_result["open_result"] = f"FAILED: {e}"
        dev_result["read_error_code"] = err

    results.append(dev_result)
    print()

# Also enumerate ALL HID devices to see what else is on the bus
print("=== ALL HID Devices (not just 8BitDo) ===")
all_hid = []
for d in hid.enumerate():
    all_hid.append(d)
print(f"Total HID devices on system: {len(all_hid)}")
for d in all_hid:
    path_hash = hashlib.md5(d["path"]).hexdigest()[:8]
    print(f"  VID=0x{d['vendor_id']:04X} PID=0x{d['product_id']:04X} usage=0x{d['usage_page']:04X}:0x{d['usage']:04X} iface={d['interface_number']} path_hash={path_hash} product={d['product_string'][:40]}")

# Save
os.makedirs("artifacts/phase_2a_g34", exist_ok=True)
with open("artifacts/phase_2a_g34/hid_deep_diagnostic.json", "w") as f:
    json.dump(results, f, indent=2)
print()
print(f"Saved {len(results)} device results to artifacts/phase_2a_g34/hid_deep_diagnostic.json")
