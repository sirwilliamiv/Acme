# Assumption ledger

**Last checked:** 2026-09-21

What in the strategy is verified, what changed when checked, and what is still standing on
an unverified claim. Re-check anything in §3 before designing to it or putting money behind
it.

---

## 1. Verified — carried forward unchanged

| Claim | Status |
|---|---|
| CIP-015-1 approved by FERC 2025-06-26, effective 2025-09-02 | Confirmed |
| INSM compliance dates 2028-10-01 (high/medium w/ ERC, control centers) and 2030-10-01 (other medium w/ ERC) | Confirmed |
| UL 2941 exists, published April 2023, developed with the national renewable energy lab | Confirmed |
| UL 2941 covers PV inverters, EV chargers, wind turbines, fuel cells | Confirmed |
| SolarSnitch is DOE/Sandia technology, CESER co-funded with the Solar Energy Technologies Office | Confirmed |
| CESER funds startups and has an SBIR track record (annual awards since 2018) | Confirmed |
| Incumbent consolidation in OT detection (Dragos, Claroty, Nozomi/Mitsubishi) | Not re-verified this pass, but unchanged from prior reporting; low risk |

## 2. Changed on verification — strategy updated

| We assumed | Actually |
|---|---|
| CIP-015-2 "due to be submitted by 2026-09-02" | Already filed **2026-06-18**, Docket RD26-6-000. Final ballot passed 2026-03-05 (86.93% / 91.58% quorum) |
| CIP-015-2 extends INSM to EACMS and PACS | Also adds **Shared Cyber Infrastructure (SCI)** and uses "Cyber Systems" in requirement language, to cover virtualized/shared-storage environments |
| Small co-ops are underserved because they have no budget | They have **RMUC** money: $250M BIL authorization, $80M announced for 400+ co-ops, ACT funding explicitly covers buying tools. Budget exists *now* |
| DER security competition is "seed-stage, DERSec the visible pure-play" | DERSec is a **SunSpec Alliance spinoff** (2022) with **Jay Johnson (Sandia)** as CTO and **Tom Tansy (SunSpec)** as CEO, partnered with Palo Alto Networks, SCE, NRECA, Tucson Electric Power, AWS, UNM on a DOE project. Capitalization is still thin ($200K OSTI grant 2024-07-22; Blu Venture Investors) |
| UL 2941 certification is an emerging signal | The **certification program launched February 2026** for microgrids and inverter-based devices. Live, not emerging |
| SolarSnitch is lab tech that might be licensable | In an active **24-month commercialization maturation** under FY2024 TCF CLIMR, $490K from CESER + SETO |
| CESER's startup path is SBIR and FOAs | Also **SENTRY** (Connectwerx CWX-024-CESER), aimed explicitly at commercial startups. Round closed 2025-12-01, awards announced **2026-09-14** to Frenos, Raptor Dynamix, and Bastazo |

## 3. Still unverified — do not design to these

| Claim | Why it's open | How to close it |
|---|---|---|
| Current DOE SBIR FY2026 Phase I topic list and deadlines | Source pages (energy.gov, the OSTI topics PDF) were **blocked by this environment's network egress proxy** | Go to science.osti.gov/sbir directly |
| Whether another SENTRY round is planned, and its dates | Connectwerx page blocked by egress proxy | connectwerx.org, or ask directly |
| Open CESER FOAs as of today | energy.gov blocked | energy.gov/ceser, netl.doe.gov solicitations, grants.gov |
| RMUC reauthorization past FY2026 | Bill introduced, outcome unknown | Track the Hickenlooper/Cortez Masto bill |
| DERSec's current headcount and any undisclosed round | PitchBook/Tracxn profiles are paywalled | Direct research before committing to any DER product |
| TSA pipeline security directive current versions | Not checked this pass | TSA primary sources |
| IEC 62443 posture, CISA SBOM minimum elements refresh, EU CRA reporting start 2026-09-11 | Not checked this pass | Primary sources |
| FERC "Computational Load Entity" class created July 2026, standards due end of 2026 | Not checked this pass | FERC dockets |
| Price point of $30–80K/yr for a 40-person co-op | Estimate only, never validated against a real quote | Customer conversations |
| 6–18 month utility sales cycle | Conventional wisdom, not measured | Customer conversations |

## 4. Environment note

`energy.gov`, `connectwerx.org`, and several other primary-source domains are blocked by the
network egress proxy in the session this research ran in. Everything sourced from those
domains below the search-summary level is therefore second-hand. The claims that depend on
them are flagged in §3 above rather than presented as verified.
