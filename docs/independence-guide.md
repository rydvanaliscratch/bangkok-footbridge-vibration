# Operating guide — running this project yourself

You own this project. Claude is a reference and a source of code, not a participant.
This document is what lets you say that truthfully.

---

## 1. The line

Your standing rule: **Claude may write code; you must be able to re-derive everything
in it.** That is a real and defensible line — engineers use reference implementations,
libraries and colleagues' code constantly. What makes it yours is that you understand it.

So the test is not "did I type this." It is:

> Could I explain every configuration choice, every equation and every threshold in
> this project to someone who asked, without looking anything up?

If the answer is no for some part, that part is not finished yet, however well it runs.

**Yours alone, always:** the prose of the paper, the literature summaries, the
interpretation of results, the essay. engrXiv rejects work showing excessive
language-model use; NHSJS bans AI-drafted prose outright even if edited afterwards.

---

## 2. What you must be able to defend

Work through these once the rig is running. If you can answer all of them cold, the
project is yours in any sense that matters.

**Instrument**
- Why is DLPF set to 21 Hz rather than left at the default 260 Hz?
- What does ±2 g full scale give you in counts per g, and what is one count worth?
- Why sample at 200 Hz when the signal is below 10 Hz?
- Why timestamp every sample instead of assuming the interval?

**Physics**
- Why is road traffic the excitation rather than contamination?
- Why does averaging many windows recover a peak the sensor's noise floor appears to swamp?
- Where does damping come from, and why can it only come from the free decay?
- Derive the pendulum's 1.00 Hz from T = 2π√(L/g). Why is there also a peak at 2 Hz?

**Analysis**
- Why subtract the mean before the FFT?
- What sets your frequency resolution, and what did you choose for window length?
- What does the logarithmic decrement measure and how does δ relate to ζ?
- Why does a peak have to be absent from the ground control before you can claim it?

**Judgement**
- Why is a footbridge frequency not transferable to a building model?
- Why is a null result still publishable?
- What is your largest source of uncertainty, and how big is it?

---

## 3. The standing rules

- No result-tuning. Disagreements between methods get reported, not averaged away.
- Raw data committed, not only plots. SI units throughout.
- Never write "published" before it is true. "Submitted for peer review" is honest.
- No claim that this is an early-warning system, that footbridges are at seismic risk,
  or that the method is novel. The method is published — cite it.
- The null result is publishable. Decide that before you have data.

---

## 4. Getting the repository onto GitHub

Everything below you run yourself. Ten minutes.

**One-time setup**

1. Create a free account at github.com if you have none.
2. Install Git. Windows: git-scm.com. macOS: `xcode-select --install`.
3. Set your identity:

```
git config --global user.name "Your Name"
git config --global user.email "your@email"
```

**Create the repository**

4. On github.com click **New repository**. Name it `bangkok-footbridge-vibration`.
   Public. Do **not** tick "add a README" — you already have one.
5. In a terminal, from the project folder:

```
git init
git add .
git commit -m "Instrument firmware, repository structure, data dictionary"
git branch -M main
git remote add origin https://github.com/<your-username>/bangkok-footbridge-vibration.git
git push -u origin main
```

GitHub will ask for a **personal access token**, not your password: Settings →
Developer settings → Personal access tokens → Fine-grained → generate one with
repository write access, and paste it when prompted.

**Working from then on**

```
git add .
git commit -m "Bench gate B3: noise floor 34 counts SD over 60 s"
git push
```

Commit after every gate and every field session. Write commit messages that say
what happened, including failures — `"B4 failed, 900 us jitter, was printing floats"`
is a more valuable line in the history than a tidy repository.

---

## 5. What makes the repository worth more than a journal name

A journal name is a claim about your work. The repository *is* the work, and anyone
can open it. Put in it the things that cannot be faked:

- The calibration numbers you actually measured, including the ones that failed first.
- The ground control recordings, not just the bridge ones.
- Raw CSVs alongside every plot.
- A limitations section in the README that says what you could not conclude.
- The build log, with the dead ends in it.

An interviewer who opens this and finds a documented noise floor, a pendulum
calibration against an analytically known answer, and a control measurement designed
to rule out the obvious objection, learns more about you than any acceptance letter
would tell them.

---

## 6. Order of work

1. Solder the headers. Wire the four jumpers.
2. Upload `firmware/logger/logger.ino`. Confirm `WHO_AM_I ok` at 115200 baud.
3. Bench gates B1–B5. Commit the calibration CSVs.
4. Write the capture script; capture to `data/raw/`.
5. Pilot bridge, full protocol, analyse the same evening.
6. Freeze the protocol. Seven more bridges plus two repeat visits.
7. Analysis, figures, results table.
8. Zenodo DOI for a frozen snapshot of the repository.
9. engrXiv preprint. Then a journal if you choose to.

Nothing advances past a gate that has not passed.
