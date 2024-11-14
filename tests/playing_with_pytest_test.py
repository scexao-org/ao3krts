import pytest


def square(x):
    if isinstance(x, (int, float)):
        return x**2
    raise ValueError()


# yapf: disable
@pytest.mark.parametrize('x, x_test', [
    (1,1),
    (0,0),
    (2,4),
    (-1,1),
    (100, 10000),
    # (0, 1),
    (1.5, 2.25),
    (3.14159265, 3.141592650000001**2),
    (1+1j, False)
]) # yapf: enable
def test_square(x, x_test):
    if isinstance(x, int):
        assert square(x) == x_test
    elif isinstance(x, float):
        assert square(x) == pytest.approx(x_test)
    else:
        with pytest.raises(ValueError):
            square(x)

def test_test_passes():
    assert True

def test_test_raises_w_success():
    with pytest.raises(Exception) as e_info:
        s = 1 / 0

def _test_test_fails():
    assert False

def test_wraps_test_fails():
    with pytest.raises(AssertionError) as e_info:
        _test_test_fails()

def _test_test_raises_something_else():
    with pytest.raises(OSError) as e_info:
        x = 1 / 0

def test_wraps_test_raises_something_else():
    with pytest.raises(ZeroDivisionError) as e_info:
        _test_test_raises_something_else()

def _test_test_fails_to_raise():
    with pytest.raises(OSError) as e_info:
        x = 1 / 1

def test_wraps_test_fails_to_raise():
    with pytest.raises(pytest.fail.Exception) as e_info:
        _test_test_fails_to_raise()
