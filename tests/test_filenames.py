from src.util.filenames import sanitize_id_to_filename


def test_sanitize_digits_only():
    assert sanitize_id_to_filename("12345") == "12345_carve.nc"


def test_sanitize_mixed():
    assert sanitize_id_to_filename("12A-34#") == "12_34_carve.nc"


def test_empty_id():
    assert sanitize_id_to_filename("") == "id_carve.nc"

