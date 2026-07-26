# Mock publishing queue

`POST /candidates/{candidate_id}/queue` adds an approved candidate to the local mock queue with a scheduled time and moves it to `READY_TO_PUBLISH`. No social platform is contacted. `GET /publishing-queue` returns scheduled mock items for the UI.
