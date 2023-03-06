import epac_data_py_skeleton.hello


def test_magic_number() -> None:
    number = epac_data_py_skeleton.hello.magic_number()
    assert number == 42
