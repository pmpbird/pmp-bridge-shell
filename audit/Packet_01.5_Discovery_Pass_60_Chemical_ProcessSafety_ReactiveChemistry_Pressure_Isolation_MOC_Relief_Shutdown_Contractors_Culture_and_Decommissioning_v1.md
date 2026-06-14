# Packet 01.5 — Discovery Pass 60

STATUS: DISCOVERY IN PROGRESS
PHASE: PROBLEM FINDING ONLY
ROUTING: NOT STARTED
COUNT MODE: NATURAL YIELD
DATE: 2026-06-14

This pass looks for chemical and high-hazard process-industry failure involving continuous-process plants, reactive chemistry, pressure systems, process isolation, management of change, relief systems, shutdown, contractor work, process-safety culture, emergency response, and decommissioning.

APPLICABILITY GATE: These are conditional future candidates, not proof of current app defects. They become applicable only if the project stores, interprets, recommends, coordinates, routes, or governs chemical-process, industrial-safety, plant-operation, maintenance, emergency, environmental, or decommissioning information, decisions, or services.

## Provisional records

### PROC-001 — Process safety model separates units that share utilities and material paths

Power, steam, cooling, control, ventilation, feed, storage, and waste systems may couple nominally independent units.

HARM: one upset propagates across the plant beyond the validated scenario.

OVERLAP TO CHECK: REFINERY-001, NUCSAFE-002.

### PROC-002 — Production target narrows the operating margin gradually

Throughput, energy efficiency, yield, inventory, maintenance delay, and staffing pressure may accumulate without one clear violation.

HARM: ordinary optimization converts a robust process into a brittle one.

OVERLAP TO CHECK: THROUGHPUT-001, MAINT-005.

### PROC-003 — Instrument reading is trusted after the process has left the sensor’s valid range

Temperature, pressure, flow, level, composition, and density may exceed calibration assumptions or become spatially uneven.

HARM: reassuring data continue while the real process moves into danger.

OVERLAP TO CHECK: CALIB-001, DAM-004.

### PROC-004 — Process model omits material already accumulated in dead legs, vessels, filters, and drains

Residual chemicals, deposits, contamination, and incompatible material may remain outside normal inventory accounting.

HARM: startup, cleaning, maintenance, or mixing encounters an unrecognized reactive mass.

OVERLAP TO CHECK: TRACE-004, HAZWASTE-002.

### PROC-005 — Plant layout forces emergency actions through the hazard area

Valves, controls, exits, muster points, sampling stations, and manual interventions may be located near the release or fire source.

HARM: the response plan requires people to enter the danger it is meant to control.

OVERLAP TO CHECK: SAFEGUARD-004, FIRE-004.

### REACT-001 — Reaction hazard is tested at laboratory scale but not at production scale

Heat removal, mixing, concentration, impurities, hold time, surface area, and equipment geometry may differ materially.

HARM: a reaction considered controllable becomes unstable after scale-up.

OVERLAP TO CHECK: LAB-001, TEST-005.

### REACT-002 — Trace contamination changes chemistry without changing the recipe

Water, oxygen, cleaning residue, corrosion products, prior batches, recycled material, and raw-material variation may alter behavior.

HARM: the documented formula produces an unexpected reaction pathway.

OVERLAP TO CHECK: CONTAM-002, QUALITY-003.

### REACT-003 — Delayed reaction is mistaken for no reaction

Induction periods, accumulation, poor mixing, low temperature, and slow decomposition may hide energy or gas generation.

HARM: operators add more material or leave the process unattended before the hazard emerges.

OVERLAP TO CHECK: TIME-001, INCDET-002.

### REACT-004 — Incompatible materials share transfer, drainage, or waste systems

Normal segregation may fail through hoses, shared manifolds, mislabeled containers, valves, sumps, and cleanup routes.

HARM: materials react outside the controlled process vessel.

OVERLAP TO CHECK: MEDWASTE-001, HAZWASTE-003.

### REACT-005 — Reaction knowledge remains with a few specialists rather than the operating system

Critical warning signs, impurity sensitivity, safe limits, and abnormal behavior may be poorly documented.

HARM: staff turnover removes the knowledge needed to recognize a developing runaway condition.

OVERLAP TO CHECK: DIRECTCARE-001, STEWARD-002.

### PRESSURE-001 — Pressure protection is sized for one initiating cause at a time

Fire, blocked flow, thermal expansion, reaction, utility failure, contamination, and control error may combine.

HARM: the protective system is overwhelmed by a credible multi-cause event.

OVERLAP TO CHECK: AIRCERT-002, CASCADE-001.

### PRESSURE-002 — Vessel condition is inferred from external inspection while internal damage progresses

Corrosion, erosion, cracking, fouling, lining failure, and localized thinning may remain hidden.

HARM: apparently intact equipment fails under ordinary operating pressure.

OVERLAP TO CHECK: PIPELINE-001, NUCSAFE-006.

### PRESSURE-003 — Pressure cycling is omitted from life assessment

Startups, shutdowns, trips, cleaning, batch changes, and control oscillation may create repeated stress.

HARM: equipment reaches fatigue failure earlier than calendar-based planning predicts.

OVERLAP TO CHECK: BATSTORE-001, STRUCT-002.

### PRESSURE-004 — Temporary hose, fitting, or portable equipment becomes permanent process infrastructure

Emergency substitutions and maintenance aids may remain in service beyond their intended duty.

HARM: lower-integrity components become hidden weak points in a high-energy system.

OVERLAP TO CHECK: REFINERY-003, MAINT-005.

### ISOLATE-001 — Lockout record does not match actual energy and material pathways

Electrical, hydraulic, pneumatic, thermal, chemical, gravity, pressure, and stored energy may have alternate routes.

HARM: maintenance begins while hazardous energy remains connected.

OVERLAP TO CHECK: GOVREC-001, GUARD-001.

### ISOLATE-002 — Closed valve is treated as positive isolation

Leakage, bypasses, valve failure, trapped pressure, wrong-line identification, and shared headers may remain.

HARM: workers open equipment that is still connected to hazardous material or energy.

OVERLAP TO CHECK: AUTHENT-001, PIPELINE-003.

### ISOLATE-003 — Isolation protects maintenance staff while destabilizing the running process

Removing equipment, utilities, sensors, or control paths may shift load or disable safeguards elsewhere.

HARM: safe maintenance on one item creates an unsafe operating condition in another area.

OVERLAP TO CHECK: CONTAIN-001, INTERACT-001.

### ISOLATE-004 — Restart occurs before temporary blinds, jumpers, bypasses, and tools are reconciled

Complex outages may leave the plant in an undocumented mixed configuration.

HARM: startup energizes a process that no longer matches the approved design.

OVERLAP TO CHECK: AIRMAINT-001, STRUCT-006.

### MOC-001 — Management of change captures hardware but misses software, staffing, procedures, and vendor behavior

Control logic, alarm settings, workforce skill, maintenance interval, raw material, and service contracts may alter risk without visible construction.

HARM: the plant changes materially outside the formal change process.

OVERLAP TO CHECK: REMOTE-003, GOV-002.

### MOC-002 — Temporary change escapes re-review because its expiration is not enforced

Bypasses, staffing exceptions, substitute materials, manual controls, and temporary repairs may persist.

HARM: exceptional risk becomes permanent without a permanent safety case.

OVERLAP TO CHECK: EXP-006, REFINERY-003.

### MOC-003 — Change review studies the modified item but not its interactions

Flow, pressure, heat, control, relief, maintenance, emergency, and human workload may shift elsewhere.

HARM: local improvement creates remote failure.

OVERLAP TO CHECK: FEATURE-001, PIPELINE-003.

### MOC-004 — Organizational change is excluded from process-safety review

Mergers, outsourcing, shift restructuring, remote support, leadership turnover, and budget cuts may alter competence and authority.

HARM: the plant’s safety system changes without any equipment modification.

OVERLAP TO CHECK: SUCCESS-001, BUILDCHAIN-003.

### MOC-005 — Documentation is updated after field implementation rather than before it

Drawings, procedures, training, labels, spare parts, and emergency plans may lag the installed change.

HARM: operators and responders act on the previous plant configuration.

OVERLAP TO CHECK: GOVREC-002, PIPELINE-005.

### RELIEF-001 — Relief path protects equipment while discharging into an unsafe destination

Vapor, liquid, heat, toxic material, or reaction products may reach occupied areas, drainage, flare, atmosphere, or nearby equipment.

HARM: pressure protection prevents rupture by creating another hazardous release.

OVERLAP TO CHECK: REFINERY-004, SEWAGE-002.

### RELIEF-002 — Shared relief system creates backpressure and interaction between units

Simultaneous discharges, fouling, liquid carryover, weather, and downstream restriction may reduce capacity.

HARM: protection for one unit weakens protection for others.

OVERLAP TO CHECK: MONO-001, PRESSURE-001.

### RELIEF-003 — Flare or treatment-system availability is assumed rather than proven during the initiating event

Power, pilot, steam, knockout, controls, weather, maintenance, and upstream composition may fail together.

HARM: hazardous discharge reaches an unready disposal system.

OVERLAP TO CHECK: GRIDFORM-002, PUBLICDEP-001.

### RELIEF-004 — Protective discharge remains below reporting thresholds while cumulative exposure grows

Small releases, repeated trips, maintenance venting, and low-level emissions may be treated individually.

HARM: chronic community and worker burden remains invisible inside event-by-event compliance.

OVERLAP TO CHECK: FOSSIL-002, RADHEALTH-002.

### SHUTDOWN-001 — Emergency shutdown sequence assumes utilities and instrumentation remain available

Power, air, cooling, communications, valves, and sensors may fail during the same event.

HARM: the safe-state path disappears when it is most needed.

OVERLAP TO CHECK: EMCONT-002, NUCSAFE-002.

### SHUTDOWN-002 — Shutdown stabilizes pressure while causing freezing, polymerization, settling, or contamination

Materials may become hazardous when flow, heat, agitation, or purge stops.

HARM: the immediate emergency ends but creates a difficult latent restart hazard.

OVERLAP TO CHECK: PERSIST-001, REACT-003.

### SHUTDOWN-003 — Production restart is authorized before abnormal-event causes are understood

Economic pressure, inventory needs, customer commitments, and apparent equipment recovery may drive early restart.

HARM: the plant re-enters service with the initiating weakness still present.

OVERLAP TO CHECK: RESTORE-002, DEAD-005.

### SHUTDOWN-004 — Black-start or cold-start procedure does not match aged or modified equipment

Long-idle seals, instruments, heaters, utilities, software, and temporary configurations may behave differently.

HARM: recovery creates new leaks, trips, or unstable process conditions.

OVERLAP TO CHECK: GRIDFORM-003, DECOMNUC-001.

### PROCWORK-001 — Contractor qualification does not include site-specific process knowledge

A worker may be technically skilled but unfamiliar with local chemistry, alarms, routes, isolation, and emergency expectations.

HARM: competent work is performed unsafely in the actual plant context.

OVERLAP TO CHECK: MUTUAL-003, DIRECTCARE-005.

### PROCWORK-002 — Simultaneous maintenance tasks interact across permits and work groups

Hot work, line opening, lifting, electrical work, cleaning, scaffolding, and testing may each be approved separately.

HARM: individually permitted work creates a combined hazardous condition.

OVERLAP TO CHECK: INTERACT-001, REFINERY-005.

### PROCWORK-003 — Contractor injury and near-miss data do not enter the owner’s learning system

Subcontracting, separate reporting, liability concern, and employment status may fragment evidence.

HARM: repeated warning signs remain invisible to the institution controlling the process.

OVERLAP TO CHECK: WASTELABOR-001, AUD-003.

### PROCWORK-004 — Schedule pressure shifts verification from independent check to mutual assumption

Operations, maintenance, contractors, and supervision may each believe another party confirmed the condition.

HARM: critical isolation, configuration, or readiness is never actually verified.

OVERLAP TO CHECK: ELDER-004, HANDOFF-005.

### PSMCULT-001 — Low incident count is treated as proof of strong process safety

Rare catastrophic hazards may remain while minor injury metrics and production reliability look favorable.

HARM: absence of recent disaster creates confidence without evidence of barrier health.

OVERLAP TO CHECK: QUALITY-001, MEAS-001.

### PSMCULT-002 — Reporting bad news is experienced as disloyalty or production obstruction

Career pressure, contractor status, hierarchy, blame, and incentive systems may suppress concerns.

HARM: weak signals disappear before they can prevent a major event.

OVERLAP TO CHECK: DEFCMD-004, MINEWORK-001.

### PSMCULT-003 — Personal-safety success distracts from process-safety degradation

Slip, trip, and routine injury programs may improve while containment, relief, corrosion, reaction, and control barriers weaken.

HARM: visible safety activity masks catastrophic-risk deterioration.

OVERLAP TO CHECK: FRAME-002, MEAS-004.

### PROCDECOM-001 — Plant closure begins before full hazardous inventory and contamination are known

Buried lines, residues, waste, groundwater, insulation, buildings, and undocumented modifications may remain.

HARM: workers and communities inherit hazards absent from the closure plan.

OVERLAP TO CHECK: ENDECOM-001, DECOMNUC-001.

### PROCDECOM-002 — Decommissioning removes operating expertise before hazardous systems are made safe

Specialists, operators, vendors, responders, and maintenance staff may leave as production ends.

HARM: the most unfamiliar dismantling work occurs after institutional knowledge disappears.

OVERLAP TO CHECK: DECOMNUC-002, STEWARD-002.

## Pass 60 result

Natural-yield provisional records: 40
Routing decisions made: 0
Records closed: 0
Deduplication required later: Yes
Discovery saturation: NOT REACHED

Corrected working total:
- Preserved baseline: 122
- Prior actual provisional headings: 2345
- Pass 60 natural-yield provisional: 40
- Current actual provisional headings: 2385
- Current combined working total: 2507

NEXT DISCOVERY PASS:
Pharmaceutical and medical-product lifecycle, including discovery, formulation, clinical development, manufacturing scale-up, regulatory approval, device lifecycle, recall, post-market field correction, and end-of-life.

END PACKET 01.5 — DISCOVERY PASS 60
