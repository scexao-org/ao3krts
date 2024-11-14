import pytest

from aorts.control.foc_offloader import FocusLGSOffloader


@pytest.fixture(scope="module")
def focusLGSOffloader(request):

    # No FPS name spoofing required since we're running the MILK_SHM_DIR override fixture
    # automaticaly
    foc_ctrl = FocusLGSOffloader()

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
