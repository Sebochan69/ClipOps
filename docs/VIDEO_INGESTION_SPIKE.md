# Video/transcription research spike

## Scope

Future video ingestion should remain separate from ClipOps v1's timestamped-transcript contract. No implementation is included here.

## Candidate path

1. Upload or import a transcript export from one approved transcription service.
2. Normalize it through an adapter into the existing `Transcript` model.
3. Preserve source timestamps and original text.
4. Keep video upload, transcription, FFmpeg preview/export, and social posting as separate future tickets.

## Trade-offs and risks

- External transcription formats vary in timestamps, speaker labels, confidence fields, and punctuation.
- Video storage and FFmpeg add large local/cloud, privacy, cost, and reliability surfaces.
- A future adapter should use fixture exports and feed the existing parser without changing candidate/review workflow behavior.

## Recommendation

Approve one transcription-export format only after a real demo requirement exists; then implement its parser adapter with fixtures. Do not add video processing to v1.
