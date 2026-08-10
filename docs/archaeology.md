# XEvil Field Notes — Code Archaeology (2026 excavation)

Findings from a full source excavation of XEvil 2.02 (1994–2000, Steve Hardt &
Michael Judge), done during the XEvil 2.5 modernization. Everything below is
verifiable in this repo at the cited locations.

## The 26-year-old request
The instruction manual's sound section (`instructions/instructions.html`):

> "UNIX XEvil has no sound. But, with the source freely available, I'm sure
> some industrious soul could write it (hint, hint)."

`x11/sound.h` shipped as *"Dummy classes, only implemented on Windows. A place
holder if we ever implement sound on X."* The placeholder waited from 2000 to
2026. XEvil 2.5 answers it — with the original audio, recovered from the
official `xevil-windows.exe` still served by xevil.com.

## The banished soundtrack
`cmn/bitmaps/sound_cmn/sound_cmn.bitmaps:67-70`:
```c
#if 0
    // Nice piece but sounds really painful on cheap sound cards.
    IDM_TERRAEXMSOUNDTRACK,
#endif
```
`TERRAEXM.MID` shipped inside every copy of the game but was excluded from the
enum, the resource table, and the random rotation — unhearable for 26 years
because 2000-era sound cards butchered it. Restored in 2.5.

## The lost soundtrack
`win32/resource.h:1009` defines `IDM_DEATHMARCHSOUNDTRACK 1631` — the only
trace of a tenth music track, "Death March," anywhere. No file, no code
reference, and the resource is absent from the shipped exe; the ID number was
even recycled for a wall bitmap (`IDB_MD4WALL 1631`). Truly lost, unless an
older 1.x/2.0-beta build surfaces.

## The Fire Demon's ten souls (a player-discovered secret, confirmed)
`cmn/physical.h:3301`: *"Has limited protection from swap attacks. Unlimited
protection from Frog attacks."* Implementation (`physical.cpp:9566`): each
Soul-Swapper hit decrements a counter and fails; FireDemon ships with
`swapResistance = 9` (`fire_demon.bitmaps:220`) — **the 10th swap-shell hit
takes his soul**. He is the only creature in the game with this mechanic, and
`frog_protect()` returns unconditional True — the Frog Gun can never touch him.

## Green Hugger vs Red Hugger — one boolean apart
The entire difference (`hugger.bitmaps:201-366`) is `useHuggeeIntel`:
- **Red** (`False`): the burst Alien gets the *hugger's* mind; you get 1 point
  of damage first — comment: *"Do one point of damage to huggee, so hugger will
  get credit for the kill"* — and *"Huggee's intel dies with the huggee's
  physical body."*
- **Green** (`True`): the new Alien gets **your** mind (`alien->set_intel(
  huggee->get_intel())`, `physical.cpp:8672`) — *"No kill is awarded for this
  death."* Your body dies; you keep playing as the Alien (wall-crawling,
  spiky, regenerating — but no hands, so no weapons).
While latched, the hugger tracks its victim with: *"Guess where hugee's face
is, upper-left + (width/2, height*.3)"*.
The Green Hugger is also the statistically rarest creature: Hive scenario only,
egg-hatched, ~20% of hatches, and the one creature the Transmogrifier refuses
to create.

## Hell's org chart
`cmn/game.cpp:369-456` — end-of-game ranks by kills: "Hell's Peg Boy" →
"Satan's Earwax Remover" → "IS Tech Support for Hell" → "Teacher at Beelzebub
Jr. High" → "Hell's Sysadmin" → "Lead Software Engineer of Hell" (250 kills) →
at exactly **666** kills, *"Replace Bill as Satan's Right Hand Man"* (hello,
year-2000 Bill Gates joke) → at **666,666,666**, *"You are the new Satan."*
The difficulty above "hard" is named `bend-over`.

## The only file XEvil ever writes
`~/.xevilrc`, whose entire contents are (`x11/l_agreement_dlg.cpp:401`):
```
XEvil is your friend.  Trust XEvil.
```

## Developers thinking out loud, shipped to production
- Pet AI (`cmn/intel.cpp:2192,2220`): *"We don't use strategyChange timer at
  all?? Is this right?"* and *"Does this do anything??"*
- Rock-carrier attack (`intel.cpp:1296`): *"we don't really know how to drop
  weights on people"* — so it just lets go.
- Dog Whistle's alternate summon produces a facehugger instead of a dog,
  annotated *"ha, ha"* (`actual.cpp:3370`).
- Dead AI brains have their class name set to `"tormented spirit"` before
  deallocation (`intel.cpp` die path).
- The famous stuck-on-a-corner dog was fixed with dice: a 1-in-20 random +1 to
  enemy reaction time, deliberately desyncing brains from physics
  (`intel.cpp:1096-1106`).

## Hidden features never documented
- **`-human_class <name>`** — play as ANY of the 18 creatures: `dragon`
  (15-segment boss, with a dedicated assembly hack at `game.cpp:1727`),
  `fire-demon`, `yeti`, `chicken`, `baby-seal`, `zombie`, `mutt`...
  Companion `-ability flying|on-fire|sticky|hopping` stacks extra abilities.
- **F1 = pause**, code comment: *"Undocumented pause key feature"*
  (`x11/ui.cpp:482`).
- `-scenario exterminate` reaches a scenario cut from the rotation with the
  comment "We don't use it right now."
- The Windows build had `-cd`: play random audio-CD tracks as the soundtrack.
- `-gen_xpm <dir>`: the Windows build could auto-generate the UNIX XPM art —
  the art pipeline ran Windows→UNIX.

## Miscellany
- Orphan sounds in `win32/res/`: `FROG.WAV` and `WOOB.WAV`, wired to nothing.
- A 2000-era real bug, fixed in 2.5: `Item::dieMessage` was declared `Boolean`
  but assigned a 3-value enum, so destroyed items have said "has been used."
  instead of "is destroyed." for 26 years (`physical.h:1396`).
- Contact email in the readme: `satan@xevil.com`. Artwork credit: Comrade.Cid.

---

# Part II — The 2026 deep excavation

A second, longer dig (source tree + the original v2.02 `xevil.exe` + the dead web
via archive.org). New material only; everything cited.

## The 148 things your character can say
`cmn/game.cpp:128-277` — `Game::wittySayings[148]` (`WITTY_SAYINGS_NUM = 148`,
`game.h:271`). At the start of **every new game** (`Game::reset`, `game.cpp:2585`)
one is picked at random and pushed to the on-screen message queue
(`msg << wittySayings[Utils::choose(WITTY_SAYINGS_NUM)]`). Most players saw a
handful and never knew there were 148. It is a wall of late-'90s pop culture and
MIT-engineer humor. A sampler, verbatim:
- Film/TV: *"I love the smell of napalm in the morning."*, *"Wake up, time to
  die."*, *"Ho, ho, ho.  Now I have a machine gun."*, *"I'm sorry, Dave.  I can't
  do that."*, *"Fuck me gently with a chainsaw."*, *"I'm here to chew bubble-gum
  and kick ass.  And I'm all out of bubble-gum."*, *"Oh, my God!  They killed
  Kenny!"*, *"We're going to need a bigger boat."*, *"Do not taunt
  Happy-Fun-Ball."*
- Monty Python: *"Nobody expects the Spanish Inquisition!!!"*, *"Come see the
  violence inherent in the system."*, *"Oh, I'm a lumberjack and I'm ok..."*
- MIT: *"We are, we are, we are, we are, we are the engineers. / We can, we can,
  we can, we can demolish forty beers."* (the Engineers' Drinking Song) and
  *"You're immune to both romance and mirth.  You must be a... a... / That's
  right.  I'm an engineer."*
- Hacker/self-aware: *"Hackito ergo sum."*, *"It's not a bug, it's a feature."*,
  *"XEvil.  The carpal tunnel game."*, *"Aaaaa!!  My soul is trapped in XEvil.
  Send help!!"*, *"fnord"*, *"M\*cr\*s\*ft:  Who need quality when you have
  marketing."*
- And the sign-off it saves for last: *"XEvil.  The peak of abnormality."*

We can even date the last five. Diffing the shipped array against the earliest
surviving source (May 28 1999, recovered below) shows **exactly five sayings were
added in the final stretch** and none removed: *"You're my bitch now."*,
*"Prepare to Qualify."*, *"I got a bad feeling about this drop."*, *"Cowboys never
quit!"*, and *"XEvil.  The peak of abnormality."*

## The 74 names of the damned
`cmn/game.cpp:281-356` — `Game::intelNames[74]` (`INTEL_NAMES_NUM = 74`). At game
start the list is shuffled (`Utils::random_list`, `game.cpp:1074,3276`) and dealt
out to every bot and player (`game.cpp:3358`). It is a self-portrait of the
authors' world:
- **The author signs his own kill-list**: `"hardts"` (`game.cpp:284`) is Steve
  Hardt's literal MIT Athena username — you can frag *him*. `"Steve"`, `"Sensei
  Steve"`, `"Cowboy Steve"` recur; `"Cid"` (`game.cpp:355`), the artist
  Comrade.Cid, is the very last name in the array.
- **MIT deep cuts**: `"James E. Tetazoo"` (the MIT Physics department's legendary
  fictitious professor), `"Ben Bitdiddle"` (the stock character from 6.001 / SICP),
  `"e^x Man"`, `"Pixie of Pass/Fail"`, `"Josh the 10-yr Old"`.
- **'90s cartoons**: Beavis, Butt-Head, Ren, Stimpy, Mr. Horse, Dilbert, Dogbert,
  Gromit, The Tick, Spaceman Spiff, Brain, and the entire South Park core
  (Kenny, Kyle, Cartman, Stan, Mr. Hat).
- **Aliens/Star Wars**: Hudson, Hicks, Wedge, Redshirt — the same movie whose
  lines seeded the witty sayings ("Marines!  We are leaving.", "Game over, man").

## Hell's full org chart (extending the earlier ranks)
The earlier note quoted the tentpoles; the whole ladder (`cmn/game.cpp:370-456`,
`rankingSets[]`, keyed by kill count) is a sustained corporate-satire bit worth
preserving. Each tier picks one title at random. Highlights not previously
recorded: at **0 kills** you might be *"Member of Hell's Children's Choir"* or
*"Satan's Vibrating Sex Toy"*; the 25-tier includes *"Hell's Speedbump"*; the
40-tier *"QA of Vomit Production"* and *"Teacher at Beelzebub Jr. High"*; a whole
**middle-management tier at 90 kills** (*"Manager, Department of Graft and
Corruption"*, *"Manager, Medieval Torture Devices Maintenance"*) sitting right
next to *"Postal Worker"* (a "going postal" joke); then *"VP of Hell Marketing"*,
*"VP of Hell Legal"*, *"Torture Methods Research Scientist"*, and at 250
*"Lead Software Engineer of Hell"* — the same title the manual dangles as
aspirational. The 666 and 666,666,666 capstones were already noted.

## The Armory, recovered from the dead web
The manual (`instructions/instructions.html:573`) links to *"The XEvil Armory"* at
`xevil.com/xevil/armory` — a page that no longer exists on the live domain (which
now hosts an unrelated CAPTCHA product). Recovered from the Wayback Machine
(`web.archive.org/web/20030219192631/http://www.xevil.com/xevil/armory/`,
"Copyright(c) 1998 Steve Hardt and Michael Judge", banner "by Frank Wu"). The
weapon/item flavor text the owner never saw, quoted:
- **Pistol**: *"High caliber sidearm.  Do you feel lucky, punk."*
- **Machine-Gun**: *"...Won Bombs 'n Ammo 'Weapon of the Year' three times
  consecutively."*
- **Chainsaw**: *"It slices! It dices! It can even cut a steel can... 'The
  Weed-Whacker from Hell'"*
- **Soul-Swapper**: *"Swaps the souls of the shooter and shootee...  Be careful
  to hit the right target."*
- **Frog-Gun**: *"Zaaaapp.  Ribbet.  You get the picture."*
- **Crack Pipe**: *"Increases speed and hand-to-hand damage.  Occasional lethal
  overdose.  'C'mon baby, I need my fix.'"*
- **P.C.P.**: *"Invulnerability, increased speed and hand-to-hand damage.  The
  come-down is a real bitch.  Be careful of overdose.  Long or short-term use may
  cause irreversible psychosis."* (this exactly describes the code — see below)
- **Demon-Summoner**: *"Contains a Demon held by Ka'Shi'Taath enslavement spell.
  Do not taunt."*
- **X-Shield**: *"Shield of solidified evil gives protection from 300 points of
  any type of damage."* — and indeed `XProtection` is created with 300 in
  `game.cpp` (the bonus path). The flavor text is load-bearing documentation.
- **Auto-Lancer**: *"Lancer chassis and energy coils connected to the
  ever-burning-scorching heart of a condemned sinner as power supply."*
- **Altar-Of-Sin**: *"Sell your soul to the Altar-Of-Sin for cool stuff.  Like
  saving cereal-box tops, but better."*

## The Character Profiles, recovered from the dead web
Also linked but long dead: *"XEvil Character Profiles"* at `xevil.com/xevil/profiles`
(a frameset; the real pages are `profiles/<name>.html`). Recovered via Wayback
(`web.archive.org/web/20021205*/http://www.xevil.com/xevil/profiles/`). Each
creature has a full dossier — name, age at death, blood type, sins, cause of
death, favorite food, and a backstory. The owner has almost certainly never read
these. The best bits:
- **Hero** — Marine Drill Sergeant, sins "Murder, bad jokes." A mock *Bombs 'n
  Ammo* interview where the interviewer tries to get his old lieutenant to admit
  Hero was dumb, and the lieutenant just keeps repeating *"Hero was a good
  soldier, a dedicated and honorable man.  It was a privilege serving with him."*
  Cause of death: *"Cigar smoking near ammo dump."*
- **Ninja** — is a **woman** ("Sex: F"), age "none of your damn business," the
  only Caucasian ever admitted to the Fujiyakamoto School of Ninjitsu; her entire
  clan was poisoned at a ceremonial meal and she is the sole survivor seeking the
  murderer. A real tragic backstory hiding behind a deathmatch sprite.
- **ChopperBoy** — 17, "M.I.T. student, sophomore," sins include "masturbation,"
  "Kicks ass at 'Quake'," "Has a serious 'thing' for Ninja," built the helicopter
  backpack to "impress the chicks," and was **killed by his own creation,
  Enforcer.**
- **Enforcer** — the payoff: it is *"ChopperBoy's entry for the M.I.T. 6.270 Lego
  Robot Competition.  Disqualified for use of non-regulation... military-grade
  quantum driver cores,"* whereupon it decided all humanity was the enemy, *"Killed
  85.3% of the contest attendants, including ChopperBoy,"* and went on a 23-hour
  rampage "through Cambridge and downtown Boston before destruction by
  Massachusetts National Guard forces." (6.270 is a real MIT LEGO-robot class.)
- **Walker** — a human brain (age 52) in a 1.3-year-old polycarbon chassis, built
  by "Chief Scientist Stephen Healy, Ph.D." at "Cruncheed Combat Technologies";
  project hit "97.32% of projected capacity... with only minor schedule and budget
  overruns." Blood type: "EM Radiation (753-872nm)."
- **Yeti** — "Good friends with Elvis and the Loch Ness Monster," does "occasional
  modeling work for fur coat manufacturers," quote "Mrrrrghhhh!" translated as
  *"Goddamn it.  I said no pictures."*, and died of **heat stroke** on an iceberg
  drifting into warm water.
- **Dog** — reveals the Mutt's origin: *"Dog is good friends with Mutt, a slightly
  slower, but tougher animal than Dog."* Cause of death: "Hit by car."
- **Dragon** — *"Segmented, capable of splitting into multiple independent
  sub-dragons"* (the profile documents the 15-segment composite the code
  implements); "Lord of fear, pain, and torment in the Earthly realm of Asia."

## The pharmacology of XEvil (the exact drug math)
Three drugs, three `Modifier` subclasses in `cmn/actual.cpp`, each a stack of
attribute multipliers. Timing calibrates against `PH_INVISIBLE_TIME 1500 //
One minute` (`physical.h:65`), i.e. ~25 turns/sec.
- **Crack** (`Crack::apply`, `actual.cpp:1627`; `CRACK_TIME 500` ≈ 20s): speed
  ×2.0, jump ×1.5, melee damage ×2, sets `HIGH`. Overdose chance **1-in-10** per
  use (`crack_pipe.bitmaps:70`, `odChance` checked at `physical.cpp:2732`, message
  *"dies from crack overdose."*).
- **Caffine** (`CaffineM::apply`, `actual.cpp:1702`; `CAFFINE_M_TIME 300` ≈ 12s):
  speed ×1.4, jump ×1.3, no damage boost. Overdose chance **0** — the only
  completely safe drug (`caffine.bitmaps` `odChance = 0`). The manual's *"little
  boost to get you going in the morning."*
- **PCP** (`PCPM::apply`, `actual.cpp:1774`; `PCP_M_TIME 350` ≈ 14s): the
  berserker. Incoming `CORPOREAL_ATTACK` is negated — *"Turn damage into
  superficial damage"* (impact/melee can't hurt you); `HEAT_ATTACK` set to 0 (fire
  immunity); melee damage ×2. **But**: overdose chance **1-in-6** (deadliest to
  even touch), and `PCPM::preDie` (`actual.cpp:1803`) *"Whack off half of health"*
  when it wears off — the comedown the Armory warns is "a real bitch." Everything
  the flavor text promised, in code.

## The Altar of Sin has two faces
Two entirely different mechanics on one object (`cmn/actual.cpp`):
- **Touch it as a human** (`AltarOfSin::collide`, `actual.cpp:1094`): it grants one
  random **blessing** from `Utils::choose(9)` (`actual.cpp:1117-1307`) and then
  consumes itself (`kill_self`). The nine: extra life, Double Speed, Double Jump,
  Double Health, Healing (regen), HellFire (become on-fire), Fireballs (a built-in
  fireball weapon), Flying, or Sticky (wall-crawl). Several are skipped if
  redundant, so you always get something useful. Buried in case 0 is a removed
  feature: a commented-out *"You Gain 5 Kills"* path with the note *"Everybody
  hates the 'You Gain 5 Kills' thing.  So, I removed it."* (`actual.cpp:1123-1133`).
- **Attack it** (`AltarOfSin::corporeal_attack`, `actual.cpp:1015`): a coin-flip
  either morphs you into a **Frog or a Baby-Seal**, or *"BLASPHMER!  ... loses
  health for daring to attack the Altar of Sin"* (drains all health). Either way
  the arena flashes *"Don't FUCK with the Altar of Sin."* [sic — the code comment
  at `1016` opens with *"Don't fuck with the Altar of Sin."*]

## The facehugger's ninety turns
`Hugger::collide`/`act` (`physical.cpp:8666-8775`). On latching to a valid
biological victim it **stuns itself** for `HUGGER_TIME` (90 turns ≈ 3.6s) and
stuns the **victim** for `HUGGER_TIME + 1` and marks them alien-immune for
`HUGGER_TIME + 2` — so during the whole gestation the victim is completely frozen
and nothing else can touch them. The hugger rides their face the entire time
(*"Guess where hugee's face is, upper-left + (width/2,height\*.3)"*). When its own
stun expires it spawns the Alien and kills both bodies. This is the ~3.6-second
window in which a hugged player can only watch. Red vs Green (whose mind the new
Alien gets) was covered in Part I.

## Coolness: the weapon-switch brain you never noticed
Every weapon and item has a `coolness` integer, and picking up gear silently
auto-selects your "coolest" one (`User::coolest_weapon`/`coolest_item`,
`physical.cpp:6324-6376`; only non-negative coolness is eligible). The values
(from each `.bitmaps`) explain years of muscle memory:
- Weapons: Auto-Lancer 11000 > Demon-Summoner 10100 > Dog-Whistle 10000 > Launcher
  8000 > Lancer 7000 > Stars 6000 > Pistol 5000 > Flame-Thrower 900 > Chainsaw 800
  > Frog-Gun 700.
- **Deliberately un-auto-equippable** (negative coolness): **Napalm Grenades −5,
  Grenades −10, Soul-Swapper −20.** The game will *never* auto-switch you to these
  — so you can't accidentally lob a grenade or swap souls the instant you grab one;
  you must select them by hand. Ammo weapons carry a separate `coolnessNoAmmo`
  (Dog-Whistle −30, Demon-Summoner −25) so they drop to the bottom once empty.
- Items: N-Shield 9000 > Med-Kit 8000 > T-Shield 7000 > Caffine 6500 > PCP 6300 >
  Crack 6000 > Doppel 900 > Cloak 800 > Transmogifier 90 > Bomb 80 — which is why
  grabbing a Bomb never bumps you off your Med-Kit.

## The Cloak and the blind machines
`Cloak` grants near-total invisibility for `PH_INVISIBLE_TIME` (1500 turns ≈ one
minute, per the comment). The part that matters: the enemy AI is **hard-coded to
ignore invisible things entirely** — both invisible creatures and invisible items
are skipped in the target scan (`intel.cpp:1831-1832`, `1857-1858`,
`!is_invisible()`). A cloaked player is not merely hard to see; to a bot they do
not exist. The Armory's rule "You may not fire when cloaked" is the balancing cost.

## Corpses decompose; rocks need momentum
Two physics details a careful player feels but never reads:
- **Corpses** persist `CORPSE_TIME` (140 turns ≈ 5.6s) then *"corpse has
  decomposed."*; but you can gib one early by dealing enough extra damage —
  `get_health() < -corpseHealth` → *"corpse has been destroyed."*
  (`physical.cpp:4439-4451`). Bodies fall (`DROP_SPEED 2`) and never collide.
- **Thrown/falling weights and rocks** only hurt if moving fast enough: `Heavy`
  requires downward velocity `dy >= HEAVY_DAMAGE_VEL` (3) *and* the target below or
  inside it (`physical.cpp:2308-2322`). A rock at rest is harmless; kill credit
  goes to the last "pusher." Only certain bodies can even throw — `throwSpeed` is
  8 for Hero but **0 for ChopperBoy** ("ChopperBoy can't throw",
  `chopper_boy.bitmaps:232`), and only when holding no weapon.

## 666, everywhere
Beyond the two Hell ranks, the number of the beast is woven through the engine as
sentinel and filler: `intel.cpp:272` sets a dead brain's lives to `-666` with the
comment *"This should never be used."*; the world serializer writes `666` as
literal padding, twice (`world.cpp:1047,1054`, *"// padding"*). Even the
network wire format is a little satanic.

## The Story that was never written
There is a "Story" menu item (`ID_STORY`, `resource.h:1124`) wired to
`UiPlayer::doStory()` (`uiplayer.cpp:2252`), which opens `CStoryDlg`. But
`win32/storydlg.cpp` is an **empty ClassWizard stub** — constructor, DoDataExchange,
and an empty message map, and nothing else (`storydlg.cpp:39-61`). There is no
dialog template for `IDD_STORY` in the resource script either. The premise lives
only on the website ("You have sinned in life.  Now, you die and go to Hell").
The in-game Story screen was scaffolded and never filled — a blank page you can
still open.

## The shareware that almost was
`win32/aboutdialog.cpp:127` carries a commented-out line:
`// m_versionvalue += "  (Shareware)";`. It is not a joke — Frank Wu's surviving
mirror page states it plainly:
> "Since XEvil and the XEvil source code are shareware, please send a $20 check or
> money order made out to 'Steve Hardt' at XEvil, P.O. Box 391530, Mountain View,
> CA 94039-1530"
(`web.archive.org/web/20021201162153/http://www.frankwu.com/xevil.html`). So XEvil
shipped as $20 shareware before/alongside the GPL, and by ~2000 Hardt had left
Cambridge for **Mountain View, CA** (Silicon Valley). The "(Shareware)" tag in the
About box was disabled when the game went GPL, but the code remembers.
Bonus artifact: the sound effects were edited in **GoldWave** — the shipped
`xevil.exe` still contains the WAV chunk *"File created by GoldWave.  GoldWave
copyright (C) Chris Craig."*

## Who wrote what (attribution by dialect)
The two authors have unmistakable, countable fingerprints. Hardt writes function
contracts (`EFFECTS:` / `MODIFIES:` / `REQUIRES:`) and camelCase; Judge writes MFC
Hungarian (`m_`, `p`, `CDialog`, `DDX_`, `BEGIN_MESSAGE_MAP`). Counting across the
trees:
- **`cmn/` (the engine)**: 791 contract lines vs 29 MFC tokens → **Steve Hardt**,
  essentially wholesale. This is the ~40kloc cross-platform game.
- **`win32/` (the Windows UI)**: 1329 MFC tokens vs 124 contract lines →
  **Michael Judge**, with Hardt's fingerprints concentrated in the cross-platform
  glue/sound files (`s_man`, `xdata`, `draw`, `wheel`, `fsstatus`, `ui`) — matching
  the credits' "Windows Front End: Michael Judge, Steve Hardt."
- **`x11/` (the UNIX UI)**: contract-heavy → **Hardt** (the "UNIX Front End").
This exactly corroborates the credits screen buried in the license text
(`cmn/l_agreement.cpp:182-227`): Design/Architecture/Cross-Platform/UNIX = Hardt,
Windows Front End = Judge + Hardt, Sound = Judge, Artwork = Comrade.Cid + Hardt +
Judge + frankwu.com + five others, Music = Ann Greyson / Michael Cummings /
D.J. Litany. That credits block ships as one giant C string literal with a
gloriously exasperated comment about keeping the columns aligned across X11's
fixed-width and Win32's variable-width fonts: *"Ohhhh!!  This is horrible.  Putting
an #ifdef here..."* (`l_agreement.cpp:176-181`). (The "lawyer text" that the
agreement dialog word-wraps at runtime, via the hand-rolled `Line`/`Page` engine,
is simply the verbatim GPLv2 — not encoded or obfuscated, just a long literal
`get_text()` string, `l_agreement.cpp:155-514`.)

## The machine-name graveyard (config.mk)
`config.mk` is a stratigraphic record of every UNIX box XEvil was ever built on,
each architecture target tagged with the actual host's nickname in a comment or an
embedded home-directory path. A catalog of the fossils:
- Named boxes (comments): `#gargamel` (`alpha-gargamel-old`), `#russia`
  (`hp9000s700`), `#chainsaw` (`iris.old`), `#For lancer running Linux` (`i386`),
  `#for devastator and truth` (`i386-linux-old2`), `#jordan` (`rs6000jordan`,
  with *"static doesn't work on jordan"*), `#iron` (`rs6000`), `#scar`
  (`sun4-scar`), `#was acland, now worms` and `#now, mocha` (`solaris`),
  `#openwound` (`openwound-sun4`), `beepbeep-sun4`, `vision-sun4`, `jsc-sun4`.
  Two of the machine names — `chainsaw` and `lancer` — are also weapons in the
  game.
- Personal-account fossils in include/lib paths: **`/u/mjudge/xevil/xpm/...`**
  (Michael Judge's account, appearing in the alpha/hp/iris/aix/solaris targets —
  he maintained the XPM library builds) and the packaging pointer
  **`SRC_DIR = /mit/hardts/src/X/xevil1.4.9`** (Steve Hardt's MIT directory).
- **MIT Athena traces**: `athena-sun4` / `athena-sun5` targets, and
  `INCL_DIRS="-I/mit/gnu/lib"` — the game was still being compiled on Athena's
  Suns. (The modern `x86_64`, `arm`, `powerpc`, `darwin`, and `debug` targets and
  the auto-detecting `default:` rule are 2.5-era additions, not fossils.)

## The version labyrinth, reconstructed
Three different "versions" disagree in this tree, and the reason is historical
layering:
- `config.mk:42` says `VERSION = 2.1` (this is the value `Game::get_version_string`
  returns on UNIX, `game.cpp:1113-1114`) — yet the game everyone calls "2.02."
- `config.mk:45` still points `SRC_DIR` at `xevil1.4.9`.
- The shipped `xevil.exe` About box reads `2.02`.
Piecing together the strings and the recovered archive downloads, the real
timeline is:
1994‑07‑26 first release on MIT Athena (X11, monochrome, a learn-C++ project) →
UNIX 1.x line, reaching **1.4.9** (the `SRC_DIR` fossil), **1.5.1e**, and **1.5.5**
(the version shipped on the "100 Great Linux Games" CD) → Windows port with Judge,
whose earliest surviving binary is dated **Jan 16 1999** and whose May 1999 source
already carries `VERSION = 2.01` internally → public **GPL release Jan 18 2000** as
2.0 → 2.0r2, 2.01, 2.02, 2.02r2, with **2.02 dated July 26 2000 — the game's sixth
birthday, to the day.** The `config.mk` `VERSION` field was an internal/packaging
number that drifted independently of the public label the whole time; the `2.1`
you see is that drift, frozen. (The netcode protocol string tells the same story
from another angle — the original 2.02 exe advertises `XETP1.00`; the protocol was
held stable across the entire 2.x line. The 2.5 tree deliberately breaks it with
`XETP2.5X`, `xetp_basic.cpp:36`, so 2.5 clients and 2.02 servers can't handshake.)

## The built-in chaos monkey (`-buggy`)
`UDPOutStream::buggy_tests` (`streams.cpp:539-594`), enabled by the undocumented
`-buggy` flag, is a deliberate netcode fuzzer: for every outgoing packet it will,
by dice, **drop it (50%)**, **send 2–6 duplicate copies (~1/30)**, replace it with
a random-length garbage packet, truncate it, append 1–20 junk bytes, or twiddle a
few bytes at random — each logging what it did. It's proof the XETP transport was
engineered to survive hostile networks (loss, duplication, reordering, corruption),
and a lovely window into how a one-person engine got its reliability tested in
1999. Relatedly, `x11/serverping.cpp` is a whole standalone `ping`-for-XEvil-servers
utility (sends `SERVER_PING`, times the `SERVER_PONG`); `SERVER_PING` is notably
the *only* packet type the server will accept from an unknown address
(`role.cpp:2973-2975`).

## The Death March: a definitive burial
Part I flagged `IDM_DEATHMARCHSOUNDTRACK 1631` as the only trace of a tenth,
missing music track. This dig settles it. I checked every reachable build:
- v2.02 shipped `xevil.exe`: MIDI resources 1630, 1632–1639 — **nine**, no 1631.
- The **Jan 16 1999** Windows binary (recovered from
  `xevil.com/download/xevil2.0.windows/xevil2.0.windows.exe`): same nine, no 1631.
- The **May 28 1999** experimental Windows binary
  (`download/exp/xevil052899.windows.zip`): same nine, no 1631.
- The **May 28 1999 source package** (`download/developer/xevilsrc052899.zip`, the
  oldest source that survives): nine `.MID` files in `win32/res/` and no
  `deathmarch.mid`; and its `resource.h` already gives ID 1631 to **two** wall
  bitmaps (`IDB_MD5WALL`, `IDB_MD4WALL`) *in addition to* the death-march menu ID.
So by the earliest artifact that exists anywhere, the Death March had already been
cut and its ID recycled. There is no file to recover — it was gone before the tape
starts. The nine survivors, mapped (`resource.h:1008-1026` ↔ `win32/res/`):
BABYSEAL, FIRE, HIVE, KKKILL, ZEEPEEG, NIGHTSKY, SWEETDAR, TERRAEXM (the "banished"
one), NEWSONG. Sources checked are all on `web.archive.org/*/xevil.com/download/*`.

## XDeathlord, the ancestor
XEvil was not Hardt's first X11 game. `xevil.com/download/xdeathlord/` archived
**XDeathlord 1.2** (Linux binary + source, GPL'd the same Jan 18 2000). Per the
retrospectives it is *"the same style as XEvil, but in a vehicular combat mode
instead of a personal combat mode"* — the vehicular-combat prototype whose engine
ideas grew into XEvil's creatures. XEvil is the sequel to a game almost nobody
remembers.

## What became of xevil.com
For the owner's closure: the game was still officially downloadable as late as 2018
(`web.archive.org/web/20180613141954/http://www.xevil.com/download.html` lists 2.02
for "Windows 7, XP, 2000, NT, 98, 95", Unix/X, and Mac OS X). Some time after, the
`xevil.com` domain was taken over by an unrelated commercial "XEvil" CAPTCHA-solving
product (the "3.0.4.123" you'll find on download sites is *that*, not the game — no
Java rewrite of the game ever shipped). The original artwork survives on the mirror
of **Frank Wu** — a four-time Hugo Award-winning science-fiction artist — who drew
the Character Profile portraits, the Ninja, the machine guns and background tiles
(`frankwu.com/xevil.html`, credited in-game as "frankwu.com"). Comrade.Cid, the
lead pixel artist, signs the credits and appears as the final AI name "Cid";
identity otherwise undocumented.

## The two orphan sounds, measured
Part I noted `FROG.WAV` and `WOOB.WAV` sat in `win32/res/` wired to nothing.
Measured (numpy, `win32/res/`): **FROG.WAV** is 0.37s, 11025 Hz, **8-bit** mono —
a short, gritty, three-pulse mid-band croak ("rib-bit-bit"), the lo-fi bit depth
giving it a deliberately cheap texture. **WOOB.WAV** is 0.25s, 11025 Hz, **16-bit**
mono — a punchy, cleaner two-part downward "woob." The happy ending: in the 2.5
revival, WOOB finally has a job — it voices the new **Singularity** weapon
(`actual.cpp:3257-3258`, with the comment *"The long-orphaned WOOB finally gets a
job."*).

## The artist's working files (win32/res)
Rendering the oddly-named BMPs (PIL) shows they're not orphans but working sprite
frames and tiles, and they preserve the artists' file-management hacks: `27A.BMP`,
`27b.bmp`, `39A.BMP` are Hero animation frames (kneeling, punching, standing —
green fatigues, blond, magenta `#FF00FF` transparency key). `AAANEW7.BMP` (a
machinery/turret tile on hazard stripes) and `!DOG0_RU.BMP` (a cheerful white
cartoon dog, tongue out) use leading `AAA`/`!` so the work-in-progress files sort
to the top of the folder — the 1990s equivalent of pinning a tab. Nothing hidden,
but a nice human trace of how the art actually got made.

---

# Part III — The last days of XEvil (the October 2000 snapshot)

Two archives surfaced that change what we know: `xevilsrc2.02r2.zip`, the official
source release recovered from archive.org, and `xevilsrc102200.zip`, a developer
snapshot nobody has looked at in twenty-six years. Read against this repository,
they rewrite the end of XEvil's history. Throughout, **A** = the official 2.02r2
zip, **B** = the October 2000 developer zip, **C** = lvella's 2011 preservation
(this repo's `master`). Unqualified `file:line` citations below are to **`master`**;
citations prefixed `A` are into the 2.02r2 zip.

## The timeline, corrected

**A, the "2.02r2 source release," is not the 2.02 source.** Its file dates fall
into two clumps and nothing in between: **810 files dated 19–20 January 2000**
(the GPL release), and **eighteen files re-edited 19–23 March 2003**, plus 138
directory entries stamped `2003-03-23 15:24` — the signature of someone unzipping
an old archive into a fresh tree, editing, and re-zipping. The eighteen are
`config.mk`, `makefile`, `unzipxevil`, `win32/xevil.rc`, `cmn/{game,game_style,
locator,intel,area,utils}.*` and `x11/{ui,panel,main,serverping}.cpp`.

What was that 2003 session? A compatibility pass. `config.mk` gains a target that
says so out loud:

```make
# Versions of Linux with gcc 3.2.
# Added no-deprecated option so wouldn't complain about using old-style c++
# header names, eg <iostream.h> instead of <iostream>
i686:
```
and the edited sources gain exactly the includes gcc 3.2 stopped providing for
free — `#include <stdlib.h> // For exit().` in `cmn/utils.h`, `#include
<iostream.h>` in `x11/panel.cpp` and `x11/serverping.cpp`. `config.mk:42` is where
the label lives: `VERSION = 2.02r2`.

So **XEvil 2.02r2 is a March 2003 make-it-build-again re-release of the January
2000 source tree.** Its content is 2.0-era. The give-aways are everywhere: it
still ships `xevil-2.0.spec`; its `makefile` still packages `.tar.Z` through a
`$(COMPRESS)` macro; its `win32/resource.h` is dated 2 March 1999.

And it demonstrably predates 2.02. `Flying::act()` in the developer tree carries
Hardt's own version note in place of a preprocessor guard
(`cmn/physical.cpp:8357-8359`):

```c
//#if WIN32  Took it out after XEvil 2.01
  acceleration = (int)(acceleration * 1.5);
//#endif
```
A change made *after 2.01* — and the 2.02r2 release still has the live `#if WIN32`
at A `cmn/physical.cpp:8203`. The official "2.02r2" source does not contain the
2.02 work.

**B is the newest thing that exists.** Its most recent file is `x11/ui.cpp` at
**21 August 2000, 07:00**; the zip is named for the day it was packaged, 22
October 2000.

**C is B.** Byte for byte:

```
$ diff -rq B C   # C = git archive 4386fbc ("Satan's original version")
Only in B/x11/gen_xpm: explosion, fire_explosion, n_protection,
                       phys_mover, t_protection, x_protection
```
— six *empty* directories, the only thing git cannot store. Every one of the 1432
files hashes identically (`md5sum` over the sorted file list: `5a5dc03d…` for
both). Lucas Vella's "Satan's original version" is `xevilsrc102200.zip`.

So the order, newest first, is **C ≡ B (Aug 2000) → A (Jan 2000 content, 2003
packaging)**. The official source release is the *oldest* of the three. Which
means:

> **Everyone who has built XEvil from source since 2011 — including XEvil 2.5 —
> has been building Steve Hardt's private, unreleased development branch, not the
> game he shipped.**

One correction to Part II falls out of this. `config.mk`'s `VERSION = 2.1` is not
drift: A proves the field tracked the real label (`2.02r2`), so the `2.1` sitting
in this repo is Hardt's *next* version number. XEvil 2.1 was in development.

## Did lvella lose anything? No.

The treasure question has a clean answer: **nothing was lost.** No file, no
comment, no asset, no stray artifact — including the editor backup discussed
below — is in B and missing from C. The 27 commits between `4386fbc` and `master`
are 64-bit/clang/OSX/Raspberry-Pi build fixes by Vella, denilsonsa and Lee
Bradley; not one line of gameplay changed. The preservation is exact.

## The unreleased XEvil

Because A is the 2.0-era tree, everything below is work Steve Hardt did **between
19 January and 21 August 2000** that appears in no official source release. Since
C ≡ B, every citation is a live path in this repository.

### Two creatures the world never met

**The Zombie** (`cmn/actual.h:1863`, art in `x11/gen_xpm/zombie/`, 23 XPM frames
plus 8 "duplicate_of" aliases, and 14 BMPs in `win32/res/`): a
green-skinned shambler in torn shirt and blue jeans, arms out, fully animated
walk/climb/attack cycles and a gory death sprite. Not a joke character —
`cmn/bitmaps/zombie/zombie.bitmaps` gives him **400 health** (tied with the
Enforcer for the toughest thing on two legs, double the Hero's 200) and a body
slam doing **75 free damage**, the hardest melee hit in the game (Hero and Ninja
do 50). `False, /* biological */` (line 82) makes him facehugger-proof; he bleeds
`DROPLET_GREEN_BLOOD` (line 83) like the Alien; `corpseHealth 0` means he leaves
nothing behind. And `True, /* potentialEnemy */` with `enemyWeight 25` (line 207)
— **he was wired into the normal enemy rotation and ready to ship.**

**The Chicken** (`cmn/actual.h:2334`, art in `x11/gen_xpm/chicken/`): a white-and-
brown hen with a red comb and yellow feet, complete with flight frames and a
peck attack. 185 health, flying (`gravTime 3`), 15/20 melee damage. It is
`potentialEnemy False` — it never spawns in a normal game — but it is a
`transmogifyTarget`, a `doppelUser`, and reachable as `-human_class chicken`.
Its death sound is a placeholder, annotated
(`cmn/bitmaps/chicken/chicken.bitmaps:64`):

```c
  SoundNames::SEAL_DEATH,  // Need a better death sound.
```

**The Feather** (`cmn/actual.h:1117`, replacing the long-dead `Spark` class) is a
new kind of droplet — and the reason for the whole `DropletSet` bit-flag system
(`cmn/physical.h:68-81`). Creatures now bleed *sets* of things: the Chicken sheds
`(DROPLET_BLOOD | DROPLET_FEATHER)`, and the Walker finally got the right answer
(`cmn/bitmaps/walker/walker.bitmaps:78-79`):

```c
  // Walker is a cyborg, so both blood and oil, but twice the chance of oil.
  DROPLET_OIL | DROPLET_MORE_OIL | DROPLET_BLOOD, /* dropletType */
```
Feathers behave nothing like blood: `dissolveTime 45`, `gravity -2` (one pixel
every two turns), `speedModifier 0.7f`, `stickWalls False`
(`cmn/bitmaps/feather/feather.bitmaps:43-46`). They drift down and never stick.

### Two scenarios that were never played

The scenario roster went from 10 to 12 (`cmn/game_style.cpp:1825`,
`Utils::choose(12)`), with two additions to `ScenarioType`
(`cmn/game_style.cpp:90-91`):

- **The Coop** (`-scenario the-coop`, `cmn/game_style.cpp:574,3063-3099`): a 4×3
  room world containing ten chickens on their own team, and nothing else. Clear
  it and the arena announces **"Finger Lickin' Good"** (`:3072`).
- **Chicken Little** (`-scenario chicken-little`, class `LookOut`,
  `cmn/game_style.cpp:593,3103-3222`): an eight-room-wide, one-room-tall open
  map with no maze at all, an Xit in the far corner, and **the sky falling** —
  a rock or a weight dropped from above every three turns, up to 40 alive at
  once. The level text is *"The sky is falling.\nFind the exit."* (`:3177`).
  It needed a new physics rule, and Hardt wrote down why
  (`cmn/game_style.cpp:3216-3218`, API at `cmn/physical.h:1244-1248`):
  ```c
  // Kind of a hack.  On this level any Heavy object in the air can hurt.
  // So that ChopperBoys/Ninjas can't just cruise along on the top of the
  // ceiling, only hitting the Heavies on the side and not taking damage.
  ```
  Rock damage was raised from 100 to **155** for it
  (`cmn/bitmaps/rock/rock.bitmaps:50`).

Chicken Little is only expressible because of a rewrite of world generation that
landed on 24 March 2000 (`cmn/world.h` mtime `2000-03-24 05:01`): the old
`typedef int WSpecialMap` with its four hard-coded maps (`MAP_NONE, SEALS,
ZIG_ZAG, FLAG`) became a proper polymorphic `class SpecialMap`
(`cmn/world.h:99-143`) with `room_maze()`, `horiz_extra_walls()`, `use_movers()`,
`big_physicals()`, `do_doors()` — and a brand-new `EMPTY` maze mode plus
`Blueprints::implement_edges_only()` (`cmn/world.cpp:291-319`).

### The Psycho-Chicken

The end-of-level bonus wheel grew from five prizes to six
(`cmn/game.cpp:2050`, `Utils::choose(6)`). The sixth
(`cmn/game.cpp:2129-2153`):

```c
        // Grant a psycho-chicken.
        case 5: {
          ...
            // Create psychotic pet inteligence.
            IntelOptions ops;
            ops.psychotic = True;
            NeutralP pet = new Pet(&world,&locator,"psycho-chicken",...);
          ...
          awardMsg = "Bonus: Psycho-Chicken";
```
Three chickens (`BONUS_CHICKENS_NUM 3`, `cmn/game.cpp:115`), yours, and insane.

### The machines learned to get bored

The single largest AI change since the release is a new class, `Boredom`
(`cmn/intel.h:356-370`, `cmn/intel.cpp:937-969`). Every reflex cycle a bot's
position is compared with the previous one; five identical cycles
(`BOREDOM_CYCLES 5`, `cmn/intel.cpp:78`) and it is officially bored, whereupon it
picks a random spot on the map and walks there (`cmn/intel.cpp:1005-1022`):

```c
      // Check for boredom, if bored,
      Boolean bored = boredom.check(get_locator(),p);
      ...
      // Instead of just sitting there, go somewhere randomly.
      if (strategy == doNothing) {
```
This is the real fix for the stuck-on-a-corner dog that Part I described being
papered over with dice in 1999. It was never released.

Worth noting for the record: the two most-quoted lines in Part I —
*"We don't use strategyChange timer at all??  Is this right?"* and
*"////// Does this do anything?? //////"* (`cmn/intel.cpp:2192,2220`) — **do not
exist in the 2.02r2 release at all.** They were written in the final months.

### A seventh world

`W_THEME_NUM` went 6 → 7 (`cmn/coord.h:64`), with three new blocks, a background,
an outside, and two doors (`cmn/coord.h:70-76`). Theme "MD 5"
(`cmn/bitmaps/world/world.bitmaps:291-380`) is a dusk woodland: grassy dirt
ledges, a vine ladder, wooden slats, a golden cobblestone exterior, a hollow-tree
door, and a violet sky with pink clouds. It shipped enabled, with an off-switch
in the comments (`cmn/world.cpp:2250-2253`):

```c
  // To disable the unfinished MD5 theme, subtract one here, and kill
  // W_DOORS_TRANSPARENT.

  const int ACTIVE_THEME_NUM = W_THEME_NUM;
```
The theme brought transparent doors with it — `#define W_DOORS_TRANSPARENT`
(`cmn/coord.h:85`) plus a whole new mask plane on both frontends
(`x11/xdata.h:273`, `x11/draw.cpp:91-98,109-114,387-395`, `win32/draw.cpp:290-292`).
That code was never built with the flag off: in the archive, `x11/draw.cpp:388`
says `#elif` where it means `#else`, so turning MD5 off would not have compiled.
(Vella fixed it in 2011 — `ca21c5a`, "With permissive mode and only in 32 bits
mode, the code compiles with modern GCC"; `master`'s `x11/draw.cpp:389` reads
`#else`. It is one of the very few original-code bugs the preservation touched.)

The art existed long before it was switched on: `win32/resource.h` in the *1999*
release already defines `IDB_MD5WALL`, `IDB_MD5DOOR1`, `IDB_MD5BACKGROUND`… but
aliased on top of the MD4 ids and the MIDI menu ids (three symbols share 1631).
Turning the theme on meant giving them real numbers — 1709–1719 in the dev tree
(`win32/resource.h:1081-1087`).

### Balance and engine work

- **Flying creatures got 50% more acceleration on UNIX** — the `#if WIN32` around
  `acceleration * 1.5` was commented out for `Flying::act()` only
  (`cmn/physical.cpp:8357`); `Walking` and the third locomotion still have it live.
- **Air combat in eight directions.** Previously a creature in mid-air could only
  head-stomp. Flyers can now attack any direction while airborne
  (`cmn/physical.cpp:7069-7086`), free attacks time out
  (`FIGHTER_FREE_TIME 8`, `cmn/physical.cpp:88`), and a flyer is locked out of
  movement commands mid-swing (`cmn/physical.cpp:8402-8407`). This is the Chicken's
  dive attack, built into the engine.
- **Fractional gravity became a first-class engine feature**: a negative `Grav` of
  −X now means "one unit down every X turns" (`cmn/physical.cpp:4262-4276`,
  `cmn/physical.h:2200-2203`), replacing Flying's private hand-rolled version.
- **Rank now scales with difficulty.** `DifficultyLevel` gained `rankMultiplier`
  (`cmn/coord.h:637`): trivial 0.5×, normal 1.0×, hard 1.5×, bend-over 2.0×
  (`cmn/game.cpp:359-365`), applied in `Game::choose_ranking`
  (`cmn/game.cpp:1862-1865`). On bend-over you replace Bill as Satan's Right Hand
  Man at 333 real kills; on trivial it takes 1332.
- **Scenario lives cut from 10 to 7** (`cmn/game_style.cpp:72`,
  `#define HUMAN_LIVES_SCENARIOS 7 //10`).
- **The Alien, the Dog, the Mutt and both Huggers can use the Doppelganger now**
  (`cmn/bitmaps/alien/alien.bitmaps:170`) — annotated
  `True, /* doppelUser */  // Changed, why not let em use it.`
- **Transmogifying someone no longer litters live Bombs**: `drop_all` gained a
  `killNonPersistent` flag (`cmn/physical.h:590`), and the Transmogifier passes
  `True` (`cmn/actual.cpp:1506-1507`).
- **Teams became closures** (`cmn/locator.h:362-365`), so `Scenarios::dog_team`
  generalised into `class_team` taking a `ClassId` — which is how The Coop puts
  all chickens on one side.
- **A machines-only game can now end properly**: if no humans were playing, the
  arena prints *"Total Devastation: Everyone is Dead"* or *"One Machine Player
  Survived"* (`cmn/game.cpp:1906-1917`).

### Bugs he found after shipping, that nobody got

- **Blood, Green Blood and Oil Droplets could not be created over the network.**
  In the release, all three `create()` functions are `assert(0); return NULL;` —
  and worse, GreenBlood's and OilDroplet's `PhysicalContext` both pointed at
  `Blood::create`. All fixed in `cmn/bitmaps/{blood,green_blood,oil_droplet}/*.bitmaps`.
- **NULL-holder crash in `Fighter::act()`** (`cmn/physical.cpp:6980`): the guard
  `if (holder && holder->get_weapon_current())` was added because the Zombie and
  the Chicken are Fighters with no hands.
- **Carriers dropped items on a quiet death** (`cmn/physical.cpp:6854-6856`):
  ```c
      // FIXED: Don't drop persistent items if doing a quiet death.
      // Copied this fix from User, haven't tested it too much.
  ```
  The corresponding `WARNING:` about the known bug was deleted from the header.
- **The "negative damage means superficial damage" hack was removed** — which is
  the change that broke the Altar of Sin. See below.

### The dedicated server

The last feature Hardt ever built. `-log_file <name>` (`cmn/game.cpp:2646`) and,
if you run as a server, automatic daemonisation with output redirected to
`./xevil.log` (`cmn/game.cpp:913-924`, `LOG_FNAME_DEFAULT` at `:117`). The
implementation is `class Daemon` (`x11/xdata.h:335-357`), introduced with the
best comment in the platform layer:

```c
// Handle the black magic to be a UNIX Daemon.
...
  // 1) fork new process
  // 2) New session id
  // 3) change working directory to /tmp
  // 4) redirect all output from stdout and stderr to logfile
```
`-v` / `-version` arrived at the same time (`cmn/game.cpp:2544` and `:2804-2810`).

### The protocol quietly broke

Part II recorded the wire version as `XETP1.00`, held stable across the 2.x line.
The dev tree says otherwise (`cmn/xetp_basic.cpp:36`):

```c
char *XETPBasic::versionStr = "XETP1.0X";
```
An "X" for experimental — and earned: `CONNECT` is `#if 0`'d out, `ACCEPT`,
`WORLD_ROOM` and `ROOMS_KNOWN` are gone, and `TCP_CONNECT` is renumbered to 1
(`cmn/xetp_basic.h:59-81`). This tree cannot talk to any XEvil that ever shipped.
2.5's `XETP2.5X` is the second X, not the first.

### The 148th thing your character can say

The release has **147** witty sayings (A `cmn/game.h:271`); this tree has **148**
(`cmn/game.h:271`). Diffing the arrays, exactly one line was added between January
and August 2000, and it is the sign-off Part II singled out:

> *"XEvil.  The peak of abnormality."*

The 74 names of the damned are unchanged.

### The mouse the UNIX version used to have

A removal worth recording. The released X11 client had mouse controls — Button 1
moved you, Button 2 fired, Button 3 changed weapon (A `x11/viewport.cpp:1589-1600`).
In the dev tree they are fenced off (`x11/viewport.cpp:1592`):

```c
// Disable the rudimentary mouse controls, they just confuse the user.
#if 0
```
An undocumented feature of the shipped UNIX game, deleted in the last months, and
gone from every build made from this tree since.

### What did *not* change

`instructions/` is byte-identical between A and B — **not one word of the manual
was updated**, so the Chicken, the Zombie, the two scenarios, the daemon and the
new flags are undocumented everywhere. So are `readme.txt`, `compiling.html`,
`world1.xew`, `world2.xew`, `dist.bat`, and the sound tables
(`cmn/bitmaps/sound_cmn/sound_cmn.bitmaps` is unchanged, which is why the Chicken
dies with a baby seal's voice).

## The Altar's wrath, dated

Part II described the Altar of Sin's second face: attack it and you are turned
into a frog or a baby seal, or drained to zero, while the arena flashes
*"Don't FUCK with the Altar of Sin."* We can now date the day that stopped
working, and it is not a 1994 bug — it is **20 June 2000**.

In the 2.02r2 release the base virtual is two parameters
(A `cmn/physical.h:494`):

```c
  virtual Boolean corporeal_attack(PhysicalP killer,int damage);
```
and every override in `actual.h` matches it. The mechanic worked.

On 20 June 2000 (`cmn/physical.h` mtime `2000-06-20 12:05`) Hardt removed the
"negative damage means superficial damage" hack — `cmn/physical.cpp:499`,
`// Got rid of hack of using negative numbers for superficial damage.` — and gave
the virtual a third parameter (`cmn/physical.h:513-514`):

```c
  virtual Boolean Physical::corporeal_attack(PhysicalP,int damage,
           AttackFlags flags = ATT_DAMAGE | ATT_DROPLETS);
```
He updated the two overrides that live in `physical.h` (`:855` Moving, `:2078`
Creature). He never opened `actual.h` again — its mtime is `2000-04-29 23:29`,
**seven weeks older than the header it derives from.** In 2000-era C++ there was
no `override` keyword and no warning: the four two-parameter declarations simply
stopped overriding anything and became dead name-hiding shadows.

There are exactly four, and this is the complete list (verified by extracting
every `virtual` declaration in `cmn/*.h` and grouping by arity — `corporeal_attack`
is the only function in the engine with a split):

| `actual.h` | class | what it did | what it does now |
|---|---|---|---|
| 68 | `PhysMover` | `return False` — the invisible mover proxy is unattackable | nothing (health 0, so harmless) |
| 158 | `Fire` | `return False` — fire cannot be shot out | nothing (health 0, so harmless) |
| 196 | `FireExplosion` | `return False` | nothing (health 0, so harmless) |
| **390** | **`AltarOfSin`** | **the entire frog/baby-seal curse and the BLASPHMER drain** | **never runs** |

Three are duds. The fourth is the mechanic. `AltarOfSin::corporeal_attack`
(`cmn/actual.cpp:1006-1076`) is **byte-identical** in A and in this tree — 71
lines of morph-into-a-frog, `"BLASPHMER!  "`, arena message — and since 20 June
2000 nothing has called it. Two consequences, both live in the repo today:

1. Attacking the Altar has no effect on you at all.
2. The Altar became **destructible**. The old override never called up the tree,
   so the altar took zero damage and was indestructible; the base implementation
   now applies damage to its 2000 hit points
   (`cmn/bitmaps/altar_of_sin/altar_of_sin.bitmaps:87`). You can shoot it dead.

The irony is exact: the *source release* everyone could download preserves a
working Altar; the *game* everyone actually played, built after 20 June 2000,
does not.

## `world.bitmaps~` — one file caught mid-edit

The single stray artifact in either archive is an editor backup:
`cmn/bitmaps/world/world.bitmaps~`, dated **20 March 2000**, sitting next to a
live file dated **22 July 2000, 23:44** — the last thing touched in the entire
art tree. The diff between them is the whole answer:

```diff
+#include "gen_xpm/world/block_22.xpm"
+#include "gen_xpm/world/block_23.xpm"
+#include "gen_xpm/world/block_24.xpm"
+#include "gen_xpm/world/background_14.xpm"
+#include "gen_xpm/world/outside_6.xpm"
+#include "gen_xpm/world/door_10.xpm"
+#include "gen_xpm/world/door_11.xpm"
```
Seven lines. At a quarter to midnight on 22 July 2000, Steve Hardt was wiring the
seventh world into the UNIX build, one `#include` at a time, and his editor
snapshotted the file as it had stood four months earlier. It is the most precisely
dated moment in the whole excavation, and it survived into git because nobody ever
ran a cleanup.

## The last all-nighter

The mtimes of the eight most recently modified files in the archive tell one story:

```
2000-08-20 18:56  win32/xdata.h
2000-08-20 19:23  makefile
2000-08-20 20:37  cmn/game.h
2000-08-20 20:42  x11/xdata.h
2000-08-20 20:51  x11/xdata.cpp
2000-08-20 21:01  cmn/game.cpp
2000-08-21 06:59  x11/viewport.cpp
2000-08-21 07:00  x11/ui.cpp
```
Twelve hours, ending at seven in the morning. It is the dedicated-server work —
and you can watch him change his mind inside it. At 18:56 he wrote the Windows
half first, as a class called `LogFile` (`win32/xdata.h:438-449`):

```c
// All dummy on Windows.
class LogFile {
public:
  LogFile() {}
  ~LogFile() {}
  void set_file_name(const char*) {}
  void enable();
  void disable();
};
```
Two hours later the UNIX side appeared under a different name, `Daemon`, with a
different shape. `LogFile` was never mentioned again. `enable()` and `disable()`
are declared and defined nowhere; nothing in the tree constructs one. It is still
sitting in this repository at `win32/xdata.h:439`, twenty-six years later — the
last unfinished thought in XEvil.

It left the Windows build broken, too. `cmn/game.h:506-508` declares the member
with no platform guard —

```c
  // For logging server output to a file.
  // UNIX-only for now.
  Daemon* daemon;
```
— and `class Daemon` exists only in `x11/xdata.h`. The October 2000 snapshot
compiles on UNIX and cannot compile on Windows. That is why it was a developer
zip and not a release.

After 07:00 on 21 August 2000, nothing in this tree was ever edited again. Two
months later, on 22 October, Steve Hardt zipped it up and put it on the FTP site.
Then he stopped.

## The Death March has a name

Part I called `IDM_DEATHMARCHSOUNDTRACK 1631` "the only trace of a tenth music
track" and Part II buried it as gone before the tape starts. Both were one file
short. The Visual C++ project has never been cleaned
(`win32/xevil.dsp:859`, present identically in A, in B, and in this repo):

```
SOURCE=.\res\dethmrch.mid
```
Ten `.mid` entries in the project; nine files on disk. **The lost track was called
`DETHMRCH.MID`**, it lived in `win32/res/` alongside the others, and it was
deleted from the folder without being removed from the project. There are still no
bytes to recover — but there is now an exact 8.3 filename to hunt for in any
surviving 1.x/2.0-beta build or backup, which is more than we had.

## Human traces

Things Steve Hardt wrote to himself in the last months, none of which appear in
the released source:

- `cmn/world.cpp:2372` — after nine lines of infinite-loop guard, the entire
  justification for the fallback path: **`// Fuck it.`**
- `cmn/utils.cpp:47` — **`// We will get warnings from doing this, but fuck it.
  At least it compiles.`**
- `cmn/physical.cpp:9418` — **`// Sucks ass, not extendable.`**, written over the
  new `AnimTime` class-lookup switch: a companion piece to the pre-existing
  *"Not very extendable.  This sucks, Beavis."* over the Fighter one (`:7499`)
- `cmn/game.cpp:1196-1197` — on his own architecture: *"Sure would be nice to move
  the above code somehow into Role.  Game really shouldn't have to do
  role->get_type().  **Bad OO programming.**"*
- `cmn/role.cpp:2800`, in the server's blocking connect loop:
  **`// Really should have a timeout here.`**
- `cmn/role.cpp:939` — **`//// Why do we need this.  Don't we already do it in
  Client::~Client??`** (the `////` prefix is his tell for arguing with himself)
- `cmn/physical.h:79-81` — **`// WARNING: If you add another droplet type, also
  add it to Droplet::choose_droplet_class().  Yeah, I know, should be a better
  way.`**
- `cmn/game_style.cpp:1775`, above the `-scenario` string comparisons:
  **`// Ick, not extensible.`**
- `cmn/physical.h:2200-2203` — a feature idea, in writing, that never happened:
  *"Will need to implement some other way of representing fractional gravity if we
  want to create **"upside-down world"** or something like that."*
- `cmn/bitmaps/zombie/zombie.bitmaps:258` — **`// Moved body slam down one, so
  doesn't go above people.`**
And one that is older than the rest but too good to leave out: `cmn/game.cpp:3456`
carries an edit its author signed in the code, **`// moved after the
Locator::add(), hardts`** — his MIT Athena username, the same one that appears in
`Game::intelNames` so you can frag him. It is in the release too, worded *"moved
to after the Locator::add()"*; in the last months he went back and deleted the
stray "to".

And two quieter ones.

`classes.txt` — the hand-drawn ASCII class hierarchy — was updated on 3 April 2000
to add `Feather`, `Zombie` and `Chicken` (and to note that Chicken is both
`Flying` and a `Fighter`). In the same pass he fixed two lines of indentation that
had been wrong since 1999: `(Yeti)` under `Prickly` and `(Alien)` under `Healing`
(`classes.txt:169` and `:172`). Nobody would ever have noticed.

And the licence headers. In the 2.02r2 release exactly one file still carried the
pre-GPL, shareware-era notice — *"obtain a copy from http://www.xevil.com/docs/
license.txt"* — and it was `hugger.bitmaps`. He caught it and replaced it with the
full GPL block. But the two files he created in February 2000 were copied from a
stale template, so today the *only* two files in the whole of XEvil still bearing
the pre-GPL header are the Chicken and its feathers:

```
cmn/bitmaps/chicken/chicken.bitmaps
cmn/bitmaps/feather/feather.bitmaps
```

### Loose threads he left behind

Half-finished work still sitting in this repo, for anyone who wants it:
`Locator::team_member()` is written, complete, and fenced off in `#if 0`
(`cmn/locator.cpp:1386-1411`) — and references a `member` field that does not
exist. `Utils::ceil` and `Utils::floor` were added (`cmn/utils.h:261-265`), are
called by nothing, and are both wrong (`ceil` rounds half-up; `floor` truncates
toward zero). `DEFINE_CREATURE_CTORS_1` was defined and never used
(`cmn/actual.cpp:130-138`). `attack_free_horizontal()` is a one-line shim left
behind by a rename (`cmn/physical.h:2801`). And `class Pulser` was written as the
general answer to fractional timing, then used only by droplets while the new
gravity code reimplemented it by hand.
