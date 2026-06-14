# Packet 01.5 — Discovery Pass 54

STATUS: DISCOVERY IN PROGRESS
PHASE: PROBLEM FINDING ONLY
ROUTING: NOT STARTED
COUNT MODE: NATURAL YIELD
DATE: 2026-06-13

This pass looks for emergency-service command and responder-operation failure involving dispatch, fire response, emergency medical services, rescue, incident command, triage, responder exposure, mutual aid, interoperable communication, and continuity.

## Provisional records

### EMDISP-001 — Call classification misses the real emergency because the caller cannot describe it clearly

Language, panic, disability, age, intoxication, background noise, coercion, and incomplete location may distort the initial report.

HARM: the wrong priority, resource, or response mode is assigned at the first decision point.

OVERLAP TO CHECK: LOC-003, FRAME-003.

### EMDISP-002 — Dispatch protocol treats unusual emergencies as routine categories

Chemical exposure, active violence, confined rescue, behavioral crisis, infrastructure failure, and combined hazards may not fit standard scripts.

HARM: a familiar workflow delays the specialized response the event requires.

OVERLAP TO CHECK: CASEDEF-002, INCSEV-001.

### EMDISP-003 — Location data appear precise while identifying the wrong access point

Apartments, campuses, rural roads, trails, highways, large facilities, and vertical structures may have multiple entrances or levels.

HARM: responders arrive near the victim but cannot reach them in time.

OVERLAP TO CHECK: LOC-001, NAV-001.

### EMDISP-004 — Automated resource recommendation ignores current crew capability

Unit location may be known while staffing, equipment, fatigue, maintenance, training, and hospital turnaround are not.

HARM: the closest listed unit is not the fastest or safest effective response.

OVERLAP TO CHECK: HCAP-001, AIRCREW-001.

### EMDISP-005 — High call volume hides low-frequency catastrophic events

Queue pressure may reward rapid closure and standardized processing.

HARM: the rare event that needs deeper questioning is handled as routine noise.

OVERLAP TO CHECK: QUEUE-002, ALERT-001.

### FIRESVC-001 — Fireground strategy assumes building information is current

Renovation, occupancy, storage, solar systems, batteries, lightweight construction, locked areas, and hidden voids may not appear in preplans.

HARM: crews enter or position equipment against a building that no longer matches the plan.

OVERLAP TO CHECK: STRUCT-006, AIRCERT-001.

### FIRESVC-002 — Suppression water supply fails under the same event driving demand

Power loss, drought, frozen mains, damaged hydrants, pressure collapse, contamination, and competing use may reduce flow.

HARM: tactical plans depend on water that disappears during the incident.

OVERLAP TO CHECK: WATERUTIL-001, CASCADE-001.

### FIRESVC-003 — Ventilation action changes fire behavior faster than crews can coordinate

Doors, windows, roofs, fans, wind, and structural openings may alter heat, smoke, and oxygen flow.

HARM: a rescue or suppression action intensifies conditions for another team.

OVERLAP TO CHECK: INTERACT-001, FIRESVC-006.

### FIRESVC-004 — Accountability records presence but not exact location or condition

Tag systems, radio checks, assignments, and entry logs may lag crew movement and emergency changes.

HARM: command believes a responder is safe or accounted for when they are not.

OVERLAP TO CHECK: GOVREC-001, OBS-003.

### FIRESVC-005 — Property protection competes with life safety and firefighter survival

Visible assets, political pressure, owner demands, and escalation fear may influence strategy.

HARM: crews accept disproportionate risk for structures or contents that cannot justify it.

OVERLAP TO CHECK: FUELMGMT-005, WKAUTH-001.

### EMSOPS-001 — Protocol-based treatment ignores a condition outside the expected pathway

Age, pregnancy, disability, medication, atypical symptoms, trauma, and multiple illnesses may alter presentation.

HARM: correct protocol use produces the wrong treatment for the actual patient.

OVERLAP TO CHECK: MEDINT-002, CASEDEF-002.

### EMSOPS-002 — Hospital destination decision uses nominal capability rather than current capacity

A center may be designated for trauma, stroke, cardiac, pediatric, or psychiatric care while beds, specialists, imaging, or staff are unavailable.

HARM: transport time is spent reaching a facility unable to deliver the promised care.

OVERLAP TO CHECK: HCAP-001, AIRPORT-005.

### EMSOPS-003 — Handoff compresses the patient’s changing condition into a short summary

Timing, treatment response, scene observations, medications, identity uncertainty, and family information may be lost.

HARM: receiving clinicians act without the context needed to recognize deterioration or prior error.

OVERLAP TO CHECK: HANDOFF-005, RECONMED-003.

### EMSOPS-004 — Ambulance turnaround time hides incomplete restoration between calls

Cleaning, restocking, charging, equipment checks, documentation, food, and crew recovery may be shortened under demand.

HARM: the next patient receives a nominally available unit that is not fully ready.

OVERLAP TO CHECK: MAINT-003, HCAP-005.

### EMSOPS-005 — Behavioral crisis response is framed primarily as control and transport

Fear, communication difficulty, sensory overload, trauma, substance effects, and lack of alternatives may shape behavior.

HARM: escalation, restraint, or unnecessary confinement replaces stabilizing care.

OVERLAP TO CHECK: CUSTHEALTH-004, CRISIS-001.

### RESCUE-001 — Rescue plan does not account for the rescuer becoming an additional victim

Confined spaces, water, ice, heights, collapse, electricity, traffic, chemicals, and unstable terrain may change rapidly.

HARM: urgency expands the incident by exposing unprotected responders.

OVERLAP TO CHECK: HAZMAT-003, MINEWORK-002.

### RESCUE-002 — Technical rescue equipment is present but incompatible with the scene

Anchors, ropes, lifting systems, breathing equipment, boats, cutting tools, and communications may not match the geometry or hazard.

HARM: inventory is mistaken for usable rescue capability.

OVERLAP TO CHECK: PHALLOC-002, FORM-001.

### RESCUE-003 — Search coverage is counted without accounting for detection probability

Terrain, weather, darkness, water, debris, scent, noise, victim behavior, and sensor limits may leave searched areas uncertain.

HARM: command closes a search area while the missing person remains undetected.

OVERLAP TO CHECK: WILDLIFE-001, TEST-004.

### RESCUE-004 — Rescue priority favors visible victims over hidden or inaccessible victims

Media, bystander reports, ease of access, noise, and survivability assumptions may shape resource allocation.

HARM: less visible people receive delayed rescue despite comparable or greater need.

OVERLAP TO CHECK: SUPPRESS-002, TRIAGE-002.

### INCCMD-001 — Incident command structure exists on paper but authority remains ambiguous

Multiple agencies, private operators, elected officials, facility owners, and specialized teams may issue competing directions.

HARM: responders act under conflicting priorities and no one owns the whole risk.

OVERLAP TO CHECK: GOV-001, AUTH-001.

### INCCMD-002 — Command span is preserved numerically while information load becomes unmanageable

A supervisor may oversee an acceptable number of units whose tasks, hazards, and dependencies are unusually complex.

HARM: formal span-of-control compliance hides cognitive overload.

OVERLAP TO CHECK: COG-001, MEAS-001.

### INCCMD-003 — Incident objectives lag behind changing conditions

Weather, fire, violence, contamination, structure, patient count, infrastructure, and public movement may change faster than planning cycles.

HARM: teams continue executing a plan that no longer protects them or the public.

OVERLAP TO CHECK: CHANGE-005, NUCEM-001.

### INCCMD-004 — Unified command conceals unresolved conflicts rather than resolving them

Agencies may agree on a public objective while retaining incompatible legal duties, risk tolerances, and information.

HARM: apparent coordination fails at the moment a tradeoff must be decided.

OVERLAP TO CHECK: COLLAB-005, PLURAL-003.

### INCCMD-005 — Demobilization begins before hidden hazards and service gaps are understood

Hot spots, contamination, displaced residents, utility failure, responder injury, evidence, and follow-up care may persist.

HARM: visible incident closure creates a second period of unmanaged risk.

OVERLAP TO CHECK: RECOVER-003, POST-003.

### TRIAGE-001 — Triage category is treated as stable after conditions change

Bleeding, airway, shock, temperature, toxins, crush injury, stress, and delayed symptoms may worsen after initial assessment.

HARM: a patient remains low priority after becoming time-critical.

OVERLAP TO CHECK: CASEDEF-004, MEDINT-002.

### TRIAGE-002 — Triage favors patients who can communicate and move visibly

Children, disabled people, unconscious patients, non-speakers, hidden victims, and people under debris may be underassessed.

HARM: assessment speed becomes a bias toward the easiest patients to evaluate.

OVERLAP TO CHECK: RESCUE-004, PHALLOC-004.

### TRIAGE-003 — Scarcity standard is activated without shared ethical authority

Survival probability, age, disability, social role, arrival order, and resource intensity may be weighted differently across teams.

HARM: life-affecting choices vary by responder or institution without legitimate governance.

OVERLAP TO CHECK: HCAP-004, ALLOC-001.

### TRIAGE-004 — Repeated triage consumes staff and delays treatment when information systems fail

Lost tags, incompatible records, movement, and handoff gaps may force reassessment from the beginning.

HARM: scarce clinical time is spent reconstructing status instead of treating patients.

OVERLAP TO CHECK: GOVREC-001, CLEARSET-004.

### RESPX-001 — Responder exposure records omit cumulative multi-incident burden

Smoke, heat, noise, trauma, chemicals, radiation, infection, sleep loss, and musculoskeletal strain may be tracked separately or not at all.

HARM: occupational harm appears below limits while total lifetime burden grows.

OVERLAP TO CHECK: RADHEALTH-002, SUPPRESS-004.

### RESPX-002 — Protective equipment creates heat, communication, vision, and mobility penalties

Respirators, suits, armor, gloves, helmets, and hearing protection may reduce another critical capability.

HARM: protection from one hazard raises operational risk from another.

OVERLAP TO CHECK: RADPROT-004, GUARD-003.

### RESPX-003 — Psychological injury is recognized only after performance collapses

Repeated death, moral conflict, threat, fatigue, public scrutiny, and organizational stigma may accumulate silently.

HARM: responders lose health, judgment, relationships, or employment before support begins.

OVERLAP TO CHECK: STRESS-003, SUPPORT-005.

### RESPX-004 — Decontamination protects the station while transferring contamination elsewhere

Vehicles, uniforms, equipment, wastewater, waste, homes, and repair facilities may carry residual material.

HARM: responder cleanup moves exposure into family and community environments.

OVERLAP TO CHECK: DECOMNUC-003, MEDWASTE-002.

### MUTUAL-001 — Mutual-aid agreement counts resources without confirming deployment readiness

Staffing, travel time, local coverage, equipment compatibility, credentialing, and political approval may differ during the event.

HARM: promised capacity exists on paper but not at the incident.

OVERLAP TO CHECK: PHALLOC-003, HCAP-001.

### MUTUAL-002 — Donor jurisdiction weakens its own protection by sending aid

Backfill, fatigue, local incidents, maintenance, and prolonged deployment may reduce home capability.

HARM: one community stabilizes by transferring risk to another.

OVERLAP TO CHECK: HCAP-002, NUC-005.

### MUTUAL-003 — Incoming teams cannot interpret local geography, hazards, procedures, or authority

Maps, terminology, radio channels, building knowledge, community context, and command expectations may differ.

HARM: added personnel increase coordination load and operational error.

OVERLAP TO CHECK: AIRMAINT-004, COLLAB-002.

### MUTUAL-004 — Reimbursement and liability disputes delay requested assistance

Cost authorization, insurance, workers’ compensation, equipment damage, and legal authority may remain uncertain.

HARM: administrative risk blocks time-critical aid.

OVERLAP TO CHECK: BILL-003, LIAB-001.

### EMCOMMS-001 — Interoperable radio channel exists but becomes unusable under shared demand

Congestion, priority override, encryption, coverage gaps, damaged infrastructure, and incompatible talk groups may block communication.

HARM: technical interoperability fails during the event it was built for.

OVERLAP TO CHECK: TELECOM-001, ATC-004.

### EMCOMMS-002 — Plain-language policy does not eliminate agency-specific meaning

The same words may imply different urgency, authority, location, or action across organizations.

HARM: apparently clear messages produce incompatible behavior.

OVERLAP TO CHECK: LOC-003, PLURAL-003.

### EMCONT-001 — Emergency-service continuity plan assumes responders can report to work

Evacuation, family needs, illness, damaged roads, fuel, communication, and personal loss may remove staff simultaneously.

HARM: essential services fail because continuity planning treated workers as independent of the disaster.

OVERLAP TO CHECK: HCAP-005, PUBLICDEP-002.

### EMCONT-002 — Backup dispatch and station facilities depend on the same regional infrastructure

Power, telecom, fuel, data, roads, vendors, and staffing may be shared with the primary site.

HARM: nominal redundancy fails through common-mode dependency.

OVERLAP TO CHECK: MONO-001, GRID-001.

## Pass 54 result

Natural-yield provisional records: 40
Routing decisions made: 0
Records closed: 0
Deduplication required later: Yes
Discovery saturation: NOT REACHED

Corrected working total:
- Preserved baseline: 122
- Prior actual provisional headings: 2110
- Pass 54 natural-yield provisional: 40
- Current actual provisional headings: 2150
- Current combined working total: 2272

NEXT REQUIRED STEP:
Run Major-Domain Coverage Audit v2. Reassess every formerly missing and partial domain, identify any remaining major gaps, and do not begin cross-domain saturation testing unless the audit finds no major uncovered family.

END PACKET 01.5 — DISCOVERY PASS 54
