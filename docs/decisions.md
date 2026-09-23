# Decisions

Seven decisions from the project, written as short ADRs. Each one is real, and several reversed something we had already built.

---

## 1. Kill the recipe-driven inventory engine; count bottles instead

**Context.** The first inventory design derived stock usage from recipes: each cocktail listed its ingredients in millilitres, events multiplied that by expected drinks, and the system converted millilitres into bottles.

**Decision.** Kill it and build the model bars actually use: a weekly physical count per item, a par level per item, a reorder list for anything below par, and events that draw stock out of one warehouse and return what comes back.

**Why.** I researched how bar inventory tools work. Across the industry, the physical count is the foundation. Recipe-based "theoretical usage" is a premium layer whose value comes from comparing it against point-of-sale data to find loss. ByJoseM has no point of sale, so that comparison could never exist. We were building the fragile half of an equation whose other half would always be empty, and it depended on recipe data being perfectly maintained. The owner is an ex-bartender and already knew the count-and-par loop.

**Tradeoffs.** We lose automatic consumption estimates. Between counts the numbers drift and can go negative, and the weekly count is the reset. Recipes survive as a helper that suggests which items an event needs, but they never touch the ledger. The help centre explains drift in plain words so a negative number does not read as a bug.

---

## 2. Drafts consume quote numbers, but never invoice numbers

**Context.** Both quotes and invoices got drafts. The question was whether a draft takes a number.

**Decision.** A draft quote takes its number immediately. A draft invoice has no number at all; a number is assigned atomically only when the invoice is issued.

**Why.** Invoice numbers are a legal sequence and issued invoices must not have gaps. Deferring the number to issue time means abandoned drafts can be freely deleted without leaving holes, and once issued an invoice can only be voided, never deleted. Quote numbers are not a legal sequence. Giving quotes the invoice treatment would have meant loosening a not-null constraint on a table with live rows and rewriting the creation functions, a second risky migration for a cosmetic gain.

**Tradeoffs.** Quote numbers can have gaps. The app says so in the confirmation message when a draft is saved, so nobody is surprised.

---

## 3. Locale-safe money parsing for number entry on a phone keypad

**Context.** Both document builders cleaned number input by stripping everything that was not a digit or a dot. On a phone keypad that offers a comma, `1,50` became 150, `1.234,50` became 1.23, and a minus sign silently disappeared. Worse, the cleaning ran on every keystroke, so a comma could not be typed at all.

**Decision.** One shared parser for every money and quantity field. Fields keep the raw string as typed and parse only when computing. The last separator is the decimal point. The ambiguous `1.500` is resolved by the kind of field: money reads it as thousands, counts read it as a decimal. Anything the parser does not trust returns nothing rather than zero, and the builder blocks with a reason. Cents are built from digit strings, never by multiplying a float by 100.

**Why.** People type numbers the way their keypad and habits suggest, and a silent zero is how a typo becomes a zero-value quote. There was no evidence it had caused a wrong document yet, which is exactly when to fix it.

**Tradeoffs.** Any heuristic for `1.500` is a guess, so the builder echoes the parsed value back in plain words next to each line. This also led to the project's first unit test suite; the money core had only ever been read, never run.

---

## 4. An accessibility pass that gave 66 icon buttons a name

**Context.** The admin had grown to around thirty pages with many icon-only buttons: edit, delete, download, drag handles. The owner asked what some of them did. A sweep found 66 icon-only buttons, 33 of which had no accessible name at all, so a screen reader announced them as "button".

**Decision.** Fix it structurally. A small wrapper gives any icon button a tooltip and an accessible name from one label, and a codemod applied it across the codebase. Separately, colour contrast was fixed at the design-token layer: a script computes the contrast of every token pair, and the tokens were adjusted until it reported zero failures.

**Why.** The tooltip helps the owner and the name helps assistive technology, and one label serves both. Fixing tokens instead of components corrected every date picker, menu and input at once. One root cause was that the accent colour (meant for hover) had been set to the brand gold (meant for "selected"), so hovered and selected states looked identical.

**Tradeoffs.** A codemod needs a careful review of each change. The token fix changed the look of hover states across the app, which needed a pass with the owner. We also corrected an earlier claim of AAA contrast that had never been true; a false claim stops people checking.

---

## 5. One catalogue and one pricing rule

**Context.** The website listed packages from one table, the quote builder read a second, and staff hire lived in a third. Prices could disagree, and a customer who tried to book a masterclass on the website ended up recorded against a different package.

**Decision.** Merge them into one catalogue with a pricing mode (flat, per guest, per hour, per cocktail, on request) and one price in integer cents. One tested pricing function feeds the website, the booking form, the CRM, the pipeline chart, the event page and the quote builder. The old tables stopped being read in one release and were dropped in the next.

**Why.** One price in one place means editing it once changes everything, and the help centre says so where the risk is. "On request" is modelled as unpriced, never as zero.

**Tradeoffs.** A migration with preserved identifiers on live data, and a two-release retirement, because the app is a PWA and an old cached bundle could still be reading the old tables. The review also found a second bug nobody had reported: the website's "book this package" button had never pre-selected the package in the form.

---

## 6. One invoice per job, reversing our own earlier call

**Context.** The owner asked whether a job should have two invoices (deposit and balance) or one invoice with two payments. We answered two invoices, which is sound accounting.

**Decision.** After three weeks of real use the owner said it meant at least two documents per job and that was not great. We reversed it: one invoice per job, a deposit is a payment recorded against it, and every payment can produce a customer-facing receipt with its own number. The invoice reads as a statement: total, payments received, balance due.

**Why.** We had answered a question the owner did not have. A sole trader needs to know who still owes them, not a filing structure. The reversal cost almost nothing, because the earlier "what is this invoice for" choice had been kept out of the schema.

**Tradeoffs.** A receipt had to become an issued state of a payment, with a number assigned once and figures frozen, so that deleting an earlier payment could never change a receipt the customer already has. The "Paid" stamp now follows the money rather than the document status, so a refund cannot leave "Paid" printed on a page that shows a balance owed.

---

## 7. Event stock is a plan you confirm, not instant movements

**Context.** Originally, adding an item to an event took it out of the warehouse immediately. When cocktails started adding their ingredients to the event, a shared bottle (vodka in two cocktails) behaved badly, and a first fix modelled the problem per ingredient. The owner found it confusing within a day.

**Decision.** State the unit of work in the owner's words and build that. A cocktail is a task: add it, its ingredients go onto the event list, remove it and exactly what it added comes off. The event's stock list is a plan. Nothing moves in the warehouse until "Confirm inventory for the event", which shows exactly what will be taken or put back. Later edits show as changed and not confirmed, and confirming moves only the difference.

**Why.** The first design followed the data model (stock per event per item) and three reviewers checked the engineering carefully without questioning the unit of work. The owner prepares a list, then packs. A confirm step matches that and makes every warehouse movement deliberate.

**Tradeoffs.** Unconfirmed items on the night are possible, so the event brief warns about them. Confirmation had to handle two open tabs and an older cached version of the app, so every stock function takes a per-event lock and the confirm refuses if the plan changed after the review dialog was shown.
