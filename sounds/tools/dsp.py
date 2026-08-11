"""Tiny DSP toolkit for deriving XEvil 2.5 sounds from the 1994 palette.

Everything renders to the original delivery format: 8-bit unsigned PCM,
11025 Hz, mono.  Pitch shifting is plain varispeed (resampling), the way a
period sampler would have done it -- pitch and length move together.

Requires numpy and scipy.  Every step is deterministic (including the dither,
which is seeded), so make_sounds.py reproduces the shipped WAVs byte for byte;
see `make_sounds.py --check`.
"""
import os
import wave
import numpy as np
from fractions import Fraction
from scipy.signal import butter, sosfilt, resample_poly

RATE = 11025

# The palette lives in the parent directory of this one (sounds/tools -> sounds).
SOUNDS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(SOUNDS_DIR, '%s.wav')


# ---------------------------------------------------------------- io

def read(name):
    """Read a palette WAV as float64 in [-1,1] at RATE."""
    w = wave.open(SRC % name, 'rb')
    n, sw, fr, nch = (w.getnframes(), w.getsampwidth(),
                      w.getframerate(), w.getnchannels())
    raw = w.readframes(n)
    w.close()
    if sw == 1:
        a = (np.frombuffer(raw, dtype=np.uint8).astype(np.float64) - 128.0) / 128.0
    elif sw == 2:
        a = np.frombuffer(raw, dtype='<i2').astype(np.float64) / 32768.0
    else:
        raise ValueError('%s: unsupported sample width %d' % (name, sw))
    if nch > 1:
        a = a.reshape(-1, nch).mean(axis=1)
    if fr != RATE:
        f = Fraction(RATE, fr).limit_denominator(1000)
        a = resample_poly(a, f.numerator, f.denominator)
    return a.astype(np.float64)


def write8(path, x, peak_target, fade_ms=20.0):
    """Render to 8-bit unsigned / 11025 Hz / mono at an exact peak level."""
    x = np.asarray(x, dtype=np.float64)
    x = hp(x, 30.0, 2)                      # kill DC/rumble 8 bits cannot hold
    if fade_ms > 0:
        x = fade_out(x, fade_ms)
        x = fade_in(x, min(1.5, fade_ms))   # just enough to avoid a DC step
    p = np.abs(x).max()
    if p <= 0:
        raise ValueError('silent output')
    x = x * (peak_target / p)

    # TPDF dither at +/-0.5 LSB, but only where there is signal, so silence
    # quantises to exact 128 (digital silence) like the originals.
    lsb = 1.0 / 128.0
    rng = np.random.default_rng(19940101)
    d = (rng.random(len(x)) - rng.random(len(x))) * 0.5 * lsb
    d *= (moving_max(np.abs(x), int(RATE * 0.005)) > 0.75 * lsb)

    q = np.round((x + d) * 127.0) + 128.0
    lo, hi = q.min(), q.max()
    q = np.clip(q, 0, 255).astype(np.uint8)

    w = wave.open(path, 'wb')
    w.setnchannels(1)
    w.setsampwidth(1)
    w.setframerate(RATE)
    w.writeframes(q.tobytes())
    w.close()
    return dict(n=len(q), dur=len(q) / float(RATE), peak=peak_target,
                rails=int((q == 0).sum() + (q == 255).sum()),
                pre_lo=lo, pre_hi=hi)


def moving_max(x, k):
    if k < 1:
        return x
    pad = np.concatenate([np.zeros(k), x, np.zeros(k)])
    out = np.zeros(len(x))
    for i in range(-k, k + 1):
        out = np.maximum(out, pad[k + i:k + i + len(x)])
    return out


# ---------------------------------------------------------------- pitch/time

def speed(x, factor):
    """Play x `factor` times faster: length /= factor, pitch *= factor."""
    if abs(factor - 1.0) < 1e-9:
        return x.copy()
    f = Fraction(1.0 / factor).limit_denominator(600)
    return resample_poly(x, f.numerator, f.denominator).astype(np.float64)


def pitch(x, semitones):
    """Varispeed pitch shift; negative = lower and longer."""
    return speed(x, 2.0 ** (semitones / 12.0))


# ---------------------------------------------------------------- filters

def _sos(kind, freqs, order):
    ny = RATE / 2.0
    if isinstance(freqs, (list, tuple)):
        wn = [min(f / ny, 0.995) for f in freqs]
    else:
        wn = min(freqs / ny, 0.995)
    return butter(order, wn, kind, output='sos')


def lp(x, f, order=4):
    return sosfilt(_sos('low', f, order), x)


def hp(x, f, order=4):
    return sosfilt(_sos('high', f, order), x)


def bp(x, lo, hi, order=4):
    return sosfilt(_sos('band', [lo, hi], order), x)


# NOTE: this toolkit deliberately contains NO resonator.  A two-pole resonator
# (or any high-Q ring filter) sets the ring frequency from its own coefficients,
# not from the excitation -- feed it any click and you get the filter's tone, so
# the result is synthesised rather than derived.  An earlier draft of mine_arm
# used one at 1750 Hz and the "stays in the family" claim did not survive it.
# Every pitch here is inherited, by varispeed only; filters may remove bands but
# never invent one.


# ---------------------------------------------------------------- envelopes

def sat(x, drive):
    """Gentle soft saturation -- restores the density of the 1994 originals
    (death.wav has 4187 samples pinned to the rails) without any hard clip."""
    p = np.abs(x).max()
    if p <= 0:
        return x
    return np.tanh(drive * x / p) / np.tanh(drive) * p


def t_of(x):
    return np.arange(len(x)) / float(RATE)


def decay(x, tau, hold=0.0):
    t = t_of(x)
    e = np.ones(len(x))
    m = t > hold
    e[m] = np.exp(-(t[m] - hold) / tau)
    return x * e


def swell(x, peak_at=0.35, shape=1.6):
    """Rise-then-fall whoosh envelope over the whole buffer."""
    n = len(x)
    t = np.linspace(0.0, 1.0, n)
    up = np.clip(t / peak_at, 0, 1) ** shape
    dn = np.clip((1.0 - t) / (1.0 - peak_at), 0, 1) ** shape
    return x * np.minimum(up, dn) / max(np.minimum(up, dn).max(), 1e-9)


def fade_out(x, ms):
    k = min(int(RATE * ms / 1000.0), len(x))
    x = np.array(x, dtype=np.float64)
    if k > 1:
        x[-k:] *= np.linspace(1.0, 0.0, k)
    return x


def fade_in(x, ms):
    k = min(int(RATE * ms / 1000.0), len(x))
    x = np.array(x, dtype=np.float64)
    if k > 1:
        x[:k] *= np.linspace(0.0, 1.0, k)
    return x


def cut(x, a, b=None):
    """Slice by seconds."""
    i = int(a * RATE)
    j = len(x) if b is None else min(int(b * RATE), len(x))
    return np.array(x[i:j], dtype=np.float64)


def pad_to(x, seconds):
    n = int(seconds * RATE)
    if len(x) >= n:
        return np.array(x[:n], dtype=np.float64)
    return np.concatenate([x, np.zeros(n - len(x))])


def lay(dst, src, at=0.0, gain=1.0):
    """Mix src into dst at `at` seconds, growing dst as needed."""
    o = int(at * RATE)
    need = o + len(src)
    if need > len(dst):
        dst = np.concatenate([dst, np.zeros(need - len(dst))])
    dst[o:o + len(src)] += src * gain
    return dst


def blank(seconds=0.0):
    return np.zeros(int(seconds * RATE))
