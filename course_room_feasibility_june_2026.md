# June Bookings Issues Single Source of Truth

## Authority

This document is the single source of truth for all June 2026 booking-issue analysis, decisions, retries, and outcomes in this workspace.

- Authoritative file: `course_room_feasibility_june_2026.md`
- Supersedes the previously split markdown artifacts: `candidate_room_alternatives_section.md`, `candidate_room_allocation_section.md`, `candidate_room_request_followup_section.md`, `candidate_room_still_actionable_results.md`, and `G11_ElevateU_Room_Consolidation_Feasibility.md`
- If any CSV, XLSX, JSON, or database state disagrees with an older markdown artifact, use this file as the canonical narrative record and reconcile against the latest live booking data.

## Scope

This report consolidates the June 2026 booking issues handled in this workspace, including the room-feasibility workflow for the June timetable, follow-up retries from workbook actions, the column J room-list retry pass, and the G11 ElevateU consolidation issue spanning late May into early June.

## Assumptions

- `Block A`, `B`, `B1`, `B2`, `C`, `D`, and `E` were mapped from the visible timetable cells into contiguous booking spans.
- `Block C2` is split by the visible labels: `TOK (Chinese)` uses the Monday `IB-TOK` slots, and `CAS` uses the Friday `CAS-1/CAS-2` span.
- A room is marked not feasible if it conflicts with live data or with another requested course using the same room and times.

## Summary

| Outcome | Courses | Booking rows | Artifact |
| --- | ---: | ---: | --- |
| Booked from candidate allocation plan | 12 | 83 | `bookings` + `candidate_room_plan_report_verification.json` |
| Verified as already covered by existing bookings | 6 | - | `candidate_room_request_followup.csv` |
| Booked from column J room retry | 10 | 71 | `candidate_room_still_actionable_results.csv` + `candidate_room_still_actionable_results.xlsx` |
| Still unresolved after column J retry | 15 | 0 | `candidate_room_still_actionable_results.csv` + `candidate_room_still_actionable_results.xlsx` |

- Requested course-room assignments checked: 63
- Feasible as listed: 20
- Not feasible as listed: 43
- Missing room assignments in request: 1
- Blocks covered: {'A': 11, 'B': 10, 'B1': 4, 'B2': 2, 'C': 12, 'C2-CAS': 1, 'C2-TOK': 1, 'D': 12, 'E': 10}
- Total June booking rows inserted across the candidate plan and column J retry: 154

## Detailed Results

| Course | Program | Block | Teacher | Room | Status | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| Math HL | IBDP | A | Rajesh Choyikkunimmal | B3012 | Not Feasible | Live overlap(s): 2026/06/10 08:20-09:45 -> bookings 08:30-09:45 G11 IB Chinese - Paper1 (DC4 Exam) |
| Math SL | IBDP | A | Shahid Anwar | B3039 | Feasible | Checked 6 slot(s). |
| Regular Math A-1 | CIE | A | Joy Farhat | B3042 | Feasible | Checked 6 slot(s). |
| Regular Math A-2 | CIE | A | Sheryl Shane Canite | B3011 | Not Feasible | Internal room clash with requested courses: Physics A-2 (Summit) (CIE A).; Live overlap(s): 2026/06/10 08:20-09:45 -> bookings 08:20-09:45 G10 TT Physics Block A Summit  (Faisal Qureshi) / 2026/06/12 09:05-09:45 -> bookings 09:05-09:45 G10 TT Physics Block A Summit  (Faisal Qureshi) / 2026/06/15 13:00-14:25 -> bookings 13:00-14:25 G10 TT Physics Block A Summit  (Faisal Qureshi) / 2026/06/16 10:00-11:25 -> bookings 10:00-11:25 G10 TT Physics Block A Summit  (Faisal Qureshi) / 2026/06/17 08:20-09:45 -> bookings 08:20-09:45 G10 TT Physics Block A Summit  (Faisal Qureshi) / 2026/06/29 13:00-14:25 -> bookings 13:00-14:25 G10 TT Physics Block A Summit  (Faisal Qureshi) |
| Physics A-1 | CIE | A | Evelyn Yang | B3004 | Not Feasible | Live overlap(s): 2026/06/10 08:20-09:45 -> bookings 08:20-09:45 G10 TT Physics Block A  (Faisal Qureshi) / 2026/06/15 13:00-14:25 -> bookings 13:00-14:25 G10 TT Physics Block A (Faisal Qureshi) / 2026/06/16 10:00-11:25 -> bookings 10:00-11:25 G10 TT Physics Block A (Faisal Qureshi) / 2026/06/17 08:20-09:45 -> bookings 08:20-09:45 G10 TT Physics Block A (Faisal Qureshi) / 2026/06/29 13:00-14:25 -> bookings 13:00-14:25 G10 TT Physics Block A (Faisal Qureshi) |
| Chemistry A | CIE | A | Selina Sun | B4002 | Feasible | Checked 6 slot(s). |
| Economics A | CIE | A | Reza Hamroun | B2040 | Feasible | Checked 6 slot(s). |
| Chinese A | CIE | A | Jenny Li | B4009 | Feasible | Checked 6 slot(s). |
| Physics A-2 (Summit) | CIE | A | Mike Hu | B3011 | Not Feasible | Internal room clash with requested courses: Regular Math A-2 (CIE A).; Live overlap(s): 2026/06/10 08:20-09:45 -> bookings 08:20-09:45 G10 TT Physics Block A Summit  (Faisal Qureshi) / 2026/06/12 09:05-09:45 -> bookings 09:05-09:45 G10 TT Physics Block A Summit  (Faisal Qureshi) / 2026/06/15 13:00-14:25 -> bookings 13:00-14:25 G10 TT Physics Block A Summit  (Faisal Qureshi) / 2026/06/16 10:00-11:25 -> bookings 10:00-11:25 G10 TT Physics Block A Summit  (Faisal Qureshi) / 2026/06/17 08:20-09:45 -> bookings 08:20-09:45 G10 TT Physics Block A Summit  (Faisal Qureshi) / 2026/06/29 13:00-14:25 -> bookings 13:00-14:25 G10 TT Physics Block A Summit  (Faisal Qureshi) |
| Physics A-3 (EU) | CIE | A | Logan Tian | B3021 | Not Feasible | Live overlap(s): 2026/06/10 08:20-09:45 -> bookings 08:20-09:45 G10 TT Physics Block A EU  (Faisal Qureshi) / 2026/06/12 09:05-09:45 -> bookings 09:05-09:45 G10 TT Physics Block A EU (Faisal Qureshi) / 2026/06/15 13:00-14:25 -> bookings 13:00-14:25 G10 TT Physics Block A EU (Faisal Qureshi) / 2026/06/16 10:00-11:25 -> bookings 10:00-11:25 G10 TT Physics Block A EU (Faisal Qureshi) / 2026/06/17 08:20-09:45 -> bookings 08:20-09:45 G10 TT Physics Block A EU (Faisal Qureshi) / 2026/06/29 13:00-14:25 -> bookings 13:00-14:25 G10 TT Physics Block A EU (Faisal Qureshi) |
| Geography | CIE | A | Keith Seeley / Alex Oniango | B2044 | Not Feasible | Live overlap(s): 2026/06/10 08:20-09:45 -> schedule 08:20-09:00 G9 pre-IG Economics (Ms k Ding) / 2026/06/12 09:05-09:45 -> bookings 08:20-09:45 G11 IB EE support  (Chaminda ) / 2026/06/15 13:00-14:25 -> schedule 13:00-13:40 G9 pre-IG Economics (Ms k Ding) / 2026/06/16 10:00-11:25 -> schedule 10:00-10:40 G9 IG Regular Maths - F (Mr S Yang) / 2026/06/17 08:20-09:45 -> schedule 08:20-09:00 G9 pre-IG Economics (Ms k Ding) / 2026/06/29 13:00-14:25 -> schedule 13:00-13:40 G9 pre-IG Economics (Ms k Ding) |
| Economics 2 HL/SL | IBDP | B1 | Chaminda Marasinghe | B2039 | Not Feasible | Live overlap(s): 2026/06/10 11:30-12:10 -> schedule 11:30-12:10 AS Business 1 (Mr R Hamroun) / 2026/06/11 14:35-16:00 -> schedule 14:35-15:15 AS Business 1 (Mr R Hamroun) / 2026/06/12 10:00-10:40 -> schedule 10:00-10:40 AS Business 1 (Mr R Hamroun) / 2026/06/17 11:30-12:10 -> schedule 11:30-12:10 AS Business 1 (Mr R Hamroun) / 2026/06/18 14:35-16:00 -> schedule 14:35-15:15 AS Business 1 (Mr R Hamroun) |
| Biology HL/SL | IBDP | B1 | Fisher Yu | B4007 | Not Feasible | Internal room clash with requested courses: Physics HL/SL (IBDP B1). |
| Theatre HL/SL | IBDP | B1 | Chalice Rakgoale | B2003 | Not Feasible | Internal room clash with requested courses: Music (CIE B). |
| Physics HL/SL | IBDP | B1 | Logan Tian | B4007 | Not Feasible | Internal room clash with requested courses: Biology HL/SL (IBDP B1). |
| Physics B-1 | CIE | B | Chester Lim | B3005 | Not Feasible | Live overlap(s): 2026/06/10 11:30-14:25 -> bookings 11:30-14:25 G10 TT Physics Block B-1 (Faisal Qureshi) / 2026/06/12 10:00-11:25 -> bookings 10:00-11:25 G10 TT Physics Block B-1 (Faisal Qureshi) / 2026/06/17 11:30-14:25 -> bookings 11:30-14:25 G10 TT Physics Block B-1 (Faisal Qureshi) |
| Physics B-2 | CIE | B | Evelyn Yang | B3004 | Not Feasible | Live overlap(s): 2026/06/10 11:30-14:25 -> bookings 11:30-14:25 G10 TT Physics Block B-2 (Faisal Qureshi) / 2026/06/12 10:00-11:25 -> bookings 10:00-11:25 G10 TT Physics Block B-2 (Faisal Qureshi) / 2026/06/17 11:30-14:25 -> bookings 11:30-14:25 G10 TT Physics Block B-2 (Faisal Qureshi) |
| Biology | CIE | B | Ambily Biju | B3007 | Not Feasible | Live overlap(s): 2026/06/10 11:30-14:25 -> schedule 11:30-12:10 G9 IG Biology 3 (Ms A Biju) / 2026/06/11 14:35-16:00 -> schedule 14:35-15:15 G9 IG Biology 3 (Ms A Biju) / 2026/06/17 11:30-14:25 -> schedule 11:30-12:10 G9 IG Biology 3 (Ms A Biju) / 2026/06/18 14:35-16:00 -> schedule 14:35-15:15 G9 IG Biology 3 (Ms A Biju) |
| Economics B-1 | CIE | B | Helgaard Le Roux | B2041 | Not Feasible | Live overlap(s): 2026/06/10 11:30-14:25 -> schedule 11:30-12:10 AS Economics 2 (Ms Z Wang) / 2026/06/11 14:35-16:00 -> schedule 14:35-15:15 AS Economics 2 (Ms Z Wang) / 2026/06/12 10:00-11:25 -> schedule 10:00-10:40 AS Economics 2 (Ms Z Wang) / 2026/06/15 14:35-16:00 -> schedule 14:35-15:15 G9 IG Economics TBC (Ms k Ding) / 2026/06/17 11:30-14:25 -> schedule 11:30-12:10 AS Economics 2 (Ms Z Wang) / 2026/06/18 14:35-16:00 -> schedule 14:35-15:15 AS Economics 2 (Ms Z Wang) / ... |
| Computer Science | CIE | B | Bill Jiang | B1029 | Feasible | Checked 7 slot(s). |
| Music | CIE | B | Andy Clark | B2003 | Not Feasible | Internal room clash with requested courses: Theatre HL/SL (IBDP B1). |
| Chinese B | CIE | B | Ivy Zhu | B3009 | Feasible | Checked 7 slot(s). |
| Economics B-2 (Summit) | CIE | B | Fahran Nzamy | MISSING | Not Feasible | No room provided in the request. |
| Regular Maths B (EU) | CIE | B | Sheryl Shane Canite | B3011 | Not Feasible | Live overlap(s): 2026/06/10 11:30-14:25 -> bookings 11:30-12:10 G11IB Economics (Abass Mugabe) / 2026/06/12 10:00-11:25 -> bookings 10:00-11:25 G11IB Economics (Abass Mugabe) / 2026/06/17 11:30-14:25 -> bookings 11:30-12:10 G11IB Economics (Abass Mugabe) |
| Art (Dual Dose) | CIE | B | Mark Ford | B3027 | Not Feasible | Live overlap(s): 2026/06/10 11:30-14:25 -> schedule 11:30-12:10 11 AS Art 2 (Ms L Liu) / 2026/06/11 14:35-16:00 -> schedule 14:35-15:15 11 AS Art 2 (Ms L Liu) / 2026/06/12 10:00-11:25 -> schedule 10:00-10:40 11 AS Art 2 (Ms L Liu) / 2026/06/17 11:30-14:25 -> schedule 11:30-12:10 11 AS Art 2 (Ms L Liu) / 2026/06/18 14:35-16:00 -> schedule 14:35-15:15 11 AS Art 2 (Ms L Liu) |
| Chinese A | IBDP | B2 | Melody Chen | B4010 | Feasible | Checked 2 slot(s). |
| Chinese B | IBDP | B2 | Jenny Li | B4009 | Feasible | Checked 2 slot(s). |
| Physics HL/SL | IBDP | C | Logan Tian | B3005 | Feasible | Checked 7 slot(s). |
| Chemistry HL/SL | IBDP | C | Judy Zhu | B4002 | Not Feasible | Internal room clash with requested courses: Chemistry C-2 (Summit) (CIE C).; Live overlap(s): 2026/06/10 14:35-16:00 -> schedule 14:35-15:15 AS Chemistry 3 (Ms S Sun) / 2026/06/11 13:00-14:25 -> schedule 13:00-13:40 AS Chemistry 3 (Ms S Sun) / 2026/06/15 10:00-11:25 -> schedule 10:00-10:40 AS Chemistry 3 (Ms S Sun) / 2026/06/16 08:20-09:45 -> schedule 08:20-09:00 AS Chemistry 3 (Ms S Sun) / 2026/06/17 14:35-16:00 -> schedule 14:35-15:15 AS Chemistry 3 (Ms S Sun) / 2026/06/18 13:00-14:25 -> schedule 13:00-13:40 AS Chemistry 3 (Ms S Sun) / ... |
| Biology HL/SL | IBDP | C | Lily Hung | B4012 | Not Feasible | Live overlap(s): 2026/06/10 14:35-16:00 -> schedule 14:35-15:15 AS Biology 2 (Ms L Hung) / 2026/06/11 13:00-14:25 -> schedule 13:00-13:40 AS Biology 2 (Ms L Hung) / 2026/06/15 10:00-11:25 -> schedule 10:00-10:40 AS Biology 2 (Ms L Hung) / 2026/06/16 08:20-09:45 -> schedule 08:20-09:00 AS Biology 2 (Ms L Hung) / 2026/06/17 14:35-16:00 -> schedule 14:35-15:15 AS Biology 2 (Ms L Hung) / 2026/06/18 13:00-14:25 -> schedule 13:00-13:40 AS Biology 2 (Ms L Hung) / ... |
| Regular Math C-1 | CIE | C | Narmina Magsudova | B3040 | Feasible | Checked 7 slot(s). |
| Regular Math C-2 | CIE | C | Shaun Yang | B3039 | Not Feasible | Live overlap(s): 2026/06/10 14:35-16:00 -> schedule 14:35-15:15 G9.5 AS Maths (Mr S Liu) / 2026/06/15 10:00-11:25 -> schedule 10:00-10:40 G9.5 AS Maths (Mr S Liu) / 2026/06/17 14:35-16:00 -> schedule 14:35-15:15 G9.5 AS Maths (Mr S Liu) / 2026/06/29 10:00-11:25 -> schedule 10:00-10:40 G9.5 AS Maths (Mr S Liu) |
| Further Maths C | CIE | C | Rajesh | B3012 | Not Feasible | Live overlap(s): 2026/06/11 13:00-14:25 -> schedule 13:00-13:40 G9 pre-IG English (Mr T TT19 EXT,Ms T TT24 Aurora, Dai,Ms T TT25 Ariel Wang) / 2026/06/18 13:00-14:25 -> schedule 13:00-13:40 G9 pre-IG English (Mr T TT19 EXT,Ms T TT24 Aurora, Dai,Ms T TT25 Ariel Wang) |
| Advanced Maths (CIE) C | CIE | C | Mandy Chen | B3041 | Not Feasible | Live overlap(s): 2026/06/15 10:00-11:25 -> bookings 08:20-16:00 LS Self Study (Leo Li) / 2026/06/16 08:20-09:45 -> bookings 08:20-16:00 LS Self Study (Leo Li) / 2026/06/17 14:35-16:00 -> bookings 08:20-16:00 LS Self Study (Leo Li) / 2026/06/18 13:00-14:25 -> bookings 08:20-16:00 LS Self Study (Leo Li) |
| Chemistry C-1 | CIE | C | Khurram Shezad | B4004 | Feasible | Checked 7 slot(s). |
| Economics D-1 | CIE | C | Marshall Irby | B2043 | Feasible | Checked 7 slot(s). |
| Business | CIE | C | Joyce Zhou | B2039 | Not Feasible | Live overlap(s): 2026/06/10 14:35-16:00 -> schedule 14:35-15:15 AS Business 2 (Ms J Jacobs-Kraft) / 2026/06/11 13:00-14:25 -> schedule 13:00-13:40 AS Business 2 (Ms J Jacobs-Kraft) / 2026/06/15 10:00-11:25 -> schedule 10:00-10:40 AS Business 2 (Ms J Jacobs-Kraft) / 2026/06/16 08:20-09:45 -> schedule 09:05-09:45 AS Business 2 (Ms J Jacobs-Kraft) / 2026/06/17 14:35-16:00 -> schedule 14:35-15:15 AS Business 2 (Ms J Jacobs-Kraft) / 2026/06/18 13:00-14:25 -> schedule 13:00-13:40 AS Business 2 (Ms J Jacobs-Kraft) / ... |
| Chemistry C-2 (Summit) | CIE | C | Alistair Furze | B4002 | Not Feasible | Internal room clash with requested courses: Chemistry HL/SL (IBDP C).; Live overlap(s): 2026/06/10 14:35-16:00 -> schedule 14:35-15:15 AS Chemistry 3 (Ms S Sun) / 2026/06/11 13:00-14:25 -> schedule 13:00-13:40 AS Chemistry 3 (Ms S Sun) / 2026/06/15 10:00-11:25 -> schedule 10:00-10:40 AS Chemistry 3 (Ms S Sun) / 2026/06/16 08:20-09:45 -> schedule 08:20-09:00 AS Chemistry 3 (Ms S Sun) / 2026/06/17 14:35-16:00 -> schedule 14:35-15:15 AS Chemistry 3 (Ms S Sun) / 2026/06/18 13:00-14:25 -> schedule 13:00-13:40 AS Chemistry 3 (Ms S Sun) / ... |
| Economic C-2 (EU) | CIE | C | Winnie Hu | B2041 | Feasible | Checked 7 slot(s). |
| TOK (Chinese) | IBDP | C2-TOK | Miya Yang / Matthew Peatman | B3044 | Feasible | Checked 2 slot(s). |
| CAS | IBDP | C2-CAS | #N/A | B2044 | Feasible | Checked 1 slot(s). |
| Regular Maths D | CIE | D | Joy Farhat | B3042 | Not Feasible | Live overlap(s): 2026/06/11 10:00-11:25 -> bookings 10:00-12:00 G11 IB MATHS (Shahid Anwar) / 2026/06/18 10:00-11:25 -> bookings 10:00-12:00 G11 IB MATHS (Shahid Anwar) |
| Fast Maths (Edexcel) | CIE | D | Rajesh | B3012 | Not Feasible | Live overlap(s): 2026/06/10 10:00-11:25 -> schedule 10:00-10:40 G9 pre-IG English (Mr T TT19 EXT,Ms T TT24 Aurora, Dai,Ms T TT25 Ariel Wang) / 2026/06/12 11:30-12:10 -> bookings 11:00-12:00 G11 IB Maths AA H/SL P2 (DC4 Exam) / 2026/06/15 11:30-12:10 -> schedule 11:30-12:10 G9 pre-IG English (Mr T TT19 EXT,Ms T TT24 Aurora, Dai,Ms T TT25 Ariel Wang) / 2026/06/17 10:00-11:25 -> schedule 10:00-10:40 G9 pre-IG English (Mr T TT19 EXT,Ms T TT24 Aurora, Dai,Ms T TT25 Ariel Wang) / 2026/06/29 11:30-12:10 -> schedule 11:30-12:10 G9 pre-IG English (Mr T TT19 EXT,Ms T TT24 Aurora, Dai,Ms T TT25 Ariel Wang) |
| Advanced Math (CIE) D | CIE | D | Eva Wang | B3040 | Not Feasible | Live overlap(s): 2026/06/10 10:00-11:25 -> schedule 10:00-10:40 11 Reg Maths 4 9709 AS (Ms E Wang) / 2026/06/11 10:00-11:25 -> schedule 10:00-10:40 11 Reg Maths 4 9709 AS (Ms E Wang) / 2026/06/12 11:30-12:10 -> schedule 11:30-12:10 11 Reg Maths 4 9709 AS (Ms E Wang) / 2026/06/15 11:30-12:10 -> schedule 11:30-12:10 11 Reg Maths 4 9709 AS (Ms E Wang) / 2026/06/16 14:35-16:00 -> schedule 14:35-15:15 11 Reg Maths 4 9709 AS (Ms E Wang) / 2026/06/17 10:00-11:25 -> schedule 10:00-10:40 11 Reg Maths 4 9709 AS (Ms E Wang) / ... |
| Physics D | CIE | D | Raufie Shafie | B3009 | Not Feasible | Internal room clash with requested courses: Chinese D-2 (CIE D).; Live overlap(s): 2026/06/10 10:00-11:25 -> bookings 10:00-11:25 G10 TT Physics Block D (Faisal Qureshi) |
| Chemistry D | CIE | D | Selina Sun | B4004 | Not Feasible | Live overlap(s): 2026/06/10 10:00-11:25 -> bookings 10:00-11:25 Grade 11 IB Chemistry (Dr Alistair Furze) / 2026/06/12 11:30-12:10 -> bookings 11:30-12:10 Grade 11 IB Chemistry (Dr Alistair Furze) |
| History | CIE | D | Keith Seeley / Matthew Peatman | B3044 | Feasible | Checked 8 slot(s). |
| Art | CIE | D | Amanda Milne / Luciana Liu | B3027 | Not Feasible | Live overlap(s): 2026/06/11 10:00-11:25 -> bookings 09:00-12:00 G11 AS Art Practical (DC4 Exam) |
| Chinese D-1 | CIE | D | Miya Yang | B4011 | Not Feasible | Live overlap(s): 2026/06/16 14:35-16:00 -> schedule 14:35-15:15 G9.5 Summit Economics (Mr F Nzamy) / 2026/06/18 10:00-11:25 -> bookings 08:20-14:25 IB Chinese SL,IB ToK (Miya Yang) |
| Chinese D-2 | CIE | D | Ivy Zhu | B3009 | Not Feasible | Internal room clash with requested courses: Physics D (CIE D).; Live overlap(s): 2026/06/10 10:00-11:25 -> bookings 10:00-11:25 G10 TT Physics Block D (Faisal Qureshi) |
| English | IBDP | D | Warwick Midlane | B4038 | Not Feasible | Live overlap(s): 2026/06/10 10:00-11:25 -> bookings 10:40-12:00 G9.5 0580 (DC4 Exam) / 2026/06/10 10:00-11:25 -> bookings 08:30-10:10 G9.5 Chinese - Reading & Writing (DC4 Exam) / 2026/06/10 10:00-11:25 -> bookings 10:35-12:00 G9.5 Summit World History (DC4 Exam) / 2026/06/11 10:00-11:25 -> bookings 10:30-12:00 G9.5 English Listening & Reading (DC4 Exam) |
| English | IBDP | D | Donald Meyer | B4043 | Not Feasible | Live overlap(s): 2026/06/10 10:00-11:25 -> bookings 10:40-12:00 G9.5 0580 (DC4 Exam) / 2026/06/10 10:00-11:25 -> bookings 08:30-10:10 G9.5 Chinese - Reading & Writing (DC4 Exam) / 2026/06/10 10:00-11:25 -> bookings 10:35-12:00 G9.5 Summit World History (DC4 Exam) / 2026/06/11 10:00-11:25 -> bookings 10:30-12:00 G9.5 English Listening & Reading (DC4 Exam) |
| English | IBDP | D | Darren McQuay | B4040 | Not Feasible | Live overlap(s): 2026/06/10 10:00-11:25 -> bookings 10:40-12:00 G9.5 0580 (DC4 Exam) / 2026/06/10 10:00-11:25 -> bookings 08:30-10:10 G9.5 Chinese - Reading & Writing (DC4 Exam) / 2026/06/10 10:00-11:25 -> bookings 10:35-12:00 G9.5 Summit World History (DC4 Exam) / 2026/06/11 10:00-11:25 -> bookings 10:30-12:00 G9.5 English Listening & Reading (DC4 Exam) |
| Economics 1 HL/SL | IBDP | E | Chaminda Marasinghe | B3009 | Not Feasible | Live overlap(s): 2026/06/11 08:20-09:45 -> schedule 08:20-09:00 G9 pre-IG Economics (Ms k Ding) / 2026/06/18 08:20-09:45 -> schedule 08:20-09:00 G9 pre-IG Economics (Ms k Ding) |
| Business H/SL | IBDP | E | Jennifer Jacobs-Kraft | B2039 | Not Feasible | Live overlap(s): 2026/06/11 08:20-09:45 -> schedule 08:20-09:00 11G / Life Skills (Mr A Varley) / 2026/06/15 08:20-09:45 -> schedule 08:20-09:00 11A / Life Skills (Ms L Zhu) / 2026/06/18 08:20-09:45 -> schedule 08:20-09:00 11G / Life Skills (Mr A Varley) / 2026/06/29 08:20-09:45 -> schedule 09:05-09:45 AS Business 1 (Mr R Hamroun) |
| Philosophy H/SL | IBDP | E | Matthew Peatman | B3044 | Not Feasible | Live overlap(s): 2026/06/15 08:20-09:45 -> bookings 09:00-09:45 G11 IB Philosophy (Matthew Peatman) / 2026/06/29 08:20-09:45 -> bookings 09:00-09:45 G11 IB Philosophy (Matthew Peatman) |
| English E-1 | CIE | E | Kurt Shelton | B4038 | Feasible | Checked 6 slot(s). |
| English E-2 | CIE | E | Jenna Wade Dunn | B4042 | Not Feasible | Live overlap(s): 2026/06/11 08:20-09:45 -> bookings 08:30-09:55 G9.5 Summit Chemistry (DC4 Exam) / 2026/06/16 11:30-12:10 -> schedule 11:30-12:10 G9 pre-IG English (Mr T TT19 EXT,Ms T TT24 Aurora, Dai,Ms T TT25 Ariel Wang) |
| English E-3 | CIE | E | Lim Wan | B4043 | Not Feasible | Live overlap(s): 2026/06/11 08:20-09:45 -> bookings 08:30-09:30 G9.5 Pre-IG Chemistry (DC4 Exam) / 2026/06/12 08:20-09:00 -> bookings 08:30-09:30 G11 IB Physics H/SL Paper 1 (DC4 Exam) / 2026/06/15 08:20-09:45 -> bookings 08:30-09:45 G11 IB Physics H/SL Paper 2 (DC4 Exam) |
| English E-4 | CIE | E | Helen Liu | B4039 | Feasible | Checked 6 slot(s). |
| English E-5 | CIE | E | Sally Guo | B4040 | Feasible | Checked 6 slot(s). |
| English E-6 | CIE | E | Sherry Yuan | B4041 | Not Feasible | Live overlap(s): 2026/06/16 11:30-12:10 -> schedule 11:30-12:10 G9.5 Summit English (Mr T TT19 EXT,Ms T TT22 Iris Z, hou,Mr T TT23 Florence Chen) |
| English E-7 | CIE | E | Cordelia Jiao | B4011 | Not Feasible | Live overlap(s): 2026/06/18 08:20-09:45 -> bookings 08:20-14:25 IB Chinese SL,IB ToK (Miya Yang) |

## Candidate Room Feasibility From Workbook

These candidate rooms were checked against the current live state in `schedule`, `bookings`, and `room_sessions`, including the June course bookings that have already been inserted.

### Candidate Summary

- Blocked or missing courses reviewed from workbook: 43
- Courses with candidate rooms provided: 37
- Courses with at least one feasible candidate now: 19
- Candidate rooms checked: 182
- Candidate rooms feasible now: 23
- Courses still without a feasible candidate from the workbook: 24

### Candidate Results

| Course | Program | Block | Workbook candidates | Feasible now | Notes |
| --- | --- | --- | --- | --- | --- |
| Math HL | IBDP | A | B3039, B3040, B3041, B3042, B3043 | B3040 | Remaining blocked candidates: B3039: blocked by bookings 08:20-09:45 Math SL (Shahid Anwar) on 2026/06/10; B3041: blocked by bookings 08:20-16:00 LS Self Study (Leo Li) on 2026/06/15 |
| Regular Math A-2 | CIE | A | B3039, B3040, B3041, B3042, B3043 | B3040 | Remaining blocked candidates: B3039: blocked by bookings 08:20-09:45 Math SL (Shahid Anwar) on 2026/06/10; B3041: blocked by bookings 08:20-16:00 LS Self Study (Leo Li) on 2026/06/15 |
| Physics A-1 | CIE | A | No candidate provided | None | Workbook entry was blank or marked ignore. |
| Physics A-2 (Summit) | CIE | A | No candidate provided | None | Workbook entry was blank or marked ignore. |
| Physics A-3 (EU) | CIE | A | No candidate provided | None | Workbook entry was blank or marked ignore. |
| Geography | CIE | A | B2036, B2039, B2040, B2041, B2042, B2043, B2044 | B2039 | Remaining blocked candidates: B2036: blocked by bookings 08:20-09:45 Geo G11 IB (Alex Oniang'o) on 2026/06/10; B2040: blocked by bookings 08:20-09:45 Economics A (Reza Hamroun) on 2026/06/10 |
| Economics 2 HL/SL | IBDP | B1 | B2039, B2040, B2041, B2042, B2043, B2044 | None | B2039: blocked by schedule 11:30-12:10 AS Business 1 (Mr R Hamroun) on 2026/06/10; B2040: blocked by schedule 11:30-12:10 G9 IG Economics 6 (Ms J Zhou) on 2026/06/10 |
| Biology HL/SL | IBDP | B1 | B3002, B3004, B3005, B3007 | None | B3002: blocked by schedule 11:30-12:10 AS Physics 2 (Mr F Qureshi) on 2026/06/10; B3004: blocked by bookings 11:30-14:25 G10 TT Physics Block B-2 (Faisal Qureshi) on 2026/06/10 |
| Theatre HL/SL | IBDP | B1 | B2004 | B2004 | All listed candidates were feasible. |
| Physics HL/SL | IBDP | B1 | B3002, B3004, B3005, B3007 | None | B3002: blocked by schedule 11:30-12:10 AS Physics 2 (Mr F Qureshi) on 2026/06/10; B3004: blocked by bookings 11:30-14:25 G10 TT Physics Block B-2 (Faisal Qureshi) on 2026/06/10 |
| Physics B-1 | CIE | B | No candidate provided | None | Workbook entry was blank or marked ignore. |
| Physics B-2 | CIE | B | No candidate provided | None | Workbook entry was blank or marked ignore. |
| Biology | CIE | B | B4002, B4004, B4005, B4007, B3007 | B4004, B4007 | Remaining blocked candidates: B4002: blocked by schedule 11:30-12:10 G11 AS Chemistry Summit (Ms J Zhu) on 2026/06/10; B4005: blocked by schedule 11:30-12:10 AS Chemistry 2 (Ms F Fu) on 2026/06/10 |
| Economics B-1 | CIE | B | B2039, B2040, B2041, B2042, B2043, B2044 | None | B2039: blocked by schedule 11:30-12:10 AS Business 1 (Mr R Hamroun) on 2026/06/10; B2040: blocked by schedule 11:30-12:10 G9 IG Economics 6 (Ms J Zhou) on 2026/06/10 |
| Music | CIE | B | B2004 | B2004 | All listed candidates were feasible. |
| Economics B-2 (Summit) | CIE | B | B2039, B2040, B2041, B2042, B2043, B2044 | None | B2039: blocked by schedule 11:30-12:10 AS Business 1 (Mr R Hamroun) on 2026/06/10; B2040: blocked by schedule 11:30-12:10 G9 IG Economics 6 (Ms J Zhou) on 2026/06/10 |
| Regular Maths B (EU) | CIE | B | B3039, B3040, B3041, B3042, B3043 | B3039, B3043 | Remaining blocked candidates: B3040: blocked by schedule 11:30-12:10 11 AS Further Maths (Ms N Magsudova) on 2026/06/10; B3041: blocked by bookings 08:20-16:00 LS Self Study (Leo Li) on 2026/06/15 |
| Art (Dual Dose) | CIE | B | B4029 | None | B4029: blocked by schedule 11:30-12:10 11 AS Art 1 (Ms A Milne) on 2026/06/10 |
| Chemistry HL/SL | IBDP | C | B4002, B4004, B4005, B4007 | B4005 | Remaining blocked candidates: B4002: blocked by schedule 14:35-15:15 AS Chemistry 3 (Ms S Sun) on 2026/06/10; B4004: blocked by bookings 14:35-16:00 Chemistry C-1 (Khurram Shezad) on 2026/06/10 |
| Biology HL/SL | IBDP | C | B4002, B4004, B4005, B4007, B3007 | B4005, B3007 | Remaining blocked candidates: B4002: blocked by schedule 14:35-15:15 AS Chemistry 3 (Ms S Sun) on 2026/06/10; B4004: blocked by bookings 14:35-16:00 Chemistry C-1 (Khurram Shezad) on 2026/06/10 |
| Regular Math C-2 | CIE | C | B3039, B3040, B3041, B3042, B3043 | B3042 | Remaining blocked candidates: B3039: blocked by schedule 14:35-15:15 G9.5 AS Maths (Mr S Liu) on 2026/06/10; B3040: blocked by bookings 14:35-16:00 Regular Math C-1 (Narmina Magsudova) on 2026/06/10 |
| Further Maths C | CIE | C | B3039, B3040, B3041, B3042, B3043 | B3042 | Remaining blocked candidates: B3039: blocked by schedule 14:35-15:15 G9.5 AS Maths (Mr S Liu) on 2026/06/10; B3040: blocked by bookings 14:35-16:00 Regular Math C-1 (Narmina Magsudova) on 2026/06/10 |
| Advanced Maths (CIE) C | CIE | C | B3039, B3040, B3041, B3042, B3043 | B3042 | Remaining blocked candidates: B3039: blocked by schedule 14:35-15:15 G9.5 AS Maths (Mr S Liu) on 2026/06/10; B3040: blocked by bookings 14:35-16:00 Regular Math C-1 (Narmina Magsudova) on 2026/06/10 |
| Business | CIE | C | B1034, B2039, B2040, B2041, B2042, B2043, B2044 | B1034 | Remaining blocked candidates: B2039: blocked by schedule 14:35-15:15 AS Business 2 (Ms J Jacobs-Kraft) on 2026/06/10; B2040: blocked by schedule 14:35-15:15 11 AS Economics Summit (Mr F Nzamy) on 2026/06/10 |
| Chemistry C-2 (Summit) | CIE | C | B4002, B4004, B4005, B4007 | B4005 | Remaining blocked candidates: B4002: blocked by schedule 14:35-15:15 AS Chemistry 3 (Ms S Sun) on 2026/06/10; B4004: blocked by bookings 14:35-16:00 Chemistry C-1 (Khurram Shezad) on 2026/06/10 |
| Regular Maths D | CIE | D | B3039, B3040, B3041, B3042, B3043 | B3043 | Remaining blocked candidates: B3039: blocked by schedule 10:00-10:40 G11 AS Maths Learning Support (Mr S Anwar) on 2026/06/10; B3040: blocked by schedule 10:00-10:40 11 Reg Maths 4 9709 AS (Ms E Wang) on 2026/06/10 |
| Fast Maths (Edexcel) | CIE | D | B3039, B3040, B3041, B3042, B3043 | B3043 | Remaining blocked candidates: B3039: blocked by schedule 10:00-10:40 G11 AS Maths Learning Support (Mr S Anwar) on 2026/06/10; B3040: blocked by schedule 10:00-10:40 11 Reg Maths 4 9709 AS (Ms E Wang) on 2026/06/10 |
| Advanced Math (CIE) D | CIE | D | B3039, B3040, B3041, B3042, B3043 | B3043 | Remaining blocked candidates: B3039: blocked by schedule 10:00-10:40 G11 AS Maths Learning Support (Mr S Anwar) on 2026/06/10; B3040: blocked by schedule 10:00-10:40 11 Reg Maths 4 9709 AS (Ms E Wang) on 2026/06/10 |
| Physics D | CIE | D | No candidate provided | None | Workbook entry was blank or marked ignore. |
| Chemistry D | CIE | D | B4002, B4004, B4005, B4007 | None | B4002: blocked by schedule 10:00-10:40 9D/Physics (Ms A Biju,Mr F Qureshi) on 2026/06/11; B4004: blocked by bookings 10:00-11:25 Grade 11 IB Chemistry (Dr Alistair Furze) on 2026/06/10 |
| Art | CIE | D | B3027, B3029, B4029 | B3029, B4029 | Remaining blocked candidates: B3027: blocked by bookings 09:00-12:00 G11 AS Art Practical (DC4 Exam) on 2026/06/11 |
| Chinese D-1 | CIE | D | B3009, B4009, B4010, B4011 | None | B3009: blocked by bookings 10:00-11:25 G10 TT Physics Block D (Faisal Qureshi) on 2026/06/10; B4009: blocked by schedule 10:00-10:40 11 AL Chinese EU (Ms J Li) on 2026/06/10 |
| Chinese D-2 | CIE | D | B3009, B4009, B4010, B4011 | None | B3009: blocked by bookings 10:00-11:25 G10 TT Physics Block D (Faisal Qureshi) on 2026/06/10; B4009: blocked by schedule 10:00-10:40 11 AL Chinese EU (Ms J Li) on 2026/06/10 |
| English | IBDP | D | B4038, B4039, B4040, B4041, B4042, B4043 | None | B4038: blocked by bookings 10:40-12:00 G9.5 0580 (DC4 Exam) on 2026/06/10; B4039: blocked by bookings 10:40-12:00 G11 IB English A Paper 1 (DC4 Exam) on 2026/06/10 |
| English | IBDP | D | B4038, B4039, B4040, B4041, B4042, B4043 | None | B4038: blocked by bookings 10:40-12:00 G9.5 0580 (DC4 Exam) on 2026/06/10; B4039: blocked by bookings 10:40-12:00 G11 IB English A Paper 1 (DC4 Exam) on 2026/06/10 |
| English | IBDP | D | B4038, B4039, B4040, B4041, B4042, B4043 | None | B4038: blocked by bookings 10:40-12:00 G9.5 0580 (DC4 Exam) on 2026/06/10; B4039: blocked by bookings 10:40-12:00 G11 IB English A Paper 1 (DC4 Exam) on 2026/06/10 |
| Economics 1 HL/SL | IBDP | E | B2039, B2040, B2041, B2042, B2043, B2044 | None | B2039: blocked by schedule 08:20-09:00 11G / Life Skills (Mr A Varley) on 2026/06/11; B2040: blocked by schedule 08:20-09:00 G9 IG Economics 1 (Ms J Zhou) on 2026/06/11 |
| Business H/SL | IBDP | E | B2039, B2040, B2041, B2042, B2043, B2044 | None | B2039: blocked by schedule 08:20-09:00 11G / Life Skills (Mr A Varley) on 2026/06/11; B2040: blocked by schedule 08:20-09:00 G9 IG Economics 1 (Ms J Zhou) on 2026/06/11 |
| Philosophy H/SL | IBDP | E | B2036, B2039, B2040, B2041, B2042, B2043, B2044 | B2036 | Remaining blocked candidates: B2039: blocked by schedule 08:20-09:00 11G / Life Skills (Mr A Varley) on 2026/06/11; B2040: blocked by schedule 08:20-09:00 G9 IG Economics 1 (Ms J Zhou) on 2026/06/11 |
| English E-2 | CIE | E | B4038, B4039, B4040, B4041, B4042, B4043 | None | B4038: blocked by bookings 08:20-09:45 English E-1 (Kurt Shelton) on 2026/06/11; B4039: blocked by bookings 08:20-09:45 English E-4 (Helen Liu) on 2026/06/11 |
| English E-3 | CIE | E | B4038, B4039, B4040, B4041, B4042, B4043 | None | B4038: blocked by bookings 08:20-09:45 English E-1 (Kurt Shelton) on 2026/06/11; B4039: blocked by bookings 08:20-09:45 English E-4 (Helen Liu) on 2026/06/11 |
| English E-6 | CIE | E | B4038, B4039, B4040, B4041, B4042, B4043 | None | B4038: blocked by bookings 08:20-09:45 English E-1 (Kurt Shelton) on 2026/06/11; B4039: blocked by bookings 08:20-09:45 English E-4 (Helen Liu) on 2026/06/11 |
| English E-7 | CIE | E | B4038, B4039, B4040, B4041, B4042, B4043 | None | B4038: blocked by bookings 08:20-09:45 English E-1 (Kurt Shelton) on 2026/06/11; B4039: blocked by bookings 08:20-09:45 English E-4 (Helen Liu) on 2026/06/11 |

Candidate-room feasibility above is per course against the current live data. It is not yet a globally optimized room-allocation plan across the remaining blocked courses.

## Candidate Room Allocation Plan

This section converts the per-course workbook feasibility check into one conflict-free allocation plan across the remaining blocked courses. Each planned course keeps one room consistently across all of its block slots.

### Allocation Summary

- Courses reviewed from workbook: 43
- Courses with at least one live-feasible candidate: 19
- Courses allocated in one global plan: 12
- Booking rows represented by the plan: 83
- Courses still unresolved after global allocation: 31
- Unresolved export: candidate_room_unresolved_after_plan.csv

### Planned Allocations

| Course | Program | Block | Teacher | Chosen room | Other live-feasible options | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| Advanced Math (CIE) D | CIE | D | Eva Wang | B3043 | None | First live-feasible workbook option kept. |
| Advanced Maths (CIE) C | CIE | C | Mandy Chen | B3042 | None | First live-feasible workbook option kept. |
| Art | CIE | D | Amanda Milne / Luciana Liu | B3029 | B4029 | First live-feasible workbook option kept. |
| Biology HL/SL | IBDP | C | Lily Hung | B3007 | B4005 | Chosen to keep the global plan conflict-free. |
| Biology | CIE | B | Ambily Biju | B4007 | B4004 | Final room updated to keep B4007 live across all Block B slots. |
| Business | CIE | C | Joyce Zhou | B1034 | None | First live-feasible workbook option kept. |
| Chemistry C-2 (Summit) | CIE | C | Alistair Furze | B4005 | None | First live-feasible workbook option kept. |
| Geography | CIE | A | Keith Seeley / Alex Oniango | B2039 | None | First live-feasible workbook option kept. |
| Math HL | IBDP | A | Rajesh Choyikkunimmal | B3040 | None | First live-feasible workbook option kept. |
| Music | CIE | B | Andy Clark | B2004 | None | First live-feasible workbook option kept. |
| Philosophy H/SL | IBDP | E | Matthew Peatman | B2036 | None | First live-feasible workbook option kept. |
| Regular Maths B (EU) | CIE | B | Sheryl Shane Canite | B3039 | B3043 | First live-feasible workbook option kept. |

### Still Unresolved After Global Allocation

| Course | Program | Block | Teacher | Workbook candidates | Why unresolved |
| --- | --- | --- | --- | --- | --- |
| Regular Math A-2 | CIE | A | Sheryl Shane Canite | B3040, B3039, B3041, B3042, B3043 | Live-feasible candidates exist, but using them would collide with another chosen allocation in this plan. |
| Physics A-1 | CIE | A | Evelyn Yang | No candidate provided | Workbook entry was blank or marked ignore. |
| Physics A-2 (Summit) | CIE | A | Mike Hu | No candidate provided | Workbook entry was blank or marked ignore. |
| Physics A-3 (EU) | CIE | A | Logan Tian | No candidate provided | Workbook entry was blank or marked ignore. |
| Economics 2 HL/SL | IBDP | B1 | Chaminda Marasinghe | B2039, B2040, B2041, B2042, B2043, B2044 | B2039 blocked by schedule 11:30-12:10 AS Business 1 (Mr R Hamroun) on 2026/06/10 |
| Biology HL/SL | IBDP | B1 | Fisher Yu | B3002, B3004, B3005, B3007 | B3002 blocked by schedule 11:30-12:10 AS Physics 2 (Mr F Qureshi) on 2026/06/10 |
| Theatre HL/SL | IBDP | B1 | Chalice Rakgoale | B2004 | Live-feasible candidates exist, but using them would collide with another chosen allocation in this plan. |
| Physics HL/SL | IBDP | B1 | Logan Tian | B3002, B3004, B3005, B3007 | B3002 blocked by schedule 11:30-12:10 AS Physics 2 (Mr F Qureshi) on 2026/06/10 |
| Physics B-1 | CIE | B | Chester Lim | No candidate provided | Workbook entry was blank or marked ignore. |
| Physics B-2 | CIE | B | Evelyn Yang | No candidate provided | Workbook entry was blank or marked ignore. |
| Economics B-1 | CIE | B | Helgaard Le Roux | B2039, B2040, B2041, B2042, B2043, B2044 | B2039 blocked by schedule 11:30-12:10 AS Business 1 (Mr R Hamroun) on 2026/06/10 |
| Economics B-2 (Summit) | CIE | B | Fahran Nzamy | B2039, B2040, B2041, B2042, B2043, B2044 | B2039 blocked by schedule 11:30-12:10 AS Business 1 (Mr R Hamroun) on 2026/06/10 |
| Art (Dual Dose) | CIE | B | Mark Ford | B4029 | B4029 blocked by schedule 11:30-12:10 11 AS Art 1 (Ms A Milne) on 2026/06/10 |
| Chemistry HL/SL | IBDP | C | Judy Zhu | B4005, B4002, B4004, B4007 | Live-feasible candidates exist, but using them would collide with another chosen allocation in this plan. |
| Regular Math C-2 | CIE | C | Shaun Yang | B3042, B3039, B3040, B3041, B3043 | Live-feasible candidates exist, but using them would collide with another chosen allocation in this plan. |
| Further Maths C | CIE | C | Rajesh | B3042, B3039, B3040, B3041, B3043 | Live-feasible candidates exist, but using them would collide with another chosen allocation in this plan. |
| Regular Maths D | CIE | D | Joy Farhat | B3043, B3039, B3040, B3041, B3042 | Live-feasible candidates exist, but using them would collide with another chosen allocation in this plan. |
| Fast Maths (Edexcel) | CIE | D | Rajesh | B3043, B3039, B3040, B3041, B3042 | Live-feasible candidates exist, but using them would collide with another chosen allocation in this plan. |
| Physics D | CIE | D | Raufie Shafie | No candidate provided | Workbook entry was blank or marked ignore. |
| Chemistry D | CIE | D | Selina Sun | B4002, B4004, B4005, B4007 | B4002 blocked by schedule 10:00-10:40 9D/Physics (Ms A Biju,Mr F Qureshi) on 2026/06/11 |
| Chinese D-1 | CIE | D | Miya Yang | B3009, B4009, B4010, B4011 | B3009 blocked by bookings 10:00-11:25 G10 TT Physics Block D (Faisal Qureshi) on 2026/06/10 |
| Chinese D-2 | CIE | D | Ivy Zhu | B3009, B4009, B4010, B4011 | B3009 blocked by bookings 10:00-11:25 G10 TT Physics Block D (Faisal Qureshi) on 2026/06/10 |
| English | IBDP | D | Warwick Midlane | B4038, B4039, B4040, B4041, B4042, B4043 | B4038 blocked by bookings 10:40-12:00 G9.5 0580 (DC4 Exam) on 2026/06/10 |
| English | IBDP | D | Donald Meyer | B4038, B4039, B4040, B4041, B4042, B4043 | B4038 blocked by bookings 10:40-12:00 G9.5 0580 (DC4 Exam) on 2026/06/10 |
| English | IBDP | D | Darren McQuay | B4038, B4039, B4040, B4041, B4042, B4043 | B4038 blocked by bookings 10:40-12:00 G9.5 0580 (DC4 Exam) on 2026/06/10 |
| Economics 1 HL/SL | IBDP | E | Chaminda Marasinghe | B2039, B2040, B2041, B2042, B2043, B2044 | B2039 blocked by schedule 08:20-09:00 11G / Life Skills (Mr A Varley) on 2026/06/11 |
| Business H/SL | IBDP | E | Jennifer Jacobs-Kraft | B2039, B2040, B2041, B2042, B2043, B2044 | B2039 blocked by schedule 08:20-09:00 11G / Life Skills (Mr A Varley) on 2026/06/11 |
| English E-2 | CIE | E | Jenna Wade Dunn | B4038, B4039, B4040, B4041, B4042, B4043 | B4038 blocked by bookings 08:20-09:45 English E-1 (Kurt Shelton) on 2026/06/11 |
| English E-3 | CIE | E | Lim Wan | B4038, B4039, B4040, B4041, B4042, B4043 | B4038 blocked by bookings 08:20-09:45 English E-1 (Kurt Shelton) on 2026/06/11 |
| English E-6 | CIE | E | Sherry Yuan | B4038, B4039, B4040, B4041, B4042, B4043 | B4038 blocked by bookings 08:20-09:45 English E-1 (Kurt Shelton) on 2026/06/11 |
| English E-7 | CIE | E | Cordelia Jiao | B4038, B4039, B4040, B4041, B4042, B4043 | B4038 blocked by bookings 08:20-09:45 English E-1 (Kurt Shelton) on 2026/06/11 |

### Execution Status

- Planned courses booked from the global allocation plan: 12
- Planned booking rows: 83
- Verified booking rows present after execution: 83
- Missing after verification: 0
- Unresolved rows exported to `candidate_room_unresolved_after_plan.csv`: 31

## Request Follow-Up

This section records the actions requested in column G of the unresolved workbook and the outcome after rechecking the live state with the current booked candidate allocations left in place.

- Requests processed: 31
- Additional rows booked from these requests: 0
- Additional courses booked from these requests: 0
- Rows verified as already covered by existing bookings: 6
- Rows still unresolved after follow-up: 25
- Follow-up export: `candidate_room_request_followup.csv`
- Follow-up workbook: `candidate_room_request_followup.xlsx`

| Course | Request | Feasible now | Outcome |
| --- | --- | --- | --- |
| Regular Math A-2 | give detail please | None | Detailed explanation added: B3040 blocked by current booked candidate allocation 08:20-09:45 Math HL (Rajesh Choyikkunimmal) on 2026/06/10; B3040 blocked by current booked candidate allocation 09:05-09:45 Math HL (Rajesh Choyikkunimmal) on 2026/06/12 |
| Physics A-1 | Already booked as G10TT… by Faisal | None | Verified already covered: B3004 blocked by bookings 08:20-09:45 G10 TT Physics Block A (Faisal Qureshi) on 2026/06/10; B3004 blocked by bookings 13:00-14:25 G10 TT Physics Block A (Faisal Qureshi) on 2026/06/15 |
| Physics A-2 (Summit) | Already booked as G10TT… by Faisal | None | Verified already covered: B3011 blocked by bookings 08:20-09:45 G10 TT Physics Block A Summit (Faisal Qureshi) on 2026/06/10; B3011 blocked by bookings 09:05-09:45 G10 TT Physics Block A Summit (Faisal Qureshi) on 2026/06/12 |
| Physics A-3 (EU) | Already booked as G10TT… by Faisal | None | Verified already covered: B3021 blocked by bookings 08:20-09:45 G10 TT Physics Block A EU (Faisal Qureshi) on 2026/06/10; B3021 blocked by bookings 09:05-09:45 G10 TT Physics Block A EU (Faisal Qureshi) on 2026/06/12 |
| Economics 2 HL/SL | Try other rooms in the candidate rooms | None | Still blocked: B2039 blocked by schedule 11:30-12:10 AS Business 1 (Mr R Hamroun) on 2026/06/10; B2039 blocked by schedule 14:35-15:15 AS Business 1 (Mr R Hamroun) on 2026/06/11 |
| Biology HL/SL | Try other rooms in the candidate rooms | None | Still blocked: B3002 blocked by schedule 11:30-12:10 AS Physics 2 (Mr F Qureshi) on 2026/06/10; B3002 blocked by schedule 14:35-15:15 AS Physics 2 (Mr F Qureshi) on 2026/06/11 |
| Theatre HL/SL | give detail please | None | Detailed explanation added: B2004 blocked by current booked candidate allocation 11:30-14:25 Music (Andy Clark) on 2026/06/10; B2004 blocked by current booked candidate allocation 14:35-16:00 Music (Andy Clark) on 2026/06/11 |
| Physics HL/SL | Try other rooms in the candidate rooms | None | Still blocked: B3002 blocked by schedule 11:30-12:10 AS Physics 2 (Mr F Qureshi) on 2026/06/10; B3002 blocked by schedule 14:35-15:15 AS Physics 2 (Mr F Qureshi) on 2026/06/11 |
| Physics B-1 | Already booked as G10TT… by Faisal | None | Verified already covered: B3005 blocked by bookings 11:30-14:25 G10 TT Physics Block B-1 (Faisal Qureshi) on 2026/06/10; B3005 blocked by bookings 10:00-11:25 G10 TT Physics Block B-1 (Faisal Qureshi) on 2026/06/12 |
| Physics B-2 | Already booked as G10TT… by Faisal | None | Verified already covered: B3004 blocked by bookings 11:30-14:25 G10 TT Physics Block B-2 (Faisal Qureshi) on 2026/06/10; B3004 blocked by bookings 10:00-11:25 G10 TT Physics Block B-2 (Faisal Qureshi) on 2026/06/12 |
| Economics B-1 | Try other rooms in the candidate rooms | None | Still blocked: B2039 blocked by schedule 11:30-12:10 AS Business 1 (Mr R Hamroun) on 2026/06/10; B2039 blocked by schedule 14:35-15:15 AS Business 1 (Mr R Hamroun) on 2026/06/11 |
| Economics B-2 (Summit) | Try other rooms in the candidate rooms | None | Still blocked: B2039 blocked by schedule 11:30-12:10 AS Business 1 (Mr R Hamroun) on 2026/06/10; B2039 blocked by schedule 14:35-15:15 AS Business 1 (Mr R Hamroun) on 2026/06/11 |
| Art (Dual Dose) | Try other rooms in the candidate rooms | None | Still blocked: B4029 blocked by schedule 11:30-12:10 11 AS Art 1 (Ms A Milne) on 2026/06/10; B4029 blocked by schedule 14:35-15:15 11 AS Art 1 (Ms A Milne) on 2026/06/11 |
| Chemistry HL/SL | give detail please | None | Detailed explanation added: B4005 blocked by current booked candidate allocation 14:35-16:00 Chemistry C-2 (Summit) (Alistair Furze) on 2026/06/10; B4005 blocked by current booked candidate allocation 13:00-14:25 Chemistry C-2 (Summit) (Alistair Furze) on 2026/06/11 |
| Regular Math C-2 | give detail please | None | Detailed explanation added: B3042 blocked by current booked candidate allocation 14:35-16:00 Advanced Maths (CIE) C (Mandy Chen) on 2026/06/10; B3042 blocked by current booked candidate allocation 13:00-14:25 Advanced Maths (CIE) C (Mandy Chen) on 2026/06/11 |
| Further Maths C | give detail please | None | Detailed explanation added: B3042 blocked by current booked candidate allocation 14:35-16:00 Advanced Maths (CIE) C (Mandy Chen) on 2026/06/10; B3042 blocked by current booked candidate allocation 13:00-14:25 Advanced Maths (CIE) C (Mandy Chen) on 2026/06/11 |
| Regular Maths D | give detail please | None | Detailed explanation added: B3043 blocked by current booked candidate allocation 10:00-11:25 Advanced Math (CIE) D (Eva Wang) on 2026/06/10; B3043 blocked by current booked candidate allocation 10:00-11:25 Advanced Math (CIE) D (Eva Wang) on 2026/06/11 |
| Fast Maths (Edexcel) | give detail please | None | Detailed explanation added: B3043 blocked by current booked candidate allocation 10:00-11:25 Advanced Math (CIE) D (Eva Wang) on 2026/06/10; B3043 blocked by current booked candidate allocation 10:00-11:25 Advanced Math (CIE) D (Eva Wang) on 2026/06/11 |
| Physics D | Should be already booked with G10TT… By Faisal. Please double-check | None | Verified already covered: B3009 blocked by bookings 10:00-11:25 G10 TT Physics Block D (Faisal Qureshi) on 2026/06/10 |
| Chemistry D | Try other rooms in the candidate rooms | None | Still blocked: B4002 blocked by schedule 10:00-10:40 9D/Physics (Ms A Biju,Mr F Qureshi) on 2026/06/11; B4002 blocked by schedule 11:30-12:10 G9.5 Summit Physics (Mr L Zhang) on 2026/06/12 |
| Chinese D-1 | Try other rooms in the candidate rooms | None | Still blocked: B3009 blocked by bookings 10:00-11:25 G10 TT Physics Block D (Faisal Qureshi) on 2026/06/10; B4009 blocked by schedule 10:00-10:40 11 AL Chinese EU (Ms J Li) on 2026/06/10 |
| Chinese D-2 | Try other rooms in the candidate rooms | None | Still blocked: B3009 blocked by bookings 10:00-11:25 G10 TT Physics Block D (Faisal Qureshi) on 2026/06/10; B4009 blocked by schedule 10:00-10:40 11 AL Chinese EU (Ms J Li) on 2026/06/10 |
| English | Try other rooms in the candidate rooms | None | Still blocked: B4038 blocked by bookings 10:40-12:00 G9.5 0580 (DC4 Exam) on 2026/06/10; B4039 blocked by bookings 10:40-12:00 G11 IB English A Paper 1 (DC4 Exam) on 2026/06/10 |
| English | Try other rooms in the candidate rooms | None | Still blocked: B4038 blocked by bookings 10:40-12:00 G9.5 0580 (DC4 Exam) on 2026/06/10; B4039 blocked by bookings 10:40-12:00 G11 IB English A Paper 1 (DC4 Exam) on 2026/06/10 |
| English | Try other rooms in the candidate rooms | None | Still blocked: B4038 blocked by bookings 10:40-12:00 G9.5 0580 (DC4 Exam) on 2026/06/10; B4039 blocked by bookings 10:40-12:00 G11 IB English A Paper 1 (DC4 Exam) on 2026/06/10 |
| Economics 1 HL/SL | Try other rooms in the candidate rooms | None | Still blocked: B2039 blocked by schedule 08:20-09:00 11G / Life Skills (Mr A Varley) on 2026/06/11; B2039 blocked by schedule 08:20-09:00 11A / Life Skills (Ms L Zhu) on 2026/06/15 |
| Business H/SL | Try other rooms in the candidate rooms | None | Still blocked: B2039 blocked by schedule 08:20-09:00 11G / Life Skills (Mr A Varley) on 2026/06/11; B2039 blocked by schedule 08:20-09:00 11A / Life Skills (Ms L Zhu) on 2026/06/15 |
| English E-2 | Try other rooms in the candidate rooms | None | Still blocked: B4038 blocked by bookings 08:20-09:45 English E-1 (Kurt Shelton) on 2026/06/11; B4038 blocked by bookings 08:20-09:00 English E-1 (Kurt Shelton) on 2026/06/12 |
| English E-3 | Try other rooms in the candidate rooms | None | Still blocked: B4038 blocked by bookings 08:20-09:45 English E-1 (Kurt Shelton) on 2026/06/11; B4038 blocked by bookings 08:20-09:00 English E-1 (Kurt Shelton) on 2026/06/12 |
| English E-6 | Try other rooms in the candidate rooms | None | Still blocked: B4038 blocked by bookings 08:20-09:45 English E-1 (Kurt Shelton) on 2026/06/11; B4038 blocked by bookings 08:20-09:00 English E-1 (Kurt Shelton) on 2026/06/12 |
| English E-7 | Try other rooms in the candidate rooms | None | Still blocked: B4038 blocked by bookings 08:20-09:45 English E-1 (Kurt Shelton) on 2026/06/11; B4038 blocked by bookings 08:20-09:00 English E-1 (Kurt Shelton) on 2026/06/12 |

## Notes

- The original detailed results and workbook candidate section remain feasibility analysis.
- The global candidate-room allocation plan in this report has now been applied to `bookings` and verified against live data.
- The column J retry results below are later than the earlier follow-up section and therefore take precedence for the final unresolved set.
- This report supersedes all other markdown artifacts previously generated for these June booking issues.

## Column J Room Retry

This section records the recheck against the room lists added in column J of the still-actionable workbook.

- Rows processed: 25
- Courses booked now: 10
- Booking rows inserted: 71
- Still blocked: 15
- Already present: 0
- Results CSV: candidate_room_still_actionable_results.csv
- Results workbook: candidate_room_still_actionable_results.xlsx

| Course | Listed rooms | Feasible now | Outcome |
| --- | --- | --- | --- |
| Regular Math A-2 | B3009, B3010, B3011, B3012 | B3009 | Booked now: Booked in B3009 across 6 slot(s). |
| Economics 2 HL/SL | B3009, B3010, B3011, B3012 | B3010, B3012 | Booked now: Booked in B3010 across 7 slot(s). |
| Biology HL/SL | B3009, B3010, B3011, B3012 | B3012 | Booked now: Booked in B3012 across 7 slot(s). |
| Theatre HL/SL | B2003 | B2003 | Booked now: Booked in B2003 across 7 slot(s). |
| Physics HL/SL | B3009, B3010, B3011, B3012 | None | Still blocked: B3009 blocked by bookings 11:30-14:25 Chinese B (Ivy Zhu) on 2026/06/10; B3009 blocked by bookings 14:35-16:00 Chinese B (Ivy Zhu) on 2026/06/11; B3009 blocked by bookings 10:00-11:25 Chinese B (Ivy Zhu) on 2026/06/12 |
| Economics B-1 | B3009, B3010, B3011, B3012 | None | Still blocked: B3009 blocked by bookings 11:30-14:25 Chinese B (Ivy Zhu) on 2026/06/10; B3009 blocked by bookings 14:35-16:00 Chinese B (Ivy Zhu) on 2026/06/11; B3009 blocked by bookings 10:00-11:25 Chinese B (Ivy Zhu) on 2026/06/12 |
| Economics B-2 (Summit) | B3009, B3010, B3011, B3012 | None | Still blocked: B3009 blocked by bookings 11:30-14:25 Chinese B (Ivy Zhu) on 2026/06/10; B3009 blocked by bookings 14:35-16:00 Chinese B (Ivy Zhu) on 2026/06/11; B3009 blocked by bookings 10:00-11:25 Chinese B (Ivy Zhu) on 2026/06/12 |
| Art (Dual Dose) | B3029 | None | Still blocked: B3029 blocked by bookings 13:00-16:00 G9 IG Art & Design - Practical (DC4 Exam) on 2026/06/10; B3029 blocked by schedule 14:35-15:15 G9 IG Art 1 (Mr M Ford) on 2026/06/15; B3029 blocked by schedule 14:35-15:15 G9 IG Art 1 (Mr M Ford) on 2026/06/29 |
| Chemistry HL/SL | B4007 | None | Still blocked: B4007 blocked by schedule 14:35-15:15 AS Biology (Mr F Yu) on 2026/06/10; B4007 blocked by schedule 13:00-13:40 AS Biology (Mr F Yu) on 2026/06/11; B4007 blocked by schedule 10:00-10:40 AS Biology (Mr F Yu) on 2026/06/15 |
| Regular Math C-2 | B3009, B3010, B3011, B3012 | B3009, B3011 | Booked now: Booked in B3009 across 7 slot(s). |
| Further Maths C | B3009, B3010, B3011, B3012 | B3011 | Booked now: Booked in B3011 across 7 slot(s). |
| Regular Maths D | B3009, B3010, B3011, B3012 | None | Still blocked: B3009 blocked by bookings 10:00-11:25 G10 TT Physics Block D (Faisal Qureshi) on 2026/06/10; B3010 blocked by schedule 11:30-12:10 G9 pre-IG English (Mr T TT19 EXT) on 2026/06/12; B3011 blocked by schedule 10:00-10:40 IG Reg Maths 3 0580 2Y (Ms M Gou) on 2026/06/10 |
| Fast Maths (Edexcel) | B3009, B3010, B3011, B3012 | None | Still blocked: B3009 blocked by bookings 10:00-11:25 G10 TT Physics Block D (Faisal Qureshi) on 2026/06/10; B3010 blocked by schedule 11:30-12:10 G9 pre-IG English (Mr T TT19 EXT) on 2026/06/12; B3011 blocked by schedule 10:00-10:40 IG Reg Maths 3 0580 2Y (Ms M Gou) on 2026/06/10 |
| Chemistry D | B4004, B4005, B4007 | None | Still blocked: B4004 blocked by bookings 10:00-11:25 Grade 11 IB Chemistry (Dr Alistair Furze) on 2026/06/10; B4004 blocked by bookings 11:30-12:10 Grade 11 IB Chemistry (Dr Alistair Furze) on 2026/06/12; B4005 blocked by schedule 10:00-10:40 G9 pre-IG Chemistry-F (Ms A Biju) on 2026/06/11 |
| Chinese D-1 | B3009, B3010, B3011, B3012 | None | Still blocked: B3009 blocked by bookings 10:00-11:25 G10 TT Physics Block D (Faisal Qureshi) on 2026/06/10; B3010 blocked by schedule 11:30-12:10 G9 pre-IG English (Mr T TT19 EXT) on 2026/06/12; B3011 blocked by schedule 10:00-10:40 IG Reg Maths 3 0580 2Y (Ms M Gou) on 2026/06/10 |
| Chinese D-2 | B3009, B3010, B3011, B3012 | None | Still blocked: B3009 blocked by bookings 10:00-11:25 G10 TT Physics Block D (Faisal Qureshi) on 2026/06/10; B3010 blocked by schedule 11:30-12:10 G9 pre-IG English (Mr T TT19 EXT) on 2026/06/12; B3011 blocked by schedule 10:00-10:40 IG Reg Maths 3 0580 2Y (Ms M Gou) on 2026/06/10 |
| English | B2039, B2040, B2041, B2042, B2043 | B2039, B2040, B2043 | Booked now: Booked in B2039 across 8 slot(s). |
| English | B2039, B2040, B2041, B2042, B2043 | B2040, B2043 | Booked now: Booked in B2040 across 8 slot(s). |
| English | B2039, B2040, B2041, B2042, B2043 | B2043 | Booked now: Booked in B2043 across 8 slot(s). |
| Economics 1 HL/SL | B3009, B3010, B3011, B3012 | B3011 | Booked now: Booked in B3011 across 6 slot(s). |
| Business H/SL | B3009, B3010, B3011, B3012 | None | Still blocked: B3009 blocked by schedule 08:20-09:00 G9 pre-IG Economics (Ms k Ding) on 2026/06/11; B3009 blocked by schedule 08:20-09:00 G9 pre-IG Economics (Ms k Ding) on 2026/06/18; B3010 blocked by bookings 09:00-09:45 G11IB Economics (Abass Mugabe) on 2026/06/15 |
| English E-2 | B2039, B2040, B2041, B2042, B2043 | None | Still blocked: B2039 blocked by schedule 08:20-09:00 11G / Life Skills (Mr A Varley) on 2026/06/11; B2039 blocked by schedule 08:20-09:00 11A / Life Skills (Ms L Zhu) on 2026/06/15; B2039 blocked by schedule 08:20-09:00 11G / Life Skills (Mr A Varley) on 2026/06/18 |
| English E-3 | B2039, B2040, B2041, B2042, B2043 | None | Still blocked: B2039 blocked by schedule 08:20-09:00 11G / Life Skills (Mr A Varley) on 2026/06/11; B2039 blocked by schedule 08:20-09:00 11A / Life Skills (Ms L Zhu) on 2026/06/15; B2039 blocked by schedule 08:20-09:00 11G / Life Skills (Mr A Varley) on 2026/06/18 |
| English E-6 | B2039, B2040, B2041, B2042, B2043 | None | Still blocked: B2039 blocked by schedule 08:20-09:00 11G / Life Skills (Mr A Varley) on 2026/06/11; B2039 blocked by schedule 08:20-09:00 11A / Life Skills (Ms L Zhu) on 2026/06/15; B2039 blocked by schedule 08:20-09:00 11G / Life Skills (Mr A Varley) on 2026/06/18 |
| English E-7 | B2039, B2040, B2041, B2042, B2043 | None | Still blocked: B2039 blocked by schedule 08:20-09:00 11G / Life Skills (Mr A Varley) on 2026/06/11; B2039 blocked by schedule 08:20-09:00 11A / Life Skills (Ms L Zhu) on 2026/06/15; B2039 blocked by schedule 08:20-09:00 11G / Life Skills (Mr A Varley) on 2026/06/18 |

## Appendix: G11 ElevateU Consolidation

This appendix absorbs the previously separate `G11_ElevateU_Room_Consolidation_Feasibility.md` so that this file remains the only June booking-issues markdown record.

### Request Context

- Period reviewed: 27 May to 9 June 2026
- Request: move all G11 ElevateU classes to a single room for the period
- Later scope update: include G11 Chinese revision sessions for Jenny Li
- Prepared from live Supabase data in `room_sessions`, `schedule`, and `bookings`

### Current G11 ElevateU Schedule

There were 3 active ElevateU subjects in the period with 25 total sessions, plus 9 Chinese revision sessions added for the consolidation check.

| Subject | Course Code | Teacher |
| --- | --- | --- |
| Maths | 9709/NE | Joy Farhat |
| Physics | 9702/NE | Steve Pan |
| Economics | 9708/NE | Zoe Wang |
| Chinese Revision | 9868/NE | Jenny Li |

### Consolidation Finding

B3042 was identified as the strongest single-room candidate because it already hosted all ElevateU Maths sessions, had no conflicting entries across `room_sessions`, `schedule`, or `bookings`, and did not create time overlaps across the combined day structure.

### Feasibility Verdict

The consolidation was assessed as feasible in B3042 for the 27 May to 8 June operating window, subject to one operational caveat: Physics suitability in a non-lab room needed teacher confirmation.

### Sessions Requiring Action

| Action | Subject | Sessions to Update |
| --- | --- | --- |
| No change needed | Maths (Joy Farhat) | 9 sessions already in B3042 |
| Relocate to B3042 | Physics (Steve Pan) | 8 sessions |
| Relocate to B3042 | Economics (Zoe Wang) | 8 sessions |
| Relocate to B3042 | Chinese Revision (Jenny Li) | 9 sessions |

### Risks And Considerations

| Risk | Severity | Notes |
| --- | --- | --- |
| Room capacity | Low | Same student group already used B3042 for Maths. |
| Physics specialist setup | Medium | Physics teacher confirmation was required because B3042 was not a lab room. |
| Last-minute bookings in B3042 | Low | No conflicts were present at the time of review, but live bookings still needed monitoring. |
| 9 June data gap | Low | No ElevateU sessions were found for 9 June in the source data. |

### Recommendation Recorded

The recommendation at the time of that analysis was to consolidate the ElevateU and Jenny Li sessions into B3042, then update the affected rows in `room_sessions` after teacher confirmation.

## Remaining Blocked Room Retry

This section records the recheck against the updated candidate-room lists added to the remaining-blocked workbook for another review pass.

- Rows processed: 15
- Courses booked now: 0
- Booking rows inserted: 0
- Still blocked: 15
- Already present: 0
- Results CSV: candidate_room_remaining_blocked_results.csv
- Results workbook: candidate_room_remaining_blocked_results.xlsx

| Course | Listed rooms | Feasible now | Outcome |
| --- | --- | --- | --- |
| Physics HL/SL | B3009 | None | Still blocked: B3009 blocked by bookings 11:30-14:25 Chinese B (Ivy Zhu) on 2026/06/10; B3009 blocked by bookings 14:35-16:00 Chinese B (Ivy Zhu) on 2026/06/11; B3009 blocked by bookings 10:00-11:25 Chinese B (Ivy Zhu) on 2026/06/12 |
| Economics B-1 | B3009 | None | Still blocked: B3009 blocked by bookings 11:30-14:25 Chinese B (Ivy Zhu) on 2026/06/10; B3009 blocked by bookings 14:35-16:00 Chinese B (Ivy Zhu) on 2026/06/11; B3009 blocked by bookings 10:00-11:25 Chinese B (Ivy Zhu) on 2026/06/12 |
| Economics B-2 (Summit) | B3009 | None | Still blocked: B3009 blocked by bookings 11:30-14:25 Chinese B (Ivy Zhu) on 2026/06/10; B3009 blocked by bookings 14:35-16:00 Chinese B (Ivy Zhu) on 2026/06/11; B3009 blocked by bookings 10:00-11:25 Chinese B (Ivy Zhu) on 2026/06/12 |
| Art (Dual Dose) | B3029 | None | Still blocked: B3029 blocked by bookings 13:00-16:00 G9 IG Art & Design - Practical (DC4 Exam) on 2026/06/10; B3029 blocked by schedule 14:35-15:15 G9 IG Art 1 (Mr M Ford) on 2026/06/15; B3029 blocked by schedule 14:35-15:15 G9 IG Art 1 (Mr M Ford) on 2026/06/29 |
| Chemistry HL/SL | B4007 | None | Still blocked: B4007 blocked by schedule 14:35-15:15 AS Biology (Mr F Yu) on 2026/06/10; B4007 blocked by schedule 13:00-13:40 AS Biology (Mr F Yu) on 2026/06/11; B4007 blocked by schedule 10:00-10:40 AS Biology (Mr F Yu) on 2026/06/15 |
| Regular Maths D | B3009, B3010, B3011 | None | Still blocked: B3009 blocked by bookings 10:00-11:25 G10 TT Physics Block D (Faisal Qureshi) on 2026/06/10; B3010 blocked by schedule 11:30-12:10 G9 pre-IG English (Mr T TT19 EXT) on 2026/06/12; B3011 blocked by schedule 10:00-10:40 IG Reg Maths 3 0580 2Y (Ms M Gou) on 2026/06/10 |
| Fast Maths (Edexcel) | B3009, B3010, B3011 | None | Still blocked: B3009 blocked by bookings 10:00-11:25 G10 TT Physics Block D (Faisal Qureshi) on 2026/06/10; B3010 blocked by schedule 11:30-12:10 G9 pre-IG English (Mr T TT19 EXT) on 2026/06/12; B3011 blocked by schedule 10:00-10:40 IG Reg Maths 3 0580 2Y (Ms M Gou) on 2026/06/10 |
| Chemistry D | B4004, B4005 | None | Still blocked: B4004 blocked by bookings 10:00-11:25 Grade 11 IB Chemistry (Dr Alistair Furze) on 2026/06/10; B4004 blocked by bookings 11:30-12:10 Grade 11 IB Chemistry (Dr Alistair Furze) on 2026/06/12; B4005 blocked by schedule 10:00-10:40 G9 pre-IG Chemistry-F (Ms A Biju) on 2026/06/11 |
| Chinese D-1 | B3009, B3010, B3011 | None | Still blocked: B3009 blocked by bookings 10:00-11:25 G10 TT Physics Block D (Faisal Qureshi) on 2026/06/10; B3010 blocked by schedule 11:30-12:10 G9 pre-IG English (Mr T TT19 EXT) on 2026/06/12; B3011 blocked by schedule 10:00-10:40 IG Reg Maths 3 0580 2Y (Ms M Gou) on 2026/06/10 |
| Chinese D-2 | B3009, B3010, B3011 | None | Still blocked: B3009 blocked by bookings 10:00-11:25 G10 TT Physics Block D (Faisal Qureshi) on 2026/06/10; B3010 blocked by schedule 11:30-12:10 G9 pre-IG English (Mr T TT19 EXT) on 2026/06/12; B3011 blocked by schedule 10:00-10:40 IG Reg Maths 3 0580 2Y (Ms M Gou) on 2026/06/10 |
| Business H/SL | B3009, B3010 | None | Still blocked: B3009 blocked by schedule 08:20-09:00 G9 pre-IG Economics (Ms k Ding) on 2026/06/11; B3009 blocked by schedule 08:20-09:00 G9 pre-IG Economics (Ms k Ding) on 2026/06/18; B3010 blocked by bookings 09:00-09:45 G11IB Economics (Abass Mugabe) on 2026/06/15 |
| English E-2 | B2039 | None | Still blocked: B2039 blocked by schedule 08:20-09:00 11G / Life Skills (Mr A Varley) on 2026/06/11; B2039 blocked by schedule 08:20-09:00 11A / Life Skills (Ms L Zhu) on 2026/06/15; B2039 blocked by schedule 08:20-09:00 11G / Life Skills (Mr A Varley) on 2026/06/18 |
| English E-3 | B2039 | None | Still blocked: B2039 blocked by schedule 08:20-09:00 11G / Life Skills (Mr A Varley) on 2026/06/11; B2039 blocked by schedule 08:20-09:00 11A / Life Skills (Ms L Zhu) on 2026/06/15; B2039 blocked by schedule 08:20-09:00 11G / Life Skills (Mr A Varley) on 2026/06/18 |
| English E-6 | B2039 | None | Still blocked: B2039 blocked by schedule 08:20-09:00 11G / Life Skills (Mr A Varley) on 2026/06/11; B2039 blocked by schedule 08:20-09:00 11A / Life Skills (Ms L Zhu) on 2026/06/15; B2039 blocked by schedule 08:20-09:00 11G / Life Skills (Mr A Varley) on 2026/06/18 |
| English E-7 | B2039 | None | Still blocked: B2039 blocked by schedule 08:20-09:00 11G / Life Skills (Mr A Varley) on 2026/06/11; B2039 blocked by schedule 08:20-09:00 11A / Life Skills (Ms L Zhu) on 2026/06/15; B2039 blocked by schedule 08:20-09:00 11G / Life Skills (Mr A Varley) on 2026/06/18 |

## Remaining 15 Suggested Available Rooms

This section suggests rooms that are fully available across all slots for each of the remaining 15 blocked courses, based on the current live state in `schedule`, `bookings`, and `room_sessions`.

- Remaining blocked rows reviewed: 15
- Suggestions export: candidate_room_remaining_blocked_suggestions.csv
- Suggestions workbook: candidate_room_remaining_blocked_suggestions.xlsx

| Course | Block | Suggested available rooms | Count |
| --- | --- | --- | ---: |
| Physics HL/SL | B1 | B1037, B2014, B2022, B2036, B3021, B4009, B4011, B4012, B4041 | 9 |
| Economics B-1 | B | B1037, B2014, B2022, B2036, B3021, B4011, B4012 | 7 |
| Economics B-2 (Summit) | B | B1037, B2014, B2022, B2036, B3021, B4011, B4012 | 7 |
| Art (Dual Dose) | B | B1037, B2014, B2022, B2036, B3021, B4011, B4012 | 7 |
| Chemistry HL/SL | C | B1011, B1037, B2003, B2004, B2005, B2014, B2022, B2026, B2036, B3004, B3021, B3027 | 15 |
| Regular Maths D | D | B1011, B1029, B1034, B1037, B2003, B2004, B2005, B2014, B2022, B2026, B2036, B3005 | 16 |
| Fast Maths (Edexcel) | D | B1011, B1029, B1034, B1037, B2003, B2004, B2005, B2014, B2022, B2026, B2036, B3005 | 16 |
| Chemistry D | D | B1011, B1029, B1034, B1037, B2003, B2004, B2005, B2014, B2022, B2026, B2036, B3005 | 16 |
| Chinese D-1 | D | B1011, B1029, B1034, B1037, B2003, B2004, B2005, B2014, B2022, B2026, B2036, B3005 | 16 |
| Chinese D-2 | D | B1011, B1029, B1034, B1037, B2003, B2004, B2005, B2014, B2022, B2026, B2036, B3005 | 16 |
| Business H/SL | E | B1011, B1029, B1037, B2003, B2004, B2005, B2014, B2022, B2026, B3004, B3021, B3043 | 17 |
| English E-2 | E | B1011, B1029, B1037, B2003, B2004, B2005, B2014, B2022, B2026, B3004, B3021, B3043 | 17 |
| English E-3 | E | B1011, B1029, B1037, B2003, B2004, B2005, B2014, B2022, B2026, B3004, B3021, B3043 | 17 |
| English E-6 | E | B1011, B1029, B1037, B2003, B2004, B2005, B2014, B2022, B2026, B3004, B3021, B3043 | 17 |
| English E-7 | E | B1011, B1029, B1037, B2003, B2004, B2005, B2014, B2022, B2026, B3004, B3021, B3043 | 17 |

## Remaining 15 User Room Decisions

This section records the final authoritative outcome for the remaining 15 rows after the initial preferred-room pass and the later approved two-room follow-up bookings.

- Rows reviewed: 15
- Rows assigned/booked: 15
- Requested rooms honored exactly: 6
- Booking rows inserted from the initial one-room assignment pass: 69
- Additional booking rows inserted from approved two-room follow-up plans: 36
- Final booking rows inserted across this 15-row phase: 105
- Still unresolved after final approved follow-up: 0
- Results CSV: remaining_15_user_decisions_results.csv
- Results workbook: remaining_15_user_decisions_results.xlsx
- Unresolved CSV: remaining_15_user_decisions_unresolved.csv
- Unresolved workbook: remaining_15_user_decisions_unresolved.xlsx

| Course | Decision | Requested room | Assigned room | Status | Resolution |
| --- | --- | --- | --- | --- | --- |
| Physics HL/SL | use | B4012 | B4012 | Assigned | Used requested room |
| Economics B-1 | use | B4011 | B1037 | Assigned | Requested B4011 could not be used globally; assigned B1037 instead |
| Economics B-2 (Summit) | use | B2044 | B4011 | Assigned | Requested B2044 could not be used globally; assigned B4011 instead |
| Art (Dual Dose) | use | B3028 | B3028 | Assigned | Used requested room |
| Chemistry HL/SL | use | B3004 | B3004 | Assigned | Used requested room |
| Regular Maths D | find_else | None | B3039 + B3042 | Assigned | Booked in the approved two-room plan: B3042 on 2026/06/10, 2026/06/12, 2026/06/15, 2026/06/16, 2026/06/17, and 2026/06/29; B3039 on 2026/06/11 and 2026/06/18. |
| Fast Maths (Edexcel) | use | B1034 | B1034 | Assigned | Used requested room |
| Chemistry D | use | B3005 | B3005 | Assigned | Used requested room |
| Chinese D-1 | find_else | None | B3009 + B3010 | Assigned | Booked in the approved two-room plan: B3010 on 2026/06/10; B3009 for the remaining 7 slots. |
| Chinese D-2 | find_else | None | B3010 + B4011 | Assigned | Booked in the approved two-room plan: B4011 on 2026/06/10, 2026/06/11, and 2026/06/12; B3010 for the remaining 5 slots. |
| Business H/SL | use | B3043 | B3043 | Assigned | Used requested room |
| English E-2 | use | B3043 | B1029 | Assigned | Requested B3043 could not be used globally; assigned B1029 instead |
| English E-3 | use | B1034 | B4009 | Assigned | Requested B1034 could not be used globally; assigned B4009 instead |
| English E-6 | find_else | None | B3010 + B3012 | Assigned | Booked in the approved two-room plan: B3010 on 2026/06/11 and 2026/06/12; B3012 for the remaining 4 slots. |
| English E-7 | use | B1029 | B4011 + B4041 | Assigned | Requested B1029 could not be used; booked in the approved two-room plan: B4011 on 2026/06/11, 2026/06/12, 2026/06/15, and 2026/06/16; B4041 on 2026/06/18 and 2026/06/29. |

## Current Unresolved 5 Live-Feasible Rooms

This section is now retained only as historical audit context from the earlier exploration phase.

- Former unresolved rows reviewed: 5
- Current remaining unresolved rows in this former five-row set: 0
- Suggestions CSV: remaining_15_unresolved_live_options.csv
- Suggestions workbook: remaining_15_unresolved_live_options.xlsx

The exploratory suggestions in the CSV/workbook above were superseded by the later approved two-room bookings recorded in the final section below.

## Current Unresolved 5 Two-Room Possibility

This section began as the two-room feasibility analysis for the final five unresolved rows. It is now the authoritative final outcome for that former unresolved set after the approved live bookings were inserted.

- Former unresolved rows reviewed: 5
- Former unresolved rows now booked: 5
- Remaining unresolved rows in this former set: 0
- Analysis CSV: remaining_15_unresolved_two_room_max.csv
- Analysis workbook: remaining_15_unresolved_two_room_max.xlsx

| Course | Final status | Rooms used | Final authoritative outcome |
| --- | --- | --- | --- |
| Chinese D-1 | Booked live | B3009, B3010 | B3010 on 2026/06/10 10:00-11:25; B3009 for the remaining 7 slots. |
| Chinese D-2 | Booked live | B3010, B4011 | B4011 on 2026/06/10, 2026/06/11, and 2026/06/12; B3010 for the remaining 5 slots. |
| Regular Maths D | Booked live | B3039, B3042 | B3042 on 2026/06/10, 2026/06/12, 2026/06/15, 2026/06/16, 2026/06/17, and 2026/06/29; B3039 on 2026/06/11 and 2026/06/18. |
| English E-6 | Booked live | B3010, B3012 | B3010 on 2026/06/11 and 2026/06/12; B3012 for the remaining 4 slots. |
| English E-7 | Booked live | B4011, B4041 | B4011 on 2026/06/11, 2026/06/12, 2026/06/15, and 2026/06/16; B4041 on 2026/06/18 and 2026/06/29. |

## Final June Live Rooming Info

This section is the authoritative live June rooming list for the supplied course roster, built from the current `bookings` table. If a course uses more than one room, every booked session is listed explicitly.

- Courses reviewed: 63
- Courses with all expected June slots booked live: 63
- Courses partially booked live: 0
- Courses with no live booking rows found: 0
- CSV export: june_2026_live_rooming_info.csv
- JSON export: june_2026_live_rooming_info.json

| Course | Program | Block | TID | Teacher | Status | Rooms used | Session details | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Math HL | IBDP | Block A | RJE | Rajesh Choyikkunimmal | Booked live | B3040 | Single room across booked slots: B3040 | All expected June slots found in live bookings. |
| Math SL | IBDP | Block A | SAN | Shahid Anwar | Booked live | B3039 | Single room across booked slots: B3039 | All expected June slots found in live bookings. |
| Regular Math A-1 | CIE | Block A | JFA | Joy Farhat | Booked live | B3042 | Single room across booked slots: B3042 | All expected June slots found in live bookings. |
| Regular Math A-2 | CIE | Block A | SCA | Sheryl Shane Canite | Booked live | B3009 | Single room across booked slots: B3009 | All expected June slots found in live bookings. |
| Physics A-1 | CIE | Block A | EVY | Evelyn Yang | Booked live | B3004 | Single room across booked slots: B3004 | Matched via alternate live booking teacher alias. |
| Chemistry A | CIE | Block A | SSU | Selina Sun | Booked live | B4002 | Single room across booked slots: B4002 | All expected June slots found in live bookings. |
| Economics A | CIE | Block A | RHA | Reza Hamroun | Booked live | B2040 | Single room across booked slots: B2040 | All expected June slots found in live bookings. |
| Chinese A | CIE | Block A | JLI | Jenny Li | Booked live | B4009 | Single room across booked slots: B4009 | All expected June slots found in live bookings. |
| Physics A-2 (Summit) | CIE | Block A | MHU | Mike Hu | Booked live | B3011 | Single room across booked slots: B3011 | Matched via alternate live booking teacher alias. |
| Physics A-3 (EU) | CIE | Block A | LTI | Logan Tian | Booked live | B3021 | Single room across booked slots: B3021 | Matched via alternate live booking teacher alias. |
| Geography | CIE | Block A | KSL/AON | Keith Seeley / Alex Oniango | Booked live | B2039 | Single room across booked slots: B2039 | All expected June slots found in live bookings. |
| Physics B-1 | CIE | Block B | CHL | Chester Lim | Booked live | B3005 | Single room across booked slots: B3005 | Matched via alternate live booking teacher alias. |
| Physics B-2 | CIE | Block B | EVY | Evelyn Yang | Booked live | B3004 | Single room across booked slots: B3004 | Matched via alternate live booking teacher alias. |
| Biology | CIE | Block B | ABI | Ambily Biju | Booked live | B4007 | Single room across booked slots: B4007 | All expected June slots found in live bookings after retaining B4007 for every Block B Biology slot. |
| Economics B-1 | CIE | Block B | HLR | Helgaard Le Roux | Booked live | B1037 | Single room across booked slots: B1037 | All expected June slots found in live bookings. |
| Computer Science | CIE | Block B | BJI | Bill Jiang | Booked live | B1029 | Single room across booked slots: B1029 | All expected June slots found in live bookings. |
| Music | CIE | Block B | ACR | Andy Clark | Booked live | B2004 | Single room across booked slots: B2004 | All expected June slots found in live bookings. |
| Chinese B | CIE | Block B | IZH | Ivy Zhu | Booked live | B3009 | Single room across booked slots: B3009 | All expected June slots found in live bookings. |
| Economics B-2 (Summit) | CIE | Block B | FNZ | Fahran Nzamy | Booked live | B4011 | Single room across booked slots: B4011 | All expected June slots found in live bookings. |
| Regular Maths B (EU) | CIE | Block B | SCA | Sheryl Shane Canite | Booked live | B3039, B3043 | 2026/06/10 11:30-14:25=B3039, B3043; 2026/06/11 14:35-16:00=B3039, B3043; 2026/06/12 10:00-11:25=B3039, B3043; 2026/06/15 14:35-16:00=B3039, B3043; 2026/06/17 11:30-14:25=B3039, B3043; 2026/06/18 14:35-16:00=B3039, B3043; 2026/06/29 14:35-16:00=B3039, B3043 | Duplicate live rows on slot(s): 2026/06/10 11:30-14:25=B3039, B3043; 2026/06/11 14:35-16:00=B3039, B3043; 2026/06/12 10:00-11:25=B3039, B3043; 2026/06/15 14:35-16:00=B3039, B3043; 2026/06/17 11:30-14:25=B3039, B3043; 2026/06/18 14:35-16:00=B3039, B3043; 2026/06/29 14:35-16:00=B3039, B3043 |
| Art (Dual Dose) | CIE | Block B | MFO | Mark Ford | Booked live | B3028 | Single room across booked slots: B3028 | All expected June slots found in live bookings. |
| Economics 2 HL/SL | IBDP | Block B1 | CMA | Chaminda Marasinghe | Booked live | B3010 | Single room across booked slots: B3010 | All expected June slots found in live bookings. |
| Biology HL/SL | IBDP | Block B1 | FYU | Fisher Yu | Booked live | B3012 | Single room across booked slots: B3012 | All expected June slots found in live bookings. |
| Theatre HL/SL | IBDP | Block B1 | CRA | Chalice Rakgoale | Booked live | B2003 | Single room across booked slots: B2003 | All expected June slots found in live bookings. |
| Physics HL/SL | IBDP | Block B1 | LTI | Logan Tian | Booked live | B4012 | Single room across booked slots: B4012 | All expected June slots found in live bookings. |
| Chinese A | IBDP | Block B2 | MEC | Melody Chen | Booked live | B4010 | Single room across booked slots: B4010 | All expected June slots found in live bookings. |
| Chinese B | IBDP | Block B2 | JLI | Jenny Li/Ann Yang | Booked live | B4009 | Single room across booked slots: B4009 | All expected June slots found in live bookings. |
| Physics HL/SL | IBDP | Block C | LTI | Logan Tian | Booked live | B3005 | Single room across booked slots: B3005 | All expected June slots found in live bookings. |
| Chemistry HL/SL | IBDP | Block C | ZHJ | Judy Zhu | Booked live | B3004 | Single room across booked slots: B3004 | All expected June slots found in live bookings. |
| Biology HL/SL | IBDP | Block C | LHN | Lily Hung | Booked live | B3007 | Single room across booked slots: B3007 | All expected June slots found in live bookings. |
| Regular Math C-1 | CIE | Block C | NMA | Narmina Magsudova | Booked live | B3040 | Single room across booked slots: B3040 | All expected June slots found in live bookings. |
| Regular Math C-2 | CIE | Block C | SHY | Shaun Yang | Booked live | B3009 | Single room across booked slots: B3009 | All expected June slots found in live bookings. |
| Further Maths C | CIE | Block C | RJE | Rajesh | Booked live | B3011 | Single room across booked slots: B3011 | All expected June slots found in live bookings. |
| Advanced Maths (CIE) C | CIE | Block C | MCH | Mandy Chen | Booked live | B3042 | Single room across booked slots: B3042 | All expected June slots found in live bookings. |
| Chemistry C-1 | CIE | Block C | KSH | Khurram Shezad | Booked live | B4004 | Single room across booked slots: B4004 | All expected June slots found in live bookings. |
| Economics D-1 | CIE | Block C | MIR | Marshall Irby | Booked live | B2043 | Single room across booked slots: B2043 | All expected June slots found in live bookings. |
| Business | CIE | Block C | JZX | Joyce Zhou | Booked live | B1034 | Single room across booked slots: B1034 | All expected June slots found in live bookings. |
| Chemistry C-2 (Summit) | CIE | Block C | AFU | Alistair Furze | Booked live | B4005 | Single room across booked slots: B4005 | All expected June slots found in live bookings. |
| Economic C-2 (EU) | CIE | Block C | WHU | Winnie Hu | Booked live | B2041 | Single room across booked slots: B2041 | All expected June slots found in live bookings. |
| TOK (Chinese) | IBDP | Block C2 | MYA/MPE | Miya Yang / Matthew Peatman | Booked live | B3044 | Single room across booked slots: B3044 | All expected June slots found in live bookings. |
| CAS | IBDP | Block C2 | LLN | #N/A | Booked live | B2044 | Single room across booked slots: B2044 | All expected June slots found in live bookings. |
| Regular Maths D | CIE | Block D | JFA | Joy Farhat | Booked live | B3039, B3042 | 2026/06/10 10:00-11:25=B3042; 2026/06/11 10:00-11:25=B3039; 2026/06/12 11:30-12:10=B3042; 2026/06/15 11:30-12:10=B3042; 2026/06/16 14:35-16:00=B3042; 2026/06/17 10:00-11:25=B3042; 2026/06/18 10:00-11:25=B3039; 2026/06/29 11:30-12:10=B3042 | All expected June slots found in live bookings. |
| Fast Maths (Edexcel) | CIE | Block D | RJE | Rajesh | Booked live | B1034 | Single room across booked slots: B1034 | All expected June slots found in live bookings. |
| Advanced Math (CIE) D | CIE | Block D | WEV | Eva Wang | Booked live | B3043 | Single room across booked slots: B3043 | All expected June slots found in live bookings. |
| Physics D | CIE | Block D | RSH | Raufie Shafie | Booked live | B3009, B4038 | 2026/06/10 10:00-11:25=B3009; 2026/06/11 10:00-11:25=B4038; 2026/06/12 11:30-12:10=B4038; 2026/06/15 11:30-12:10=B4038; 2026/06/16 14:35-16:00=B4038; 2026/06/17 10:00-11:25=B4038; 2026/06/18 10:00-11:25=B4038; 2026/06/29 11:30-12:10=B4038 | Matched via alternate live booking teacher alias. |
| Chemistry D | CIE | Block D | SSU | Selina Sun | Booked live | B3005 | Single room across booked slots: B3005 | All expected June slots found in live bookings. |
| History | CIE | Block D | KSL/MPE | Keith Seeley / Matthew Peatman | Booked live | B3044 | Single room across booked slots: B3044 | All expected June slots found in live bookings. |
| Art | CIE | Block D | AMM/LUL | Amanda Milne / Luciana Liu | Booked live | B3029, B4029 | 2026/06/10 10:00-11:25=B3029, B4029; 2026/06/11 10:00-11:25=B3029, B4029; 2026/06/12 11:30-12:10=B3029, B4029; 2026/06/15 11:30-12:10=B3029, B4029; 2026/06/16 14:35-16:00=B3029, B4029; 2026/06/17 10:00-11:25=B3029, B4029; 2026/06/18 10:00-11:25=B3029, B4029; 2026/06/29 11:30-12:10=B3029, B4029 | Duplicate live rows on slot(s): 2026/06/10 10:00-11:25=B3029, B4029; 2026/06/11 10:00-11:25=B3029, B4029; 2026/06/12 11:30-12:10=B3029, B4029; 2026/06/15 11:30-12:10=B3029, B4029; 2026/06/16 14:35-16:00=B3029, B4029; 2026/06/17 10:00-11:25=B3029, B4029; 2026/06/18 10:00-11:25=B3029, B4029; 2026/06/29 11:30-12:10=B3029, B4029 |
| Chinese D-1 | CIE | Block D | MYA | Miya Yang | Booked live | B3009, B3010 | 2026/06/10 10:00-11:25=B3010; 2026/06/11 10:00-11:25=B3009; 2026/06/12 11:30-12:10=B3009; 2026/06/15 11:30-12:10=B3009; 2026/06/16 14:35-16:00=B3009; 2026/06/17 10:00-11:25=B3009; 2026/06/18 10:00-11:25=B3009; 2026/06/29 11:30-12:10=B3009 | All expected June slots found in live bookings. |
| Chinese D-2 | CIE | Block D | IZH | Ivy Zhu | Booked live | B3010, B4011 | 2026/06/10 10:00-11:25=B4011; 2026/06/11 10:00-11:25=B4011; 2026/06/12 11:30-12:10=B4011; 2026/06/15 11:30-12:10=B3010; 2026/06/16 14:35-16:00=B3010; 2026/06/17 10:00-11:25=B3010; 2026/06/18 10:00-11:25=B3010; 2026/06/29 11:30-12:10=B3010 | All expected June slots found in live bookings. |
| English | IBDP | Block D | WMI | Warwick Midlane | Booked live | B2039 | Single room across booked slots: B2039 | All expected June slots found in live bookings. |
| English | IBDP | Block D | DME | Donald Meyer | Booked live | B2040 | Single room across booked slots: B2040 | All expected June slots found in live bookings. |
| English | IBDP | Block D | DMC | Darren McQuay | Booked live | B2043 | Single room across booked slots: B2043 | All expected June slots found in live bookings. |
| Economics 1 HL/SL | IBDP | Block E | CMA | Chaminda Marasinghe | Booked live | B3011 | Single room across booked slots: B3011 | All expected June slots found in live bookings. |
| Business H/SL | IBDP | Block E | JJK | Jennifer Jacobs-Kraft | Booked live | B3043 | Single room across booked slots: B3043 | All expected June slots found in live bookings. |
| Philosophy H/SL | IBDP | Block E | MPE | Matthew Peatman | Booked live | B2036 | Single room across booked slots: B2036 | All expected June slots found in live bookings. |
| English E-1 | CIE | Block E | KUS | Kurt Shelton | Booked live | B4038 | Single room across booked slots: B4038 | All expected June slots found in live bookings. |
| English E-2 | CIE | Block E | JWD | Jenna Wade Dunn | Booked live | B1029 | Single room across booked slots: B1029 | All expected June slots found in live bookings. |
| English E-3 | CIE | Block E | LWA | Lim Wan | Booked live | B4009 | Single room across booked slots: B4009 | All expected June slots found in live bookings. |
| English E-4 | CIE | Block E | HLI | Helen Liu | Booked live | B4039 | Single room across booked slots: B4039 | All expected June slots found in live bookings. |
| English E-5 | CIE | Block E | SGU | Sally Guo | Booked live | B4040 | Single room across booked slots: B4040 | All expected June slots found in live bookings. |
| English E-6 | CIE | Block E | SYU | Sherry Yuan | Booked live | B3010, B3012 | 2026/06/11 08:20-09:45=B3010; 2026/06/12 08:20-09:00=B3010; 2026/06/15 08:20-09:45=B3012; 2026/06/16 11:30-12:10=B3012; 2026/06/18 08:20-09:45=B3012; 2026/06/29 08:20-09:45=B3012 | All expected June slots found in live bookings. |
| English E-7 | CIE | Block E | CJI | Cordelia Jiao | Booked live | B4011, B4041 | 2026/06/11 08:20-09:45=B4011; 2026/06/12 08:20-09:00=B4011; 2026/06/15 08:20-09:45=B4011; 2026/06/16 11:30-12:10=B4011; 2026/06/18 08:20-09:45=B4041; 2026/06/29 08:20-09:45=B4041 | All expected June slots found in live bookings. |

