# Security

This page describes the patterns, not the implementation. It deliberately leaves out table names, policy names, function names, environment configuration, project identifiers and the paths of private routes.

The platform holds customer contact details, event details, staff contact details, prices and invoices for a small business. The threat model is ordinary and real: an anonymous visitor poking at the public API, a staff member seeing more than their own work, and the owner making a mistake that changes a document a customer already has.

## Principles

1. **The database is the boundary.** The app talks to the backend directly from the browser, so every rule that matters is enforced in Postgres. Frontend route guards exist for a clean experience, never as the control.
2. **Least visibility by default.** Anonymous users read active public content and can submit an enquiry. Workers read what their current assignments need. Everything else is admin only.
3. **Money and stock are computed on the server.** The browser shows a live preview, but the stored totals and stock movements are calculated by database functions from the inputs, not accepted from the client.
4. **History is append-only where it matters.** Revisions, payments and stock movements are journals. Issued documents cannot be deleted.
5. **Verify against the running system.** A policy is not considered working until it has been exercised with a real token for each role.

## Roles and row level security

- Row level security is enabled across the application's tables, and new tables ship with their policies in the same migration.
- A role table maps each signed-in user to admin or worker. Two helper functions answer "is admin" and "is staff", and policies are written in terms of those helpers rather than repeating the lookup.
- **Public content** (packages, reviews, FAQs, recipes shown on the menu) has an anonymous read policy limited to rows the owner has marked active or visible. Hidden rows, such as imported reviews waiting for the owner's approval, are not readable anonymously.
- **Customer and business data** (enquiries after submission, leads, quotes, invoices, payments, stock, staff directory) is admin only for every operation.
- **Worker access is scoped through the assignment.** A worker can read an event, its menu and its checklists only while they hold a live assignment to it, and can update only their own progress on their own assignment.
- **The enquiry form is the only anonymous write**, and it goes through a server-side function rather than a direct insert. User input is stored as typed and escaped where it is rendered, including inside email templates.

## Database functions for money and stock

Anything that creates or changes a quote, an invoice, a payment or a stock level runs through a small set of database functions rather than direct table writes. They share the same rules:

- Each checks that the caller is an admin inside the function body, not only through grants.
- Each runs with a fixed search path.
- Totals are recomputed in integer cents from the line inputs and the document's frozen VAT settings. The client's own total is never stored.
- Stock changes take the new absolute quantity, compute the delta server-side under a row lock or a per-event lock, and write a journal row. This makes retries and two open tabs safe.

## Document integrity

- **Issued invoices cannot be deleted.** This is a database rule, not a hidden button. Cancelling an issued invoice means voiding it, which keeps its number.
- **Receipted payments cannot be deleted** through the app or through the API. Corrections are recorded as a negative payment.
- **Documents snapshot their inputs.** Business identity, VAT status, line items and prices are frozen at the time of writing, so a settings change never rewrites what a customer already holds. Because PDFs are rendered on download, any renderer change is retroactive by nature, so new rendering rules branch on data that only newer documents carry.

## Staff sign-in

- Staff never have passwords. The owner creates a login from the staff directory and the staff member receives a sign-in link by email.
- The worker sign-in page answers the same way whether or not an address is registered, so it cannot be used to discover which emails belong to staff.
- Email addresses are normalised before every comparison.
- Changing a staff member's email is an explicit, confirmed action that moves their login and their assignments and switches the old login off, instead of silently creating a second account.
- Re-using an address that already belongs to another staff member is refused.

## Admin gating

- Admin routes render only for a signed-in admin, and every query behind them is also admin-only in the database.
- Admin-only code, such as the PDF renderer and the document builders, is split into chunks that load on demand after sign-in. The PDF library in particular is a large chunk that is never part of the public bundle.
- Prices and commercial details are left off staff-facing event briefs by default, because staff read them.

## Storage

- **Site images** are publicly readable, because the public site shows them, and writable by admins only.
- **Training media** is readable by signed-in staff and writable by admins only.
- Uploads are resized in the browser before they are stored, and pages request resized versions through an image transform instead of originals.

## Secrets and configuration

- Only the public client key ships to the browser. It grants nothing on its own; row level security decides what it can do.
- Privileged keys and email provider keys exist only in the server-side functions' secret store.
- Local environment files are git-ignored, and the case study repository you are reading contains no configuration at all.

## QA and verification practice

- **Design review before code** for anything touching money, stock, auth or the schema: architecture, UX and QA concerns are written into one design note before building.
- **A written test matrix per feature** covering happy paths, edge cases, error states, responsive layouts and each role.
- **Access checked with real tokens.** Policies are verified by calling the API as anonymous, as a worker assigned to the event, as a worker not assigned to it, and as an admin, and comparing what comes back.
- **A local stack that replays every migration from scratch**, with seeded admin and worker accounts, so risky changes are exercised end to end before production.
- **Migrations ship ahead of the code that needs them** and are backward-compatible with the version already deployed, so there is no window where the site expects a column that does not exist yet.
- **Unit tests on the money, pricing, number parsing and stock logic**, run in CI along with a real type check and a production build.
- **Accessibility and contrast measured by tools** (axe, and a script that computes contrast for every design-token pair) rather than judged by eye.
- **Production error monitoring** checked after each deploy.
