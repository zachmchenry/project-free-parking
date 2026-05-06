# Persona Documentation

System rules, calibration cases, and facilitator notes for the five Project Free Parking stakeholder chatbots. One markdown file per persona, plus a shared spine document.

These docs serve three audiences:
- **Instructional designers** reviewing prompt design (the layered breakdown sections)
- **Faculty role-players** calibrating their live performance against the bot (the calibration test cases and conversational tone notes)
- **Curriculum PMs** auditing what the bots are actually doing (the rendered prompt as source of truth)

## Files

| File | Persona | Role in exercise |
|------|---------|------------------|
| [_spine.md](_spine.md) | Shared spine | Common rules every persona inherits |
| [diane.md](diane.md) | Diane Foster | Target customer (parent of three) |
| [sarah.md](sarah.md) | Sarah Park | Sponsor (Hasbro Senior PM, wrote the brief) |
| [marcus.md](marcus.md) | Marcus Webb | Loud non-customer (board game community) |
| [theo.md](theo.md) | Theo Larsen | Secondary user (age 11) — ⚠ chat fidelity warning |
| [choi.md](choi.md) | Mrs. Eleanor Choi | Pattern-recognition voice (retired teacher) |

## How to use these docs

**Before deploying a persona to a cohort.** Read the corresponding markdown file end-to-end. Pay particular attention to the "calibration test cases" section — run those 10 cases against the bot before any cohort sees it. If a case fails, the prompt needs adjustment before deployment.

**During cohort operation.** The "facilitator notes" sections contain calibration anchors for evaluating trainee work. "Did the team surface the bankruptcy-and-ice-cream insight from Theo?" is a more useful evaluation question than "did the team interview Theo well?"

**When prompts need updating.** Edit the persona's `.py` module first. Then update the markdown's "rendered prompt" section to match. Drift between the Python prompt and the markdown documentation is the most common documentation problem in operational use; a quick monthly audit catches it.

**For role-player calibration.** Live faculty role-players should read the corresponding markdown before playing the role. The calibration cases tell role-players how the bot responds to specific prompts, which lets the live role-player align — or deliberately differ — with the bot version.

## What the docs do not cover

- The architectural design of the chatbot system (in `Bundle 5c — Project Free Parking Chatbot Personas` from the curriculum bundle set)
- The full Project Free Parking exercise structure (in `Bundle 5` from the curriculum bundle set)
- Implementation details of the Flask app, off-topic classifier, or provider abstraction (in the project README and inline code comments)

## Maintenance

The markdown docs and the Python prompts can drift apart over time as one is edited but not the other. To prevent this:

1. When editing a persona's `.py` file, also update the corresponding `.md` file's "rendered prompt" section.
2. When discovering a new failure mode in operational use, add a calibration test case to the markdown so the next deployment catches it.
3. When the shared spine changes, update `_spine.md` and re-verify each persona's behavior against its calibration cases.
