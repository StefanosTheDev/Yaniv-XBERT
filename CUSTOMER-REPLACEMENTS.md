# Customer Replacement Suggestions

Status: **DRAFT — for review only. No site copy has been changed yet.**

This document maps every current customer / quoted person you flagged to its proposed replacement, lists every file + line where they appear today, and suggests an updated business category and short narrative. Once you sign off, we'll apply the changes.

A few cross-cutting notes are at the bottom (see "Open questions" — please review before we implement).

---

## 1. Bright Smile Dental → BrainDoc LA

| Field | Current | Suggested |
|---|---|---|
| Business | Bright Smile Dental | BrainDoc LA |
| Tag (proof card) | Multi-location dental | Multi-location neurology *(or: Brain health clinic — please confirm)* |
| Industry page | Healthcare | Healthcare |
| Spokesperson | *(unattributed in featured story)* | **Dr. Moshe-Samuel Hendizadeh**, Owner |
| Featured headline | "Bright Smile Dental: how three locations stopped missing the lunch-hour rush." | "BrainDoc LA: how three locations stopped missing the lunch-hour rush." *(narrative may need to shift away from "after-hours bookings" / "patients in the chair" toward neurology-appropriate language — see below)* |

**Where it appears today**
- `components/legacy/customer-stories.html:44` — featured case-study headline + narrative + KPIs
- `components/legacy/industry-healthcare.html:254` — proof card "Bright Smile Dental"
- `components/legacy/index.html:696` — homepage setup-step chip ("Greet the caller with **Bright Smile Dental**")
- `components/legacy/index-old.html:798` — same chip in the legacy/old homepage (likely safe to update for consistency)
- `components/legacy/ai-receptionist.html:170` — demo line "Hi, this is XBert at **Bright Smile Dental**. How can I help?"
- `components/legacy/ai-employee.html:355` — control-panel sample value "Bright Smile Dental, this is XBert."
- `components/legacy/agent-assist.html:186` — citation source "**Bright Smile Dental** Handbook · v3.2"

**Suggested narrative (proof card)**
> "A 3-location neurology practice put XBert on every patient line. Within 60 days, after-hours bookings tripled and the front desk stopped fielding lunch-hour overflow." *(KPI "+38% more appointments booked, same headcount" still works)*

**Open questions**
- Confirm BrainDoc LA's category (neurology, neuro-rehabilitation, brain-health, etc.) so we set the proof-card tag and narrative correctly.
- Featured-story narrative currently mentions "the patient in the chair" — that's a dental phrase. Suggest swapping for "the patient in the room" or similar.

---

## 2. Fern & Forge → Woven  (https://www.woven.is)

| Field | Current | Suggested |
|---|---|---|
| Business | Fern & Forge | Woven |
| Tag (proof card) | Apparel DTC | *(please confirm — woven.is appears to be a textile / lifestyle brand, so "Apparel DTC" or "Lifestyle DTC" likely still fit)* |
| Industry page | Retail & E-commerce | Retail & E-commerce |
| Spokesperson | **Priya Mehta**, Head of CX | **Ben Moradzadeh**, Manager |
| Featured headline | "Fern & Forge: a calm Black Friday for the first time ever." | "Woven: a calm Black Friday for the first time ever." |

**Where it appears today**
- `components/legacy/customer-stories.html:67` — featured case-study headline + narrative + KPIs
- `components/legacy/industry-retail-ecommerce.html:98` — pillar quote ("Priya Mehta · Head of CX, Fern & Forge")
- `components/legacy/industry-retail-ecommerce.html:254` — proof card "Fern & Forge"

**Suggested narrative (proof card)**
> "A boutique apparel brand replaced its WISMO inbox with XBert and freed its 4-person CX team to handle VIPs, sizing consults, and proactive outreach." *(works as-is if Woven sells apparel/textiles)*

**Open questions**
- "Manager" is a fairly generic title. Want us to use "Manager" or upgrade to "Operations Manager" / "CX Manager" to match the others (VP, Director, etc.)?
- Pillar quote on `industry-retail-ecommerce.html` is currently attributed to **Priya Mehta**, not anyone in your replacement list. Replace with Ben Moradzadeh or leave as-is?

---

## 3. Riley Tran (Harbor & Hill Realty) → Shai Abishoor (House of Shoor)

| Field | Current | Suggested |
|---|---|---|
| Business | Harbor & Hill Realty | House of Shoor |
| Tag (proof card) | Boutique brokerage | Boutique brokerage *(or: Luxury real estate — please confirm)* |
| Industry page | Real Estate | Real Estate |
| Spokesperson | **Riley Tran**, Team Lead | **Shai Abishoor**, Founder |

**Where it appears today**
- `components/legacy/customer-stories.html:93` — band quote "Riley Tran · Team Lead, Harbor & Hill Realty"
- `components/legacy/industry-real-estate.html:98` — pillar quote "Riley Tran · Team Lead, Harbor & Hill Realty"
- `components/legacy/industry-real-estate.html:255` — proof-card business name "Harbor & Hill Realty"
- `components/legacy/industry-real-estate.html:262` — proof-card attribution "Riley Tran / Team Lead"

**Suggested narrative (proof card)**
> "A boutique brokerage put XBert on every web form and missed call. Showings up, agent attention focused on the buyers ready to write." *(works as-is)*

**Open questions**
- Title shifts from "Team Lead" to "Founder," so the narrative ("a 14-agent boutique") may need a tweak — e.g., "the founder-led boutique." Confirm.

---

## 4. Sandra Holm (Summit Insurance) → Navid Bayanfar (KBHB)

| Field | Current | Suggested |
|---|---|---|
| Business | Summit Insurance | KBHB |
| Tag (proof card) | Auto + Home carrier | *(please confirm — what does KBHB do? is it still insurance?)* |
| Industry page | Insurance | Insurance *(unless KBHB is a different industry — see below)* |
| Spokesperson | **Sandra Holm**, VP Operations | **Navid Bayanfar**, Co-founder |

**Where it appears today**
- `components/legacy/customer-stories.html:97` — band quote "Sandra Holm · VP Operations, Summit Insurance"
- `components/legacy/industry-insurance.html:98` — pillar quote
- `components/legacy/industry-insurance.html:255` — proof-card business name "Summit Insurance"
- `components/legacy/industry-insurance.html:262` — proof-card attribution

**Suggested narrative (proof card, if KBHB is insurance)**
> "A regional carrier put XBert on every policyholder line. First-call resolution jumped, agents opened up capacity for binding new business."

**Open questions**
- We need to know what KBHB does. Insurance? If not, the entry no longer fits the Insurance industry page and we should decide whether to (a) drop this entry from the insurance page and place it elsewhere, or (b) reword to something industry-appropriate.
- Title goes from "VP Operations" → "Co-founder" — narrative ("a regional auto + home carrier") will need a re-write because Co-founders typically describe their company differently.

---

## 5. Lisa Bryant (Wayne & Bryant LLP) → Milana Shimanova (Milana Shimanova PLLC) **— see conflict below**

You gave **two** different replacements for Lisa Bryant in the same list:

- "Replace **Lisa Bryant** with **Milana Shimanova**, Partner at Milana Shimanova PLLC"
- "Replace **Wayne & Bryant LLP** with **Hotel Injury Law** and replace **Lisa Bryant** with **Ilan Rosen Janfaza**"

In the current site, **every** Lisa Bryant reference is tied to Wayne & Bryant LLP — see item #10 for the full list. So we can do exactly one of:

- **Option A** — Apply the Wayne & Bryant → Hotel Injury Law / Ilan Rosen Janfaza replacement everywhere (item #10 below). Drop Milana Shimanova from this round.
- **Option B** — Use Milana Shimanova at Milana Shimanova PLLC for all current Lisa Bryant slots, and drop Hotel Injury Law / Ilan Rosen.
- **Option C** — Split: keep Wayne & Bryant card → Hotel Injury Law / Ilan Rosen, and use Milana Shimanova somewhere new (e.g., as a fresh quote we add). This needs you to point at where she should go.

**Please pick A, B, or C before we touch this one.**

---

## 6. Vega Pediatrics → Elihu Institute for Pain Management

| Field | Current | Suggested |
|---|---|---|
| Business | Vega Pediatrics | Elihu Institute for Pain Management |
| Tag (proof card) | Pediatric clinic | **Pain Management** *(per your note)* |
| Industry page | Healthcare | Healthcare |
| Spokesperson | **Marcus Vega, M.D.**, Founder | **Dr. Josh Elihu**, Founder |

**Where it appears today**
- `components/legacy/customer-stories.html:113` — proof-card name + 117 attribution
- `components/legacy/industry-healthcare.html:145` — pillar quote "Marcus Vega, M.D. · Vega Pediatrics"
- `components/legacy/industry-healthcare.html:266` — proof-card name + 273 attribution

**Suggested narrative (proof card)**
> "A pain-management practice handles spike-of-the-week consults without putting patients on hold. XBert triages, books same-day slots, and routes acute cases in seconds." *(KPI "12 sec average emergency-keyword transfer time" still works conceptually)*

**Open questions**
- The current quote — *"Parents called us at 2am. We answered. That has changed how families talk about us."* — is pediatrics-specific. Suggest: *"Patients called us at 2am. We answered. That has changed how they talk about us."* Confirm.
- The current pillar quote — *"I was worried about a robot answering my patients. We trained XBert in an afternoon. Now patients say it sounds like Sarah at the desk."* — works as-is with names swapped.

---

## 7. Cho & Co. Realty → Wolf Luxury Estates

| Field | Current | Suggested |
|---|---|---|
| Business | Cho & Co. Realty | Wolf Luxury Estates |
| Tag (proof card) | Multi-office franchise | Luxury real estate *(suggested — please confirm)* |
| Industry page | Real Estate | Real Estate |
| Spokesperson | **Janelle Cho**, Broker/Owner | **Daniel Dahan**, Broker/Owner |

**Where it appears today**
- `components/legacy/customer-stories.html:122` — proof-card name + 126 attribution
- `components/legacy/industry-real-estate.html:146` — pillar quote "Janelle Cho · Broker/Owner, Cho & Co."
- `components/legacy/industry-real-estate.html:267` — proof-card name + 274 attribution

**Suggested narrative (proof card)**
> "A luxury brokerage uses XBert to route high-intent leads by neighborhood and language. Agents come in to a calendar of qualified, pre-routed showings."

**Open questions**
- Existing proof card claims "a 6-office team … 27 sec average lead response time." Keep the "6-office" detail or reframe (e.g., "a luxury brokerage")?

---

## 8. Northpath Counseling → Sofer MD

| Field | Current | Suggested |
|---|---|---|
| Business | Northpath Counseling | Sofer MD |
| Tag (proof card) | Behavioral health | **Plastic Surgery** *(per your note)* |
| Industry page | Healthcare | Healthcare |
| Spokesperson | **Renee Adler**, Director of Operations | **Dr. Eli Sofer**, Owner |

**Where it appears today**
- `components/legacy/customer-stories.html:131` — proof-card name + 135 attribution
- `components/legacy/industry-healthcare.html:278` — proof-card name + 285 attribution

**Suggested narrative (proof card)**
> "A plastic-surgery practice handles inbound consult requests securely after hours. XBert collects insurance, screens fit, and books the right specialist without ever taking a clinical question."

**Open questions**
- Existing quote — *"It is the only AI we have trusted with intake. The audit log is what got our compliance team there."* — works fine for plastic surgery. Confirm.
- "after-hours intake conversion vs. voicemail (4.7×)" KPI also fine.

---

## 9. Loom & Linen → Reforming Pilates

| Field | Current | Suggested |
|---|---|---|
| Business | Loom & Linen | Reforming Pilates |
| Tag (proof card) | Home goods | **Pilates Studio** *(per your note)* |
| Industry page | Retail & E-commerce / Customer Stories | **⚠ probably needs to move** — Pilates is not retail |
| Spokesperson | **Naomi Brooks**, CX Director | **Genevieve Ross**, CEO |

**Where it appears today**
- `components/legacy/customer-stories.html:140` — proof-card name + 144 attribution
- `components/legacy/industry-retail-ecommerce.html:146` — pillar quote "Naomi Brooks · CX Director, Loom & Linen"
- `components/legacy/industry-retail-ecommerce.html:266` — proof-card name + 273 attribution

**Suggested narrative (proof card)**
> "A boutique pilates studio uses XBert to handle scheduling, class swaps, and intake in five languages. Front desk freed up to teach and greet."

**Open questions** *(important)*
- This one is a real industry shift: a pilates studio doesn't fit the **Retail & E-commerce** industry page or the *"home goods"* and *"sizing/color/care"* narrative on it. Options:
  - **9a.** Drop the Retail page references entirely and only show Reforming Pilates on the generic Customer Stories page.
  - **9b.** Replace with a different, retail-shaped customer for Retail page slots and use Reforming Pilates only where industry-neutral (hospitality? fitness? small biz?).
  - **9c.** Re-classify the Retail & E-commerce industry page section header to something broader like "Service & retail" so Pilates fits.
- Existing CSAT / "9× viral spike" KPI doesn't fit a pilates studio at all — we'd need a new KPI. Suggested: **"~22 hrs/wk front-desk time reclaimed"** or similar.

---

## 10. Wayne & Bryant LLP → Hotel Injury Law  +  Lisa Bryant → Ilan Rosen Janfaza

| Field | Current | Suggested |
|---|---|---|
| Business | Wayne & Bryant LLP | Hotel Injury Law |
| Tag (proof card) | Personal injury law | Personal injury law *(stays)* |
| Industry page | Professional Services | Professional Services |
| Spokesperson | **Lisa Bryant**, Partner | **Ilan Rosen Janfaza**, Partner *(or Founder — please confirm title)* |

**Where it appears today**
- `components/legacy/customer-stories.html:101` — band quote "Lisa Bryant · Partner, Wayne & Bryant LLP"
- `components/legacy/customer-stories.html:149` — proof-card "Wayne & Bryant LLP" + 153 attribution
- `components/legacy/industry-professional-services.html:53` — hero demo "I'll book you a consult with **Lisa Bryant** tomorrow at 10am — she handles auto cases."
- `components/legacy/industry-professional-services.html:98` — pillar quote "Lisa Bryant · Partner, Wayne & Bryant LLP"
- `components/legacy/industry-professional-services.html:115` — animated chip "Routed to **Lisa Bryant** (auto practice)"
- `components/legacy/industry-professional-services.html:255` — proof-card "Wayne & Bryant LLP" + 262 attribution

**Suggested narrative (proof card)**
> "A personal-injury firm focused on hotel and hospitality cases uses XBert as the after-hours intake line. Senior partners walk into the office with a clean intake on every consult." *(KPI "+34% consult-to-engagement conversion" still works)*

**Open questions**
- Title: you sent "Ilan Rosen Janfaza" with no title. Default to **Partner** to match Lisa Bryant? Or **Founder**?
- Hero demo says "she handles auto cases." If Hotel Injury Law specializes in *hotel* injuries, that copy should change to e.g. "he handles hotel-injury cases." Confirm.
- See conflict in item #5 above.

---

## 11. Mariner Mutual → Black Llama  +  David Reilly → Eli Natan

| Field | Current | Suggested |
|---|---|---|
| Business | Mariner Mutual | Black Llama |
| Tag (proof card) | Independent agency | *(please confirm — is Black Llama an insurance agency or a different industry?)* |
| Industry page | Insurance | Insurance *(only if Black Llama is insurance — otherwise needs to move)* |
| Spokesperson | **David Reilly**, Head of Compliance | **Eli Natan**, CEO |

**Where it appears today**
- `components/legacy/customer-stories.html:158` — proof-card name + 162 attribution
- `components/legacy/industry-insurance.html:146` — pillar quote "David Reilly · Head of Compliance, Mariner Mutual"
- `components/legacy/industry-insurance.html:267` — proof-card name + 274 attribution

**Suggested narrative (proof card, if Black Llama is insurance)**
> "An independent agency cleared a 3,000-call renewal backlog in three weeks. XBert called every policyholder, confirmed contact, and rebooked lapsed renewals." *(works as-is)*

**Open questions**
- Title shifts from "Head of Compliance" → "CEO." The current pillar quote — *"Compliance signed off in two weeks. The audit log was the deciding factor — every word XBert said is reviewable."* — sounds odd in a CEO's voice. Suggested rewrite: *"Compliance signed off in two weeks. The audit log was the deciding factor for our team — every word XBert said is reviewable."* Confirm.
- If Black Llama isn't insurance, this entry can't stay on the Insurance industry page; we'd need to swap in something else there.

---

## 12. Jordan Mosley (Riverstone Outdoors) → Meir Zenati (Tabarka Studio)

| Field | Current | Suggested |
|---|---|---|
| Business | Riverstone Outdoors | Tabarka Studio |
| Tag (proof card) | Multi-store retailer | Design & home *(suggested — Tabarka makes hand-painted tile)* |
| Industry page | Retail & E-commerce | Retail & E-commerce *(fits — design/home goods retail)* |
| Spokesperson | **Jordan Mosley**, Director of Retail | **Meir Zenati**, Creative Director |

**Where it appears today**
- `components/legacy/customer-stories.html:174` — band quote "Jordan Mosley · Director of Retail, Riverstone Outdoors"
- `components/legacy/industry-retail-ecommerce.html:278` — proof-card "Riverstone Outdoors" + 285 attribution

**Suggested narrative (proof card)**
> "A design-led tile studio uses XBert for trade-program inquiries, sample requests, and after-hours customer service. Designers get clean orders, clients get answers."

**Open questions**
- Current KPI is "**72%** BOPIS questions resolved without a store call" — BOPIS doesn't apply to a tile studio. Suggested replacement KPI: **"~ 4 hrs/day reclaimed at the front desk"** or **"68% sample-request inquiries auto-resolved"**. Confirm.
- Current quote — *"My store managers used to hate the phone…"* — also doesn't fit. Suggested: *"My designers used to hate the phone. Now it just rings less, and only with the things they actually want."*

---

## 13. Anil Suresh (Suresh + Associates) → Daniel Sabet (GreenGrowth CPA's)

| Field | Current | Suggested |
|---|---|---|
| Business | Suresh + Associates | GreenGrowth CPA's |
| Tag (proof card) | Tax + accounting | Tax + accounting *(stays)* |
| Industry page | Professional Services | Professional Services |
| Spokesperson | **Anil Suresh, CPA**, Founding Partner | **Daniel Sabet**, Senior Manager |

**Where it appears today**
- `components/legacy/customer-stories.html:178` — band quote "Anil Suresh, CPA · Suresh + Associates"
- `components/legacy/industry-professional-services.html:146` — pillar quote
- `components/legacy/industry-professional-services.html:267` — proof-card "Suresh + Associates" + 274 attribution

**Suggested narrative (proof card)**
> "A boutique CPA firm uses XBert to handle inbound during tax season. Clients get answers; partners spend their time on returns." *(works as-is)*

**Open questions**
- Pillar quote currently reads *"Our managing partner reviewed 60 intake transcripts before we went live. She approved every one."* That's fine for a Senior Manager to say about their managing partner — keep as-is? Confirm.
- Proof-card attribution currently says "Founding Partner." Daniel Sabet is "Senior Manager" — significantly more junior. Confirm we should use that exact title (vs. e.g. "Senior Manager, Tax").

---

## 14. Mark Daley (Northpoint Property Group) → Tony Calvis (Calvis Wyant)

| Field | Current | Suggested |
|---|---|---|
| Business | Northpoint Property Group | Calvis Wyant |
| Tag (proof card) | Property management | Custom home builder *(suggested — Calvis Wyant builds luxury custom homes)* |
| Industry page | Real Estate | Real Estate *(fits)* |
| Spokesperson | **Mark Daley**, Director of Leasing | **Tony Calvis**, Founder |

**Where it appears today**
- `components/legacy/customer-stories.html:182` — band quote "Mark Daley · Director of Leasing, Northpoint Property Group"
- `components/legacy/industry-real-estate.html:279` — proof-card "Northpoint Property Group" + 286 attribution

**Suggested narrative (proof card)**
> "A luxury custom home builder uses XBert as the after-hours inquiry line. Buyers get answers, the design team gets pre-qualified consults, projects get filled."

**Open questions** *(important)*
- The current narrative is about "**leasing**, **1,400 units**, **vacancy time**" — none of which apply to a custom home builder. We'll need a brand-new narrative (suggested above) and a brand-new KPI (current is "**11 days** shaved off average vacancy time"). Suggested replacement KPI: **"+38% qualified consult bookings"** or **"~22 hrs/wk reclaimed at the front desk."** Confirm.
- Current quote — *"Our leasing line was eating four people. Now it's two, and the response is faster."* — needs replacement too. Suggested: *"Our inquiry line was eating four people. Now it's two, and the response is faster."*

---

## Open questions (cross-cutting)

Please review these before we apply anything:

1. **Lisa Bryant conflict (item #5 vs item #10)** — pick A, B, or C. Right now we can only do one.
2. **Industry-page fit** — items #4 (KBHB), #9 (Reforming Pilates), #11 (Black Llama), and #14 (Calvis Wyant) all change *what kind of business* the customer is, which means narratives, KPIs, and quotes on the Healthcare / Insurance / Retail / Real Estate industry pages no longer match the original copy. We've suggested rewrites above; please flag any you want to keep verbatim or rewrite differently.
3. **Titles** — several titles change tier (e.g., "Founding Partner" → "Senior Manager", "VP Operations" → "Co-founder", "Director of Leasing" → "Founder"). The narratives around them often reference firm size, role scope, etc. Confirm we're free to rewrite those alongside the names.
4. **Headshots** — the photos behind these people (`tomas-gorny.png`, `marco-burgarello.png`, `swarm-XX.png`, etc.) are *separate assets* that don't currently match the new names either. Do you also want us to swap photos as part of this, or only the names/copy for now?
5. **`index-old.html`** — this file looks like a stale/legacy snapshot. We can update it for consistency, or leave it untouched. Confirm.

---

*Once you reply with answers (or just "go"), we'll do the implementation in one pass and push to your branch.*
