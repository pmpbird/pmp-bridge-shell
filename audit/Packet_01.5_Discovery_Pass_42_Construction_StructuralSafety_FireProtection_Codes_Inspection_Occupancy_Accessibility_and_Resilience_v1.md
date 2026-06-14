# Packet 01.5 — Discovery Pass 42

STATUS: DISCOVERY IN PROGRESS
PHASE: PROBLEM FINDING ONLY
ROUTING: NOT STARTED
DATE: 2026-06-13

This pass looks for construction, structural-safety, fire-protection, building-code, inspection, occupancy, accessibility, material, contractor-chain, and disaster-resilience failure.

## Provisional records

### STRUCT-001 — Structural load assumptions become stale after use changes

Storage, equipment, occupancy, partitions, rooftop systems, and vibration may increase after the original design.

HARM: a compliant structure is overloaded by later reality.

OVERLAP TO CHECK: CHANGE-001, MANUF-004.

### STRUCT-002 — Hidden deterioration is absent from visible condition reports

Corrosion, moisture, fatigue, rot, settlement, delamination, and concealed cracking may advance behind finishes or underground.

HARM: apparent surface condition masks loss of capacity.

OVERLAP TO CHECK: MAINT-002, REAL-001.

### STRUCT-003 — Temporary shoring or support becomes a permanent dependency

Construction braces, props, tie-downs, and load paths may remain longer than planned or be removed without review.

HARM: stability depends on an undocumented temporary state.

OVERLAP TO CHECK: MANUF-005, RESTORE-004.

### STRUCT-004 — Local damage triggers progressive collapse beyond the initial area

Connections, transfer structures, shared supports, and irregular geometry may spread one failure.

HARM: a small initiating event causes disproportionate building loss.

OVERLAP TO CHECK: CASCADE-002, INTERACT-001.

### STRUCT-005 — Nonstructural components become major hazards during movement

Ceilings, facades, shelving, glass, equipment, piping, and partitions may detach during earthquake, wind, or impact.

HARM: the primary structure survives while occupants are injured by attached systems.

OVERLAP TO CHECK: HAZ-004, MOBACC-005.

### STRUCT-006 — Digital model diverges from the building actually constructed

Field changes, tolerances, substitutions, penetrations, repairs, and undocumented work may not reach the model.

HARM: later analysis and emergency planning rely on a fictional structure.

OVERLAP TO CHECK: TRACEPROD-003, DATA-001.

### FIRE-001 — Detection zones do not match real smoke and fire compartments

Renovation, open doors, ceiling changes, airflow, and compartment breaches may alter how smoke travels.

HARM: alarms indicate the wrong location or arrive too late.

OVERLAP TO CHECK: OT-005, STRUCT-006.

### FIRE-002 — Suppression system is unavailable when demand occurs

Closed valves, impaired pumps, frozen pipes, low water, maintenance, blockage, or missing agents may disable protection.

HARM: installed suppression creates false reassurance.

OVERLAP TO CHECK: WATERUTIL-004, REAL-002.

### FIRE-003 — Smoke-control systems interact in untested ways

Fans, dampers, elevators, doors, HVAC, and stair pressurization may compete or reverse intended airflow.

HARM: automated protection moves smoke into occupied escape routes.

OVERLAP TO CHECK: INTERACT-001, OT-002.

### FIRE-004 — Security and access controls obstruct emergency egress

Locked doors, turnstiles, gates, credential readers, shutters, and anti-theft systems may remain active during evacuation.

HARM: protection against intrusion traps occupants inside.

OVERLAP TO CHECK: AUTHZ-006, EMSAFE-001.

### FIRE-005 — Retrofit introduces concealed combustible material

Insulation, cladding, sealants, cables, furnishings, and decorations may add fuel or toxic smoke.

HARM: later energy or aesthetic upgrades invalidate the original fire strategy.

OVERLAP TO CHECK: MATERIAL-002, CHANGE-005.

### FIRE-006 — Repeated false alarms train occupants to delay evacuation

Nuisance activation, unclear messaging, poor maintenance, and frequent tests may reduce response urgency.

HARM: alarm credibility is lost before a real fire.

OVERLAP TO CHECK: NOTIFY-004, DEBRIS-003.

### CODE-001 — Minimum code compliance is mistaken for sufficient safety

Codes may be baseline, historical, politically negotiated, or unsuitable for unusual hazards and vulnerable occupants.

HARM: legal compliance substitutes for risk-appropriate design.

OVERLAP TO CHECK: TERMS-001, ACCESSLAW-001.

### CODE-002 — Wrong code edition or jurisdiction is applied

Local amendments, adoption dates, occupancy categories, and authority boundaries may differ.

HARM: technically correct design follows rules that do not govern the project.

OVERLAP TO CHECK: JUR-001, VER-001.

### CODE-003 — Alternative compliance method is accepted without equivalent performance evidence

A novel material, calculation, system, or operational control may replace prescriptive requirements.

HARM: claimed equivalence fails under real fire, load, or evacuation conditions.

OVERLAP TO CHECK: TEST-005, DESIGN-003.

### CODE-004 — Grandfathered conditions accumulate incompatible later changes

Legacy stairs, wiring, fire separation, accessibility, and structure may interact with modern renovations.

HARM: each individually permitted condition creates unsafe combined behavior.

OVERLAP TO CHECK: INTERACT-001, LIFE-005.

### CODE-005 — Partial renovation leaves a hazardous boundary between old and new systems

Fire ratings, drainage, electrical protection, structure, ventilation, and accessibility may stop at project limits.

HARM: the interface between compliant work and existing work becomes the weakest point.

OVERLAP TO CHECK: CHANGE-005, PORT-001.

### INSP-001 — Inspection timing misses work after it is concealed

Reinforcement, anchors, waterproofing, firestopping, wiring, piping, and connections may be covered before review.

HARM: critical defects become inaccessible and undocumented.

OVERLAP TO CHECK: QUALITY-001, STRUCT-002.

### INSP-002 — Checklist compliance misses a novel hazardous condition

Inspectors may verify expected items while unusual geometry, interaction, or construction sequence falls outside the form.

HARM: formal completeness hides an unmodeled failure path.

OVERLAP TO CHECK: TEST-002, MODEL-003.

### INSP-003 — Inspector independence is weakened by schedule, payment, or relationship pressure

Owners, contractors, agencies, and repeat clients may influence scope, timing, or findings.

HARM: oversight adapts to project pressure instead of safety evidence.

OVERLAP TO CHECK: PEER-002, CONTRACT-004.

### INSP-004 — Remote or photo inspection creates false completeness

Selected angles, resolution, lighting, metadata, and inaccessible areas may omit critical context.

HARM: visual proof is accepted without full site reality.

OVERLAP TO CHECK: MEDIA-005, REMSENSE-001.

### INSP-005 — Correction is closed from documentation rather than physical verification

A letter, invoice, photo, or contractor statement may be accepted as proof of repair.

HARM: unresolved defects remain in service under a closed record.

OVERLAP TO CHECK: QUALITY-005, AUTHENT-001.

### OCCUP-001 — Building use changes without reassessing life-safety systems

Warehouse, office, housing, childcare, assembly, medical, and sleeping uses create different risks.

HARM: systems designed for one occupancy protect another inadequately.

OVERLAP TO CHECK: STRUCT-001, CODE-004.

### OCCUP-002 — Actual occupant count exceeds the planning basis

Events, informal use, crowding, visitors, temporary workers, and unregistered residents may increase density.

HARM: exits, sanitation, ventilation, and structural capacity are undersized.

OVERLAP TO CHECK: TRANSIT-004, ALLOC-001.

### OCCUP-003 — Evacuation model assumes orderly individual behavior

Families, crowds, smoke, panic, disability, language, and attempts to retrieve belongings may change movement.

HARM: calculated evacuation time understates real escape time.

OVERLAP TO CHECK: EMROUTE-003, MOBILITY-001.

### OCCUP-004 — Vacant or closed status is trusted despite people remaining inside

Cleaners, guards, unhoused occupants, maintenance workers, residents, and unauthorized entrants may be present.

HARM: shutdown, demolition, fumigation, or emergency action proceeds with hidden occupants.

OVERLAP TO CHECK: GUARD-004, OBS-003.

### OCCUP-005 — Building operation depends on occupant behavior that is not communicated

Doors, windows, ventilation, cooking, charging, storage, and fire separation may require specific practices.

HARM: safe design degrades through ordinary use that occupants were never taught.

OVERLAP TO CHECK: DOC-005, TRAIN-001.

### BLDACC-001 — Accessible route is not continuous through the whole journey

Parking, entrance, security, elevator, doorway, restroom, refuge, and destination may not connect.

HARM: partial compliance is presented as usable access.

OVERLAP TO CHECK: MOBACC-001, ACCESSLAW-002.

### BLDACC-002 — Emergency evacuation plan depends on disabled occupants waiting for rescue

Areas of refuge, evacuation chairs, communication, and staff assistance may lack reliable staffing or capacity.

HARM: equal everyday access becomes unequal survival during emergency.

OVERLAP TO CHECK: HOUSE-004, PUBLICDEP-002.

### BLDACC-003 — Temporary construction barriers destroy the accessible route

Scaffolding, trenches, stored materials, detours, noise, dust, and closed elevators may block safe passage.

HARM: renovation silently removes access for days or months.

OVERLAP TO CHECK: MOBACC-001, CHANGE-001.

### BLDACC-004 — Accessibility depends on staff intervention

Portable ramps, locked lifts, alternate entrances, assistance, and manual controls may require finding an authorized worker.

HARM: nominal access disappears when staff are absent, busy, or unwilling.

OVERLAP TO CHECK: CARE-005, CIVIC-005.

### BLDACC-005 — Emergency controls and information are inaccessible under stress

Alarms, maps, intercoms, door hardware, extinguishers, and refuge communication may require vision, hearing, reach, strength, or literacy.

HARM: people cannot use life-safety systems when urgency is highest.

OVERLAP TO CHECK: MOBACC-004, EMSAFE-005.

### MATERIAL-001 — Material substitution preserves appearance but changes performance

Strength, fire behavior, toxicity, durability, moisture response, and compatibility may differ.

HARM: an approved-looking replacement invalidates design assumptions.

OVERLAP TO CHECK: COUNTERFEIT-005, CHANGE-005.

### MATERIAL-002 — Material combinations create hazards not present individually

Adhesives, coatings, insulation, metals, sealants, and membranes may react chemically, trap moisture, or spread fire.

HARM: component compliance fails to predict assembly behavior.

OVERLAP TO CHECK: INTERACT-001, FIRE-005.

### MATERIAL-003 — Environmental exposure ages materials faster than specified

Salt, UV, freeze-thaw, heat, humidity, pollution, insects, and ground chemistry may accelerate degradation.

HARM: expected service life is overstated for the actual site.

OVERLAP TO CHECK: MAINT-001, ENVRES-001.

### MATERIAL-004 — Renovation disturbs concealed hazardous material

Asbestos, lead, mold, silica, contaminated soil, and old insulation may be released during cutting or demolition.

HARM: hidden legacy material becomes an acute worker and occupant exposure.

OVERLAP TO CHECK: CONTAM-006, HAZ-003.

### MATERIAL-005 — Material certification is valid for a different product, batch, or installation

Reports and listings may be copied, expired, incomplete, or dependent on exact assembly details.

HARM: paperwork approves material that was never actually tested in this use.

OVERLAP TO CHECK: QUALITY-005, COUNTERFEIT-001.

### BUILDCHAIN-001 — Responsibility fragments across owner, designer, contractor, subcontractor, and inspector

Different parties control design intent, field execution, verification, and maintenance handoff.

HARM: defects persist because each actor assumes another owns the risk.

OVERLAP TO CHECK: LIAB-001, GOV-006.

### BUILDCHAIN-002 — Field change is approved informally and never reaches the record set

Verbal direction, sketches, substitutions, and site fixes may bypass formal revision.

HARM: as-built documents and later maintenance begin from false information.

OVERLAP TO CHECK: STRUCT-006, TRACEPROD-003.

### BUILDCHAIN-003 — Subcontractor safety and labor conditions are hidden downstream

Multiple tiers may obscure training, fatigue, language, pay pressure, and unsafe practices.

HARM: project success depends on risk transferred to less visible workers.

OVERLAP TO CHECK: CONTRACT-002, LABOR-005.

### BUILDCHAIN-004 — Schedule compression shortens curing, testing, drying, and commissioning

Concrete, coatings, waterproofing, fireproofing, systems, and controls may be accepted before stabilization.

HARM: latent defects are built into the finished structure.

OVERLAP TO CHECK: MANUF-001, DEAD-005.

### BUILDCHAIN-005 — Closeout records omit warranties, settings, and maintenance requirements

Final manuals, test results, access credentials, product data, and inspection history may be incomplete or fragmented.

HARM: the building enters operation without the information needed to keep it safe.

OVERLAP TO CHECK: HANDOFF-005, MAINT-004.

## Pass 42 result

New provisional records: 42
Routing decisions made: 0
Records closed: 0
Deduplication required later: Yes
Discovery saturation: NOT REACHED

Combined working total:
- Existing baseline: 122
- Pass 01 provisional: 10
- Pass 02 provisional: 20
- Pass 03 provisional: 21
- Pass 04 provisional: 29
- Pass 05 provisional: 33
- Pass 06 provisional: 35
- Pass 07 provisional: 40
- Pass 08 provisional: 44
- Pass 09 provisional: 42
- Pass 10 provisional: 43
- Pass 11 provisional: 44
- Pass 12 provisional: 43
- Pass 13 provisional: 43
- Pass 14 provisional: 42
- Pass 15 provisional: 42
- Pass 16 provisional: 42
- Pass 17 provisional: 42
- Pass 18 provisional: 42
- Pass 19 provisional: 42
- Pass 20 provisional: 42
- Pass 21 provisional: 42
- Pass 22 provisional: 42
- Pass 23 provisional: 42
- Pass 24 provisional: 42
- Pass 25 provisional: 42
- Pass 26 provisional: 42
- Pass 27 provisional: 42
- Pass 28 provisional: 42
- Pass 29 provisional: 42
- Pass 30 provisional: 42
- Pass 31 provisional: 42
- Pass 32 provisional: 42
- Pass 33 provisional: 42
- Pass 34 provisional: 42
- Pass 35 provisional: 42
- Pass 36 provisional: 42
- Pass 37 provisional: 42
- Pass 38 provisional: 42
- Pass 39 provisional: 42
- Pass 40 provisional: 42
- Pass 41 provisional: 42
- Pass 42 provisional: 42
- Current preserved plus provisional: 1787

NEXT DISCOVERY PASS:
Mining, extraction, tailings, hazardous materials, land rights, environmental justice, worker safety, closure, remediation, and long-term stewardship.

END PACKET 01.5 — DISCOVERY PASS 42
