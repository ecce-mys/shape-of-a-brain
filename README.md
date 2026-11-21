# Can one hear the shape of a brain?

A weekly, public study notebook on the math under brain–computer interfaces, written in English, built from scratch with AI as a pair.

In 1966 Mark Kac asked: *can one hear the shape of a drum?* If you know every frequency a drum can ring at, do you know its shape? In 1992 Gordon, Webb and Wolpert showed the answer is **no**: two differently shaped drums can sound exactly the same.

EEG has the same problem. We record voltages on the scalp and want to know where in the brain they came from. Helmholtz showed in 1853 that this inverse problem has **no unique solution**. Every source-localization method is a choice of what extra assumptions to add.

This notebook works through that question one piece at a time, from the drum to real EEG.

## Plan

| # | Entry | Question | Status |
|---|---|---|---|
| 01 | [The drum](entries/01-drum/) | What *can* you hear from a spectrum? (area, perimeter, not shape) | started |
| 02 | Where EEG comes from | How do neurons make a voltage you can measure on the scalp? | |
| 03 | The forward model | Given sources, what does the scalp see? (lead field) | |
| 04 | The inverse problem | Why there are infinitely many answers, and how minimum-norm picks one | |
| 05 | Phase locking | When do two signals "move together"? (PLV) | |
| 06 | Functional connectivity | From pairs to networks, and the volume-conduction trap | |
| 07 | Decoding | Reading a simple intention from real data | |

## Rules

1. **One entry per week.** Small is fine. Shipped beats perfect.
2. **Build it, then explain it.** Code from scratch (AI can pair), but every explanation is written in my own words.
3. **Every entry has a "what I still don't know" section.** That's the next entry's seed.
4. **Every entry ends with 3–5 English phrases I needed.** They go into my morning drill (`ody words add "phrase | 뜻"`).
5. **Real data when possible.** MNE-Python sample data, PhysioNet, OpenNeuro.

## Running

Each entry is a self-contained [uv](https://docs.astral.sh/uv/) script:

```bash
uv run entries/01-drum/drum.py
```
