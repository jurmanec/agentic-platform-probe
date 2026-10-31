# Channel policy — residential segments

Illustrative marketing-ops policy for audience segments that are **residential** and **active**.

## Allowed channels

- **Email** — allowed for residential active segments when the customer has email consent on file.
- **In-app** — allowed for residential active segments with an active app session or push token.
- **SMS** — **not allowed** for residential segments. Use email or in-app instead.

## Segment note

For the illustrative segment `seg_residential_northeast_active` (residential, Northeast region, active accounts):

- SMS is disallowed (`rule_no_sms_residential`).
- Prefer email for upgrade and billing notices.
- Prefer in-app for account-status reminders.

## Frequency

Do not send more than one promotional email per calendar day to the same residential segment journey without ops approval.
