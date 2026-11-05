# Corpus provenance and audit

The corpus is FAST-NUCES public material selected from the URLs in [`sources.yaml`](../corpus/sources.yaml). The fetcher writes the raw payloads under ignored `corpus/raw/`; [`MANIFEST.md`](../corpus/MANIFEST.md) records URL, declared version, superseded status, byte length and SHA-256. Re-fetch with `python corpus/fetch.py`; verify bytes with `python corpus/fetch.py --verify`. The raw documents are intentionally not committed.

## Required properties

| Property | Evidence in this corpus | Audit result / limitation |
| --- | --- | --- |
| At least 6 documents and 40 pages | Nine manifest entries: seven PDFs and two HTML pages. PDFs have 279 total pages. | Verified locally with pypdf page enumeration; HTML pages count as one extracted page each. |
| Two versions of one policy | Undergraduate Academic Rules Aug 2023 and Academic Rules Handbook Jun 2026 | `doc_version=2023-08, superseded=true` and `doc_version=2026-06, superseded=false`. The former is treated as historical; the handbook is the current policy. The 2023 file is image-heavy and its OCR output has not been quality-reviewed, so do not claim version-answer evaluation is complete. |
| Scanned, image-only PDF | Faculty Entrepreneurship and Technical Start-ups Policy, May 2022 | Eight pages, no extractable text and no page fonts in the PDF resource dictionaries. This is stronger evidence of a scan than an empty result from one text extractor. OCR is implemented; OCR execution and manual correction remain to be verified because Tesseract/Poppler are unavailable in this environment. |
| Table with real information | Fee Structure HTML page; Grading HTML page; annual reports | Parser audit produced 21 fee rows and 38 grading rows. Example normalized fee data includes `BBA / BS | Rs. 12,000`; grading includes `A+ | 4.00 | Excellent`. PDF tables are also serialized page by page when detected. |
| Long definitions | Student Handbook Jun 2026 and the academic rules handbook | These multi-page documents include policy prose and definitions. Chunking preserves section headings, page numbers, source and version metadata. A definition-level recall audit remains pending. |
| Deliberately absent topic | Detailed hostel application / room allocation rules | We excluded the separate Transport and Hostel Facilities document. That is a plausible student question and is used as a must-abstain test; the included handbook's mere mention of hostels is not treated as coverage of application steps. |
| Exact-term content | Academic rules, fee and grading pages | Clause numbers (for example 1.21 attendance and 5.4 academic warning), CGPA thresholds, grades and fee amounts are retained as literal text and tested by exact-term questions. Confirmed handbook text for 5.4 gives 2.00 as the minimum CGPA to avoid academic warning. |

## Page and scan audit

| PDF | Version | Pages | Text layer observation |
| --- | --- | ---: | --- |
| Undergraduate Academic Rules | 2023-08 | 26 | 212 extracted characters total; 24 pages have negligible text and need OCR |
| Academic Rules Handbook | 2026-06 | 58 | Text extractable |
| Prospectus Academic Rules | 2026 | 5 | Text extractable |
| Student Handbook | 2026-06 | 64 | Text extractable |
| Annual Report | 2019-20 | 33 | Text extractable |
| Annual Report | 2023-24 | 85 | Text extractable |
| Faculty Entrepreneurship and Technical Start-ups Policy | 2022-05 | 8 | Image-only; zero text and zero fonts on all pages |
| **Total PDF pages** | | **279** | HTML sources add two extracted pages |

Extraction marks a page as OCR-derived when its normalized text layer has fewer than 25 characters. This is a heuristic, not a substitute for visual proofreading. For scanned pages, compare OCR output with the source PDF before using its claims as golden answers. Table extraction preserves rows as pipe-separated cells; merged cells and complex multi-page layouts may still be lost.

## Provenance and limits

The manifest is the reproducibility record; URLs can change and should be re-fetched and re-hashed before a new evaluation. No licensed/private student records are included. The current local audit establishes page counts, scan status and representative HTML table rows, but not exhaustive extraction quality, definition recall, OCR accuracy, or live retrieval quality. Those require the reproducible pipeline and evaluation run described in [`PIPELINE.md`](PIPELINE.md).
