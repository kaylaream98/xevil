===============================================================================
  XEvil 2.5  --  native Windows edition (64-bit)
===============================================================================

WHAT THIS IS
------------
XEvil is a fast, side-view, splatter-happy fighting game from 1994-2000 by
Steve Hardt and Michael Judge.  You are dropped into a scrolling underworld of
clanking machines and hungry creatures; climb the ladders, ride the elevators,
grab whatever weapon you can find, and kill everything.  When you finally die,
XEvil ranks you somewhere in Hell's hierarchy -- from "Hell's Peg Boy" up to
"You are the new Satan."

This is XEvil 2.5, a 2026 revival of the last official release (2.02).  It adds
sound and music, five new weapons, a new creature, new scenarios and game
styles, smarter enemies, HiDPI display scaling, and more.

xevil.exe is a SINGLE self-contained program.  There are no DLLs to install and
no asset folders to keep next to it -- every sprite, sound effect and music
track is baked into the one file.  You can copy xevil.exe anywhere and it will
just run.


HOW TO PLAY
-----------
Double-click  xevil.exe.

A window opens on the license screen -- click "Accept" (once) to agree to the
GNU GPL.  Then use the menu bar at the top:

  * "Game style"  -- pick Levels, Kill Kill Kill, Survival, Boss Rush, etc.
  * "New Game"    -- start.  You will be asked to pick a difficulty:
                     press 0 (trivial), 1 (normal), 2 (hard) or 3 (bend-over).

(No sound card?  No problem -- XEvil detects that and plays silently.)


CHANGING THE DIFFICULTY
-----------------------
EVERY "New Game" asks for the level of difficulty, so you are never stuck with
an earlier choice.  Your previous pick is HIGHLIGHTED in the list, and [space]
or [enter] keeps it -- changing difficulty is just "New Game" and a different
number:

    0 .... trivial          2 .... hard
    1 .... normal           3 .... bend-over

The choice is remembered between sessions as the "difficulty=" line in
%APPDATA%\XEvil\.xevilrc, and it comes back as the highlighted default next
time.  Prefer not to be asked?  Start with  xevil.exe -difficulty hard  (or
trivial / normal / bend-over) to pin it for that run.


FULLSCREEN: F11, AND TWO WAYS TO FILL THE SCREEN
------------------------------------------------
F11 toggles fullscreen at any time; xevil.exe -fullscreen starts there.  XEvil
draws at a fixed, chunky pixel size, so a widescreen monitor leaves some room
around it -- how that room is used is up to you:

    fill (the default) ..... stretched to the screen with the aspect ratio kept
                             (a bar only where the screen's shape demands one).
                             The biggest picture; pixels are no longer uniform.
                             This is exactly how fullscreen has always looked.
    crisp .................. whole-pixel scaling, black surround.  Every pixel
                             of the art stays a perfect square -- sharpest, but
                             a noticeably smaller picture on a wide monitor.

Choose it with a flag --  xevil.exe -fullscreen_crisp  /  -fullscreen_fill  --
or permanently by putting a line in %APPDATA%\XEvil\.xevilrc:

    fullscreen_mode=crisp


CONTROLS (quickstart)
---------------------
Movement is on the NUMERIC KEYPAD (turn NumLock OFF).  The arrow keys and
W/A/S/D also move you.

    Keypad 8 / 2 / 4 / 6 .... up / down / left / right
    Keypad 7 / 9 / 1 / 3 .... diagonals
    Keypad 5 ................ stand still
    Insert .................. fire / use your weapon
    Home .................... switch to the next weapon
    Page Up ................. drop the current weapon
    Delete .................. use your item (e.g. a med-kit)
    End ..................... switch to the next item
    Space ................... chat (type a message, Enter to send)

    F1 ..................... PAUSE (shows a "PAUSED" overlay; any key resumes)
    F11 ................... toggle FULLSCREEN
    Esc ................... close an overlay / the Help screen

Everything is remappable from "Set Controls" in the menu bar; "Show Controls"
displays the current layout.  Two players can share one keyboard.

Handy command-line flags (open a Command Prompt in this folder):
    xevil.exe -kill                 free-for-all deathmatch
    xevil.exe -survival             endless escalating waves
    xevil.exe -human_class dragon   play as a Dragon (try yeti, ninja, ...)
    xevil.exe -fullscreen           start in fullscreen (F11 toggles)
    xevil.exe -fullscreen_crisp     fullscreen, whole pixels + black surround
    xevil.exe -difficulty hard      pin the difficulty; skip the New Game prompt
    xevil.exe -scale 2              enlarge everything 2x for big / 4K screens
    xevil.exe -help                 full list of flags


WHERE YOUR SETTINGS AND HIGH SCORES ARE SAVED
---------------------------------------------
XEvil stores two small text files in your Windows profile, under:

    %APPDATA%\XEvil\

which is normally:

    C:\Users\<you>\AppData\Roaming\XEvil\

  * .xevilrc        -- your saved settings: sound, window mode, the last
                       difficulty you picked ("difficulty="), and the
                       fullscreen look ("fullscreen_mode=fill", the default,
                       or "=crisp")
  * .xevil_scores   -- the top-10 high-score table, stamped with Hell ranks

The folder is created automatically the first time it is needed.  Delete these
files to reset your settings or clear the high scores.


LICENSE AND SOURCE CODE
-----------------------
XEvil is free software under the GNU General Public License, version 2 or later.
It comes with ABSOLUTELY NO WARRANTY.  See the file "gpl.txt" in the XEvil
source tree for the full license text; the in-game license screen (the one you
Accept at startup, or run "xevil.exe -info") also reproduces it.

This binary was built entirely from freely available source code.  The complete
corresponding source -- the cross-platform game engine, the SDL2 front end, and
the mingw-w64 build files that produce this exact xevil.exe -- is distributed
with the XEvil 2.5 project.  The static SDL2 library linked into the exe is the
official SDL2 mingw development release (also under the zlib license).

XEvil(TM) is a trademark of Steve Hardt and Michael Judge.  http://www.xevil.com
===============================================================================
