# Review lifecycle

`POST /candidates/{candidate_id}/review` accepts `SUBMIT_FOR_REVIEW`, `APPROVE`, `REJECT`, or `EDIT`. Only valid transitions are allowed; rejections require a reason. Decisions are persisted, and invalid changes return `INVALID_STATE_TRANSITION`. The frontend queue filters a workflow run by status and exposes submit, approve, reject, and edit actions.
