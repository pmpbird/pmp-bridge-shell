# Packet 01.5 — Discovery Pass 63

STATUS: DISCOVERY IN PROGRESS
PHASE: PROBLEM FINDING ONLY
ROUTING: NOT STARTED
COUNT MODE: NATURAL YIELD
DATE: 2026-06-14

This pass looks for rail-system and mass-freight-corridor failure involving signaling, dispatch, train integrity, grade crossings, track and rolling-stock maintenance, dangerous-goods trains, passenger evacuation, automation, corridor communities, and accident investigation.

APPLICABILITY GATE: These are conditional future candidates, not proof of current app defects. They become applicable only if the project stores, interprets, recommends, coordinates, routes, or governs rail, transit, freight, signaling, maintenance, emergency, hazardous-cargo, passenger, corridor, or investigation information, decisions, or services.

## Provisional records

### RAILSIG-001 — Signal indication is trusted after track occupancy data become stale or incomplete

Broken circuits, communication loss, sensor contamination, maintenance, software fault, and unusual vehicle behavior may distort block status.

HARM: a safe-looking movement authority is issued against an uncertain track state.

OVERLAP TO CHECK: ATC-001, OBS-003.

### RAILSIG-002 — Fail-safe design creates a dangerous operational workaround under persistent fault

Repeated restrictive indications may encourage manual authority, procedural bypass, or normalized delay pressure.

HARM: a protection system remains technically safe while human adaptation erodes the barrier.

OVERLAP TO CHECK: REFINERY-003, ALERT-001.

### RAILSIG-003 — Interlocking logic is changed without revalidating every route interaction

Software, switch layout, temporary track, maintenance state, and operating rules may alter conflict protection.

HARM: individually approved changes create an unsafe route combination.

OVERLAP TO CHECK: GRIDFORM-001, MOC-003.

### RAILSIG-004 — Positive-train-control coverage ends at the boundary of a mixed system

Yards, terminals, industrial tracks, low-speed zones, legacy lines, and foreign equipment may use different protections.

HARM: operators assume continuous protection where responsibility and capability change.

OVERLAP TO CHECK: MIXVER-001, AUTHZ-006.

### RAILSIG-005 — Wayside and onboard systems disagree without a clear authority rule

Map, speed limit, switch state, work zone, temporary restriction, and consist data may conflict.

HARM: crew and automation act on different versions of the railway.

OVERLAP TO CHECK: GOVREC-001, AVAUTO-001.

### RAILDISP-001 — Dispatch optimization reduces recovery margin between trains

Tighter meets, shorter headways, complex precedence, and limited sidings may improve throughput while reducing flexibility.

HARM: minor delay or fault propagates into network-wide congestion and unsafe pressure.

OVERLAP TO CHECK: ATC-002, THROUGHPUT-001.

### RAILDISP-002 — Dispatcher workload is measured by train count rather than conflict complexity

Weather, maintenance windows, mixed traffic, hazardous cargo, crew limits, and infrastructure faults may make a small territory cognitively dense.

HARM: nominal staffing hides decision overload.

OVERLAP TO CHECK: INCCMD-002, COG-001.

### RAILDISP-003 — Handoff between dispatch territories loses abnormal context

Brake issue, track condition, crew concern, dangerous cargo, temporary restriction, and emergency coordination may not transfer fully.

HARM: the receiving dispatcher manages a train without critical operational context.

OVERLAP TO CHECK: ATC-003, HANDOFF-005.

### RAILDISP-004 — Centralized dispatch becomes a common-mode operational dependency

Power, telecom, software, cyber compromise, staffing, and building access may affect a large territory simultaneously.

HARM: one control-center failure immobilizes or destabilizes an entire network.

OVERLAP TO CHECK: CLEARSET-004, MONO-001.

### TRAININT-001 — Train length and weight are treated as sufficient measures of handling behavior

Distributed power, slack, grade, curvature, loading pattern, braking condition, and weather may alter in-train forces.

HARM: a compliant consist experiences separation, derailment, or loss of control.

OVERLAP TO CHECK: FLIGHTOPS-003, MEAS-002.

### TRAININT-002 — Brake continuity test does not reveal degraded performance under real heat and grade

Temperature, contamination, wear, moisture, leakage, repeated application, and long descent may change braking.

HARM: a train passes departure testing but cannot stop within the expected margin.

OVERLAP TO CHECK: TEST-005, AIRMAINT-001.

### TRAININT-003 — Consist records diverge from the physical train after switching and interchange

Cars, loads, order, hazardous material, brakes, and ownership may change across yards and carriers.

HARM: crew, dispatch, responders, and maintenance act on the wrong train identity.

OVERLAP TO CHECK: TRACEPROD-002, AIRCARGO-002.

### TRAININT-004 — Distributed-power communication failure changes train forces without obvious visual indication

Command delay, loss, fallback mode, terrain, and antenna conditions may alter synchronized traction and braking.

HARM: automation intended to improve handling creates hidden longitudinal stress.

OVERLAP TO CHECK: AVAUTO-002, TELECOM-001.

### TRAININT-005 — Defective car is moved under a temporary condition that becomes extended service

Inspection waiver, speed restriction, shop delay, routing pressure, and limited repair capacity may prolong operation.

HARM: a controlled exception becomes normalized network risk.

OVERLAP TO CHECK: AIRMAINT-002, MOC-002.

### CROSSING-001 — Grade-crossing timing assumes vehicle and pedestrian behavior that does not match the site

Long vehicles, school buses, wheelchairs, queues, turning traffic, poor sight distance, and road signals may change clearance time.

HARM: technically correct warning time remains insufficient for real users.

OVERLAP TO CHECK: MASSEVAC-001, BLDACC-002.

### CROSSING-002 — Crossing protection operates normally while road congestion traps users on the track

Downstream signals, construction, events, emergency queues, and blocked intersections may remove escape space.

HARM: warning begins after the vehicle has nowhere to go.

OVERLAP TO CHECK: COAST-005, LOGISTICS-002.

### CROSSING-003 — Repeated false activations train the public to ignore protection

Track circuits, switching, maintenance, slow trains, and long closures may produce frequent nonhazardous warnings.

HARM: warning fatigue weakens response to the one event that requires immediate compliance.

OVERLAP TO CHECK: VOLCANO-003, ALERT-001.

### CROSSING-004 — Closure or separation project shifts access burden onto nearby communities

Long detours, emergency response, school access, walking, farming, business, and disability may be affected.

HARM: rail safety improves locally while mobility and emergency risk are transferred elsewhere.

OVERLAP TO CHECK: COAST-001, EJ-001.

### TRACK-001 — Track inspection frequency does not match rapidly changing local conditions

Heat, cold, flood, fire, landslide, vegetation, heavy axle loads, and maintenance disturbance may accelerate degradation.

HARM: a recently inspected segment becomes unsafe before the next planned check.

OVERLAP TO CHECK: LANDSLIDE-001, STRUCT-002.

### TRACK-002 — Automated inspection detects geometry but misses context and causation

Drainage, subgrade, contamination, recurring impact, adjacent construction, and maintenance quality may not be visible in the measured defect.

HARM: repeated repair treats the symptom while the failure mechanism continues.

OVERLAP TO CHECK: RESTORE-002, ROBOT-003.

### TRACK-003 — Temporary speed restriction remains undocumented or inconsistently propagated

Dispatch, onboard systems, crews, work gangs, maps, and contractors may receive different versions.

HARM: train speed authority does not match the actual infrastructure condition.

OVERLAP TO CHECK: GOVREC-002, RAILSIG-005.

### TRACK-004 — Maintenance possession protects workers while disrupting adjacent live operations

Track access, single tracking, temporary routing, work equipment, signals, and communication may change risk elsewhere.

HARM: safe work on one segment creates unsafe congestion or conflict on another.

OVERLAP TO CHECK: ISOLATE-003, PROCWORK-002.

### TRACK-005 — Deferred drainage maintenance becomes a track and slope failure

Blocked culverts, erosion, saturation, washout, frost, and debris may remain outside core track metrics.

HARM: water-management neglect produces sudden loss of alignment or support.

OVERLAP TO CHECK: WATERSHED-004, LANDSLIDE-002.

### ROLL-001 — Rolling-stock inspection misses defects hidden by loading or assembly

Bearings, wheels, axles, brakes, couplers, suspension, doors, and structural damage may not be observable in routine checks.

HARM: a serviceable-looking vehicle fails under dynamic load.

OVERLAP TO CHECK: PRESSURE-002, AIRMAINT-001.

### ROLL-002 — Hot-bearing detection threshold misses rapid failure between detectors

Sensor spacing, weather, calibration, train speed, shielding, and defect progression may limit warning.

HARM: a developing bearing failure becomes a derailment before the next observation point.

OVERLAP TO CHECK: INCDET-002, MARMON-001.

### ROLL-003 — Passenger-door control confirms command without confirming safe physical closure

Obstruction, platform gap, sensor failure, crowding, mobility devices, and manual intervention may create mismatch.

HARM: train movement begins with a person or object endangered at the doorway.

OVERLAP TO CHECK: NOTIFY-003, UI-003.

### ROLL-004 — Maintenance history is fragmented across owners, lessors, carriers, and repair shops

Parts, mileage, loads, damage, software, inspections, and modifications may not follow the vehicle reliably.

HARM: lifecycle decisions rely on an incomplete condition history.

OVERLAP TO CHECK: MEDDEV-005, AIRMAINT-004.

### HAZRAIL-001 — Hazardous-cargo manifest does not match current car order and contents

Switching, interchange, relabeling, mixed loads, residue, and record delay may change the physical train.

HARM: responders and crews act on incorrect location and hazard information.

OVERLAP TO CHECK: MARTRANS-004, TRAININT-003.

### HAZRAIL-002 — Routing minimizes network cost while concentrating community exposure

Population, water, schools, hospitals, terrain, evacuation, and response capacity may be secondary to distance and congestion.

HARM: economic efficiency transfers catastrophic risk to less powerful corridor communities.

OVERLAP TO CHECK: FUELMGMT-005, EJ-001.

### HAZRAIL-003 — Emergency braking or derailment control increases release risk for certain cargoes

Train forces, car placement, tank condition, terrain, heat, and adjacent materials may shape consequence.

HARM: action intended to stop movement worsens containment failure.

OVERLAP TO CHECK: RELIEF-001, CONTAIN-001.

### HAZRAIL-004 — Corridor responders lack current equipment and material-specific readiness

Rural departments, mutual aid, water supply, protective equipment, mapping, and communication may be limited.

HARM: a transport network moves hazards beyond the emergency capacity of the communities along it.

OVERLAP TO CHECK: HYDROGEN-004, MUTUAL-001.

### RAILPAX-001 — Platform and train accessibility fail at the transfer between systems

Vehicle floor, gap, lift, ramp, staff, signage, ticketing, elevator, and emergency route may not work together.

HARM: each component is compliant while the journey remains unusable or unsafe.

OVERLAP TO CHECK: SANACC-002, BLDACC-001.

### RAILPAX-002 — Emergency evacuation assumes passengers can self-extract to a safe trackside location

Tunnel, bridge, smoke, darkness, electrification, disability, children, luggage, weather, and terrain may block movement.

HARM: certified evacuation assumptions fail in the real environment.

OVERLAP TO CHECK: AIRPAX-001, SHELTER-001.

### RAILPAX-003 — Crowd-management action protects platform capacity while stranding vulnerable travelers

Gate closure, skipped stops, express operation, queueing, and rerouting may disproportionately affect people with mobility, language, caregiving, or time constraints.

HARM: system recovery transfers delay and exclusion to those least able to adapt.

OVERLAP TO CHECK: PHALLOC-004, ATC-002.

### RAILPAX-004 — Service restoration is announced before the whole passenger journey is functional

Connecting lines, elevators, stations, ticketing, information, last-mile transport, and staffing may remain unavailable.

HARM: passengers enter a partially restored system and become stranded.

OVERLAP TO CHECK: RESTORE-003, AIRPORT-005.

### RAILAUTO-001 — Automated train operation depends on infrastructure state it cannot fully observe

Track workers, debris, intrusion, weather, degraded signals, platform behavior, and local operating exceptions may remain outside the model.

HARM: correct automated behavior against incomplete state creates collision or entrapment risk.

OVERLAP TO CHECK: AVAUTO-001, SENSE-003.

### RAILAUTO-002 — Automation hands control to a human after skill and situational awareness have decayed

Long routine operation may reduce manual route knowledge, degraded-mode practice, and readiness.

HARM: the human receives responsibility at the point of greatest complexity with the least current context.

OVERLAP TO CHECK: AIRCREW-002, AUTO-005.

### RAILINV-001 — Accident investigation overweights the final crew action and underweights network conditions

Scheduling, maintenance, staffing, training, design, contractor work, management pressure, and regulation may be treated as background.

HARM: blame closes around the last operator while systemic causes persist.

OVERLAP TO CHECK: AIRINV-001, WKAUTH-003.

### RAILINV-002 — Safety recommendation is closed by rule change without proving field risk reduction

Bulletins, training, inspections, software, and procedures may satisfy closure while behavior and infrastructure remain unchanged.

HARM: formal completion substitutes for evidence that recurrence is less likely.

OVERLAP TO CHECK: AIRINV-002, POST-003.

## Pass 63 result

Natural-yield provisional records: 39
Routing decisions made: 0
Records closed: 0
Deduplication required later: Yes
Discovery saturation: NOT REACHED

Corrected working total:
- Preserved baseline: 122
- Prior actual provisional headings: 2463
- Pass 63 natural-yield provisional: 39
- Current actual provisional headings: 2502
- Current combined working total: 2624

NEXT REQUIRED STEP:
Run Major-Domain Coverage Audit v3. Reassess the complete major-domain map, test whether Passes 55–63 close the nine outstanding families from Audit v2, search again for omitted major families, and do not begin cross-domain saturation testing unless no major missing or materially partial family remains.

END PACKET 01.5 — DISCOVERY PASS 63
