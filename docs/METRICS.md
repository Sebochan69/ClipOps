# Dashboard metrics

`GET /dashboard` returns simulated approval rate, queue count, and account metrics. Health score is a transparent capped formula: median simulated engagement rate × 500, capped at 100. It is not a growth or causal claim. The dashboard UI displays the same metrics with a simulated-data disclosure.
