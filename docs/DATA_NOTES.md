# Data Notes

Findings from Step 1 exploration. All conclusions based on the **dev set only**
(20 invoices), never the test set.

---

## Text layer vs scanned

| Set | Text layer | Scanned | Total |
|-----|-----------|---------|-------|
| Dev | 11 | 9 | 20 |
| Test | 29 | 26 | 55 |
| **All** | **40** | **35** | **75** |

47% of the clean original PDFs yield no extractable text via pdfplumber
(< 50 characters after stripping whitespace). These are image-based scans, not
degraded variants — they are the original documents.

**v1 decision:** return a `blocked` review with reason
`"no text layer detected"` for scanned PDFs. v1 covers 40/75 invoices.
Tracking scanned handling as a future step (see Ideas for later in CLAUDE.md).

---

## Line item rates and the gross total

`LineItemRate` is a **unit rate per spot**, not a line total. A single line item
can cover a multi-day schedule (e.g. "M–F Local News @ 6a", 10/11–10/17,
`MTWTF--` = 5 spots). The gross total equals the sum of `rate × spots_aired`
per line, not the sum of rates.

| Invoice | Items | Sum of rates | Gross | Match? |
|---------|-------|-------------|-------|--------|
| a501c2b1 | 2 | 60.00 | 60.00 | yes (1 spot/line) |
| bd6cfc5d | 1 | 1400.00 | 1400.00 | yes (1 spot/line) |
| cd3fc779 | 23 | 8814.00 | 8814.00 | yes (1 spot/line) |
| d66e599a | 36 | 43900.00 | 43900.00 | yes (1 spot/line) |
| 3d239b34 | 17 | 1455.00 | 1555.00 | no (multi-spot) |
| f3eb6504 | 25 | 20625.00 | 45525.00 | no (multi-spot) |
| beedfe69 | 247 | 12185.00 | 44674.00 | no (multi-spot) |

**v1 implication:** the BRIEF's "line item rates sum to gross" check cannot be
implemented with a simple sum. Computing `rate × spots` requires parsing the
start date, end date, and day-pattern for each line. This check is deferred to
a later step once day-pattern parsing is in place.

---

## Commission rate

All 11 dev text-layer invoices use **15% agency commission**.
`AgencyCommission == GrossTotal × 0.15` in every case. The commission-rate
check (warning if not 15%) is consistent with the data.

---

## Net reconciliation

Most invoices satisfy `NetAmountDue == GrossTotal − AgencyCommission`. Two dev
exceptions found — both appear to be labeling errors, not real invoice defects:

| Invoice | Gross | Commission | Expected net | Labeled net | Δ |
|---------|-------|-----------|-------------|-------------|---|
| 7ec89578 | 9072.00 | 1360.80 | 7711.20 | 6284.62 | −1426.58 |
| bd6cfc5d | 1400.00 | 210.00 | 1190.00 | 1035.30 | −154.70 |

`7ec89578` also has zero line items despite a non-zero gross, suggesting the
label was partially parsed. These will be recorded as label-error corrections
in `manifest/` when the validation step arrives.

---

## Date formats

Multiple formats observed across stations:

| Format | Example | Invoices |
|--------|---------|----------|
| `MM/DD/YY` | `10/11/16` | most common |
| `MM-DD-YY` | `10-28-16` | bd6cfc5d, d66e599a |

No 4-digit year examples seen in the dev set. The schema normalizer will need
to handle both separators and 2-digit years (assume 2000s).

---

## Days-aired formats

Highly varied across stations. Six distinct patterns observed:

| Pattern style | Examples |
|--------------|---------|
| 7-char bitmask (MTWTFSS) | `MTWTF--`, `---T---`, `------S`, `-----S-` |
| 7-char Y/N mask | `NYYYYYY`, `NNNNNYY` |
| Y/N mask with spaces | `Y N N N N N N`, `N Y Y Y Y N N` |
| Comma-separated abbreviations | `M,T,W,Th,F`, `W,Th,F,S,Su`, `S,Su` |
| Full day names | `Wednesday`, `Friday`, `Saturday` |
| Short abbreviations (no comma) | `M`, `Tu`, `Th`, `F`, `Sa`, `Su` |

The BRIEF's "days-aired pattern is well formed" check will need to accept all
six styles, or normalize to one canonical form first. Normalization is the
cleaner approach and enables spot-counting later.
