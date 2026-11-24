# AI use log

Some venues screen for AI use (engrXiv rejects papers showing excessive LLM use; some student journals
ban AI-drafted prose; JHSS asks authors to identify writing assistance). This log keeps the answer easy
and honest. Drafted by Claude on 17 Nov 2026 from `docs/build-log.md`, in the format of Project 2's log;
Rydvanali checks every line before it is committed. All lines were checked by Rydvanali (20 Nov 2026).

## Policy for this project

- **Recording and analysis runs:** every field and bench recording was made by Rydvanali. Every official
  analysis run (results/, figures/) was made by Rydvanali on his own computer (10 Nov 2026). Claude's runs
  were previews in scratch copies, logged as "preview, not the record".
- **Code:** written and tested by Claude (Anthropic) at Rydvanali's request, explained to him line by line.
  Tested on made-up signals with known answers (`analysis/selftest.py`, 12 of 12 pass) and by Rydvanali's own
  runs, which matched the previews.
- **Predictions:** written and worked by hand by Rydvanali on 14 Oct 2026, before any bridge recording
  (`predictions/predictions_20261014.md`).
- **Prose, interpretation and decisions in the paper:** written by Rydvanali. Claude helps with section
  outlines and checks facts and numbers. Claude corrects grammar and adds small connecting words or phrases between
  his sentences (policy set by Rydvanali on 17 Nov 2026, same as Project 2). Each change is shown to him
  before it is kept. Claude does not write new sentences, claims or interpretation.
- **Repository documentation** (README, licences, literature notes, this log, and build-log entries marked
  as Claude's): drafted by Claude, checked and approved by Rydvanali. It is not part of the paper.

## Entries

| Date | Tool | What it was used for | What was checked |
|---|---|---|---|
| Sep 2026 | Claude | Suggested several project ideas and drafted the study plan (outside the repo), from Rydvanali's directions | Rydvanali chose this project from the options |
| Sep-Oct 2026 | Claude | Wrote `firmware/i2c_scanner/i2c_scanner.ino` and `firmware/logger/logger.ino`, to Rydvanali's requirements | WHO_AM_I check on the real board; bench gates B1-B4 |
| Sep-Oct 2026 | Claude | Wrote `analysis/capture.py`, `bench_checks.py`, `b2_check.py`, `common.py`, `spectrum.py`, `damping.py`, `pendulum_check.py`, `pendulum_ringdown.py`, `analyse_bridge.py`, `span_fit.py`, `selftest.py` | Tests on simulated data; Rydvanali's runs |
| Sep-Oct 2026 | Claude | Wrote `docs/how-to-record.md`, `docs/independence-guide.md` and `docs/limitations.md`, from Rydvanali's instructions and field notes | Read and used by Rydvanali |
| 20 Oct-1 Nov 2026 | Claude | Preview checks of each new recording (rate, gaps, clipping, peak, ground ratio, drops), logged as previews | Rydvanali's official runs on 10 Nov matched |
| 26 Oct 2026 | Claude | Proposed and coded the post hoc change to drop detection (band-passed signal); logged as post hoc, old count still printed | Rydvanali decided; selftest 12 of 12 |
| 10 Nov 2026 | Claude | Preview of the span fit; an incorrect first comment (f x L^2 scaling) was withdrawn the same day and logged | Correction logged in build-log |
| 12 Nov 2026 | Claude | Frequency check of mislabelled files (31 Oct, 24 Oct) | Rydvanali confirmed the 31 Oct label on 13 Nov |
| 16 Nov 2026 | Claude | Secret scan of git history; drafted README, LICENSE, data/LICENSE, literature notes; literature search (web and TCI) | Rydvanali reviewed and committed (3919faf) |
| 17 Nov 2026 | Claude | README fixes (install step order; question 2 marked as background); read JHSS author rules; drafted this log | Rydvanali to review |
| From 17 Nov 2026 | Claude | Paper: outlines and facts per section; grammar fixes and small connecting phrases in Rydvanali's text, each shown to him | Rydvanali approves every change |
| 20 Nov 2026 | Claude | Built Tables 1 and 2 from results/; recounted the old detection rule's drop counts per decay file (scratch copy); calculated the span-fit slope without bridge03 (-1.21, 95% range -1.80 to -0.62) in a scratch copy, because span_fit.py cannot leave out a bridge (the sensitivity fit was decided by Rydvanali before his official run on 10 Nov) | Rydvanali ran the official damping run on the 31 Oct file (same result as the preview); the without-bridge03 slope is not from an official run |
| 21-24 Nov 2026 | Claude | Discussion: averaged the per-drop ringing frequencies (f_ring_hz) from the official runs in results/damping.csv (bridge05 3.31 Hz, bridge02 4.76 Hz, bridge03 3.33 Hz) for the decay-vs-ambient comparison; grammar fixes, fact fixes and two honesty fixes in Rydvanali's Discussion text, each shown to him | Rydvanali approved every change (24 Nov) |
| | | | |

## Who did what

| | Rydvanali (sole author) | Claude (AI assistant, not an author) |
|---|---|---|
| Question and design | Directed the work; chose this project from Claude's options; wrote the sealed predictions by hand | Suggested several project ideas; drafted the plan |
| Hardware and fieldwork | Soldered, wired, mounted, recorded every file; paced the spans | Advice on mounting and procedure |
| Decisions | Made every decision in the build log | Drafted options and recommendations |
| Code and runs | Ran every official analysis | Wrote all code and tests; ran previews |
| Paper | Writes the paper; decides what to keep | Outline, facts, number checks; grammar and small connecting phrases |

## What the paper's AI statement must cover (Rydvanali writes the wording)
It must not be narrower than this log: (1) the firmware and analysis code; (2) preview checks of the data;
(3) help with the plan, decision options, literature search and repository documentation; (4) grammar
correction and small connecting phrases in the paper; (5) that all recordings, official runs, predictions,
decisions and the paper's content are Rydvanali's.
