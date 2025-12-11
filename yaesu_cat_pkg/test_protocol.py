from yaesu_cat_pkg import protocol


def test_build_get_set_freq():
    assert protocol.build_get_freq("FA") == b"FA;"
    assert protocol.build_get_freq("FB") == b"FB;"
    assert protocol.build_set_freq("FA", 14250000) == b"FA014250000;"
    assert protocol.build_set_freq("FB", 7100000) == b"FB007100000;"


def test_parse_freq_response():
    assert protocol.parse_freq_response(b"FA014250000;") == 14250000
    assert protocol.parse_freq_response(b"\x10FB007100000;") == 7100000
    import pytest
    with pytest.raises(ValueError):
        protocol.parse_freq_response(b"NO_DIGITS")

