# tests/test_frontend_utils.py
from frontend.utils import _safe_roas

def test_safe_roas_basic():
    assert _safe_roas(200.0, 100.0) == 2.0
    assert _safe_roas(0.0, 0.0) == 0.0
    assert _safe_roas(100.0, 0.0) == 0.0
