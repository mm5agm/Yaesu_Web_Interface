import sys
import types
import time
import importlib
import importlib.util
from pathlib import Path


def make_fake_serial(responses=None):
    class FakeSerial:
        def __init__(self, *args, **kwargs):
            self.is_open = True
            self.writes = []
            # make a shallow copy so tests can pass a list literal
            self._responses = list(responses or [])

        def write(self, data):
            self.writes.append(data)

        def read_until(self, sep=b";"):
            if self._responses:
                return self._responses.pop(0)
            return b""

        def readline(self):
            return self.read_until()

        def reset_input_buffer(self):
            pass

        def flushInput(self):
            pass

        def close(self):
            self.is_open = False

    return FakeSerial


def prep_fake_serial_module(fake_class):
    mod = types.ModuleType("serial")
    mod.Serial = fake_class
    # provide constants used by main.py
    mod.EIGHTBITS = 8
    mod.PARITY_NONE = 'N'
    mod.STOPBITS_TWO = 2
    return mod


def load_main_module():
    # Load main.py from the repository root path to ensure import works under pytest
    repo_root = Path(__file__).resolve().parent.parent
    main_path = repo_root / 'main.py'
    spec = importlib.util.spec_from_file_location('main', str(main_path))
    module = importlib.util.module_from_spec(spec)
    sys.modules['main'] = module
    spec.loader.exec_module(module)
    return module


def test_set_freq_writes_command(tmp_path, monkeypatch):
    # fake serial will capture writes
    FakeSerial = make_fake_serial(responses=[])
    fake_mod = prep_fake_serial_module(FakeSerial)
    sys.modules['serial'] = fake_mod

    # import main after we've injected fake serial
    main = load_main_module()

    client = main.app.test_client()

    resp = client.post('/set_freq', json={'vfo': 'FA', 'hz': 14250000})
    assert resp.status_code == 200
    # main.ser should be instance of our FakeSerial
    assert hasattr(main, 'ser') and main.ser is not None
    assert main.ser.writes[-1] == b'FA014250000;'


def test_poll_updates_freq_and_freq_endpoint(monkeypatch):
    # prepare fake serial that will return FA then FB responses
    responses = [b'FA014250000;', b'FB007100000;']
    FakeSerial = make_fake_serial(responses=responses)
    fake_mod = prep_fake_serial_module(FakeSerial)
    sys.modules['serial'] = fake_mod

    # reload main to pick up fake serial
    main = load_main_module()

    # allow poll thread a short time to run
    time.sleep(0.1)

    client = main.app.test_client()
    r = client.get('/freq')
    assert r.status_code == 200
    j = r.get_json()
    assert j['frequency'] == '14.25000 MHz'
    assert j['frequency_b'] == '7.10000 MHz'
