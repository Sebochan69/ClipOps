# Domain model

Foreign keys define the initial SQLite relationships:

- `SourceContent` → `Transcript` → `TranscriptSegment`
- `WorkflowRun` → `ModelRun` and `ClipCandidate`
- `AccountProfile` → `ClipCandidate` and `PublishingQueueItem`
- `ClipCandidate` → `ClipScore`, `GeneratedAsset`, `ReviewDecision`, and `PublishingQueueItem`
- `PublishingQueueItem` → `PerformanceRecord`

`ContentBrief`, `ContentExperiment`, and `WeeklyGrowthReport` are independent records until their workflow/API tickets define the required links. Performance and weekly-report records carry a simulated-data flag.
