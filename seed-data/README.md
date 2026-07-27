# Seed data

`accounts.json`, `briefs.json`, `demo-transcript.md`, and `demo-2min.srt` are fictional demo inputs. Load the seeded JSON and markdown transcript with `cd backend && uv run python -m clipops.seed`.

`demo-2min.srt` is a standalone subtitle import fixture for exercising the SRT adapter. It is not loaded by the seed command.

Only fictional data belongs here. Simulated performance data must be labeled.
