# Packet 01.5 — Discovery Pass 57

STATUS: DISCOVERY IN PROGRESS
PHASE: PROBLEM FINDING ONLY
ROUTING: NOT STARTED
COUNT MODE: NATURAL YIELD
DATE: 2026-06-13

This pass looks for social-care, long-term-care, aging, disability-support, home-and-community-service, direct-care-workforce, elder-abuse, caregiver, supported-decision-making, and care-transition failure.

APPLICABILITY GATE: These are conditional future candidates, not proof of current app defects. They become applicable only if the project stores, interprets, recommends, coordinates, routes, or governs social-care, aging, caregiving, disability-support, or long-term-care information, decisions, or services.

## Provisional records

### HCBS-001 — Home support exists on paper but not at the required time

Authorized hours, staffing, transport, scheduling, geography, and provider availability may not match daily need.

HARM: a person is technically approved for support while remaining unable to eat, bathe, communicate, move, or stay safe.

OVERLAP TO CHECK: ACCESSLAW-001, QUEUE-001.

### HCBS-002 — Service plans assume a stable home environment

Housing condition, electricity, water, internet, family conflict, landlord rules, and neighborhood safety may change.

HARM: a valid care plan becomes unusable because the living environment cannot support it.

OVERLAP TO CHECK: HOUSING-004, CRISCONT-002.

### HCBS-003 — Fragmented providers leave no one responsible for the whole daily routine

Personal care, nursing, therapy, transport, meals, equipment, and case management may each cover only one task.

HARM: each provider completes its assignment while essential gaps remain between them.

OVERLAP TO CHECK: HANDOFF-005, WATERGOV-001.

### HCBS-004 — Consumer choice is nominal when only one provider is available

Rural markets, low reimbursement, language, disability, behavioral needs, and staffing shortages may eliminate meaningful alternatives.

HARM: formal choice conceals dependence on a provider the person cannot safely replace.

OVERLAP TO CHECK: LOCKIN-001, SPACEACCESS-001.

### HCBS-005 — Remote monitoring is substituted for human support beyond its capability

Sensors, cameras, alerts, wearables, and automated check-ins may detect events without understanding context or providing assistance.

HARM: visible technology masks reduced human care and delayed response.

OVERLAP TO CHECK: SENSE-003, AUTO-005.

### LTCARE-001 — Facility staffing ratios count bodies rather than usable capability

Skill mix, experience, language, fatigue, assignment load, agency staff, and resident acuity may differ.

HARM: compliant staffing numbers coexist with unsafe care capacity.

OVERLAP TO CHECK: HCAP-001, BHWORK-001.

### LTCARE-002 — Congregate infection control protects the facility by restricting residents indefinitely

Visitors, dining, activities, movement, and family contact may remain limited long after acute danger changes.

HARM: infection prevention creates isolation, cognitive decline, and loss of dignity.

OVERLAP TO CHECK: BHINPT-002, ISOLATE-002.

### LTCARE-003 — Resident decline is normalized as aging rather than investigated

Pain, infection, dehydration, medication effects, abuse, depression, sensory loss, and environmental stress may be misattributed.

HARM: treatable harm continues because deterioration is considered inevitable.

OVERLAP TO CHECK: PHARMVIG-002, BHINPT-005.

### LTCARE-004 — Facility closure transfers residents faster than continuity can be preserved

Records, medication, belongings, relationships, accessibility, location, and family contact may be disrupted.

HARM: relocation intended to preserve care accelerates decline and distress.

OVERLAP TO CHECK: DETAIN-004, RECONMED-003.

### LTCARE-005 — Quality rating hides selective admission and discharge practices

Facilities may avoid high-acuity residents, transfer deteriorating residents, or optimize documented measures.

HARM: apparent quality improves by moving difficult cases elsewhere.

OVERLAP TO CHECK: MEAS-004, INCENT-001.

### DIRECTCARE-001 — Direct-care worker turnover destroys person-specific knowledge

Communication style, routines, warning signs, preferences, equipment, and trust may remain undocumented.

HARM: replacement staff repeat preventable errors and distress.

OVERLAP TO CHECK: SUCCESS-001, LANDSTEWARD-003.

### DIRECTCARE-002 — Low wages and unstable hours create hidden care instability

Workers may hold multiple jobs, lack paid leave, lose transport, or leave suddenly.

HARM: workforce precarity becomes missed care for people who cannot substitute independently.

OVERLAP TO CHECK: LABOR-002, ECONSHOCK-002.

### DIRECTCARE-003 — Time-per-task scheduling makes relational and safety work invisible

Listening, reassurance, observation, communication, setup, and unexpected needs may not be billable.

HARM: workers must choose between schedule compliance and humane care.

OVERLAP TO CHECK: THROUGHPUT-001, BHWORK-002.

### DIRECTCARE-004 — Worker safety policy frames the supported person as the hazard

Behavior, movement, communication, pain, trauma, and environmental triggers may be managed through exclusion or restraint.

HARM: staff protection becomes coercion rather than better staffing, design, and support.

OVERLAP TO CHECK: BHWORK-003, FORCECUST-001.

### DIRECTCARE-005 — Training is generic while support needs are highly individual

Disability, culture, communication, medication, equipment, feeding, seizure, and behavioral support may require specific competence.

HARM: certified workers remain unprepared for the person they serve.

OVERLAP TO CHECK: TRAIN-003, FORM-001.

### ELDER-001 — Abuse detection depends on the person reporting through the suspected caregiver

Communication, transport, finances, appointments, and device access may be controlled by the alleged abuser.

HARM: the reporting path is structurally blocked by the same relationship causing harm.

OVERLAP TO CHECK: DETAIN-005, ABUSE-005.

### ELDER-002 — Financial exploitation appears as ordinary authorized activity

Joint accounts, powers of attorney, gifts, property transfers, loans, subscriptions, and caregiver payments may look legitimate.

HARM: assets and housing are lost before coercion or incapacity is recognized.

OVERLAP TO CHECK: FRAUD-002, GUARD-001.

### ELDER-003 — Protective intervention removes autonomy more broadly than necessary

Bank restrictions, guardianship, relocation, communication limits, and family exclusion may follow one suspected risk.

HARM: prevention of one harm creates unnecessary loss of liberty and identity.

OVERLAP TO CHECK: INVOLT-002, CONTAIN-001.

### ELDER-004 — Neglect is hidden by fragmented responsibility

Family, facility, clinician, agency, landlord, insurer, and public program may each assume another party is meeting the need.

HARM: no single omission appears decisive while the person deteriorates.

OVERLAP TO CHECK: HCBS-003, GOV-001.

### DISELIG-001 — Eligibility assessment measures deficits in an artificial setting

A short interview or examination may not capture fatigue, fluctuation, pain, communication, environmental barriers, or support needs over time.

HARM: real disability is underestimated because the assessment context temporarily removes it.

OVERLAP TO CHECK: MEAS-002, FRAME-003.

### DISELIG-002 — Improvement caused by support is used to remove the support

Medication, assistance, equipment, therapy, and stable housing may make a person appear less disabled.

HARM: successful support becomes evidence that support is no longer needed.

OVERLAP TO CHECK: REBOUND-001, BHOUT-005.

### DISELIG-003 — Recertification repeatedly forces proof of permanent conditions

People may need to reproduce medical records, evaluations, functional evidence, and identity documentation.

HARM: administrative burden interrupts essential support and causes avoidable distress.

OVERLAP TO CHECK: BENEFIT-001, GOVREC-001.

### DISELIG-004 — Category boundaries exclude people with interacting moderate impairments

Mobility, cognition, sensory loss, mental health, fatigue, pain, and chronic illness may each fall below separate thresholds.

HARM: combined severe limitation is missed because no single category is sufficient.

OVERLAP TO CHECK: MEDINTX-004, CASEDEF-002.

### DISELIG-005 — Automated eligibility tools reproduce unequal documentation quality

People with continuous specialists, insurance, stable housing, and fluent records may appear more eligible than equally impaired people without them.

HARM: administrative privilege is mistaken for greater need.

OVERLAP TO CHECK: CUSTTECH-001, PHSURV-001.

### CAREGIVER-001 — Unpaid caregiving capacity is treated as limitless infrastructure

Sleep, employment, health, finances, relationships, skill, and physical strength may erode gradually.

HARM: the care system appears stable until the caregiver collapses suddenly.

OVERLAP TO CHECK: PUBLICDEP-002, FAT-004.

### CAREGIVER-002 — Respite eligibility arrives only after crisis-level burden

Programs may require documented severity, waiting lists, assessments, and available providers.

HARM: relief begins after preventable injury, hospitalization, abandonment, or institutional placement.

OVERLAP TO CHECK: MHPREV-001, QUEUE-001.

### CAREGIVER-003 — Family caregiver is expected to perform clinical tasks without equivalent training or protection

Medication, feeding, lifting, wound care, equipment, behavior, and emergency decisions may be delegated informally.

HARM: both caregiver and supported person face avoidable injury and error.

OVERLAP TO CHECK: DIRECTCARE-005, MEDWASTE-002.

### CAREGIVER-004 — Caregiver monitoring becomes surveillance of the supported person

Apps, cameras, location, medication tracking, and home sensors may be introduced for reassurance or accountability.

HARM: safety support erodes privacy and autonomy inside the home.

OVERLAP TO CHECK: HCBS-005, CUSTTECH-002.

### CAREGIVER-005 — Conflict between caregivers is interpreted as unreliability rather than a governance failure

Family members, professionals, guardians, and agencies may disagree about risk, preference, money, and responsibility.

HARM: the supported person loses continuity while authority remains unresolved.

OVERLAP TO CHECK: FAMILYCUST-003, INCCMD-004.

### SUPDEC-001 — Supported decision-making is offered only after capacity has already been denied

Communication aids, trusted supporters, extra time, accessible information, and decision-specific help may not be tried first.

HARM: inability to decide without accommodation is mistaken for inability to decide at all.

OVERLAP TO CHECK: INVOLT-002, BLDACC-001.

### SUPDEC-002 — Supporter influence becomes invisible coercion

Dependence for housing, care, money, communication, or transport may shape choices presented as voluntary.

HARM: formal autonomy conceals pressure from the person controlling essential support.

OVERLAP TO CHECK: ELDER-002, ABUSE-001.

### SUPDEC-003 — Substitute decision-maker prioritizes risk avoidance over the person’s values

Safety, liability, convenience, family preference, and institutional rules may outweigh dignity, relationships, culture, and acceptable risk.

HARM: protection preserves existence while erasing the person’s chosen life.

OVERLAP TO CHECK: GUARD-001, BHOUT-005.

### SUPDEC-004 — Decision authority is unclear across healthcare, finance, housing, and services

Different documents and laws may name different supporters, proxies, guardians, or agents.

HARM: conflicting authorities delay essential decisions or enable selective control.

OVERLAP TO CHECK: JUR-001, CAREGIVER-005.

### CARETRANS-001 — Hospital discharge assumes home support starts immediately

Equipment, medication, home access, transport, personal assistance, food, and nursing may arrive later or not at all.

HARM: a medically stable discharge becomes an unsafe home emergency.

OVERLAP TO CHECK: RELEASECUST-001, BHINPT-003.

### CARETRANS-002 — Transition to long-term care loses the person’s routines and communication methods

Preferences, sensory needs, behavior meanings, relationships, equipment setup, and cultural practice may not transfer.

HARM: relocation creates distress that is then misclassified as decline or noncompliance.

OVERLAP TO CHECK: LTCARE-004, DIRECTCARE-001.

### CARETRANS-003 — Service eligibility changes when a person crosses age or program boundaries

Children’s services, adult disability, aging programs, insurance, education, and employment supports may use different rules.

HARM: support disappears at an administrative birthday rather than a change in need.

OVERLAP TO CHECK: EXP-006, EDUC-004.

### CARETRANS-004 — Emergency placement becomes permanent because community support cannot restart

Housing, staffing, equipment, funding, and provider availability may not recover after hospitalization or caregiver crisis.

HARM: a temporary safety move causes unnecessary long-term institutionalization.

OVERLAP TO CHECK: RADWASTE-003, INVOLT-004.

### CARETRANS-005 — Transition records transfer diagnoses but not practical support knowledge

What calms, triggers, assists, communicates, feeds, moves, or endangers the person may remain undocumented.

HARM: receiving services know the condition but not how to support the person safely.

OVERLAP TO CHECK: EMSOPS-003, HANDOFF-005.

### CARETECH-001 — Assistive technology failure removes multiple forms of independence at once

Communication, mobility, environmental control, medication, work, and emergency contact may depend on one device or platform.

HARM: a single failure converts independence into immediate dependence or danger.

OVERLAP TO CHECK: MONO-001, HW-004.

### CARETECH-002 — Service platform treats proxy access as equivalent to the person’s consent

Caregivers, family, staff, guardians, and coordinators may use shared accounts or broad permissions.

HARM: support access becomes unauthorized control over private information and decisions.

OVERLAP TO CHECK: AUTHZ-006, SUPDEC-002.

## Pass 57 result

Natural-yield provisional records: 40
Routing decisions made: 0
Records closed: 0
Deduplication required later: Yes
Discovery saturation: NOT REACHED

Corrected working total:
- Preserved baseline: 122
- Prior actual provisional headings: 2229
- Pass 57 natural-yield provisional: 40
- Current actual provisional headings: 2269
- Current combined working total: 2391

NEXT DISCOVERY PASS:
Military, defense, weapons lifecycle, and veteran-transition systems, including procurement, contractor dependence, command authority, escalation control, storage, transport, maintenance, decommissioning, training ranges, unexploded ordnance, autonomous systems, service-member health, family burden, and veteran transition.

END PACKET 01.5 — DISCOVERY PASS 57
