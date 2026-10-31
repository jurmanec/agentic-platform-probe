
## idempotency key

Question:
Give me the practical use case. Where would the key come from if a person is calling the API?

Answer:
The person does not invent the key on each retry. The program that sends POST /ask creates it once, when the person commits to one question, and reuses that same string if the HTTP call has to be sent again.

Maya types “Is SMS allowed for residential Northeast active segments?” and clicks Ask. The page generates a key at that click, for example 8f3c1a2e-6b14-4d0a-9c77-2a1e0b9d44c1, and posts it with the query. The API runs E2 and stores the answer under that key. If the browser times out and the page automatically retries, it sends the same key and the same query. E3 returns the stored answer and does not call the model again. If she changes the wording and clicks Ask a second time, that is a new operation, so the page mints a new key.

In the demo curls and in Bruno, a person pastes demo-happy-001 by hand because there is no application in front of the API. That string is standing in for the id the real client would have generated. Common sources for that id are a UUID created at submit time, or an id the caller already has for the operation, such as a campaign-request id. The rule is the same either way: one intended ask, one key, held constant across retries.
