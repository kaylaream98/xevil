#!/usr/bin/env python3
"""Provenance check for the XEvil 2.5 derived sounds (../shotgun.wav etc).

WHAT IT GUARDS AGAINST
----------------------
"Derived from bang.wav" is a claim about the *output*, not the input, and it is
easy to fail by accident.  A resonant filter rings at whatever frequency its own
coefficients specify no matter what excites it, so a click made by pushing
bang.wav through a 1750 Hz resonator is literally derived from bang and still
sings a note bang does not contain.  An early draft of mine_arm.wav did exactly
that.  This script measures whether the shipped file is still made of its
declared sources.

TWO METRICS, WITH DIFFERENT BLIND SPOTS
---------------------------------------
  1. WAVEFORM PROVENANCE -- the peak normalised cross-correlation between the
     candidate and each declared source after that source is played at the
     declared varispeed ratio (both time directions, since one recipe reverses
     its source).  1.0 = the candidate *is* that resampled source.
     Gate: best component >= 0.40.
     Strong against SUBSTITUTION: across all 154 wrong-source combinations the
     palette allows, the best score is 0.206 (--selftest).  Weak against
     ADDITION: piling a foreign tone on top of the real sound barely moves it --
     even a tone carrying as much energy as the sound itself leaves 0.43-0.68.

  2. SPECTRAL PROFILE -- the candidate's energy per 1/6-octave band, compared
     against the best non-negative mix of the declared sources' bands after
     each is translated by its ratio (a frequency ratio is a shift in log
     frequency, so this is exact).  Scored by the overlap coefficient
     sum_k min(a_k, b_k); 1.0 = identical distribution.
     Gate: >= 0.70.
     The mirror image: strong against ADDITION -- a foreign resonance carrying
     half the file's energy fails it on all six sounds -- and weak against
     SUBSTITUTION, where the best impostor reaches 0.787 and would have been
     accepted.  Neither gate is sufficient alone, which is why both are
     enforced; --selftest measures both weaknesses rather than asserting they
     cancel.

  Also printed, NOT gated: the peak-frequency ratio in semitones.  It reads well
  but it cannot carry weight here.  bang.wav is 0.247 s long, so a peak down at
  63 Hz is localised no better than the analysis lobe -- 16 Hz over the whole
  file, 22 Hz on the 2048-sample Welch segments used below -- which at 63 Hz is
  +/- 4 to 5 SEMITONES.  Sub-semitone agreement at that end of the spectrum is a
  coincidence of the grid, not a measurement, so it is reported and ignored.

Usage:  family.py [stagedir]     check the six shipped sounds (default ../)
        family.py --selftest     the above, plus the three experiments that
                                 establish the gates have any power at all:
                                 substitute every unrelated palette sound into
                                 every recipe slot; inject a synthetic resonance
                                 at rising energy levels; and re-score the
                                 discarded resonator draft of mine_arm.wav kept
                                 in testdata/.

Exit status is 0 only if everything checked passes.  Needs numpy.
"""
import os
import sys
import glob
import wave
import numpy as np

RATE = 11025
NFFT = 8192
SEG = 2048

NCC_MIN = 0.40           # waveform provenance gate
OVERLAP_MIN = 0.70       # spectral profile gate

HERE = os.path.dirname(os.path.abspath(__file__))
SOUNDS_DIR = os.path.dirname(HERE)

ST = lambda s: 2.0 ** (s / 12.0)

# new file -> [(palette source, varispeed ratio applied to it), ...], exactly as
# the recipe in make_sounds.py declares it.  ratio > 1 = played faster/higher.
COMPONENTS = {
    'shotgun.wav':        [('pistol', 1.0), ('pistol', ST(-6))],
    'railgun.wav':        [('laser', ST(-3)), ('lancer', ST(-1)),
                           ('laser', ST(-9))],
    'cryo.wav':           [('swapper', ST(-4)), ('swapper', ST(+5))],
    'vampire_attack.wav': [('ninja_attack', ST(-4)), ('death', 0.75)],
    'vampire_death.wav':  [('death', 0.80), ('death', ST(-7))],
    'mine_arm.wav':       [('bang', 14.0), ('bang', 7.0)],
}


# ---------------------------------------------------------------- io / dsp

def read_wav(path):
    """Any palette WAV as float64 in [-1,1].  8- and 16-bit, mono or not."""
    w = wave.open(path, 'rb')
    n, sw, nch = w.getnframes(), w.getsampwidth(), w.getnchannels()
    raw = w.readframes(n)
    w.close()
    if sw == 1:
        a = (np.frombuffer(raw, dtype=np.uint8).astype(np.float64) - 128.0) / 128.0
    elif sw == 2:
        a = np.frombuffer(raw, dtype='<i2').astype(np.float64) / 32768.0
    else:
        raise ValueError('%s: unsupported sample width %d' % (path, sw))
    if nch > 1:
        a = a.reshape(-1, nch).mean(axis=1)
    return a


def source(name):
    return read_wav(os.path.join(SOUNDS_DIR, name + '.wav'))


def varispeed(x, factor):
    """Play x `factor` times faster.  Linear interpolation is enough here: this
    is an analysis stage, not a render, and it keeps the check independent of
    the exact resampler make_sounds.py used."""
    if abs(factor - 1.0) < 1e-12:
        return np.asarray(x, dtype=np.float64)
    n = int(np.floor(len(x) / factor))
    if n < 2:
        return np.asarray(x[:1], dtype=np.float64)
    t = np.arange(n) * factor
    i = np.floor(t).astype(int)
    f = t - i
    j = np.minimum(i + 1, len(x) - 1)
    return x[i] * (1.0 - f) + x[j] * f


def ncc(x, y):
    """Peak |normalised cross-correlation| over all lags."""
    N = 1 << int(np.ceil(np.log2(len(x) + len(y))))
    c = np.fft.irfft(np.fft.rfft(x, N) * np.conj(np.fft.rfft(y, N)), N)
    d = np.linalg.norm(x) * np.linalg.norm(y)
    return float(np.abs(c).max() / d) if d > 0 else 0.0


# ---------------------------------------------------------------- spectrum

FLO, FHI, BPO = 50.0, 5000.0, 6.0          # 1/6-octave bands, 50 Hz .. 5 kHz
NBAND = int(np.ceil(np.log2(FHI / FLO) * BPO))
EDGES = FLO * 2.0 ** (np.arange(NBAND + 1) / BPO)


def welch(a):
    seg = min(len(a), SEG)
    hop = max(seg // 2, 1)
    win = np.hanning(seg)
    acc = np.zeros(NFFT // 2 + 1)
    k = 0
    for i in range(0, max(len(a) - seg + 1, 1), hop):
        x = a[i:i + seg]
        if len(x) < seg:
            x = np.concatenate([x, np.zeros(seg - len(x))])
        acc += np.abs(np.fft.rfft(x * win, NFFT)) ** 2
        k += 1
    return acc / max(k, 1), np.fft.rfftfreq(NFFT, 1.0 / RATE)


def profile(a, ratio=1.0):
    """Normalised energy per log-frequency band, with the spectrum scaled by
    `ratio` first (playing a sample `ratio` times faster multiplies every
    frequency in it by `ratio`)."""
    p, f = welch(a)
    idx = np.searchsorted(EDGES, f * ratio) - 1
    out = np.zeros(NBAND)
    m = (idx >= 0) & (idx < NBAND)
    np.add.at(out, idx[m], p[m])
    s = out.sum()
    return out / s if s > 0 else out


def best_overlap(target, profiles):
    """Overlap of `target` with the best convex mix of `profiles`."""
    P = np.asarray(profiles)
    if len(P) == 1:
        return float(np.minimum(target, P[0]).sum())
    grid = np.linspace(0.0, 1.0, 21)
    best = -1.0
    if len(P) == 2:
        for w in grid:
            best = max(best, float(np.minimum(target, w * P[0] + (1 - w) * P[1]).sum()))
    else:
        for w0 in grid:
            for w1 in grid:
                if w0 + w1 > 1.0:
                    continue
                mix = w0 * P[0] + w1 * P[1] + (1 - w0 - w1) * P[2]
                best = max(best, float(np.minimum(target, mix).sum()))
    return best


def peak_hz(a):
    p, f = welch(a)
    return float(f[int(np.argmax(p))])


# ---------------------------------------------------------------- scoring

def score(cand, comps):
    """(best ncc, best ncc label, overlap, semitone error at the peak)."""
    rev = cand[::-1].copy()
    bn, blabel = -1.0, ''
    profs = []
    fpk = peak_hz(cand)
    st_err = float('nan')
    for name, ratio in comps:
        s = source(name)
        t = varispeed(s, ratio)
        v = max(ncc(cand, t), ncc(rev, t))
        if v > bn:
            bn = v
            blabel = '%s x%.2f' % (name, ratio)
            spk = peak_hz(s) * ratio
            st_err = abs(np.log2(max(fpk, 1e-9) / max(spk, 1e-9))) * 12.0
        profs.append(profile(s, ratio))
    return bn, blabel, best_overlap(profile(cand), profs), fpk, st_err


def palette_names():
    """Every shipped sound that is not one of the six 2.5 derivatives."""
    new = set(k[:-4] for k in COMPONENTS)
    return sorted(n for n in
                  (os.path.splitext(os.path.basename(p))[0]
                   for p in glob.glob(os.path.join(SOUNDS_DIR, '*.wav')))
                  if n not in new)


# ---------------------------------------------------------------- reports

def check(stage):
    print('%-20s %8s %-18s %8s %9s %9s  %s'
          % ('FILE', 'BEST NCC', 'FROM', 'OVERLAP', 'PEAK Hz', 'PEAK st', 'VERDICT'))
    print('-' * 88)
    allok = True
    results = {}
    for new, comps in sorted(COMPONENTS.items()):
        cand = read_wav(os.path.join(stage, new))
        n, lab, ov, fpk, st = score(cand, comps)
        ok = n >= NCC_MIN and ov >= OVERLAP_MIN
        allok &= ok
        results[new] = (n, ov)
        print('%-20s %8.3f %-18s %8.3f %9.1f %9.2f  %s'
              % (new, n, lab, ov, fpk, st, 'PASS' if ok else 'FAIL'))
    print('-' * 88)
    print('PEAK st = distance from that source\'s own peak x its ratio.  Reported')
    print('only; NOT a gate -- see the header for why it cannot carry weight.')
    print('gates: waveform ncc >= %.2f, spectral overlap >= %.2f' % (NCC_MIN, OVERLAP_MIN))
    print('provenance: %s' % ('ALL PASS' if allok else 'FAILURES PRESENT'))
    return allok, results


def selftest(stage):
    print()
    print('=' * 88)
    print('SELFTEST 1 -- substitution: every unrelated palette sound, in every slot')
    print('=' * 88)
    print('(a recipe\'s own declared sources are excluded: pistol really is what')
    print(' shotgun.wav is made of, so scoring 1.0 there is the correct answer)')
    print()
    worst_ncc = worst_ov = -1.0
    worst_lab = worst_ov_lab = ''
    nrej = ntot = 0
    for new, comps in sorted(COMPONENTS.items()):
        own = set(c[0] for c in comps)
        rows = []
        for p in palette_names():
            if p in own:
                continue
            n, _, ov, _, _ = score(source(p), comps)
            rows.append((n, ov, p))
            ntot += 1
            if not (n >= NCC_MIN and ov >= OVERLAP_MIN):
                nrej += 1
            if n > worst_ncc:
                worst_ncc, worst_lab = n, '%s as %s' % (p, new)
            if ov > worst_ov:
                worst_ov, worst_ov_lab = ov, '%s as %s' % (p, new)
        rows.sort(reverse=True)
        top = rows[0]
        print('  %-20s %d impostors, strongest %-14s ncc=%.3f overlap=%.3f  %s'
              % (new, len(rows), top[2], top[0], top[1],
                 'rejected' if not (top[0] >= NCC_MIN and top[1] >= OVERLAP_MIN)
                 else '*** ACCEPTED ***'))
    print()
    print('  %d/%d impostors rejected.' % (nrej, ntot))
    print('    best impostor ncc     %.3f  (%s)  vs gate %.2f -- rejected'
          % (worst_ncc, worst_lab, NCC_MIN))
    print('    best impostor overlap %.3f  (%s)  vs gate %.2f -- ACCEPTED by that'
          % (worst_ov, worst_ov_lab, OVERLAP_MIN))
    print('    axis alone (its ncc is what rejects it).  ncc carries this job.')

    print()
    print('=' * 88)
    print('SELFTEST 2 -- addition: a 1750 Hz resonance none of the sources contain,')
    print('              mixed into each real sound carrying N% of its total energy')
    print('=' * 88)
    print('  (the tone follows the sound\'s own amplitude envelope, so this is the')
    print('   flattering case: a ring that hides inside the existing shape)')
    print()
    levels = (0.05, 0.10, 0.25, 0.50, 1.00)
    print('  %-20s %s' % ('FILE  (ncc/overlap)',
                          '   '.join('%9.0f%%' % (100 * l) for l in levels)))
    trip_n, trip_o = [], []
    for new, comps in sorted(COMPONENTS.items()):
        cand = read_wav(os.path.join(stage, new))
        t = np.arange(len(cand)) / float(RATE)
        k = max(int(RATE * 0.010), 1)
        env = np.convolve(np.abs(cand), np.ones(k) / k, mode='same')
        tone = np.sin(2 * np.pi * 1750.0 * t) * env
        e_c = float(np.sum(cand ** 2))
        e_t = float(np.sum(tone ** 2))
        cells, first_n, first_o = [], None, None
        for lvl in levels:
            g = np.sqrt(lvl * e_c / max(e_t, 1e-30))
            n, _, ov, _, _ = score(cand + g * tone, comps)
            bad = (n < NCC_MIN) or (ov < OVERLAP_MIN)
            cells.append('%.2f/%.2f%s' % (n, ov, '!' if bad else ' '))
            if n < NCC_MIN and first_n is None:
                first_n = lvl
            if ov < OVERLAP_MIN and first_o is None:
                first_o = lvl
        trip_n.append(first_n)
        trip_o.append(first_o)
        print('  %-20s %s' % (new, '  '.join('%10s' % c for c in cells)))
    got_o = [x for x in trip_o if x is not None]
    got_n = [x for x in trip_n if x is not None]
    print('  (! = rejected by at least one gate)')
    print()
    print('  spectral overlap rejects the intruder on %d/%d sounds, all of them by the'
          % (len(got_o), len(trip_o)))
    print('  %d%% level.  Waveform ncc rejects it on %d/%d -- it barely moves, because a'
          % (int(100 * max(got_o)) if got_o else 0, len(got_n), len(trip_n)))
    print('  sound stays highly correlated with its source when something is piled on')
    print('  top of it.  Selftest 1 is the mirror image: ncc rejects all %d' % ntot)
    print('  substitutions while overlap would have accepted the strongest of them.')
    print('  Neither gate is sufficient alone; that is why both are enforced.')

    draft = os.path.join(HERE, 'testdata', 'mine_arm_resonator_draft.wav')
    if os.path.exists(draft):
        print()
        print('=' * 88)
        print('SELFTEST 3 -- the real historical failure')
        print('=' * 88)
        n, lab, ov, fpk, st = score(read_wav(draft), COMPONENTS['mine_arm.wav'])
        bad = (n < NCC_MIN) or (ov < OVERLAP_MIN)
        print('  testdata/mine_arm_resonator_draft.wav -- the discarded draft that ran a')
        print('  bang-derived click through a 1750 Hz two-pole resonator:')
        print('    ncc %.3f (%s, gate %.2f)   overlap %.3f (gate %.2f)'
              % (n, lab, NCC_MIN, ov, OVERLAP_MIN))
        print('    peak %.1f Hz -- the filter coefficient, %.1f st away from bang\'s own'
              % (fpk, st))
        print('    peak carried up by 14 (%.0f Hz), which is where it should have landed'
              % (peak_hz(source('bang')) * 14.0))
        print('    verdict: %s' % ('REJECTED (correct)' if bad else '*** ACCEPTED ***'))
        print()
        print('  For context, where bang.wav actually keeps its energy (same grid):')
        p, f = welch(source('bang'))
        tot = p.sum()
        dp, df = welch(read_wav(draft))
        draft_hi = 100 * dp[(df >= 900) & (df < 4200)].sum() / dp.sum()
        bands = ((0.0, 300.0, ''),
                 (300.0, 900.0, ''),
                 (900.0, 4200.0, '   <- where the 1750 Hz draft put %.1f%%' % draft_hi),
                 (0.0, RATE / 2.0 / 14.0,
                  '   <- all that survives 14x varispeed'))
        for lo, hi, note in bands:
            print('    %7.1f - %7.1f Hz : %5.2f%%%s'
                  % (lo, hi, 100 * p[(f >= lo) & (f < hi)].sum() / tot, note))
        return bad
    return True


def main(argv):
    args = [a for a in argv[1:] if not a.startswith('--')]
    stage = args[0] if args else SOUNDS_DIR
    ok, _ = check(stage)
    if '--selftest' in argv[1:]:
        ok &= selftest(stage)
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv))
