# Golden question review

The JSONL files label generated questions as synthetic and pending human review. Use the pinned corpus or the authored policy fixtures to inspect each label.

1. Check the expected document and one-based physical page. For Markdown or HTML, use page 1.
2. Verify the answer hint directly against the source. For an abstention, search both batches for applicable evidence.
3. Verify the split. Questions about new Batch B content stay out of the Batch A run. The recorder loan duration uses its version-specific hint.
4. For at least eight synthetic rows, mark `reviewed: true`, set `review_status: human_reviewed` and record who reviewed the label in `notes`.

## Human-written question slots

Have the team write the wording independently. Add new rows with distinct IDs and use `source: human` only when a member wrote the question.

| ID slot | Evidence area | Author and question |
| --- | --- | --- |
| human-01 | Attendance policy | Pending |
| human-02 | Academic warning | Pending |
| human-03 | Credit hours | Pending |
| human-04 | Summer repeats | Pending |
| human-05 | Fee-page row | Pending |
| human-06 | Grading table | Pending |
| human-07 | Recorder loan | Pending |
| human-08 | Accessible seating | Pending |

Faithfulness uses a cited-excerpt overlap proxy, so LLM judge agreement is outside this evaluator.
