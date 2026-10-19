from assistant.system.hotkey import to_pynput_combo


def test_ctrl_space():
    assert to_pynput_combo("ctrl+space") == "<ctrl>+<space>"


def test_three_keys():
    assert to_pynput_combo("ctrl+shift+space") == "<ctrl>+<shift>+<space>"


def test_spaces_and_case():
    assert to_pynput_combo(" Ctrl + Space ") == "<ctrl>+<space>"