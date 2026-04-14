from src.hotkey import parse_hotkey_string


def test_parse_ctrl_shift_t():
    """Standard hotkey string should parse into components."""
    combo = parse_hotkey_string("ctrl+shift+t")
    assert combo["char"] == "t"
    assert combo["modifiers"] == {"ctrl", "shift"}


def test_parse_ctrl_alt_s():
    """Alternate combo with alt."""
    combo = parse_hotkey_string("ctrl+alt+s")
    assert combo["char"] == "s"
    assert combo["modifiers"] == {"ctrl", "alt"}


def test_parse_single_key():
    """A single key with no modifiers."""
    combo = parse_hotkey_string("f1")
    assert combo["char"] == "f1"
    assert combo["modifiers"] == set()


def test_parse_case_insensitive():
    """Parsing should be case-insensitive."""
    combo = parse_hotkey_string("Ctrl+Shift+T")
    assert combo["char"] == "t"
    assert combo["modifiers"] == {"ctrl", "shift"}
