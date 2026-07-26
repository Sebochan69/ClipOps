# Simulated performance

`POST /performance-records` imports local demo metrics only. Every record is forced to `simulated: true`; importing metrics moves its queued candidate to `PUBLISHED`. No external analytics connector exists.
