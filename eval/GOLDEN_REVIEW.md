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

Suggested first eight to check: `rgo-01`–`rgo-08`. Open the pinned source in
`corpus/raw/` or the authored fixture named in the row; verify the exact page and hint.
For example, `rgo-02` says “100%” for attendance, while the source also notes a
possible HoD exception. Decide whether the hint and question represent that clause
fairly before marking it reviewed. Correct a label if the source shows it is wrong and
describe the correction in `notes`.

## Human-written questions

Rows `human-01` through `human-08` preserve the project owner's question wording. Codex checked the source labels. The credit-limit and total-degree-fee questions are abstention cases because the request lacks necessary program details. The accessibility question uses the exam-seating fixture in the Batch B split. Team review of the synthetic rows remains open.

Codex checked the answer hints for `rgo-01` through `rgo-08` against the specified handbook pages. These rows use `source_checked_by_codex` in `review_status`. The [source check record](source_checks.json) lists the results.

Faithfulness uses a cited-excerpt overlap proxy, so LLM judge agreement is outside this evaluator.
