# Golden question review

The JSONL files label generated questions as synthetic and pending human review. Use the pinned corpus or the authored policy fixtures to inspect each label.

1. Check the expected document and one-based physical page. For Markdown or HTML, use page 1.
2. Verify the answer hint directly against the source. For an abstention, search both batches for applicable evidence.
3. Verify the split. Questions about new Batch B content stay out of the Batch A run. The recorder loan duration uses its version-specific hint.
4. For at least eight synthetic rows, mark `reviewed: true`, set `review_status: human_reviewed` and record who reviewed the label in `notes`.

## Human-written questions

Rows `human-01` through `human-08` preserve the project owner's question wording. Codex checked the source labels. The credit-limit and total-degree-fee questions are abstention cases because the request lacks necessary program details. The accessibility question uses the exam-seating fixture in the Batch B split. Team review of nine synthetic rows is recorded below.

Codex checked the answer hints for `rgo-01` through `rgo-08` against the specified handbook pages. These rows use `source_checked_by_codex` in `review_status`. The [source check record](source_checks.json) lists the results.

Faithfulness uses a cited-excerpt overlap proxy, so LLM judge agreement is outside this evaluator.


## Human review record

Reviewer: Momna Khan, 2026-11-28. Each label was checked by hand against the pinned corpus, not by Codex. Both `golden.jsonl` and `golden_expanded.jsonl` carry `reviewed: true` and `review_status: human_reviewed` for these rows.

Reviewed rows: `rgo-09`, `rgo-10`, `rgo-11`, `rgo-12`, `rgo-13`, `rgo-14`, `rgo-15`, `rgo-21`, `rgo-22`.

| ID | Source checked | Finding |
|---|---|---|
| rgo-09 | handbook p28, clause 6.2 | Only repeat courses are allowed; no new courses. |
| rgo-10 | handbook p29, clause 6.10 | No fee concession in the summer semester. |
| rgo-11 | handbook p24, clause 5.6 | CGPA below 2.00 for 3 consecutive semesters closes admission. |
| rgo-12 | handbook p12, grade table | A+ is 4.00. |
| rgo-13 | fee-structure page | BBA / BS row is Rs. 12,000 per credit hour. |
| rgo-14 | grading page | A+ is 4.00. |
| rgo-15 | data/batch_a/equipment-loan.md | Audio recorders are lent for three working days. |
| rgo-21 | data/batch_a/equipment-loan.md | The borrowing period starts at pickup. |
| rgo-22 | handbook p28, clause 6.2 | Rule covers all four categories, including graduating students; no new courses. |

Rows `rgo-01` to `rgo-08` stay `source_checked_by_codex` and do not count towards this review. The remaining pending rows (`rgo-16` to `rgo-20`, `rgo-23` to `rgo-26`) are not part of the nine reviewed here.