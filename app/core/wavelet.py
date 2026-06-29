"""Wavelet decomposition for multi-scale trend detection.

Pure-Python by default (PyWavelets, else a Haar fallback). A MATLAB hook is
stubbed behind ``USE_MATLAB`` for the thesis extension and is never required.
"""
from __future__ import annotations


def _haar_levels(signal: list[float], levels: int) -> list[list[float]]:
    """Minimal Haar approximation coefficients per level (no external deps)."""
    out, cur = [], list(signal)
    for _ in range(levels):
        if len(cur) < 2:
            break
        approx = [(cur[i] + cur[i + 1]) / 2 for i in range(0, len(cur) - 1, 2)]
        out.append(approx)
        cur = approx
    return out


def decompose(signal: list[float], levels: int = 3, use_matlab: bool = False) -> dict:
    """Return approximation coefficients per level plus the method used."""
    if use_matlab:
        try:
            import matlab.engine  # noqa: WPS433 (thesis-only optional)

            eng = matlab.engine.start_matlab()
            coeffs = eng.wavedec(matlab.double(signal), levels, "db4", nargout=2)
            eng.quit()
            return {"method": "matlab_db4", "levels": coeffs}
        except Exception:
            pass  # fall through to Python

    try:
        import pywt  # noqa: WPS433

        coeffs = pywt.wavedec(signal, "db4", level=levels)
        return {"method": "pywt_db4",
                "levels": [list(map(float, c)) for c in coeffs]}
    except Exception:
        return {"method": "haar_fallback", "levels": _haar_levels(signal, levels)}
