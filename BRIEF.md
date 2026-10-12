# Client Brief: Station Invoice Review

## The client

**Calloway Media Group** is a fictional media-buying agency. It buys broadcast TV airtime from local stations across the US on behalf of its advertisers, which include political campaigns, advocacy groups, and businesses.

The agency's business model shapes this project. When an ad airs, the station bills the agency the **gross** amount. The agency keeps a commission, usually 15%, and pays the station the **net** amount. It then bills its client the gross. A mistake on a station invoice therefore costs money twice: once in what the agency pays, and again in what it bills.

The tool is content-neutral. It checks arithmetic and paperwork, never the ads or the advertisers.

## The user

**Dana** is the agency's billing coordinator. After each flight of ads runs, invoices arrive from dozens of stations. Every station uses its own invoice format: different layouts, different labels for the same field, one page or several.

For each invoice, Dana has to find the key values, confirm the line items add up, confirm the commission and net amount are correct, and only then send it on for payment. Today she does this by hand, with a calculator, invoice by invoice.

## The user story

> As a billing coordinator at a media-buying agency, I want to drop in a station invoice and get back a prepared review — the extracted values, the results of every check, and a clear status — so that I can approve correct invoices quickly and spend my time on the ones with real problems.

Dana does not want a system that pays invoices. She wants a **prepared review**. The tool does the reading and checking; she makes the decision.

## The rule that shapes the design

**Claude reads. Python checks. Dana decides.**

- **Claude** extracts values from invoices, because station layouts vary too much for templates.
- **Plain Python** applies every business rule, because rules must be readable, testable, and give the same answer every time. No model output decides whether an invoice is correct.
- **Dana** makes the final call, with the evidence in front of her.

## What a prepared review contains

1. **Extracted fields:** agency, advertiser, gross total, payment terms, agency commission, net amount due, and line items (description, start date, end date, days aired, rate).
2. **Where each value came from:** the extraction method that produced it.
3. **Check results:** each rule, whether it passed, and why.
4. **A status:**
   - **Ready:** all checks pass.
   - **Warning:** approvable, but something deserves a look.
   - **Blocked:** a check failed that must be resolved before payment.

## Version 1 checks

| Check | Fails as |
|---|---|
| Required fields are present (gross, commission, net) | Blocked |
| Net amount = gross − commission (to the cent) | Blocked |
| Line item rates sum to the gross total | Blocked *(verify against data in Step 1)* |
| Commission is 15% of gross | Warning (some deals use other rates) |
| Each line item's end date is on or after its start date | Warning |
| Days-aired pattern is well formed (e.g. `-T-----`) | Warning |
| Invoice looks like a duplicate of one already processed | Warning |

The thresholds and rules above are a starting point. Step 1 (looking at the data) will confirm or change them. One sample invoice already appears not to reconcile, which is either a labeling quirk or a real discrepancy — exactly what this tool should surface.

## Out of scope for version 1

- Matching invoices against the original order or the station's proof of airing (the real industry workflow, and a good future extension)
- Paying invoices, billing clients, or connecting to accounting systems
- Degraded or scanned documents (the dataset's noisy variants are saved for a later version)
- A user interface (a command-line tool comes first)
- Authentication, multiple users, or cloud deployment (version 2 moves to AWS)
- Anything involving the content of the ads

## The data

- **Source:** 75 real FCC station invoices (public records) with verified ground-truth labels, from the `amazon/ConfBench` dataset on Hugging Face. License: CC BY-NC 4.0 (non-commercial use).
- **Development set:** 20 invoices used while building.
- **Test set:** the remaining invoices, held back and used only to measure results. This keeps prompt tuning from quietly overfitting to the examples I've looked at.
- **Seeded defects:** copies of clean invoices with deliberate errors (wrong net, missing commission, duplicates, and a prompt-injection attempt) so every check is proven to fire.

## How success is measured

- **Field accuracy:** extracted values versus ground truth, per field.
- **Exact documents:** share of invoices where every field is correct.
- **Status accuracy:** share of invoices given the right status (ready, warning, blocked).
- **Cost:** dollars per invoice and per full run, with a hard budget cap.

## Constraints

- Python
- Cloud agnostic in version 1: storage, database, and LLM provider sit behind interfaces
- Cost conscious: free text extraction first, the cheapest model that meets accuracy targets, cached responses, and a spending limit

## Open questions for Step 1

- How many invoices have a usable text layer versus scanned pages?
- Do line item rates actually sum to the gross total, or do some invoices bill multiple spots per line?
- Is commission always 15%?
- What date and number formats appear across stations?
