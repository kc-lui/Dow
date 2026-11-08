# Quote audit (P1)

I checked all quotes against their sources rather than a 15% sample: about 95% match word for word. One real misquote was found and has since been fixed, and the rest are small wording or sourcing problems in nine notes. The folder was being edited by other agents during the audit, so all results describe the files as they stood at 13:56 CST.

## How the audit ran

- **Snapshot.** During the audit, one note was renamed to `russell-history-of-the-dow-theory.md`. Six primary-source notes were renamed with a `-v2` suffix and their slugs updated to match. The folder still holds 43 files.
- **Coverage.** All 530 quotes were checked by exact string match, which covers far more than the requested sample. Spacing, curly-versus-straight quotes, dashes and Markdown bold were ignored.
- **Fetching.** Pages were downloaded with curl and PDFs converted to text, because WebFetch only returns a summary. Wantgoo was rendered in a browser. Google Books snippets were checked through the legacy Google Books feed.
- **OCR noise.** Page headers and OCR misreads that a note already marks with [sic] count as verbatim.

## 1. Structure

| Status | Notes |
|---|---|
| All six fields present, slug equals filename, `## Verbatim quotes` with Q-ids, all 17 rule rows (counting phases_bull / phases_bear as one row) | 41 of 43 |
| `academic-search-log.md` | Fails every check. It is a search log, not a source note: no fields, no quotes, no rule table. Exclude it or rename it so it doesn't look like a source note. |
| `zh-defense-line-search-log.md` | Passes the structure check. Its only "quote" is the text "NOT FOUND", not a quotation. |

**Other structural points:**
- No rule row was missing and no cell was blank. The only empty cells are inside a contingency table in the Brown, Goetzmann and Kumar note.
- `kirkpatrick-…-v2.md` writes "NOT VISIBLE" in two rows (line_definition and volume) instead of "NOT MENTIONED".
- The Reason 1974 note leaves the figure cell as "—" on its NOT MENTIONED rows. The template allows this.
- Two pairs of notes share one URL. `aaii-dow-theory-21st-century` and `schannep-dow-theory-21st-century` both point to the AAII article. `stockcharts-chartschool-dow-theory` and `takasugi-volume-leads-price` both point to the StockCharts page.

## 2. Quote fidelity

| Verdict | Count |
|---|---|
| VERBATIM | 504 |
| MINOR-DIFF | 16 |
| MISQUOTE (words changed) | 1 |
| NOT-FOUND at the note's URL | 5 |
| PAGE-UNREACHABLE | 4 |
| **Total** | **530** |

Every note not listed in the table below scored 100% verbatim. The Wantgoo, stockcloud, OANDA and Wikipedia notes are among them.

| Note | Q | Verdict | Evidence |
|---|---|---|---|
| hamilton-1922 | Q5 | MISQUOTE (fixed in `-v2`) | The source reads "the barometer considers everything which affects the weather". The note had "atmospheric pressure". The `-v2` note now reads "the weather". |
| cowles-1933 | Q21 | MINOR-DIFF | The page reads "45 of his changes of position were unsuccessful, 45 successful". The note swaps the order. |
| brown-goetzmann-kumar-1998 | Q11, Q24 | MINOR-DIFF | "[fn5]" and "[fn6]" footnote markers are inserted inside the quotes. |
| stockfeel | Q7 | MINOR-DIFF | The page has 屬日常震盪. The note inserts a 於 that the page doesn't have. |
| zh-ctyeh | Q5 | MINOR-DIFF | The page has 主多頭中每次10-20%回調. The note inserts a 要 that the page doesn't have. |
| reason-1974 | Q3, Q6, Q11, Q14 | MINOR-DIFF | Each quote is cut mid-sentence and closed with a period. The source sentence continues, for example "10 to 60 days, and finally the main movement…". |
| schannep-21st-century | Q2, Q4, Q11 | MINOR-DIFF | Same truncation pattern. Q2 drops ", and usually one or both will exceed 7%". |
| thedowtheory-schannep-vs-classical | Q4, Q13, Q14 | MINOR-DIFF | Same truncation pattern. |
| roboforex-sperandeo | Q4 | MINOR-DIFF | Same pattern. A colon in the source becomes a period. |
| schannep-21st-century | Q12 | NOT-FOUND | This is a Wiley-VCH book subtitle and does not appear on the AAII URL. |
| russell-dow-theory-letters | Q4, Q5 | NOT-FOUND | These are not on the FNArena page. The note credits "The Dow Theorist, Nov 19, 2013" but gives no URL for it. |
| cowles-1934-follow-up | Q2, Q3 | NOT-FOUND | The note calls these "search-tool text". They do not appear on the Econometric Society page. |
| sideris-russell-thesis | Q1–Q4 | PAGE-UNREACHABLE | SciSpace returned HTTP 202 with an empty body. The browser rendered an empty page. |
| edwards-magee | Q1–Q8 | VERBATIM | All eight were confirmed through the Google Books feed. Q1 punctuation varies between editions. |
| kirkpatrick-dahlquist | Q1–Q8 | VERBATIM | All eight were confirmed through the Google Books feed. |

An earlier version of `dow-editorials-wsj-1900-1902.md` had a serious misquote. It quoted Dow's 22 January 1901 editorial as "3/8", but the Bishop PDF reads "amounts to ¼ to ½ of the primary move". That version was replaced during the audit, and the current `-v2` note matches the Nelson and Hamilton texts exactly.

## 3. Quotes that may be paraphrases

- **cowles-1934 Q2 and Q3.** Both look like a search tool's summary. Q2's aside "(but whom Cowles did not name)" reads like a summary, not an abstract. These should be dropped or moved to Notes.
- **sideris Q3.** "The Dow Theory is basically to do with buying great values…" is an unverifiable snippet that reads like a summary.
- **russell Q4 and Q5.** The wording is plausible, but the source is uncited and not by Russell.

## 4. Figures not supported by a quote in the same note

- **rhea-1932-v2.** Q4 does not support "bull avg >2 yrs". Q5 does not support "alt. 3-12 weeks". Q7 does not support "15 days / 5 %". The phases figure "3 and 3" is marked "— (paraphrase)".
- **edwards-magee-v2.** The primary_duration figure ">1 year; >20 %" has no quote. The line_definition figure "~5 %; 2-3 weeks+" cites Q7, which contains neither number. The phases figure "3 and 3" has no quote.
- **kirkpatrick-v2.** The phases figure "3" has no quote, and its statement says the bull phases are only "presumably" reproduced.
- **hamilton-1922.** The line_definition figures "3-4 points" and "66-71 trading days" come only from the unquoted paraphrase paragraph. The phrases "largely negligible" and "with almost uncanny accuracy" appear in quotation marks in the table but match no Q-id.
- **reason-1974.** The 10-to-60-day secondary swing is filed under minor_duration, while secondary_duration says NOT MENTIONED. Its three_trends row also says NOT MENTIONED but cites Q2 and Q3.
- **roboforex-sperandeo.** The defense_line row holds the 2B setup and a 5:1 target figure. That belongs under reversal_definition or as an exit rule, not as a defense line.
- **stockcharts.** The figure "3 stages each" is only weakly supported, because the quotes mention only a "second stage" of bull markets.

## Overall fidelity

| Measure | Rate |
|---|---|
| Verbatim, of all 530 quotes | 95.1% |
| Verbatim or minor typographic difference | 98.1% |
| Verbatim, excluding the 4 unreachable quotes | 95.8% |

## Notes needing correction

1. `cowles-1934-follow-up` should drop or relabel Q2 and Q3.
2. `russell-dow-theory-letters` should cite a URL for Q4 and Q5 or remove them.
3. `schannep-dow-theory-21st-century` should move Q12 to its real source and add "…" or the missing text to Q2, Q4 and Q11.
4. `reason-1974-dow-theory-revisited` should fix the truncation in Q3, Q6, Q11 and Q14, and move the 10-to-60-day swing to secondary_duration.
5. `thedowtheory-schannep-vs-classical` should fix the truncation in Q4, Q13 and Q14.
6. `cowles-1933-can-forecasters-forecast` should restore the word order in Q21.
7. `brown-goetzmann-kumar-1998` should remove the [fn] markers from Q11 and Q24.
8. `stockfeel-dow-theory` Q7 should drop the extra 於, and `zh-ctyeh-dow-theory` Q5 should drop the extra 要.
9. `roboforex-sperandeo-123-2b` should re-file the defense_line row and fix the Q4 ending.
10. The `-v2` notes for Rhea, Edwards-Magee, Kirkpatrick and Hamilton should add quotes for the figures listed in section 4 or mark them as paraphrase. Kirkpatrick should also replace "NOT VISIBLE" with "NOT MENTIONED".
11. `academic-search-log` should be excluded from the source-note set or renamed so it doesn't look like a source note.
12. `sideris-russell-dow-theory-thesis` could not be checked. It should be re-fetched or treated as unverifiable.

The matching scripts and downloaded pages are in `/private/tmp/claude-501/-Users-lui-workspace-Dow/306a67ac-f215-4afb-969a-8daa52bf6810/scratchpad/`. The per-quote results are in `final.json` in that folder.
