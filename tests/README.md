# Tests

Browser checks (Playwright + Chrome) for the whole app: map taps and gestures, search and coffee, Steps tab,
audio guide (play, pause, iPhone-style interruptions, resume, guide mode), guide text and photo setup,
directions box, parts and banner, walk chooser, repeated-text handling, street map tiles, blue dot and arrival chip.

Run: `GUIDE_TEXT=/path/to/chapter.txt tests/run_all.sh` (add `GUIDE_PHOTOS=/folder` to include the photo-page checks).

The book's text and photos are deliberately **not** in this repository; the tests read your own copies from those paths.
Map tiles are replaced with stand-in tiles in `maptest.py`, so the tests work without network access.
