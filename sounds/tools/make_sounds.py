#!/usr/bin/env python3
"""Derive the XEvil 2.5 sound assets from the original 1994/2000 palette.

Every new sound is built only from bytes that already ship with the game:
pistol/laser/lancer/swapper/ninja_attack/death/bang.  Output is the original
delivery format -- 8-bit unsigned PCM, 11025 Hz, mono.

This is the actual generator for the six 2.5 WAVs in ../ -- it is deterministic
and reproduces them byte for byte, so the provenance story in ../README.md can
be re-checked from the repository rather than taken on trust.

Usage:  make_sounds.py <outdir>     regenerate into <outdir>
        make_sounds.py --check      regenerate into a temp dir and diff the
                                    bytes against the shipped ../*.wav
"""
import os
import sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dsp import (RATE, SOUNDS_DIR, read, write8, speed, pitch, lp, hp, bp, sat,
                 decay, swell, fade_out, cut, pad_to, lay, blank)


def norm_to(x, ref, ratio):
    """Scale x so its peak sits `ratio` times ref's peak."""
    p = np.abs(x).max()
    return x * (ratio * np.abs(ref).max() / p) if p > 0 else x


# ---------------------------------------------------------------- shotgun
def shotgun():
    """pistol.wav doubled against a -6 st copy; tail cut short.  A BOOM."""
    p = read('pistol')

    # The report itself, tail clamped from pistol's 1.05 s ring-out to ~0.25 s.
    crack = cut(decay(p, 0.14, hold=0.045), 0, 0.55)

    mix = blank(0.0)
    mix = lay(mix, crack, 0.000, 1.00)
    mix = lay(mix, crack, 0.020, 0.35)   # the doubled barrel slap

    # Weight: the same pistol six semitones down, dark and slower to fall.
    # Kept off the transient so the sum peaks on the crack, not on the boom --
    # otherwise normalising the mix buries the attack.
    deep = hp(lp(pitch(p, -6.0), 2200.0, 4), 120.0, 2)
    deep = cut(decay(deep, 0.22, hold=0.050), 0, 0.60)
    mix = lay(mix, deep, 0.010, 0.95)

    return sat(cut(mix, 0, 0.62), 2.0), 0.94


# ---------------------------------------------------------------- railgun
def railgun():
    """laser.wav -3 st under a lancer.wav crack, with a rung-out tail."""
    L = read('laser')
    A = read('lancer')

    body = decay(pitch(L, -3.0), 0.90)
    crack = bp(pitch(A, -1.0), 500.0, 5200.0, 4)
    crack = cut(decay(crack, 0.22, hold=0.02), 0, 0.30)

    # Lengthened tail: laser's sustain dropped most of an octave, ringing down.
    tail = bp(pitch(cut(L, 0.12, 0.46), -9.0), 180.0, 3000.0, 4)
    tail = decay(tail, 0.22)

    mix = blank(0.0)
    mix = lay(mix, body, 0.000, 0.85)
    mix = lay(mix, crack, 0.000, 1.10)
    mix = lay(mix, tail, 0.400, 0.55)
    return sat(cut(mix, 0, 0.88), 1.8), 0.94


# ---------------------------------------------------------------- cryo
def cryo():
    """swapper.wav reversed and -4 st, ending in a high crystalline snap."""
    S = read('swapper')
    R = S[::-1].copy()

    base = lp(pitch(R, -4.0), 4000.0, 4)

    shimmer = decay(pitch(hp(R, 2600.0, 4), 5.0), 0.10)
    shimmer = norm_to(shimmer, base, 0.75)

    mix = blank(0.0)
    mix = lay(mix, base, 0.000, 1.00)
    mix = lay(mix, shimmer, 0.330, 1.00)
    return cut(mix, 0, 0.56), 0.80


# ---------------------------------------------------------------- vampire
def vampire_attack():
    """ninja_attack.wav -4 st with a breath layer filtered out of death's tail."""
    N = read('ninja_attack')
    D = read('death')

    base = pitch(N, -4.0)

    breath = bp(cut(D, 1.13, 1.36), 260.0, 2200.0, 4)
    breath = speed(breath, 0.75)                     # more air, lower rasp
    breath = pad_to(breath, len(base) / float(RATE))
    breath = swell(breath, 0.40)
    breath = norm_to(breath, base, 0.60)

    mix = blank(0.0)
    mix = lay(mix, base, 0.000, 1.00)
    mix = lay(mix, breath, 0.020, 1.00)
    return cut(mix, 0, 0.40), 0.45


def vampire_death():
    """death.wav at 0.8x over a -7 st moan of itself."""
    D = read('death')

    slow = speed(cut(D, 0.0, 1.15), 0.80)
    moan = lp(pitch(cut(D, 0.0, 1.00), -7.0), 900.0, 4)

    mix = blank(0.0)
    mix = lay(mix, slow, 0.000, 1.00)
    mix = lay(mix, moan, 0.000, 0.55)
    # death.wav is slammed into the rails; soft saturation gets that density
    # back after the layered mix has been scaled down to fit.
    return fade_out(sat(cut(mix, 0, 1.45), 2.2), 140.0), 0.94


# ---------------------------------------------------------------- mine
def mine_arm():
    """bang.wav on fast-forward, struck twice: contact tick, then latch.

    Pure varispeed, nothing else.  bang played 14x faster is a 17.7 ms tick
    whose whole spectrum is bang's own spectrum translated up by 14 -- the way
    a sampler transposes a one-shot -- so its peak lands near 890 Hz, bang's
    own low hump carried up.  The latch under the second strike is the same
    bang at 7x, i.e. the identical waveform one octave lower.  Every frequency
    in the result is one of bang's, scaled by a known ratio; there is no filter
    tone anywhere in it.  family.py checks that against the shipped bang.wav.
    """
    B = read('bang')

    tick = fade_out(speed(B, 14.0), 2.0)    # 17.7 ms
    latch = fade_out(speed(B, 7.0), 3.0)    # 35.3 ms, one octave lower

    mix = blank(0.0)
    mix = lay(mix, tick, 0.000, 1.00)
    mix = lay(mix, tick, 0.150, 0.70)
    mix = lay(mix, latch, 0.150, 0.25)      # second strike lands lower and longer
    return cut(mix, 0, 0.30), 0.80


SOUNDS = [
    ('shotgun.wav', shotgun),
    ('railgun.wav', railgun),
    ('cryo.wav', cryo),
    ('vampire_attack.wav', vampire_attack),
    ('vampire_death.wav', vampire_death),
    ('mine_arm.wav', mine_arm),
]


def generate(outdir):
    os.makedirs(outdir, exist_ok=True)
    for name, fn in SOUNDS:
        x, peak = fn()
        info = write8(os.path.join(outdir, name), x, peak)
        print('%-20s %6d frames  %.3fs  peak=%.3f  rails=%d  '
              'pre[%.1f..%.1f]' % (name, info['n'], info['dur'], info['peak'],
                                   info['rails'], info['pre_lo'], info['pre_hi']))


def check():
    """Regenerate and compare byte-for-byte with the shipped assets."""
    import tempfile
    bad = 0
    with tempfile.TemporaryDirectory() as tmp:
        generate(tmp)
        print()
        for name, _ in SOUNDS:
            a = open(os.path.join(tmp, name), 'rb').read()
            shipped = os.path.join(SOUNDS_DIR, name)
            b = open(shipped, 'rb').read() if os.path.exists(shipped) else None
            if b is None:
                print('%-20s MISSING in %s' % (name, SOUNDS_DIR))
                bad += 1
            elif a == b:
                print('%-20s identical (%d bytes)' % (name, len(a)))
            else:
                print('%-20s DIFFERS (%d vs %d bytes)' % (name, len(a), len(b)))
                bad += 1
    print('\nregeneration: %s' % ('byte-identical' if not bad else '%d MISMATCH' % bad))
    return 1 if bad else 0


def main(argv):
    if len(argv) > 1 and argv[1] == '--check':
        return check()
    generate(argv[1] if len(argv) > 1 else '.')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
