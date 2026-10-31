# Ops runbook — journey step validation

Illustrative runbook for marketing-ops engineers before activating a journey step.

## Before activation

1. Confirm the **segment ID** resolves in the audience platform.
2. Load **channel policy** and audience rules for that segment.
3. Review the proposed step: channel, message theme, timing, rationale.
4. Run **constraint validation**. Reject if any rule is violated (for example SMS on a residential segment).
5. Obtain human or workflow approval when the step is promotional or customer-facing.

## After validation fails

- Do not activate.
- Capture the cited `rule_id` and reason in the ops ticket.
- Revise channel or theme and re-validate.

## After validation passes

- Hand off to the activation queue.
- Do not treat an LLM draft as activated until the platform activation API succeeds.
