# Energy-sector security startup: strategy memo

**Date:** 2026-09-21
**Status:** Decision memo. Supersedes the unverified version of this plan.

This memo closes out the open items flagged in the earlier CESER conversation. Every
regulatory date, competitor claim, and funding figure below was checked against a public
source on 2026-09-21; the ones that could not be verified are listed explicitly in
`assumptions.md` rather than silently carried forward.

One recommendation changed as a result. Two got stronger.

---

## 1. Headline

**Lead with the compliance-monitoring business for small utilities (previously "Option A").**
Verification made it stronger on both sides of the equation: the regulatory scope grew,
and a federal program is actively putting purchase money into the exact customers who
otherwise have no budget.

**Do not build the DER attestation product as originally framed (previously "Option B").**
The visible competitor is materially better positioned than assumed — it is a spinoff of
the standards body whose standard the product would attest against, with the relevant
national-lab researcher as CTO. Competing on certification means competing with the people
who write the certification. There is still an opening next to it, described in §5.

---

## 2. What the regulation actually says now

### CIP-015 (internal network security monitoring) — confirmed, and broader than we thought

- CIP-015-1 was approved by FERC on 2025-06-26, published in the Federal Register
  2025-07-02, and became effective **2025-09-02**.
- Compliance dates confirmed: **2028-10-01** for high- and medium-impact BES Cyber Systems
  with external routable connectivity in control centers and backup control centers;
  **2030-10-01** for all other medium-impact systems with ERC.
- **CIP-015-2 has already been filed.** NERC submitted it to FERC on **2026-06-18** under
  Docket No. RD26-6-000 — earlier than the "by September 2026" we had assumed. It passed
  final ballot 2026-03-05 at 86.93% approval, 91.58% quorum (initial ballot 2026-01-20 at
  84.33%).
- CIP-015-2's scope expansion is bigger than "EACMS and PACS outside the ESP." The drafting
  team (Project 2025-02) also pulled in **Shared Cyber Infrastructure (SCI)** and used the
  term *Cyber Systems* in the requirement language, specifically so that INSM coverage
  follows virtualized and shared-storage environments.

Why this matters commercially: the addressable footprint per utility is larger than a
perimeter-only reading suggests, and it now includes the virtualized infrastructure that
smaller utilities are consolidating onto. The deadline is far enough out (2028) that
procurement conversations start in 2027 — which is the right lead time for a product
started now.

### Everything else

The rest of the regulatory picture from the earlier conversation (TSA pipeline directives,
IEC 62443, SBOM expectations, the FERC Computational Load Entity class) was not
re-verified and should be treated as unconfirmed. See `assumptions.md`.

---

## 3. The demand-side fact we were missing: RMUC

The standing objection to selling security software to electric cooperatives and municipal
utilities is that they have no budget. That is less true right now than at any point before
or, plausibly, after.

- The **Rural and Municipal Utility Advanced Cybersecurity Grant and Technical Assistance
  (RMUC) Program** is a CESER program authorized by the Bipartisan Infrastructure Law at
  **$250 million over five years**, aimed at electric cooperatives, municipal utilities, and
  small investor-owned utilities.
- Its Advanced Cybersecurity Technology (ACT) funding explicitly covers **direct support for
  utilities to invest in cybersecurity technologies, tools, and training** — i.e. money to
  buy products, not just to do research.
- DOE has announced **$80 million supporting more than 400 electric co-ops**, and much of
  that has not yet been released to award winners.

Two implications, pulling in opposite directions:

1. **Positive:** there is a named, funded, identifiable list of small utilities with
   cybersecurity money to spend and a federal mandate arriving in 2028. That is an unusually
   legible early market.
2. **Timing risk:** the program is authorized *through FY2026*. A bipartisan Senate bill
   (Hickenlooper, Cortez Masto, Curtis, Hoeven, McCormick) has been introduced to strengthen
   and extend rural/municipal utility cybersecurity support, but reauthorization is not
   assured. If the money lapses, the long tail goes back to having no budget, and this
   market gets materially harder.

Treat the RMUC cohort as the beachhead and move while the money is moving.

---

## 4. CESER's own posture, and the startup on-ramp we did not know about

### The strategic plan gives a commercialization commitment

CESER published its **FY2026–2030 Strategic Plan in February 2026**, organized around three
goals: develop world-class security technologies, harden U.S. energy infrastructure, and
respond to and recover from incidents. Reporting on the plan highlights an explicit
emphasis on **supply chain cybersecurity** and **AI-driven security tools**, and — most
usefully — a stated commitment under Goal 1 to **complete at least two new technology
solutions for private-sector adoption each year through 2030**.

That last item is a standing, published intent to hand lab technology to commercial
partners. It is the strongest available argument for approaching the labs now rather than
waiting until there is a product to show.

### SENTRY is the direct startup path

We did not know this existed. **Securing ENergy Technology ResiliencY (SENTRY)** is a CESER
opportunity announcement run through Connectwerx (CWX-024-CESER) that solicits proposals
**specifically from commercial technology startups**. Its four focus areas:

1. Energy risk quantification
2. Cybersecurity for industrial control systems
3. **Cybersecurity of decentralized asset management systems** (i.e. DER)
4. Counter-drone capabilities

Timeline of the round just completed: submissions closed **2025-12-01**; award recipients
were announced **2026-09-14** — one week before this memo. Winners were **Frenos**
(automated conversion of threat intelligence into energy-specific attack chains, executed
across substations and distributed resources, with remediation prioritization),
**Raptor Dynamix** (Grid Guardian, counter-UAS), and **Bastazo** (cyber-informed
engineering risk quantification).

Three things to take from this:

- The submission-to-award cycle was roughly **nine months**. Plan accordingly; this is free
  money, not a runway.
- Two of the four focus areas map onto the businesses under consideration here.
- The round just closed, which is the *best* time to build a submission for the next one.
  Confirming whether another round is planned is the highest-value single question to ask.

Other CESER funding visible in the same period, for context: a **$39M** DER cybersecurity
research announcement, a **$30M** announcement for cyber tools protecting clean energy
infrastructure, and a **$10M** Next Generation Academia-Based Cyber RD&D NOFO.

---

## 5. The DER recommendation, revised

The DER thesis was right about the market and wrong about the competition.

### What confirmed the market

- **UL 2941** was published in April 2023, developed with the national renewable energy lab,
  covering PV inverters, EV chargers, wind turbines, and fuel cells, with testable
  requirements spanning access management, cryptography, sensitive-data handling, and
  documentation.
- In **February 2026** UL Solutions **launched the certification program** for microgrids and
  inverter-based devices, complementing (not replacing) UL 1741 safety testing. The standard
  is no longer just a document; there is now a live certification business attached to it.
- **SolarSnitch** is real, Sandia-developed, and *currently in commercialization*: CESER and
  the Solar Energy Technologies Office put **$490,000** into it under the FY2024 Technology
  Commercialization Fund CLIMR lab call, funding a **24-month** maturation program with
  real-world ML testing. The licensing conversation is timely right now, not hypothetical.

### What killed the original framing

**DER Security Corp (DERSec)** is not a generic seed-stage competitor:

- Founded **2022 as a spinoff of the SunSpec Alliance** — the trade alliance whose Modbus
  profile and certification work the DER industry runs on.
- CEO **Tom Tansy** (SunSpec), CTO **Jay Johnson** (Sandia National Labs — the DER
  cybersecurity research lineage, the same institution behind SolarSnitch), CFO
  **Venkat Prabhala**.
- Product is squarely the thing we described: continuous monitoring across DER endpoints,
  protocol-aware detection with deep packet inspection, automated regulatory alignment.
- Named partner in a DOE-funded project alongside **Palo Alto Networks, Southern California
  Edison, NRECA, Tucson Electric Power, AWS, and the University of New Mexico**.

A product whose moat is "produces certification and supply-chain attestation evidence"
cannot beat the organization that co-owns the certification regime and employs the lab
researcher. That was the moat we proposed. It is gone.

### What DERSec has not got

Capital. Public records show a **$200K grant (OSTI, 2024-07-22)** and backing from Blu
Venture Investors — no large institutional round is visible. They hold the standards seat
with a small balance sheet.

### The opening that remains

Not certification attestation. **Fleet operations for mixed-vendor DER** — the aggregator's
and utility's problem of running thousands of inverters from different OEMs, firmware
vintages, and communication stacks, where the questions are operational ("which of these
6,000 devices is behaving abnormally, and can I curtail safely?") rather than conformance
("does this device meet UL 2941?"). DERSec's standards position is an advantage in
conformance and a neutral in operations.

Treat this as an adjacency to revisit, not the opening move — and note that DERSec's thin
capitalization makes them a plausible *partner* or acquisition target rather than only a
rival.

---

## 6. Recommended sequence

1. **Build for CIP-015 in the long tail.** Passive INSM sensor plus auto-generated audit
   evidence for CIP-015 / CIP-007 / CIP-010, priced for a 40-person cooperative. The
   evidence-generation half remains the moat: incumbents sell detection, and the customers'
   loudest pain is proving compliance without weeks of manual work.
2. **Target the RMUC cohort first.** 400+ named co-ops with federal money in hand and a 2028
   deadline. Move while the authorization holds.
3. **Prepare a SENTRY submission** against focus area 2 (ICS cybersecurity), and confirm
   whether a next round is opening. Nine-month cycle; treat it as validation and
   non-dilutive cash, not revenue.
4. **Open the lab-licensing conversation now**, on the strength of CESER's published
   commitment to move two technologies per year into private-sector hands.
5. **Hold the DER fleet-operations idea** as a second act, informed by whether DERSec raises.

---

## 7. Revised asks for the McClure conversation

Sharper than the generic version, and all answerable without asking him to steer money or
disclose anything non-public:

- **"Is there another SENTRY round, and when?"** The one that just announced awards on
  September 14 is the clearest on-ramp CESER has for startups, and the timing question is
  purely procedural.
- **"The strategic plan commits to two technologies into private-sector adoption per year
  through 2030 — what's in that pipeline for grid monitoring?"** He can answer this from the
  published plan, and the answer is a shortlist of licensable technology.
- **"Who at Sandia should I talk to about where SolarSnitch goes after the CLIMR
  maturation?"** Specific, public, and an introduction rather than a favor.
- **"Is RMUC going to be reauthorized past FY2026?"** He may not know, but the answer
  determines whether the long-tail market has a budget in 2027.
- **"What are co-ops in the RMUC cohort actually buying with the money, and what are they
  failing to find?"** This is the "ask for problems, not opportunities" question, aimed at a
  cohort whose purchasing CESER can see and outsiders cannot.

Unchanged guidance: do not pitch, do not ask him to move money, do not name-drop him.
Government ethics rules constrain what he can do for a personal contact, and the durable
version of this relationship is informal advisor to something that already works.

---

## 8. Honest caveats

- This remains a **5–7 year path**. Utility sales cycles of 6–18 months are unchanged by
  anything above.
- Option A is a **cash-flow business, not an acquisition story**. Verification made it more
  likely to work and no more likely to make anyone rich quickly.
- The **RMUC authorization cliff at FY2026** is the single largest risk to the recommended
  plan, and it is outside our control.
- Several load-bearing facts are still unverified — notably the current DOE SBIR topic list,
  whose source pages were unreachable from this environment. See `assumptions.md` before
  designing to any of them.

---

## Sources

- [NERC petition for approval of CIP-015-2 (Docket RD26-6-000)](https://www.nerc.com/globalassets/who-we-are/legal--regulatory/filings--orders/nerc-filings-to-ferc/2026/petition-for-approval-of-cip-015-2_signed.pdf)
- [Dragos — NERC CIP-015-2: EACMS, PACS, SCI Monitoring Explained](https://www.dragos.com/blog/nerc-cip-015-eacms-pacs-sci-monitoring-explained)
- [Dragos — NERC CIP-015-1 Is Approved: What Asset Owners Need to Do](https://www.dragos.com/blog/nerc-cip-015-is-approved-what-asset-owners-need-to-do)
- [Covington Inside Privacy — FERC Finalizes New INSM Requirements](https://www.insideprivacy.com/critical-infrastructure/ferc-finalizes-new-internal-network-security-monitoring-requirements-for-bulk-electric-systems/)
- [Nozomi Networks — Preparing for NERC CIP-015-1](https://www.nozominetworks.com/blog/preparing-for-nerc-cip-015-1-internal-network-security-monitoring-for-electric-utilities)
- [DOE — Rural and Municipal Utility Advanced Cybersecurity Grant and Technical Assistance Program](https://www.energy.gov/ceser/rural-and-municipal-utility-advances-cybersecurity-grant-and-technical-assistance-program)
- [Nozomi Networks — How to Tap DOE Cybersecurity Funds for Rural, Municipal & Small Investor-Owned Utilities](https://www.nozominetworks.com/blog/how-to-tap-doe-cybersecurity-funds-for-rural-municipal-small-investor-owned-utilities)
- [America's Electric Cooperatives — Kentucky Co-op Leader to Congress](https://www.electric.coop/kentucky-co-op-leader-to-congress-federal-investment-crucial-to-securing-grid)
- [Sen. Hickenlooper — Bipartisan Bill to Strengthen Cybersecurity for Rural, Municipal Utilities](https://www.hickenlooper.senate.gov/press_releases/hickenlooper-cortez-masto-curtis-hoeven-mccormick-hoeven-introduce-bipartisan-bill-to-strengthen-cybersecurity-for-rural-municipal-utilities/)
- [MeriTalk — DOE's CESER Unveils 2026-2030 Strategy](https://www.meritalk.com/articles/does-ceser-unveils-2026-2030-strategy-to-bolster-energy-security/)
- [ExecutiveGov — DOE CESER Unveils First Strategy Plan](https://www.executivegov.com/articles/doe-ceser-strategy-plan-energy-security)
- [Connectwerx — CWX-024-CESER: Securing ENergy Technology ResiliencY (SENTRY)](https://www.connectwerx.org/portfolio-items/cwx-024-ceser-securing-energy-technology-resiliency-sentry/)
- [Industrial Cyber — DOE announces $30 million for cybersecurity tools to protect clean energy infrastructure](https://industrialcyber.co/utilities-energy-power-water-waste/doe-announces-30-million-funding-for-cybersecurity-tools-to-protect-clean-energy-infrastructure/)
- [UL Solutions — Distributed Energy and Inverter-Based Resources Cybersecurity Certification Requirements](https://www.ul.com/news/ul-solutions-and-nrel-announce-distributed-energy-and-inverter-based-resources-cybersecurity)
- [UL Solutions — First Certification Program to Advance Microgrid Cybersecurity and Safety](https://www.ul.com/news/ul-solutions-launches-first-certification-program-advance-microgrid-cybersecurity-and-safety)
- [PV Tech — UL Solutions releases cybersecurity certification programme for PV inverters](https://www.pv-tech.org/ul-solutions-releases-cybersecurity-certification-programme-for-pv-inverters/)
- [Utility Dive — NREL, UL publish requirements for a new DER cybersecurity standard](https://www.utilitydive.com/news/nrel-ul-2941-DERMS-cybersecurity-standard/648378/)
- [Industrial Cyber — DOE debuts SolarSnitch technology](https://industrialcyber.co/threats-attacks/doe-debuts-solarsnitch-technology-to-boost-cybersecurity-in-solar-energy-systems/)
- [Renewable Energy World — The SolarSnitch is here to save DERs from cyber-attacks](https://www.renewableenergyworld.com/solar/the-solarsnitch-is-here-to-save-ders-from-cyber-attacks/)
- [DER Security Corp — About](https://dersec.io/about/)
- [DER Security Corp — Team](https://dersec.io/team/)
- [Blu Venture Investors — DER Security](https://www.bluventureinvestors.com/cyber/der-security)
- [Tracxn — DER Security Corp company profile](https://tracxn.com/d/companies/der-security-corp/__Q0RjKplHaluGev1wW6pA3GHu9U9dlcY6WVe4duultlg)
- [Crunchbase News — So Far, 2026 Is A Solid Year For Cybersecurity Startup Funding](https://news.crunchbase.com/cybersecurity/solid-startup-venture-funding-growth-h1-2026/)
