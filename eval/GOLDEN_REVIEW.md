# Golden question review

There are 26 synthetic rows in `golden.jsonl`; at least eight need a genuine team
member's manual check before submission. The first eight source-checked examples are
convenient candidates, but Codex's checks below do not count as the required review.
Review each source independently and record only rows actually checked by a person.

1. Check the expected document and one-based physical page. For Markdown or HTML, use page 1.
2. Verify the answer hint directly against the source. For an abstention, search both batches for applicable evidence.
3. Verify the split. Questions about new Batch B content stay out of the Batch A run. The recorder loan duration uses its version-specific hint.
4. For at least eight synthetic rows, a team member checks the cited source and answer
   hint, then sets `reviewed: true`, `review_status: human_reviewed`, and records their
   name/handle and what they checked in `notes`.
5. Apply the same review fields to matching rows in `golden_expanded.jsonl`, preserving
   the question and source labels. Do not mark a row reviewed in one file only.

## Human review record

Reviewer: Momna Khan, 2026-11-28. Each label below was checked by hand against the pinned corpus, not by Codex. Both `golden.jsonl` and `golden_expanded.jsonl` carry `reviewed: true` and `review_status: human_reviewed` for these rows.

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

Rows `rgo-01` to `rgo-08` remain `source_checked_by_codex` and do not count towards the review. The other pending rows (`rgo-16` to `rgo-20`, `rgo-23` to `rgo-26`) were not reviewed.