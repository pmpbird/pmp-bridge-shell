# Packet 01.5 — Discovery Pass 36

STATUS: DISCOVERY IN PROGRESS
PHASE: PROBLEM FINDING ONLY
ROUTING: NOT STARTED
DATE: 2026-06-14

This pass looks for critical-infrastructure and utility failure involving electricity, water, telecommunications, operational technology, industrial control, cascading dependency, public reliance, and recovery under constrained resources.

## Provisional records

### GRID-001 — Load forecast excludes rare compound demand

Heat, smoke, evacuation, charging, medical equipment, industrial restart, and communication demand may rise together.

HARM: capacity planning passes ordinary peaks but fails during compound stress.

OVERLAP TO CHECK: ENVRES-002, ALLOC-001.

### GRID-002 — Protective shutdown is mistaken for equipment failure

Automatic isolation, frequency protection, thermal protection, and fault clearing may appear as unexplained outage.

HARM: operators restore power without understanding the condition that required shutdown.

OVERLAP TO CHECK: CONTAIN-001, INCDET-001.

### GRID-003 — Distributed generation creates hidden backfeed risk

Solar, batteries, generators, vehicles, and local microgrids may energize circuits assumed to be dead.

HARM: workers and residents encounter lethal voltage during repair or evacuation.

OVERLAP TO CHECK: HAZ-001, EMSAFE-001.

### GRID-004 — Remote-control compromise changes physical power flow

Substations, breakers, inverters, charging systems, and load controls may be manipulated through connected systems.

HARM: cyber compromise becomes blackout, fire, equipment damage, or public-safety failure.

OVERLAP TO CHECK: VEH-005, AUTHN-001.

### GRID-005 — Grid restoration creates a damaging demand surge

Heating, cooling, pumps, chargers, appliances, and industrial loads may all restart simultaneously.

HARM: restored power triggers another failure or damages equipment.

OVERLAP TO CHECK: REBOUND-001, RESTORE-002.

### GRID-006 — Priority power allocation lacks transparent criteria

Hospitals, shelters, water systems, communications, businesses, homes, and vulnerable individuals may compete for limited supply.

HARM: hidden value judgments determine who receives essential power.

OVERLAP TO CHECK: ALLOC-001, ESSENTIAL-001.

### WATERUTIL-001 — Water-quality monitoring samples too little of the system

Contamination may vary by neighborhood, pipe, pressure zone, storage tank, building, and time.

HARM: compliant samples coexist with unsafe water elsewhere.

OVERLAP TO CHECK: CONTAM-004, MEAS-002.

### WATERUTIL-002 — Pressure loss allows contamination intrusion

Breaks, outages, firefighting, pump failure, and maintenance may draw groundwater or sewage into distribution lines.

HARM: restored flow carries hidden contamination.

OVERLAP TO CHECK: COLD-004, CONTAM-002.

### WATERUTIL-003 — Boil or do-not-use notice is unclear or delayed

Different hazards require different actions, and notices may not reach all languages, buildings, institutions, or disconnected users.

HARM: people follow the wrong protective action or receive none.

OVERLAP TO CHECK: TRANSIT-002, COMMS-001.

### WATERUTIL-004 — Automated treatment responds to faulty sensor data

Chemical dosing, pumping, filtration, and disinfection may continue after calibration drift, fouling, spoofing, or signal loss.

HARM: automation creates unsafe water while dashboards appear normal.

OVERLAP TO CHECK: CALIB-001, LAB-004.

### WATERUTIL-005 — Wastewater failure contaminates downstream systems

Power loss, flooding, blockage, overflow, and treatment failure may affect rivers, agriculture, recreation, and drinking-water sources.

HARM: one utility failure propagates across health and environment.

OVERLAP TO CHECK: CONTAM-006, CASCADE-001.

### WATERUTIL-006 — Restoration confirms pressure but not water safety

Service may resume before flushing, testing, building-level checks, and public notice are complete.

HARM: operational restoration is mistaken for safe restoration.

OVERLAP TO CHECK: TRACE-003, RESTORE-003.

### TELECOM-001 — Network availability metric excludes emergency usability

A network may be technically online while overloaded, power-limited, inaccessible, or unable to reach emergency services.

HARM: reported uptime overstates real communication capacity.

OVERLAP TO CHECK: REAL-002, OBS-001.

### TELECOM-002 — Backup power duration is shorter than the outage

Cell sites, exchanges, routers, towers, and local equipment may exhaust batteries or fuel after initial survival.

HARM: communications fail late, when public dependence has increased.

OVERLAP TO CHECK: BAT-004, ENVRES-002.

### TELECOM-003 — Emergency traffic competes with automated background traffic

Updates, backups, media, telemetry, retries, and device synchronization may consume scarce bandwidth.

HARM: nonessential automation blocks urgent communication.

OVERLAP TO CHECK: ECON-005, QUEUE-001.

### TELECOM-004 — Geographic failover preserves service but changes surveillance and jurisdiction

Traffic may be rerouted through different regions, providers, or government-access regimes.

HARM: emergency resilience silently changes privacy conditions.

OVERLAP TO CHECK: ENVRES-004, JUR-002.

### TELECOM-005 — Public warning depends on one communication channel

SMS, apps, radio, sirens, social media, email, and landlines may not reach the same people.

HARM: channel-specific failure leaves parts of the public uninformed.

OVERLAP TO CHECK: NOTIFY-003, CIVIC-006.

### OT-001 — Operational technology remains on unsupported software

Industrial systems may depend on old operating systems, firmware, protocols, hardware, and vendor tools that cannot be updated safely.

HARM: known vulnerabilities persist because replacement threatens operation.

OVERLAP TO CHECK: LIFE-005, FIRM-001.

### OT-002 — Safety system and production system share dependencies

Power, network, identity, time, sensors, controllers, and vendor access may support both operation and emergency shutdown.

HARM: one failure disables the process and its protection simultaneously.

OVERLAP TO CHECK: MONO-001, INTERACT-001.

### OT-003 — Remote maintenance bypasses local operational context

A vendor may change logic, thresholds, firmware, or configuration without seeing physical conditions, staffing, or maintenance state.

HARM: technically valid change creates unsafe physical behavior.

OVERLAP TO CHECK: REMOTE-001, LAB-003.

### OT-004 — Manual fallback has not been practiced under real constraints

Paper procedures, local controls, radio communication, and human operation may exist but be slow, incomplete, or unfamiliar.

HARM: nominal fallback fails during actual automation loss.

OVERLAP TO CHECK: LABOR-006, JOBSKILL-004.

### OT-005 — Alarm flood hides the initiating event

One physical disturbance may generate thousands of secondary alerts across controllers, sensors, and interfaces.

HARM: operators respond to symptoms while the root cause expands.

OVERLAP TO CHECK: NOTIFY-004, INCDET-003.

### OT-006 — Physical process continues after monitoring is lost

Flow, pressure, heat, chemical reaction, rotating equipment, and stored energy may persist without visibility.

HARM: loss of data is mistaken for loss of hazard.

OVERLAP TO CHECK: REAL-001, HAZ-006.

### CASCADE-001 — Utility dependencies form an unrecorded loop

Electricity needs fuel and telecom; telecom needs electricity; water needs pumps; fuel delivery needs transport and payment.

HARM: restoration plans assume resources that depend on the failed system.

OVERLAP TO CHECK: MONO-001, ESSENTIAL-003.

### CASCADE-002 — Small local failure propagates through synchronized automation

Shared schedules, common software, uniform settings, and automated responses may cause many systems to fail similarly.

HARM: standardization converts one defect into regional outage.

OVERLAP TO CHECK: CROP-002, PRICE-005.

### CASCADE-003 — Public behavior amplifies infrastructure stress

Panic buying, simultaneous charging, evacuation, water storage, fuel demand, and repeated status checking may overload systems.

HARM: protective individual actions create collective failure.

OVERLAP TO CHECK: REBOUND-001, EMROUTE-002.

### CASCADE-004 — Interdependency is visible only after restoration begins

A utility may appear ready but require unavailable telecom, chemicals, staff, transport, cooling, or authentication.

HARM: recovery stalls after scarce resources have already been committed.

OVERLAP TO CHECK: LOGISTICS-001, RESTORE-001.

### CASCADE-005 — Financial and contractual failure interrupts physical infrastructure

Payment, insurance, vendor access, licensing, subscription, or procurement issues may stop maintenance and operation.

HARM: administrative failure becomes public physical outage.

OVERLAP TO CHECK: PAY-001, CONTRACT-001.

### RESTORE-001 — Restoration priority ignores dependency order

Power may return before cooling, telecom before authentication, or water before treatment and testing.

HARM: restored components cannot operate safely or trigger new damage.

OVERLAP TO CHECK: CASCADE-004, GRID-005.

### RESTORE-002 — Automatic restart restores unsafe pre-failure state

Valves, motors, heaters, pumps, access systems, and scheduled processes may resume without human verification.

HARM: recovery reactivates the condition that caused or worsened the incident.

OVERLAP TO CHECK: AUTO-005, GRID-005.

### RESTORE-003 — Service restoration is declared before downstream users are safe

Buildings, medical devices, industrial customers, food storage, and private infrastructure may remain damaged or contaminated.

HARM: public restoration status causes unsafe reuse.

OVERLAP TO CHECK: WATERUTIL-006, COLD-003.

### RESTORE-004 — Temporary emergency configuration becomes permanent

Bypasses, manual overrides, reduced monitoring, shared credentials, and temporary routing may remain after urgency ends.

HARM: degraded controls become the new normal.

OVERLAP TO CHECK: PERSIST-001, DEPR-001.

### RESTORE-005 — Recovery workforce is unavailable or overextended

The same specialists may be needed across electricity, water, telecom, transport, fuel, hospitals, and vendors.

HARM: plans overbook scarce human capability.

OVERLAP TO CHECK: LABOR-003, CARE-005.

### PUBLICDEP-001 — Household survival assumes uninterrupted utilities

Medical devices, refrigeration, heating, cooling, sanitation, communication, and mobility may depend on continuous service.

HARM: ordinary outage becomes immediate health or safety emergency.

OVERLAP TO CHECK: HOUSE-004, ESSENTIAL-001.

### PUBLICDEP-002 — Vulnerable users are absent from outage models

People using oxygen, dialysis, mobility devices, refrigerated medicine, elevators, or home care may not be identified safely.

HARM: restoration priorities ignore those with the shortest survival margin.

OVERLAP TO CHECK: MOBILITY-001, HEALTH-005.

### PUBLICDEP-003 — Public contingency guidance assumes money, transport, and storage

Advice may require fuel, generators, batteries, bottled water, hotels, food, or relocation.

HARM: emergency preparation excludes low-resource households.

OVERLAP TO CHECK: FOODACCESS-002, EMROUTE-003.

### PUBLICDEP-004 — Critical-infrastructure status disclosure creates security risk

Publishing exact failures, reserves, access points, weak sites, and restoration order may aid attackers.

HARM: transparency intended for trust exposes operational vulnerability.

OVERLAP TO CHECK: PUB-006, DUAL-003.

### PUBLICDEP-005 — Utility disconnection process lacks meaningful emergency protection

Billing, identity, fraud, landlord conflict, or administrative error may interrupt essential service.

HARM: procedural dispute creates physical danger.

OVERLAP TO CHECK: ESSENTIAL-001, ABUSE-003.

### RESCON-001 — Emergency resources are counted without condition or compatibility

Generators, pumps, radios, fuel, batteries, parts, and vehicles may be damaged, expired, incompatible, or inaccessible.

HARM: inventory exists on paper but cannot support restoration.

OVERLAP TO CHECK: LOGISTICS-001, TRACE-003.

### RESCON-002 — Fuel and spare-part allocation favors visible systems over hidden dependencies

Public-facing services may receive resources while treatment, cooling, control, or communication support remains unfunded.

HARM: high-visibility recovery prevents complete recovery.

OVERLAP TO CHECK: ALLOC-001, COST-004.

### RESCON-003 — Emergency procurement weakens quality and security controls

Urgency may introduce counterfeit parts, unverified vendors, shared credentials, unsafe substitutes, and undocumented changes.

HARM: rapid recovery creates latent failure and compromise.

OVERLAP TO CHECK: SUPPLY-003, RESTORE-004.

### RESCON-004 — Mutual-aid resources cannot integrate with local systems

Different connectors, frequencies, procedures, credentials, data formats, safety rules, and command structures may block assistance.

HARM: available external support cannot be used when needed.

OVERLAP TO CHECK: COLLAB-002, PORT-001.

## Pass 36 result

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
- Current preserved plus provisional: 1535

NEXT DISCOVERY PASS:
Media, advertising, persuasion, recommender systems, attention capture, political influence, dark patterns, consumer autonomy, and manipulation-resistant communication.

END PACKET 01.5 — DISCOVERY PASS 36
