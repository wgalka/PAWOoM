# Contract for the project idea form

## Reference

- Retained reference: `C:\UR\Instrukcje\ProjektInżynierskiSZwI\2026-2027\lab1\Karta projektu.docx`
- SHA-256 before authoring: `E1E78F1147F1C351A0A62418C9DF2779A440E12BB7728030F8ABCF4FDD41E43B`
- The reference file must remain unchanged.
- Reference render was attempted with the bundled renderer, but the runtime did not expose `soffice.exe`; visual verification therefore requires an available Word or LibreOffice renderer before delivery.

## Page system

- One section, A4 portrait.
- Page size: 8.27 x 11.69 in.
- Margins: left/right/top 0.75 in; bottom 0.67 in.
- Footer distance: 0.30 in.
- Existing footer retained and updated only where the document title changes.

## Typography and hierarchy

- Title: `Title`, Corbel 22 pt, bold, blue `0033A0`.
- Subtitle: `UR Subtitle`, Corbel 10.5 pt, bold, gray `606A73`.
- Introductory instructions: `UR Instruction`, Corbel 9.5 pt, gray `606A73`.
- Main section headings: `Heading 1`, Corbel 12.5 pt, bold, blue `0033A0`.
- Label cells: `UR Etykieta`, Corbel 9.5 pt, bold, blue `0033A0`.
- Student response cells: `UR Wpis studenta`, Corbel 9.5 pt, black.
- Table headers: `UR Nagłówek tabeli`, Corbel 9 pt, bold, white on blue `0033A0`.
- Table body: `UR Table Body`, Corbel 9 pt, black.
- Spacer paragraphs: `UR Spacer`, 2 pt white text with small after spacing.

## Table system

- Available table patterns: two-column label/response tables and three-column responsibility/result tables.
- Two-column grid: approximately 1.73 in / 5.04 in.
- Three-column grid: approximately 2.26 in / 2.26 in / 2.26 in.
- Table cell margins: top/bottom 100 twips, start/end 150 twips.
- Borders: single, light gray `D9D9D9`, 6 eighths of a point.
- Label fills: `EAF2FB`; response fills: `F6F9FD`.
- Header fills: `0033A0`; body fills: `F6F9FD`.
- Rows use at-least heights and must be allowed to expand; no fixed heights that clip writing space.

## Content flow for the new form

1. Title and subtitle identify a project idea form for LAB1.
2. Opening instruction explains that the form is for the first project idea, not final documentation.
3. Project metadata: team/group, date, working name.
4. Problem and users.
5. Project value and basic use scenario.
6. Domain concepts and candidate service boundary.
7. Planned services and data ownership.
8. Candidate first microservice and API sketch.
9. MVP and success criteria.
10. Team responsibilities and individual deliverables.
11. Risks and use of AI.

## Editable slots

- All response-cell text is replaceable placeholder content intended for student input.
- Headings, labels, examples, explanatory prompts, styles, page system, table colors and footer are retained or adapted from the reference style system.
- The form should not present a complete solution; it should ask students to make the architectural decisions.

## Fidelity gates

- Reference file remains byte-for-byte unchanged.
- Final document preserves A4 portrait geometry, margins, Corbel typography, blue heading hierarchy, blue label cells, pale response cells, gray borders and footer treatment.
- Every page of the final document must be rendered and visually inspected at 100% before delivery.
- Check for clipped placeholder text, crowded tables, unexpected page breaks, missing Polish glyphs and footer placement.
