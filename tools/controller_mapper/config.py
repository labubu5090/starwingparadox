"""Controller Mapper configuration schema and I/O."""
import json
import os
import shutil
import time
from dataclasses import asdict, dataclass, field

CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config")
CONFIG_PATH = os.path.join(CONFIG_DIR, "controller_mapping.json")

SCHEMA_VERSION = 1

DEFAULT_DEADZONE = 0.15
CREDIT_COOLDOWN_SEC = 0.5
CREDIT_MAX_PER_ARM = 2
CREDIT_DEFAULT_ARMED = False

DEFAULT_MAPPINGS: dict = {
    "forward": {"type": "axis", "axis": "lx_pos", "key": "W"},
    "left": {"type": "axis", "axis": "lx_neg", "key": "A"},
    "right": {"type": "axis", "axis": "rx_pos", "key": "D"},
    "foot_pedal": {"type": "button", "button": 0, "key": "Space"},
    "start": {"type": "button", "button": 7, "key": "Enter"},
    "shot_left": {"type": "button", "button": 4, "key": "LMB"},
    "shot_right": {"type": "button", "button": 5, "key": "RMB"},
    "dash": {"type": "button", "button": 6, "key": "Shift"},
    "left_button": {"type": "button", "button": 8, "key": "Q"},
    "right_button": {"type": "button", "button": 9, "key": "E"},
    "weapon_change": {"type": "button", "button": 3, "key": "MMB"},
    "step": {"type": "button", "button": 10, "key": "LCtrl"},
    "ar_skill": {"type": "button", "button": 1, "key": "F"},
    "credit": {"type": "unassigned", "key": "Z"},
}

KEY_SYNONYMS = {
    "left shift": "Shift",
    "shift": "Shift",
    "spacebar": "Space",
    "space": "Space",
    "left control": "LCtrl",
    "lctrl": "LCtrl",
    "enter": "Enter",
    "return": "Enter",
    "left mouse button": "LMB",
    "right mouse button": "RMB",
    "middle mouse button": "MMB",
    "middlemousebutton": "MMB",
}


def normalize_key(raw: str) -> str:
    return KEY_SYNONYMS.get(raw.strip().lower(), raw.strip())


@dataclass
class ButtonMapping:
    button: int
    key: str


@dataclass
class AxisMapping:
    axis: str  # lx_pos, lx_neg, ly_pos, ly_neg, rx_pos, rx_neg, ry_pos, ry_neg
    key: str


@dataclass
class CreditMapping:
    key: str = "Z"
    armed: bool = CREDIT_DEFAULT_ARMED
    cooldown: float = CREDIT_COOLDOWN_SEC
    max_per_arm: int = CREDIT_MAX_PER_ARM


@dataclass
class MappingConfig:
    version: int = SCHEMA_VERSION
    device_id: int = 0
    deadzone: float = DEFAULT_DEADZONE
    button_mappings: dict = field(default_factory=dict)
    axis_mappings: dict = field(default_factory=dict)
    credit: CreditMapping = field(default_factory=CreditMapping)
    created: str = ""
    modified: str = ""

    def __post_init__(self):
        now = time.strftime("%Y-%m-%dT%H:%M:%S")
        if not self.created:
            self.created = now
        self.modified = now


def load_config() -> MappingConfig:
    if not os.path.exists(CONFIG_PATH):
        return _create_default()
    try:
        with open(CONFIG_PATH, "r") as f:
            data = json.load(f)
        return _from_dict(data)
    except (json.JSONDecodeError, KeyError, TypeError, OSError):
        return _create_default()


def save_config(cfg: MappingConfig) -> None:
    os.makedirs(CONFIG_DIR, exist_ok=True)
    if os.path.exists(CONFIG_PATH):
        ts = time.strftime("%Y%m%d_%H%M%S")
        backup = CONFIG_PATH + f".backup-{ts}"
        shutil.copy2(CONFIG_PATH, backup)
    cfg.modified = time.strftime("%Y-%m-%dT%H:%M:%S")
    data = asdict(cfg)
    tmp = CONFIG_PATH + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, CONFIG_PATH)


def _create_default() -> MappingConfig:
    cfg = MappingConfig()
    for action, mapping in DEFAULT_MAPPINGS.items():
        if mapping["type"] == "button":
            cfg.button_mappings[action] = ButtonMapping(
                button=mapping["button"], key=mapping["key"]
            )
        elif mapping["type"] == "axis":
            cfg.axis_mappings[action] = AxisMapping(
                axis=mapping["axis"], key=mapping["key"]
            )
        elif mapping["type"] == "unassigned":
            pass
    save_config(cfg)
    return cfg


def _from_dict(data: dict) -> MappingConfig:
    cfg = MappingConfig(
        version=data.get("version", SCHEMA_VERSION),
        device_id=data.get("device_id", 0),
        deadzone=data.get("deadzone", DEFAULT_DEADZONE),
        created=data.get("created", ""),
        modified=data.get("modified", ""),
    )
    credit = data.get("credit", {})
    cfg.credit = CreditMapping(
        key=credit.get("key", "Z"),
        armed=credit.get("armed", CREDIT_DEFAULT_ARMED),
        cooldown=credit.get("cooldown", CREDIT_COOLDOWN_SEC),
        max_per_arm=credit.get("max_per_arm", CREDIT_MAX_PER_ARM),
    )
    for action, bm in data.get("button_mappings", {}).items():
        if isinstance(bm, dict):
            cfg.button_mappings[action] = ButtonMapping(
                button=bm.get("button", 0),
                key=normalize_key(bm.get("key", "")),
            )
    for action, am in data.get("axis_mappings", {}).items():
        if isinstance(am, dict):
            cfg.axis_mappings[action] = AxisMapping(
                axis=am.get("axis", ""),
                key=normalize_key(am.get("key", "")),
            )
    return cfg
