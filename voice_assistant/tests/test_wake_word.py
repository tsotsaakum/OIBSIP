from src.wake_word import is_wake, is_wake_only, strip_wake


def test_strip_wake_keeps_command():
    assert strip_wake("Lentswe, the date").lower().startswith("the date")


def test_is_wake():
    assert is_wake("hey lentswe weather")
    assert not is_wake("weather in cape town")


def test_wake_only():
    assert is_wake_only("Lentswe")
    assert not is_wake_only("Lentswe, the date")
