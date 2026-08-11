# XEvil Sound Assets

The original XEvil 2.02 Windows build shipped its audio embedded as PE resources
inside `xevil.exe`. The X11/UNIX build never had sound at all
(`SoundNames::lookup()` in `cmn/sound_cmn.cpp` was a stub returning 0).

These files were recovered from the original `xevil-windows.exe` (2.02,
2000-01-19) distributed at http://www.xevil.com/download, extracted with
`wrestool --raw` and renamed per the resource-ID tables in
`win32/resource.h` and `cmn/bitmaps/sound_cmn/sound_cmn.bitmaps`.

## Sound effects (WAV, mostly 8-bit mono 11 kHz — authentic 90s)

| File | SoundName | Resource |
|---|---|---|
| chainsaw.wav | CHAINSAW_SOUND | IDW 818 |
| flamethrower.wav | FLAMETHROWER | IDW 819 |
| death.wav | DEATH | IDW 820 |
| seal_death.wav | SEAL_DEATH | IDW 821 |
| hugger_death.wav | HUGGER_DEATH | IDW 822 |
| frog_death.wav | FROG_DEATH | IDW 823 |
| breakdown.wav | BREAKDOWN | IDW 826 |
| bang.wav | BANG | IDW 827 |
| pistol.wav | PISTOL | IDW 832 |
| mgun.wav | MGUN | IDW 833 |
| launcher.wav | LAUNCHER | IDW 834 |
| explosion.wav | EXPLOSION | IDW 835 |
| dog_death.wav | DOG_DEATH | IDW 877 |
| laser.wav | LASER | IDW 878 |
| hero_attack.wav | HERO_ATTACK | IDW 879 |
| ninja_attack.wav | NINJA_ATTACK | IDW 880 |
| dog_attack.wav | DOG_ATTACK | IDW 881 |
| chop_death.wav | CHOP_DEATH | IDW 882 |
| doppel_use.wav | DOPPEL_USE | IDW 883 |
| cloak_use.wav | CLOAK_USE | IDW 884 |
| trans_use.wav | TRANS_USE | IDW 885 |
| shield_use.wav | SHIELD_USE | IDW 886 |
| ninja_death.wav | NINJA_DEATH | IDW 887 |
| froggun.wav | FROGGUN | IDW 888 |
| lancer.wav | LANCER | IDW 889 |
| swapper.wav | SWAPPER | IDW 890 |
| woob.wav | WOOB | *(none)* — `win32/res/WOOB.WAV` |

(IDW 824/830/831 wave soundtracks were already disabled in 2.02 and are not
present in the exe.)

**woob.wav** is the odd one out: the 5500-byte `WOOB.WAV` shipped in the
original `win32/res/` directory but had **no resource ID and no code reference**
— an orphaned *name* that never played in any release. XEvil 2.5 finally
gives it a job as the collapse sound of the new **Singularity** weapon
(`SoundNames::WOOB`, wired up on X11 only).

One caveat on that story, for honesty: `WOOB.WAV` and `BANGBANG.WAV` in
`win32/res/` are byte-identical (md5 `377c1038…`), and `BANGBANG.WAV` is what
`IDW_BANG` resolves to. So the *audio* was always audible in 2.02 as the BANG
sound — it is the filename `WOOB.WAV`, not the waveform, that was orphaned.
`sounds/bang.wav` and `sounds/woob.wav` are consequently the same 5500 bytes.

## XEvil 2.5 sound effects (derived, not sampled)

The 2.5 content originally reused classic sounds (shotgun = PISTOL, railgun =
LASER, cryo ray = SWAPPER, vampire = the ninja's). These six give it its own
voice **without introducing any new source material**: every one is built
entirely out of bytes already in the table above, using pitch/speed changes
(plain varispeed, the way a period sampler would), reversal, filtering,
layering, envelope shaping and soft saturation — then rendered back to the original
delivery format, 8-bit unsigned PCM / 11025 Hz / mono. No sample from outside
the 1994–2000 palette is present in any of them.

| File | SoundName | Derived from | Character |
|---|---|---|---|
| shotgun.wav | SHOTGUN | pistol.wav | The pistol's report doubled against a copy of itself six semitones down, tail cut from 1.05 s to 0.6 s — a heavier, blunter BOOM that still cracks like its parent. |
| railgun.wav | RAILGUN | laser.wav + lancer.wav | The laser three semitones down under a bandpassed lancer transient, with its own sustain dropped nine semitones and rung out behind it — a heavy energy CRACK with a long electric tail. |
| cryo.wav | CRYO | swapper.wav | The swapper played backwards and four semitones down, so it swells instead of fires, ending in a high crystalline snap made from a highpassed copy of itself — icy and alien, unmistakably swapper family. |
| vampire_attack.wav | VAMPIRE_ATTACK | ninja_attack.wav + death.wav | The ninja's whoosh four semitones down with a breath layer filtered out of the rasping tail of death.wav — the same strike, darker and wetter. |
| vampire_death.wav | VAMPIRE_DEATH | death.wav | The human death scream at 0.8× speed over a moan of itself seven semitones lower — slower, heavier, undead rather than merely dying. |
| mine_arm.wav | MINE_ARM | bang.wav | The bang itself on fast-forward — played 14× faster it collapses from a 247 ms thud to a 17 ms tick, and struck twice (the second over a copy at 7×, one octave lower) it reads as a latch closing. Dry and mechanical rather than electronic. |

All six are 8-bit unsigned PCM / 11025 Hz / mono (`soxi`), with no sample pinned
to either rail. Durations run from 0.185 s to 1.450 s; `mine_arm.wav` is the
short one, still longer than the palette's own shortest sample
(`frog_death.wav`, 0.131 s). Each one peaks within 3 dB of the classic sound it
sits beside — the largest gap is `mine_arm.wav` at 1.97 dB under `bang.wav`, the
rest are within 1 dB. Together they add 44,586 bytes (43.5 KiB).

### On "derived": reproduce it yourself

The generator is in the tree, not just described here. `tools/` holds the whole
derivation — `dsp.py` (the toolkit), `make_sounds.py` (the six recipes) and
`family.py` (the provenance test), ~800 lines of numpy/scipy between them:

```
python3 sounds/tools/make_sounds.py --check     # regenerate + diff the bytes
python3 sounds/tools/family.py --selftest       # provenance test + its own controls
```

`make_sounds.py` is deterministic down to its seeded dither, so `--check`
regenerates all six shipped WAVs **byte for byte**. That is the primary evidence
for everything on this page: the recipes are not a story told after the fact, they
are the code that produced the files.

`dsp.py` is the toolkit those recipes are written in. It deliberately contains
no resonator, and says so in a comment, for the reason below.

### Why pitch is inherited, never synthesised

Every pitch above comes from playing a source sample at a different rate —
varispeed, exactly what a period sampler did when you transposed a one-shot.
Filters appear only to *remove* bands (the lowpass under the shotgun's weight
layer, the highpass that makes the cryo shimmer), never to add one.

That distinction is load-bearing, because it is easy to fail by accident. A
resonant filter rings at whatever frequency its own coefficients specify no
matter what you excite it with, so "derived from bang.wav" can be true of the
*input* and still produce a tone the source does not contain. An earlier draft of
`mine_arm.wav` did precisely that: a bang-derived click through a 1750 Hz
two-pole resonator. Its audible pitch was the filter's, not the bang's — it
peaked at exactly 1750 Hz, the coefficient, and put 95% of its energy in
900–4200 Hz, a band where bang keeps 1.9% of its own (bang is a thud: 94% of it
lives below 300 Hz). It was replaced by the plain 14×/7× varispeed described
above.

That draft is kept as `tools/testdata/mine_arm_resonator_draft.wav` so the
failure it represents stays testable rather than anecdotal.

### The provenance test and what it is actually worth

`family.py` scores each shipped file against the sources its recipe declares,
after applying the declared varispeed ratios, on two axes:

| | shotgun | railgun | cryo | vamp_atk | vamp_death | mine_arm | gate |
|---|---|---|---|---|---|---|---|
| **waveform** (peak normalised cross-correlation with the resampled source) | 0.601 | 0.771 | 0.880 | 0.969 | 0.886 | 0.749 | ≥ 0.40 |
| **spectrum** (1/6-octave energy overlap with the ratio-shifted sources) | 0.835 | 0.873 | 0.910 | 0.766 | 0.965 | 0.863 | ≥ 0.70 |

The resonator draft scores **0.220 / 0.374** and fails both gates.

`--selftest` measures whether those gates have any power, instead of assuming it:

- **Substitution.** Every palette sound is dropped into every recipe slot it does
  not belong to — 154 combinations. All 154 are rejected. The best any impostor
  manages on waveform is 0.206 (`frog_death` as shotgun) against the 0.40 gate.
  On the spectral axis, though, the best impostor reaches **0.787** (`launcher`
  as shotgun) — **above the 0.70 gate**, so spectrum alone would have accepted
  it, and only its waveform score rejects it. Waveform correlation is what
  separates substitutions.
- **Addition.** A 1750 Hz resonance shaped by the sound's own envelope is mixed
  into each real file at rising energy. By the point it carries half the file's
  energy, the spectral axis rejects it on 6/6 — and waveform correlation rejects
  it on **0/6**, because a sound stays correlated with its source when something
  is piled on top. The spectral axis is what separates additions.

Neither number means much alone; that is the reason both are enforced and the
reason the self-test prints its own failure modes.

One figure that is **not** evidence, and is printed ungated for exactly that
reason: the peak-frequency ratio. `mine_arm.wav` peaks at 893.6 Hz and
`bang.wav` at 63.25 Hz on that grid, so dividing by the declared 14× lands
0.16 semitones from bang's own peak. That is arithmetic on real bins and it is
worth nothing as precision. `bang.wav` is 0.247 s long, so a peak down at 63 Hz
is localised no better than the analysis lobe — 16 Hz over the whole file, 22 Hz
on the 2048-sample Welch segments the script actually uses — which at 63 Hz is
±4 to ±5 *semitones*. Any sub-semitone agreement there is a coincidence of the
grid, and an earlier version of this file quoted one as if it were a
measurement. The claim that carries weight is the whole-spectrum one above.

Like `woob.wav` they have **no Win32 resource IDs** — the modern Windows build
is the SDL one, which embeds `sounds/*.wav` by filename via `sdl/gen_audio.py`,
so the `SoundNames::names[]` table in
`cmn/bitmaps/sound_cmn/sound_cmn.bitmaps` carries zeros for them purely to stay
aligned with `SOUND_MAX`.

That embedding is a flat `os.listdir` of this directory, so the six new files are
picked up with no manifest edit — and `tools/` and `tools/testdata/` are *not*,
being subdirectories. The generator's own count is the check: `gen_audio.py`
reports **42 assets, 29,688,786 bytes** embedded, the 36 originals plus these six.
The measured effect on the release download is +43.5 KiB of raw asset bytes
(35.8 KiB once deflated) inside a `dist/XEvil-2.5-win64.zip` of **29.424 MiB**
(the exe is stripped for the dist copy; see `make dist-windows`). The proportions
are worth stating plainly: the nine MP3 soundtracks are 27.9 MiB and deflate to
27.4, i.e. **93% of the download**, while all 33 sound effects together —
originals and 2.5 additions — come to 0.375 MiB.

`MINE_ARM` is emitted from the `!armed -> armed` transition in `Mine::act()`
(`cmn/actual.cpp`) — the moment a planted mine's ~2 s grace period expires and
it goes live — and not from the plant itself. `Mine::use()` deliberately does
not chain to `Item::use()`, so `ItemContext::useSound` stays 0 in
`cmn/bitmaps/mine/mine.bitmaps`: planting is silent, arming clicks, and the
Explosion object still makes the detonation noise.

## Music (original MIDI + pre-rendered MP3)

MP3s rendered with FluidSynth (FluidR3 GM soundfont) at 44.1 kHz / 128 kbps so
the game can stream them without a MIDI synth. The .mid originals are kept for
authenticity.

| File | SoundName | Resource | Notes |
|---|---|---|---|
| fire.mid/.mp3 | FIRE_SOUNDTRACK | IDM 1632 | |
| hive.mid/.mp3 | HIVE_SOUNDTRACK | IDM 1633 | |
| kill.mid/.mp3 | KILL_SOUNDTRACK | IDM 1634 | Kill'em All mode |
| seal.mid/.mp3 | SEAL_SOUNDTRACK | IDM 1630 | |
| zeepeeg.mid/.mp3 | ZEEPEEG_SOUNDTRACK | IDM 1635 | |
| nightsky.mid/.mp3 | NIGHTSKY_SOUNDTRACK | IDM 1636 | |
| sweetdark.mid/.mp3 | SWEETDARK_SOUNDTRACK | IDM 1637 | |
| terraexm.mid/.mp3 | (was disabled) | IDM 1638 | "sounds really painful on cheap sound cards" — restored |
| newsong.mid/.mp3 | NEWSONG_SOUNDTRACK | IDM 1639 | |

There is a tenth soundtrack that got away: `win32/resource.h:1009` defines
`IDM_DEATHMARCHSOUNDTRACK 1631` — the only surviving trace of a **"Death
March"** track. No `.mid`, no `.mp3`, and no code reference exists; the resource
is absent from the shipped exe, and the ID `1631` was even recycled for a wall
bitmap (`IDB_MD4WALL`). Truly lost unless an older 1.x / 2.0-beta build ever
surfaces. See `docs/archaeology.md`.

XEvil is GPL v2; these assets ship with the official free distribution.
