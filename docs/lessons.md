# What I learned

## The owner tells you the answer before you ask

Before one feedback meeting I checked how the product was actually being used. The CRM was in daily use. Almost everything built after it had stopped: quotes untouched for weeks, stocktakes abandoned, events unstaffed in the system. It changed the meeting from "what should we build next" to "why did you stop". The answer was friction and disconnection, not rejection. Later, when the owner could not build a quote for two bartenders for four hours plus a waiter for five, the evidence was already in the data: the owner had made the quote without extras and then typed the invoice by hand, because that screen allowed typing. Usage data is the cheapest user research there is.

## Model the unit of work in their words first

The one design that shipped and was rejected within a day was modelled on the database table, not on how the owner works. Three careful reviews checked everything except the thing that was wrong. Now, before any design review, I write down the unit of work in the owner's words and confirm it with them.

## Good accounting can be the wrong answer

"Two invoices per job" was correct and useless to a one-person business. Keeping that choice out of the schema is the only reason reversing it was cheap. Where I am unsure a rule reflects how the customer thinks, I keep it in the UI layer until it has survived real use.

## Retroactive by construction

PDFs are rendered when downloaded, so any change to the renderer changes every document ever sent. That forced a discipline I now use everywhere: freeze what a document was, and when rendering has to change, branch on data that only newer documents carry. A regression that would have relabelled old documents was only caught by seeding an old-style record and rendering it, not by reading the code.

## A check with no failing case is not a check

The CI type check was green on every pull request for months and checked zero files, because the root config only references other configs and the command did not follow them. A build guard for duplicated headings existed from day one and never fired, because its pattern could never match. An asset audit searched for a vendor's name in text and missed the vendor's logo sitting in the favicon. Since then, every new guard is shown failing once before it is trusted, and audits look at the thing itself, not a text proxy for it.

## Verify with the real system, and with real tokens

Several things I believed were true were not. One example: a form flow the documentation described as manual had been handled by a database trigger for months. Reading code and migrations tells you what should be true. Calling the API as each role, and querying the live state, tells you what is.

## Local-first migrations saved production more than once

Making every migration replay from scratch on a local stack, with seeded admin and worker accounts, took real effort early on. It paid for itself repeatedly: prod and local drifted in small ways that would have silently deleted fields from generated types, and every risky change could be run end to end before it reached Jose's data.

## Write the manual as part of the product

For months every "how do I" question lived in my head or a chat thread, and the only written guide was months out of date and wrong about how staff logins worked. The help centre now lives on the product's own domain, is organised around the flow of a job rather than the list of screens, and is rebuilt on every deploy from markdown so it cannot drift. It also caught me: my first draft described a flow backwards, in exactly the place Jose would have relied on it.

## What I would do differently

- **Name the design system on day one.** The token mix-up between "hovered" and "selected" cost more to find than to prevent.
- **Get a real test runner in before the first money feature.** The money logic was designed carefully and reviewed, but not executed as tests until months later.
- **One combined preview for a batch of changes.** Handing over six separate preview builds for one feedback round made it look as though nothing had shipped.
- **Ask about the PWA cache earlier.** A service worker that never activated the new version made three releases look like they had not happened, and because documents are generated in the browser, a stale app can produce a stale document.
