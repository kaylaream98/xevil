# Changelog

All notable changes in the **XEvil 2.5** revival, relative to the last official
release, **XEvil 2.02** (Steve Hardt & Michael Judge, 2000). Grouped by area.

## [2.5] — 2026

### Sound & music (new — X11/UNIX had none before)
- Real `SoundManager` on the vendored **miniaudio** engine, with lazy
  initialization and a graceful silent fallback when no audio device is present
  (so headless / no-soundcard machines still run).
- All **26 original sound effects** play, with stereo panning and
  distance-based attenuation. The WAVs were recovered from the official
  `xevil-windows.exe` and are documented in `sounds/README.md`.
- All **nine original MIDI soundtracks** stream, chosen per game style.
- **terraexm** restored to the rotation — it shipped in every copy since 2000
  but was `#if 0`'d out because it *"sounds really painful on cheap sound
  cards."*
- **WOOB.WAV**, orphaned in the original Win32 resources and never played, is
  now the collapse sound of the new Singularity weapon.
- **Six new effects for the 2.5 content** — shotgun, railgun, cryo ray, vampire
  attack and death, and a mine-arming click — so it stops borrowing the pistol's
  and the ninja's. Each is *derived* from the recovered 1994 samples by
  varispeed, filtering and layering; no material from outside the original
  palette is used. The generator ships in `sounds/tools/`
  (`make_sounds.py --check` reproduces all six byte for byte) alongside
  `family.py --selftest`, which scores each file against the sources its recipe
  declares and measures its own ability to reject impostors.
- New flags: `-no_sound`, `-sound_volume <0-100>`, `-music_volume <0-100>`.
  Network clients request the server's sound relay.

### Weapons
- **Shotgun** — fires a three-shell spread.
- **Railgun** — a single fast, piercing Rail shot. The Rail travels 60px per
  turn against a 30px beam, and XEvil's collision test only ever looks at the
  discrete stops, so it used to fly straight past people (measured: it hit on
  43 of the 60 possible 1px alignments head-on, 38 of 60 diagonally) and
  through one-block walls. `Rail::act()` now sweeps the segment it crosses each
  turn in sub-steps no longer than the beam itself: 60/60 alignments hit, each
  victim damaged exactly once however many sub-steps see it, and a Rail stops
  at the first wall on its path instead of coming out the far side.
- **Cryo Ray** — fires an IceBolt that freezes/stuns what it hits.
- **Singularity** — lobbed like a grenade; anchors, drags every nearby moving
  thing into its collapse (a GravityWell), then explodes. Voiced by WOOB.
- **Proximity Mine** — blinks, arms, and detonates when something approaches.

### Creatures
- **Vampire** — a Walking/Fighter/Healing palette-swap of the Hero with a new
  `melee_hit_hook` that steals health on landed hits only.
- The random enemy pool grew from **8 to 12 classes**: Dogs, Mutts, and
  Chickens now spawn in ordinary levels at treat-tier weights (8/5/4).

### Scenarios (added to the random rotation and the `-scenario` override list)
- **Melt the Yetis** (`-scenario yeti`) — fire weapons vs. heat-sensitive yetis.
- **The Graveyard Shift** (`-scenario graveyard`) — chainsaws vs. 25 zombies.
- **The Nest** (`-scenario hugger-nest`) — a dense egg/hugger hive.
- **Junkyard Dogs** (`-scenario junkyard`) — a mutt pack.

### Game styles
- **Survival** (`-survival`) — endless escalating waves; a Fire Demon every
  fifth wave.
- **Boss Rush** (`-bossrush`) — a Fire Demon / Dragon / Yeti boss cycle.

### AI
- Difficulty-gated smartness: on **hard** and **bend-over**, enemies use
  distance-weighted target selection, check line of sight before firing, lead
  moving targets, and hunt the human players. **Trivial** and **normal**
  behavior is unchanged.

### Worlds
- Six handcrafted worlds in `worlds/`: **citadel, catacombs, skyline, arena,
  vertigo, depths**. Load any with `-world <file>`; the `.xew` format is plain
  text (see `world1.xew`).

### Attract-mode demo
- Three new demo scenes join the eight originals (`Game::demo_setup` now picks
  from eleven): **Vampire hunt** (Heroes vs. Vampires), **New arms expo**
  (Ninjas fighting over the 2.5 arsenal), and **Singularity storm** (Heroes
  dueling with WOOB singularities amid collapsing gravity wells).

### Quality of life
- **F1** pauses the game and shows a visible **PAUSED** overlay.
- **`-scale <1-4>`** (X11): integer display scaling for modern / HiDPI screens.
- Persistent **`~/.xevilrc`** config (v2 format; still readable by pre-2.5
  builds) remembers your settings between sessions.
- **`~/.xevil_scores`** — a top-10 high-score table stamped with Hell-rank
  titles.
- New **Sound**, **Survival**, and **Boss Rush** entries in the menu bar.
- Version strings bumped to **2.5** (network protocol `XETP2.5X`); `-help` now
  documents flags that were previously undocumented.
- **Every New Game asks for the difficulty**, with your last choice highlighted
  as the default that `[space]`/`[enter]` accepts. 2.02 asked once per process
  and then locked the answer in for the rest of the session — which, once 2.5
  started remembering the choice in `~/.xevilrc`, meant a player could never
  change it again. `-difficulty <name>` still pins one and skips the prompt.
- **Two fullscreen looks** (SDL): `fullscreen_mode=fill` in `~/.xevilrc` (the
  default, and pixel-for-pixel the classic picture — the game stretched to the
  screen with the aspect ratio kept) or `fullscreen_mode=crisp` (whole-pixel
  scaling in a black surround: sharper, smaller). Also `-fullscreen_fill` /
  `-fullscreen_crisp`; **F11** toggles fullscreen at any time. An `.xevilrc`
  written before 2.5 has no `fullscreen_mode=` line and so keeps `fill`.

### Build
- Plain **`make`** now auto-detects the architecture (`uname -m`) and builds
  without hand-set environment variables; the binary lands at
  `x11/REDHAT_LINUX/xevil` on x86-64.
- New **`make debug`** target (`-O0 -g` into `x11/DEBUG/`) and a **`make
  clean`** that removes every real objdir.
- Builds and runs on **Windows 11 / WSL2** via WSLg (display and audio work out
  of the box).
- Normal quit now `exit(0)`s cleanly.

### Native Windows port (Wave 4)
- A **single self-contained `xevil.exe`** for 64-bit Windows, cross-compiled
  from the *same* sources as the Linux build with **mingw-w64**. No DLLs, no
  asset folders: SDL2, libgcc, libstdc++ and **all 33 sound effects + 9 music
  tracks are statically linked / embedded into the one file** (~35 MB stripped;
  the release zip is 29.4 MiB). Copy it anywhere and double-click.
- New **SDL2 front end** (`sdl/`) — a portable, X11-independent frontend the
  engine renders through, so the identical `cmn/` engine drives both the Linux
  `xevil-sdl` and the Windows `xevil.exe`. The classic X11/Xlib build is
  untouched and remains the default `make` target.
- Genuine-OS code keyed on `_WIN32` for the port: **winsock2** sockets
  (`WSAStartup`/`closesocket`, `-lws2_32`), `rand()` in place of `random()`,
  `SIGPIPE` guarded out, and config/scores relocated to **`%APPDATA%\XEvil\`**
  (`.xevilrc`, `.xevil_scores`) when there is no `$HOME`. The MFC `WIN32` flag
  is neutralized with `-UWIN32` so the X11-flavor arms stay live, exactly as on
  Linux.
- Audio auto-selects **WASAPI** via miniaudio on Windows, with the same
  graceful silent fallback when no audio device is present.
- Build targets: **`make windows`** (cross-compile the exe) and
  **`make dist-windows`** (package `dist/xevil.exe` + `dist/XEvil-2.5-win64.zip`
  with a `README-WINDOWS.txt`). The static SDL2 devel copy is vendored under
  `sdl/vendor/SDL2-mingw` for reproducible builds.
- Verified end-to-end under Wine: license → New Game → difficulty → play (move,
  climb, grab, fire weapons), F1 pause, Help, chat, death → game over → high
  score written, restart, clean quit; plus `-survival`, `-human_class dragon`,
  `-fullscreen`/F11 and `-scale` clamping.

### Bug fixes (carried over from the 2.5 modernization)
- `Item::dieMessage` changed from `Boolean` to the `MESSAGE` enum, so destroyed
  items say *"is destroyed."* again.
- Font fallback chain so modern X servers without the `6x13` font no longer
  `exit(1)`.
- `XkbKeycodeToKeysym` keycode handling; signed-`char` map-indexing fix.
- Added a virtual destructor to `ITickRenderer`; fixed a delete-`void*` closure
  undefined-behavior bug.
- Bounded several network-reachable `strcpy`s.

### Bugs inherited from 2.02, fixed here
- **The Altar of Sin works again.** On 20 June 2000 Steve Hardt gave
  `Physical::corporeal_attack()` a third parameter and never reopened
  `actual.h`, so four declarations there silently stopped overriding anything.
  Three were harmless; the fourth was the Altar's whole second face. For 26
  years attacking the Altar did nothing to you *and* the base implementation
  quietly made the Altar destructible — you could shoot it dead. The signature
  is restored, so the frog/baby-seal curse and the *"BLASPHMER!"* drain run
  again and the Altar absorbs everything. `Fire`'s matching declaration is
  deliberately left as found: it is the one of the four that is reachable, so
  restoring it would change gameplay rather than tidy a header. The full
  history is in `docs/archaeology.md`, *"The Altar's wrath, dated."*
- **`User::drop_all()` could hang the game.** The loop dropped weapons until
  the count reached zero, but `weapon_drop()` is a no-op whenever the selection
  arithmetic cannot reach a slot — a weapon whose coolness exactly equals the
  wielder's built-in, or one whose `Id` the Locator no longer resolves, sits in
  a permanent blind spot. The count then never fell and the loop spun forever;
  this is what the original *"BUG, can get into an infinite loop here from
  `User::drop_all`"* note warned about. Both loops now have a forward-progress
  guarantee, and `weapon_drop()` resolves *reserved* Locator entries too, so a
  weapon picked up earlier in the same turn is no longer undroppable.

### Known cosmetic note
- `config.mk`'s `VERSION` (used only for the packaged tarball name) still reads
  `2.1` from the 2.02 tree; it does not affect the in-game version, which is
  2.5 everywhere it is shown.
