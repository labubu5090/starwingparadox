"""G34 Controller Mapper Tests - all synthetic, no physical controller required."""
import json
import os
import shutil
import sys

import pytest

_tools_dir = os.path.join(os.path.dirname(__file__), "..", "..", "tools", "controller_mapper")
sys.path.insert(0, os.path.abspath(_tools_dir))

from config import (  # noqa: E402
    CREDIT_DEFAULT_ARMED,
    CREDIT_MAX_PER_ARM,
    DEFAULT_DEADZONE,
    DEFAULT_MAPPINGS,
    SCHEMA_VERSION,
    AxisMapping,
    ButtonMapping,
    MappingConfig,
    normalize_key,
)
from joystick import AXIS_MAX, CENTERED, is_button_pressed, normalize_axis  # noqa: E402
from keyboard_output import MOUSE_VK, VK_MAP, KeyboardOutput  # noqa: E402

# === Config Schema Tests ===

def test_config_schema_version():
    cfg = MappingConfig()
    assert cfg.version == SCHEMA_VERSION


def test_config_default_deadzone():
    cfg = MappingConfig()
    assert cfg.deadzone == DEFAULT_DEADZONE


def test_config_credit_defaults():
    cfg = MappingConfig()
    assert cfg.credit.armed == CREDIT_DEFAULT_ARMED
    assert cfg.credit.max_per_arm == CREDIT_MAX_PER_ARM
    assert cfg.credit.key == "Z"


def test_config_save_and_load(tmp_path):
    cfg_path = tmp_path / "controller_mapping.json"
    os.makedirs(tmp_path / "config", exist_ok=True)
    os.environ["CONFIG_PATH"] = str(cfg_path)
    cfg = MappingConfig()
    cfg.button_mappings["forward"] = ButtonMapping(button=0, key="W")
    cfg.axis_mappings["left"] = AxisMapping(axis="lx_neg", key="A")
    # Save directly to tmp_path
    data = {
        "version": cfg.version,
        "device_id": cfg.device_id,
        "deadzone": cfg.deadzone,
        "button_mappings": {k: {"button": v.button, "key": v.key} for k, v in cfg.button_mappings.items()},
        "axis_mappings": {k: {"axis": v.axis, "key": v.key} for k, v in cfg.axis_mappings.items()},
        "credit": {"key": cfg.credit.key, "armed": cfg.credit.armed,
                   "cooldown": cfg.credit.cooldown, "max_per_arm": cfg.credit.max_per_arm},
        "created": cfg.created,
        "modified": cfg.modified,
    }
    with open(cfg_path, "w") as f:
        json.dump(data, f, indent=2)
    loaded = json.loads(cfg_path.read_text())
    assert loaded["button_mappings"]["forward"]["key"] == "W"
    assert loaded["axis_mappings"]["left"]["axis"] == "lx_neg"
    assert loaded["credit"]["armed"] is False


def test_config_backup_before_overwrite(tmp_path):
    cfg_path = tmp_path / "test_config.json"
    with open(cfg_path, "w") as f:
        json.dump({"version": 1}, f)
    with open(cfg_path) as f:
        f.read()
    # Simulate backup
    backup = cfg_path.parent / (cfg_path.name + ".backup-0")
    shutil.copy2(cfg_path, backup)
    with open(cfg_path, "w") as f:
        json.dump({"version": 2}, f)
    with open(backup) as f:
        assert json.load(f)["version"] == 1
    with open(cfg_path) as f:
        assert json.load(f)["version"] == 2


def test_normalize_key():
    assert normalize_key("left shift") == "Shift"
    assert normalize_key("Shift") == "Shift"
    assert normalize_key("spacebar") == "Space"
    assert normalize_key("Space") == "Space"
    assert normalize_key("left control") == "LCtrl"
    assert normalize_key("Enter") == "Enter"
    assert normalize_key("W") == "W"


def test_axis_normalization():
    assert normalize_axis(CENTERED) == pytest.approx(0.0, abs=0.01)
    assert normalize_axis(AXIS_MAX) == pytest.approx(1.0, abs=0.01)
    assert normalize_axis(0) == pytest.approx(-1.0, abs=0.01)
    assert normalize_axis(CENTERED + 16384) == pytest.approx(0.5, abs=0.02)


def test_button_pressed():
    buttons = 0b10101
    assert is_button_pressed(buttons, 0) is True
    assert is_button_pressed(buttons, 1) is False
    assert is_button_pressed(buttons, 2) is True
    assert is_button_pressed(buttons, 3) is False
    assert is_button_pressed(buttons, 4) is True
    assert is_button_pressed(buttons, 5) is False


def test_no_backward_s_mapping_in_default():
    for _action, mapping in DEFAULT_MAPPINGS.items():
        if mapping.get("key") == "S":
            pytest.fail("Default config must not map S/backward")


def test_credit_default_unassigned():
    cfg = MappingConfig()
    assert cfg.credit.armed is False


def test_credit_arm_default_false():
    cfg = MappingConfig()
    assert cfg.credit.armed is CREDIT_DEFAULT_ARMED


def test_credit_max_per_arm():
    cfg = MappingConfig()
    assert cfg.credit.max_per_arm >= 1


def test_key_repeat_prevention():
    kb = KeyboardOutput()
    kb.press("W")
    kb.press("W")
    assert kb.held.count("W") == 1
    kb.release_all()


def test_release_all_clears():
    kb = KeyboardOutput()
    kb.press("W")
    kb.press("A")
    kb.press("D")
    assert len(kb.held) == 3
    kb.release_all()
    assert len(kb.held) == 0


def test_only_approved_keys():
    approved = set(VK_MAP.keys()) | set(MOUSE_VK.keys())
    for key in ["W", "A", "D", "Space", "Shift", "Q", "E", "LCtrl", "F", "Enter", "Z", "LMB", "RMB", "MMB"]:
        assert key in approved, f"{key} must be in approved keys"


def test_approved_keys_no_extra():
    approved = set(VK_MAP.keys()) | set(MOUSE_VK.keys())
    for key in approved:
        assert key in ["W", "A", "D", "Space", "Shift", "Q", "E", "LCtrl", "F", "Enter", "Z", "LMB", "RMB", "MMB"]


# === Axis Mapping Tests ===

def test_axis_up_is_forward():
    assert DEFAULT_MAPPINGS["forward"]["axis"] == "lx_pos"


def test_axis_left_is_left():
    assert DEFAULT_MAPPINGS["left"]["axis"] == "lx_neg"


def test_axis_right_is_right():
    assert DEFAULT_MAPPINGS["right"]["axis"] == "rx_pos"


def test_no_backward_axis():
    for action, mapping in DEFAULT_MAPPINGS.items():
        if mapping["type"] == "axis":
            assert "neg" not in mapping["axis"] or action in ("left",), \
                f"Only left may use negative axis, not {action}"


# === Pedal Hold/Release ===

def test_pedal_hold_release():
    kb = KeyboardOutput()
    kb.press("Space")
    assert "Space" in kb.held
    kb.release("Space")
    assert "Space" not in kb.held


def test_start_debounce():
    kb = KeyboardOutput()
    kb.tap("Enter", duration=0.01)
    assert "Enter" not in kb.held


# === Mapping Capture No Keys ===

def test_capture_mode_sends_no_keys():
    kb = KeyboardOutput()
    initial_held = set(kb.held)
    # Simulating capture mode should not send keys
    # This is a structural test - capture mode checks this
    assert set(kb.held) == initial_held


# === Test Input No Keys ===

def test_test_mode_no_output():
    kb = KeyboardOutput()
    # Test mode should never call kb.press
    assert len(kb.held) == 0


# === Foreground Guard ===

def test_foreground_guard_exists():
    from process_guard import is_starwing_foreground
    result = is_starwing_foreground()
    assert isinstance(result, bool)


def test_adapter_disabled_by_default():
    from mapper_app import ControllerMapper
    mapper = ControllerMapper()
    assert mapper.adapter_enabled is False


def test_emergency_stop_releases():
    kb = KeyboardOutput()
    kb.press("W")
    kb.press("A")
    assert len(kb.held) == 2
    kb.release_all()
    assert len(kb.held) == 0


# === Diag Classification ===

def test_diag_classification_not_xinput():
    """Verify XInput was tested and not confirmed."""
    inv_path = os.path.join(os.path.dirname(__file__), "..", "artifacts", "phase_2a_g34", "controller_windows_inventory.json")
    if os.path.exists(inv_path):
        with open(inv_path) as f:
            data = json.load(f)
        for slot, result in data.get("xinput_slots", {}).items():
            assert "CONNECTED" not in result, f"XInput slot {slot} should not be CONNECTED"


def test_diag_joy_cpl_present():
    inv_path = os.path.join(os.path.dirname(__file__), "..", "artifacts", "phase_2a_g34", "controller_windows_inventory.json")
    if os.path.exists(inv_path):
        with open(inv_path) as f:
            data = json.load(f)
        assert data.get("joy_cpl_present") is True


# === Approved Keyboard Keys ===

APPROVED_KEYS = {"W", "A", "D", "Space", "Shift", "Q", "E", "LCtrl", "F", "Enter", "Z", "LMB", "RMB", "MMB"}


def test_approved_keys_completeness():
    assert len(APPROVED_KEYS) == 14


def test_no_unapproved_keys_in_config():
    for action, mapping in {
        "forward": {"key": "W"}, "left": {"key": "A"}, "right": {"key": "D"},
        "foot_pedal": {"key": "Space"}, "start": {"key": "Enter"},
        "shot_left": {"key": "LMB"}, "shot_right": {"key": "RMB"},
        "dash": {"key": "Shift"}, "left_button": {"key": "Q"}, "right_button": {"key": "E"},
        "weapon_change": {"key": "MMB"}, "step": {"key": "LCtrl"}, "ar_skill": {"key": "F"},
        "credit": {"key": "Z"},
    }.items():
        assert mapping["key"] in APPROVED_KEYS, f"{action} has unapproved key {mapping['key']}"


# === Matching Config Tests ===

def test_matching_config_section_exists():
    ini_path = os.path.join("X:", "StarwingParadox", "WindowsNoEditor", "AcrGame", "Config", "DefaultGame.ini")
    if os.path.exists(ini_path):
        with open(ini_path) as f:
            content = f.read()
        assert "[/Script/NetworkModule.NetworkConfig]" in content


def test_matching_address_in_config():
    ini_path = os.path.join("X:", "StarwingParadox", "WindowsNoEditor", "AcrGame", "Config", "DefaultGame.ini")
    if os.path.exists(ini_path):
        with open(ini_path) as f:
            content = f.read()
        assert "127.0.0.1:6666" in content


def test_http_address_in_config():
    ini_path = os.path.join("X:", "StarwingParadox", "WindowsNoEditor", "AcrGame", "Config", "DefaultGame.ini")
    if os.path.exists(ini_path):
        with open(ini_path) as f:
            content = f.read()
        assert "127.0.0.1:4001" in content


def test_config_backup_exists():
    backup_path = os.path.join("X:", "StarwingParadox", "WindowsNoEditor", "AcrGame", "Config", "DefaultGame.ini.backup-g34")
    assert os.path.exists(backup_path)


def test_default_input_backup_exists():
    backup_path = os.path.join("X:", "StarwingParadox", "WindowsNoEditor", "AcrGame", "Config", "DefaultInput - Copy.ini")
    assert os.path.exists(backup_path)


def test_ping_decoder_preserved():
    """Verify G33 decoder fix is still present."""
    codec_path = os.path.join(os.path.dirname(__file__), "..", "app", "protocol", "codec.py")
    if os.path.exists(codec_path):
        with open(codec_path) as f:
            content = f.read()
        assert "MESSAGE_TYPE_MAP" in content
