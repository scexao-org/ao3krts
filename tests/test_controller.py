import pytest

from aorts.control.foc_offloader import FocusLGSOffloader


class FocusLGSOffloaderSpoof(FocusLGSOffloader):
    FPS_NAME = 'foc_offl_test'


@pytest.fixture(scope="module")
def focusLGSOffloader(request):

    foc_ctrl = FocusLGSOffloaderSpoof()

    def teardown():
        foc_ctrl.fps.disconnect()
        foc_ctrl.fps.destroy()

    request.addfinalizer(teardown)

    return foc_ctrl


def test_focoff_basic(focusLGSOffloader):
    assert focusLGSOffloader.fps is not None

    assert "in_stream" in focusLGSOffloader.fps.key_types

    focusLGSOffloader.set_input_stream('yolo')
    assert focusLGSOffloader.fps['in_stream'] == 'yolo'


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
