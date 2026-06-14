# Packet 01.5 — Discovery Pass 41

STATUS: DISCOVERY IN PROGRESS
PHASE: PROBLEM FINDING ONLY
ROUTING: NOT STARTED
DATE: 2026-06-13

This pass looks for manufacturing, robotics, machine-guarding, quality-control, counterfeit-component, maintenance, worker-machine interaction, product-traceability, recall, and physical-product-liability failure.

## Provisional records

### MANUF-001 — Production speed target overrides safe process limits

Cycle time, throughput, utilization, and delivery pressure may encourage operation beyond validated temperature, pressure, load, cure, or inspection limits.

HARM: output rises while hidden physical failure accumulates.

OVERLAP TO CHECK: LABOR-004, DEAD-005.

### MANUF-002 — Process capability is inferred from average performance

Mean output may look acceptable while variation, drift, edge conditions, and rare defects remain unsafe.

HARM: a stable average hides dangerous tails.

OVERLAP TO CHECK: MEAS-002, DESIGN-006.

### MANUF-003 — Line changeover carries prior material into the next product

Residue, tooling, software settings, labels, recipes, and fixtures may persist across batches.

HARM: one product contaminates or misconfigures the next.

OVERLAP TO CHECK: CONTAM-002, CHANGE-005.

### MANUF-004 — Work instruction does not match the current machine state

Paper, screen, memory, and actual configuration may diverge after repair, update, or local modification.

HARM: workers follow correct instructions for the wrong setup.

OVERLAP TO CHECK: DOC-005, OT-003.

### MANUF-005 — Temporary production workaround becomes normal operation

Bypasses, manual corrections, extra inspection, and improvised fixtures may persist after the urgent need ends.

HARM: degraded control becomes institutionalized without revalidation.

OVERLAP TO CHECK: RESTORE-004, PERSIST-001.

### MANUF-006 — Capacity planning ignores simultaneous equipment degradation

Machines sharing age, environment, supplier, maintenance window, or software may lose capacity together.

HARM: apparent redundancy disappears during common-mode failure.

OVERLAP TO CHECK: SAT-001, CASCADE-002.

### ROBOT-001 — Robot safety envelope is invalidated by layout change

New racks, tools, pallets, people, lighting, floors, or workstations may alter reach, visibility, stopping distance, and collision paths.

HARM: a previously safe cell becomes dangerous without robot-code change.

OVERLAP TO CHECK: LAB-003, CHANGE-001.

### ROBOT-002 — Collaborative robot treats human presence as predictable

Worker speed, posture, impairment, distraction, loose clothing, and unexpected entry may fall outside assumptions.

HARM: proximity control fails against real human variability.

OVERLAP TO CHECK: MOBILITY-001, REAL-001.

### ROBOT-003 — Vision system misclassifies reflective, transparent, damaged, or novel objects

Lighting, glare, dirt, occlusion, packaging, and deformation may change appearance.

HARM: the robot grips, rejects, or moves the wrong object.

OVERLAP TO CHECK: SENSE-003, REMSENSE-001.

### ROBOT-004 — Autonomous recovery repeats the hazardous motion

After jam, failed pick, sensor loss, or blocked path, the robot may retry without understanding the physical cause.

HARM: automation escalates equipment damage or worker exposure.

OVERLAP TO CHECK: AUTO-005, LAB-004.

### ROBOT-005 — Remote robot update changes motion behavior without local validation

Path planning, speed, force limits, perception, and stop logic may change through software or vendor service.

HARM: physical behavior changes before the site verifies it.

OVERLAP TO CHECK: VEH-003, REMOTE-001.

### ROBOT-006 — Human operator cannot tell when automation has degraded

A robot may silently fall back to reduced sensing, slower control, alternate logic, or manual confirmation.

HARM: workers assume full protection while operating under degraded capability.

OVERLAP TO CHECK: HEALTH-002, BOUND-001.

### GUARD-001 — Machine guard is removed because it obstructs routine work

Access, cleaning, setup, visibility, and speed pressure may encourage bypass or removal.

HARM: a known barrier disappears during the most frequent tasks.

OVERLAP TO CHECK: WKAUTH-003, HAZ-003.

### GUARD-002 — Interlock proves position but not protection

A switch may indicate closed while the guard is misaligned, damaged, defeated, or too weak.

HARM: electrical permission is mistaken for physical safety.

OVERLAP TO CHECK: AUTHENT-002, REAL-002.

### GUARD-003 — Lockout isolates expected energy but not stored or secondary energy

Gravity, pressure, heat, springs, capacitors, hydraulics, pneumatics, and backfeed may remain.

HARM: equipment moves or releases energy during maintenance.

OVERLAP TO CHECK: GRID-003, HAZ-001.

### GUARD-004 — Safety reset is reachable from outside the hazard view

A person may restart equipment without seeing who or what remains inside the guarded area.

HARM: reset converts hidden occupancy into immediate injury risk.

OVERLAP TO CHECK: EMSAFE-001, NAV-004.

### GUARD-005 — Safety device is tested functionally but not under real stopping load

Light curtains, brakes, scanners, relays, and emergency stops may pass low-stress tests.

HARM: the system fails only at full speed, mass, or momentum.

OVERLAP TO CHECK: TEST-005, VEH-002.

### QUALITY-001 — Inspection plan samples away the rare catastrophic defect

Routine sampling may miss intermittent, clustered, startup, shutdown, or supplier-specific failures.

HARM: high-consequence defects escape statistically acceptable inspection.

OVERLAP TO CHECK: CONTAM-004, DESIGN-004.

### QUALITY-002 — Automated inspection learns cosmetic rather than functional quality

Vision or sensor systems may focus on visible patterns correlated with past rejects.

HARM: attractive products pass while hidden functional defects remain.

OVERLAP TO CHECK: DESIGN-003, MEDIA-005.

### QUALITY-003 — Calibration reference is itself damaged, expired, or wrong

Gauges, masters, fixtures, software constants, and reference parts may drift or be misidentified.

HARM: the inspection system certifies products against a false standard.

OVERLAP TO CHECK: CALIB-001, LAB-001.

### QUALITY-004 — Rework removes evidence of the original defect

Grinding, welding, reflashing, retesting, relabeling, and manual correction may erase failure history.

HARM: recurring process problems become invisible.

OVERLAP TO CHECK: DATA-001, FORENSIC-003.

### QUALITY-005 — Supplier certificate substitutes for incoming verification

Documentation may be forged, copied, stale, incomplete, or valid only for a different lot.

HARM: trust in paperwork bypasses physical confirmation.

OVERLAP TO CHECK: AUTHENT-001, TRACEPROD-002.

### QUALITY-006 — Acceptance criteria shift quietly under schedule pressure

Deviations, concessions, waivers, and temporary limits may expand without customer or safety review.

HARM: defective output is redefined as acceptable.

OVERLAP TO CHECK: INCENT-001, RESTORE-004.

### COUNTERFEIT-001 — Counterfeit component passes visual and documentary checks

Markings, packaging, certificates, date codes, and serials may be convincingly copied.

HARM: unqualified parts enter safety-critical products.

OVERLAP TO CHECK: AUTHENT-005, SUPPLY-003.

### COUNTERFEIT-002 — Genuine component is harvested from unknown prior use

Recovered parts may have hidden fatigue, thermal, radiation, moisture, or electrical damage.

HARM: authentic identity disguises degraded condition.

OVERLAP TO CHECK: TRACE-003, LIFE-005.

### COUNTERFEIT-003 — Approved supplier sources from an unapproved sub-tier

Brokers, subcontractors, emergency purchasing, and allocation pressure may change origin invisibly.

HARM: trusted vendor status does not guarantee trusted provenance.

OVERLAP TO CHECK: CONTRACT-003, TRACE-001.

### COUNTERFEIT-004 — Software or firmware counterfeit alters physical component behavior

Cloned, modified, or unauthorized code may exist inside apparently genuine hardware.

HARM: inspection confirms the part while missing compromised behavior.

OVERLAP TO CHECK: FIRM-001, BUILD-005.

### COUNTERFEIT-005 — Scarcity-driven substitution preserves fit but not performance

A replacement may match dimensions or interface while differing in material, tolerance, rating, or durability.

HARM: short-term continuity creates latent field failure.

OVERLAP TO CHECK: RESCON-003, CHANGE-005.

### MAINT-001 — Preventive maintenance interval assumes average operating conditions

Dust, heat, vibration, humidity, overload, idle time, and cycling may age equipment differently.

HARM: service occurs too late for harsh conditions or wastes scarce capacity elsewhere.

OVERLAP TO CHECK: EXP-006, HW-003.

### MAINT-002 — Predictive-maintenance model misses novel failure modes

Models trained on known patterns may treat unseen deterioration as normal variation.

HARM: confidence remains high before an unfamiliar breakdown.

OVERLAP TO CHECK: MODEL-003, INCDET-002.

### MAINT-003 — Maintenance restores operation but changes alignment or configuration

Replacement, adjustment, lubrication, calibration, wiring, or software reset may alter behavior.

HARM: repair introduces a new defect while clearing the old alarm.

OVERLAP TO CHECK: RESTORE-002, QUALITY-003.

### MAINT-004 — Maintenance knowledge is concentrated in one worker or vendor

Undocumented settings, diagnosis, access, tools, and workarounds may reside with one person.

HARM: departure or unavailability makes safe repair impossible.

OVERLAP TO CHECK: CONTRACT-001, CARE-005.

### MAINT-005 — Deferred maintenance is hidden by repeated temporary fixes

Resets, patches, lubrication, tightening, bypasses, and component swaps may restore short-term function.

HARM: deteriorating equipment appears manageable until catastrophic failure.

OVERLAP TO CHECK: MANUF-005, PERSIST-001.

### TRACEPROD-001 — Product genealogy breaks when lots are mixed or split

Bulk material, rework, assembly, repackaging, and subcontracting may combine or divide traceable units.

HARM: affected products cannot be isolated during defect investigation.

OVERLAP TO CHECK: TRACE-002, LOGISTICS-003.

### TRACEPROD-002 — Serial or lot record proves identity but not configuration

The same product identifier may span firmware, supplier, material, process, or repair differences.

HARM: recall scope is too broad, too narrow, or wrong.

OVERLAP TO CHECK: VER-001, QUALITY-005.

### TRACEPROD-003 — Field repair is not written back into the product record

Replacement parts, software, damage, inspection, and local modification may remain off-system.

HARM: later service and safety decisions use an obsolete product history.

OVERLAP TO CHECK: EMPREC-002, GOVREC-002.

### TRACEPROD-004 — Recall message cannot identify who currently possesses the product

Resale, rental, gifting, export, secondhand markets, and address changes may break customer linkage.

HARM: dangerous products remain in use after a valid recall.

OVERLAP TO CHECK: CONTAM-005, COMMS-001.

### LIAB-001 — Responsibility is fragmented across designer, manufacturer, integrator, operator, and updater

Multiple parties may control hardware, software, setup, maintenance, and use.

HARM: each actor attributes the failure to another layer.

OVERLAP TO CHECK: GOV-006, CONTRACT-003.

### LIAB-002 — Product warning transfers unreasonable burden to the user

Dense labels, manuals, training, and disclaimers may attempt to compensate for unsafe design.

HARM: foreseeable misuse is reframed as user fault.

OVERLAP TO CHECK: TERMS-001, DOC-005.

### LIAB-003 — Software update changes the product after certification or sale

Performance, safety limits, interfaces, data use, and failure behavior may change remotely.

HARM: the product in use differs from the product evaluated and purchased.

OVERLAP TO CHECK: VEH-003, REMOTE-003.

### LIAB-004 — Evidence needed for product-failure analysis is controlled by the manufacturer

Logs, telemetry, design data, error codes, and update history may be proprietary or erasable.

HARM: injured users and investigators cannot independently reconstruct failure.

OVERLAP TO CHECK: VEH-006, PEER-004.

### LIAB-005 — Recall remedy does not cover downstream loss

Repair or replacement may not address injury, downtime, contamination, missed work, or damage to connected systems.

HARM: the defective product is corrected while the real consequences remain uncompensated.

OVERLAP TO CHECK: INSUR-006, DUE-006.

## Pass 41 result

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
- Current preserved plus provisional: 1745

NEXT DISCOVERY PASS:
Construction, buildings, structural safety, fire protection, building codes, inspections, occupancy, accessibility, materials, contractor chains, and disaster resilience.

END PACKET 01.5 — DISCOVERY PASS 41
