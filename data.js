// Seed data for the ergonomics program. Plain globals so the app also works
// when index.html is opened straight from disk (no server needed).

// Who is qualified to perform a home-office ergonomic assessment.
// "tier" drives the badge in the directory: expert > specialist > clinical.
var CREDENTIALS = [
  {
    code: "CPE",
    name: "Certified Professional Ergonomist",
    issuer: "Board of Certification in Professional Ergonomics (BCPE)",
    tier: "expert",
    requires: "Degree in ergonomics or a related field, several years of practice, and a comprehensive exam.",
    registry: "https://bcpe.org/find-a-professional/find-a-consultant/"
  },
  {
    code: "CHFP / AEP",
    name: "Certified Human Factors Professional / Associate Ergonomics Professional",
    issuer: "BCPE",
    tier: "expert",
    requires: "BCPE-issued; AEP is the early-career track toward CPE.",
    registry: "https://bcpe.org/find-a-professional/find-a-consultant/"
  },
  {
    code: "CEAS I–III",
    name: "Certified Ergonomics Assessment Specialist",
    issuer: "The Back School (Atlanta)",
    tier: "specialist",
    requires: "Tiered course plus exam. Level I covers office and industrial assessments using OSHA tools.",
    registry: "https://thebackschool.net/professional-directory/find-a-certified-professional"
  },
  {
    code: "CRESp",
    name: "Certified Remote Ergonomics Specialist",
    issuer: "Worksite International",
    tier: "specialist",
    requires: "For practitioners already certified in office ergonomics (CEAS, COESp, etc.). Focused on remote and home setups.",
    registry: "https://www.worksiteinternational.com/certified-remote-ergonomics-specialist"
  },
  {
    code: "COESp",
    name: "Certified Office Ergonomics Specialist",
    issuer: "Worksite International",
    tier: "specialist",
    requires: "Office ergonomics course plus exam.",
    registry: "https://www.worksiteinternational.com/online-ergonomics-certification-course"
  },
  {
    code: "PT / OT",
    name: "Licensed Physical or Occupational Therapist",
    issuer: "State licensing board",
    tier: "clinical",
    requires: "State license. Best for employees who already have pain or an injury. Look for one who also holds an ergonomics certification.",
    registry: ""
  }
];

// Organizations that assess remote/home workstations. Services are summarized
// from each provider's own site; confirm coverage and pricing before contracting.
var PROVIDERS = [
  {
    name: "Briotix Health (incl. Humantech)",
    url: "https://www.briotix.com/office-health-ergonomics/assessments",
    modes: ["virtual", "in-home"],
    coverage: "Nationwide / international",
    credentials: ["CPE", "PT / OT"],
    bestFor: "Large employers who want assessments, self-assessment software and training from one vendor",
    notes: "Onsite and virtual assessments with self-service tools and professional follow-up."
  },
  {
    name: "Pacific Ergonomics",
    url: "https://pacificergo.com/services/virtual-ergonomic-assessment/",
    modes: ["virtual", "in-home"],
    coverage: "Nationwide (U.S.)",
    credentials: ["CPE"],
    bestFor: "Assessment plus equipment installation at the employee's home",
    notes: "Virtual assessments, plus installation services anywhere in the U.S."
  },
  {
    name: "Ergo Global",
    url: "https://ergoglobal.com/service/ergonomics-assessments/",
    modes: ["virtual", "in-home"],
    coverage: "Nationwide / multi-location",
    credentials: ["CPE", "CEAS I–III"],
    bestFor: "Distributed teams that need a mix of in-person and virtual assessments",
    notes: "Individual workstation assessments for office, home and multi-site employees."
  },
  {
    name: "Ask Ergo Works",
    url: "https://askergoworks.com/pages/ergonomic-evaluations-assessements",
    modes: ["virtual"],
    coverage: "U.S., Canada, UK, India, UAE",
    credentials: ["CPE"],
    bestFor: "Global remote workforces",
    notes: "Assessments by certified ergonomists covering monitor, keyboard/mouse, seating, lighting and workflow."
  },
  {
    name: "Bay Area Ergonomics",
    url: "https://ergonomicsconsulting.com/nationwide-virtual-ergonomic-assessments",
    modes: ["virtual", "in-home"],
    coverage: "Nationwide by video; in person in the SF Bay Area",
    credentials: ["PT / OT"],
    bestFor: "Employees with existing pain who need a clinician's eye",
    notes: "Run by a licensed physical therapist."
  },
  {
    name: "The Rising Workplace, PLLC",
    url: "https://www.risingworkplace.com/home-office-ergonomics",
    modes: ["virtual"],
    coverage: "All U.S. states",
    credentials: ["PT / OT"],
    bestFor: "Home-office assessments bundled with remote training",
    notes: "Remote workstation assessments, training and workshops."
  },
  {
    name: "ErgoPlus",
    url: "https://ergo-plus.com/",
    modes: ["virtual"],
    coverage: "Nationwide",
    credentials: ["CPE"],
    bestFor: "Building an in-house ergonomics program with software and training",
    notes: "Software, training and consulting. More program-building than one-off assessments."
  }
];

// Registries for finding individual credentialed professionals near an employee.
var DIRECTORIES = [
  { name: "BCPE Find a Consultant (CPE, CHFP, AEP)", url: "https://bcpe.org/find-a-professional/find-a-consultant/" },
  { name: "The Back School: Find a Certified Professional (CEAS)", url: "https://thebackschool.net/professional-directory/find-a-certified-professional" },
  { name: "Puget Sound HFES consultant list", url: "https://www.pshfes.org/consultants" },
  { name: "NexGen Ergonomics consultants directory", url: "https://nexgenergo.com/ergocenter/directory.html" }
];

// Marketplace catalog. "fixes" lists the assessment findings each item addresses.
// Prices are typical street prices in USD. Final pricing comes from the vendor.
var FINDINGS = {
  "neck": "Neck strain / looking down at screen",
  "eyes": "Eye strain / glare",
  "back": "Low back pain / poor chair support",
  "wrist": "Wrist or forearm pain",
  "shoulder": "Shoulder tension / reaching",
  "legs": "Feet don't reach floor / leg pressure",
  "sedentary": "Sitting all day",
  "laptop": "Working only on a laptop"
};

var PRODUCTS = [
  { id: "chair",     category: "Seating",      name: "Fully adjustable task chair",           price: 450, fixes: ["back", "legs", "shoulder"], examples: "Steelcase Series 1, Herman Miller Sayl, HON Ignition" },
  { id: "lumbar",    category: "Seating",      name: "Lumbar support cushion",                price: 40,  fixes: ["back"],                     examples: "Everlasting Comfort, ObusForme" },
  { id: "footrest",  category: "Seating",      name: "Adjustable footrest",                   price: 45,  fixes: ["legs"],                     examples: "Fellowes, Humanscale FM300" },
  { id: "desk",      category: "Desks",        name: "Electric sit-stand desk",               price: 550, fixes: ["sedentary", "shoulder", "neck"], examples: "Uplift V2, Fully Jarvis, Ergotron WorkFit" },
  { id: "converter", category: "Desks",        name: "Sit-stand desk converter",              price: 250, fixes: ["sedentary"],                examples: "Ergotron WorkFit-TX, VariDesk" },
  { id: "kbtray",    category: "Desks",        name: "Under-desk keyboard tray",              price: 200, fixes: ["wrist", "shoulder"],        examples: "Humanscale 6G, Fellowes Office Suites" },
  { id: "mat",       category: "Desks",        name: "Anti-fatigue standing mat",             price: 60,  fixes: ["sedentary"],                examples: "Ergodriven Topo, Imprint" },
  { id: "monitor",   category: "Screens",      name: "24–27\" external monitor",              price: 200, fixes: ["neck", "eyes", "laptop"],   examples: "Dell P2425, LG 27UP" },
  { id: "arm",       category: "Screens",      name: "Monitor arm",                           price: 130, fixes: ["neck"],                     examples: "Ergotron LX, Humanscale M2.1" },
  { id: "laptopstand", category: "Screens",    name: "Laptop stand",                          price: 50,  fixes: ["neck", "laptop"],           examples: "Rain Design mStand, Roost" },
  { id: "lamp",      category: "Screens",      name: "Adjustable task lamp",                  price: 70,  fixes: ["eyes"],                     examples: "BenQ e-Reading, Humanscale Nova" },
  { id: "keyboard",  category: "Input",        name: "Split / ergonomic keyboard",            price: 110, fixes: ["wrist", "shoulder", "laptop"], examples: "Logitech Ergo K860, Microsoft Sculpt" },
  { id: "mouse",     category: "Input",        name: "Vertical ergonomic mouse",              price: 100, fixes: ["wrist"],                    examples: "Logitech MX Vertical, Lift" },
  { id: "headset",   category: "Input",        name: "Wireless headset",                      price: 120, fixes: ["neck", "shoulder"],         examples: "Jabra Evolve2, Poly Voyager" },
  { id: "install",   category: "Services",     name: "In-home delivery & installation",       price: 150, fixes: [],                           examples: "Offered by some assessment providers" },
  { id: "followup",  category: "Services",     name: "30-day follow-up re-assessment",        price: 95,  fixes: [],                           examples: "Virtual check with the original assessor" }
];
