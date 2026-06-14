# Packet 01.5 — Discovery Pass 40

STATUS: DISCOVERY IN PROGRESS
PHASE: PROBLEM FINDING ONLY
ROUTING: NOT STARTED
DATE: 2026-06-13

This pass looks for space-system failure involving satellites, remote sensing, launch, orbital debris, positioning-navigation-timing dependence, ground-segment control, access inequality, dual use, and recovery from space-service loss.

## Provisional records

### SPACE-001 — Space-service dependency is hidden inside ordinary systems

Banking, telecom, transport, weather, agriculture, emergency response, power grids, and logistics may rely on satellites without exposing that dependency.

HARM: a space-service disruption causes failures that appear unrelated and are hard to diagnose.

OVERLAP TO CHECK: CASCADE-001, TELECOM-001.

### SPACE-002 — Space environment assumptions are treated as stable

Radiation, solar storms, atmospheric drag, charging, temperature, and geomagnetic conditions may exceed design expectations.

HARM: systems fail under conditions omitted from normal reliability planning.

OVERLAP TO CHECK: ENVRES-001, HW-003.

### SPACE-003 — Mission success metric excludes downstream public harm

Coverage, uptime, revisit rate, launch success, or data volume may improve while privacy, inequality, environmental, or safety harms rise.

HARM: technical success masks societal failure.

OVERLAP TO CHECK: MEAS-001, LABOR-001.

### SPACE-004 — Space-service loss lacks a practiced terrestrial fallback

Users may have no tested alternative for timing, navigation, communication, weather, imaging, or coordination.

HARM: nominal redundancy fails when satellite service disappears.

OVERLAP TO CHECK: OT-004, LABOR-006.

### SPACE-005 — Mission lifetime extension exceeds original risk assumptions

Aging hardware, batteries, sensors, propulsion, shielding, memory, and software may operate long beyond planned service life.

HARM: continued usefulness hides rising failure probability and degraded control.

OVERLAP TO CHECK: LIFE-005, FIRM-001.

### SPACE-006 — Space-system ownership changes without continuity of obligations

Acquisition, bankruptcy, restructuring, or state transfer may alter maintenance, privacy, safety, and deorbit responsibility.

HARM: long-lived infrastructure loses a clearly accountable steward.

OVERLAP TO CHECK: SUCCESS-001, OWN-001.

### SAT-001 — Constellation health appears normal while common-mode failure grows

Shared hardware, software, suppliers, or command systems may affect many satellites simultaneously.

HARM: fleet scale turns one defect into global service loss.

OVERLAP TO CHECK: CASCADE-002, CROP-002.

### SAT-002 — Satellite safe mode preserves hardware but removes essential service

Protective behavior may stop payload, timing, communication, or observation functions.

HARM: survivability of the satellite conflicts with continuity for users.

OVERLAP TO CHECK: GRID-002, CONTAIN-001.

### SAT-003 — Onboard autonomy acts on stale or incomplete ground intent

Communication delay, outage, or schedule conflict may leave the spacecraft operating from old objectives.

HARM: autonomous behavior remains internally valid but operationally wrong.

OVERLAP TO CHECK: AUTO-005, SCHED-007.

### SAT-004 — Satellite sensor calibration drifts without obvious failure

Radiation, contamination, aging, thermal cycling, and component change may bias measurements gradually.

HARM: inaccurate data remains trusted because the instrument still functions.

OVERLAP TO CHECK: CALIB-001, SENSE-003.

### SAT-005 — Crosslink failure partitions the constellation

Satellites may continue operating locally while routing, coordination, timing, or fleet awareness fragments.

HARM: partial operation is mistaken for coherent service.

OVERLAP TO CHECK: SYNC-003, NET-001.

### SAT-006 — Satellite end-of-life state is not reliably controlled

Fuel limits, power loss, command failure, or ownership ambiguity may prevent disposal or passivation.

HARM: inactive spacecraft remain collision, debris, and interference hazards.

OVERLAP TO CHECK: EWASTE-004, SPACE-006.

### REMSENSE-001 — Remote-sensing image is treated as direct ground truth

Cloud, angle, resolution, processing, season, shadows, and sensor limits may change what appears visible.

HARM: interpretation exceeds what the observation can support.

OVERLAP TO CHECK: MEDINT-002, MEDIA-005.

### REMSENSE-002 — Classification model imports bias into land or population mapping

Training labels may misrepresent informal settlements, crops, ecosystems, conflict zones, or minority communities.

HARM: biased maps guide policy, targeting, and resource allocation.

OVERLAP TO CHECK: HIRE-001, GOVREC-001.

### REMSENSE-003 — Environmental monitoring misses local or short-lived events

Revisit time, cloud cover, spatial resolution, and orbital geometry may skip brief pollution, fire, flooding, or habitat loss.

HARM: absence in imagery is mistaken for absence in reality.

OVERLAP TO CHECK: OBS-003, WATERUTIL-001.

### REMSENSE-004 — High-resolution imagery exposes vulnerable people and sites

Movement, homes, camps, sacred locations, farms, and critical infrastructure may become visible to hostile or commercial actors.

HARM: observation intended for planning creates surveillance and targeting risk.

OVERLAP TO CHECK: CONFLICT-004, SACRED-001.

### REMSENSE-005 — Image-processing pipeline changes the meaning of evidence

Compression, enhancement, mosaicking, interpolation, color mapping, and AI completion may alter interpretation.

HARM: processed imagery is presented as if it were raw observation.

OVERLAP TO CHECK: AUTHENT-005, DATA-001.

### LAUNCH-001 — Launch schedule pressure weakens anomaly response

Range availability, customer deadlines, weather windows, and financial pressure may discourage delay.

HARM: unresolved concerns are accepted because postponement is costly.

OVERLAP TO CHECK: DEAD-005, INCENT-001.

### LAUNCH-002 — Launch failure affects communities outside the mission boundary

Debris, toxic propellant, noise, evacuation, wildfire, and maritime or airspace closure may burden nearby populations.

HARM: mission risk is externalized onto communities and ecosystems.

OVERLAP TO CHECK: HAZ-004, PARTICIP-002.

### LAUNCH-003 — Payload integration changes vehicle risk late in the process

Mass, vibration, power, software, thermal, radio, and separation behavior may differ from earlier assumptions.

HARM: a late interface change invalidates tested safety margins.

OVERLAP TO CHECK: LAB-003, CHANGE-005.

### LAUNCH-004 — Range safety depends on incomplete tracking or telemetry

Sensor loss, weather, communication failure, and ambiguous trajectory may delay protective action.

HARM: hazardous flight continues while decision confidence is low.

OVERLAP TO CHECK: OT-006, NAV-003.

### LAUNCH-005 — Successful launch masks early orbital deployment failure

Separation, antenna release, solar-array deployment, attitude control, or commissioning may fail after ascent.

HARM: public and operational success is declared before service is actually viable.

OVERLAP TO CHECK: RESTORE-003, LOGISTICS-003.

### DEBRIS-001 — Small debris is undertracked but still mission-ending

Fragments below routine tracking thresholds may damage sensors, shielding, solar arrays, or crewed vehicles.

HARM: unobserved objects create high-consequence collision risk.

OVERLAP TO CHECK: HAZ-006, OBS-003.

### DEBRIS-002 — Collision-avoidance action creates new operational conflicts

Maneuvers consume fuel, interrupt service, change geometry, and may conflict with another operator’s plan.

HARM: avoiding one risk creates another or shortens mission life.

OVERLAP TO CHECK: CHANGE-005, COLLAB-002.

### DEBRIS-003 — Conjunction warnings overwhelm operators

Large alert volumes, uncertainty, and repeated false positives may reduce attention to the most dangerous event.

HARM: warning saturation causes missed collision response.

OVERLAP TO CHECK: OT-005, NOTIFY-004.

### DEBRIS-004 — Debris responsibility is unclear across operators and states

Fragments may be difficult to attribute, and legal responsibility may remain disputed for decades.

HARM: cleanup and prevention lack an accountable actor.

OVERLAP TO CHECK: SPACE-006, GOV-006.

### DEBRIS-005 — Debris-removal capability can be repurposed against active satellites

Rendezvous, capture, inspection, and maneuver technology may have defensive and offensive uses.

HARM: cleanup infrastructure also creates coercive or hostile capability.

OVERLAP TO CHECK: DUAL-001, CONFLICT-003.

### PNT-001 — Positioning signal is accepted without independent validation

Spoofing, jamming, multipath, constellation error, and receiver faults may produce plausible but false location.

HARM: vehicles, responders, finance, and infrastructure act from incorrect position.

OVERLAP TO CHECK: NAV-003, SPOOF-002.

### PNT-002 — Timing dependence is hidden in distributed systems

Telecom, grids, trading, databases, industrial control, and authentication may rely on satellite time.

HARM: timing loss creates data corruption, instability, and coordination failure.

OVERLAP TO CHECK: TIME-001, OT-002.

### PNT-003 — Backup clocks drift beyond safe tolerance

Local oscillators may preserve operation briefly but diverge during extended outage.

HARM: delayed failure occurs after systems appear to have survived.

OVERLAP TO CHECK: TELECOM-002, EXP-006.

### PNT-004 — Navigation integrity warning reaches users too slowly

A service may detect degraded accuracy after receivers and downstream systems have already acted.

HARM: correction cannot reverse physical movement or transaction effects.

OVERLAP TO CHECK: POLICE-006, DUE-006.

### PNT-005 — Civil and military uses compete during interference or conflict

Signal policy, power, availability, and protection may favor one class of user.

HARM: public dependency is disrupted by strategic priorities not visible to civilians.

OVERLAP TO CHECK: GRID-006, CONFLICT-004.

### GROUND-001 — Ground segment becomes the true single point of failure

Mission control, authentication, scheduling, data processing, and key management may be centralized.

HARM: distributed satellites depend on one terrestrial control boundary.

OVERLAP TO CHECK: MONO-001, CASCADE-001.

### GROUND-002 — Command credentials outlive the people and systems that issued them

Keys, certificates, accounts, and recovery paths may persist through staff, vendor, and ownership changes.

HARM: stale authority can control long-lived spacecraft.

OVERLAP TO CHECK: REVOKE-001, SUCCESS-001.

### GROUND-003 — Ground-station outage creates hidden data gaps

Weather, power, network, antenna, staffing, and scheduling failures may interrupt command and downlink.

HARM: missing observations or commands are mistaken for normal mission behavior.

OVERLAP TO CHECK: TELECOM-001, OBS-003.

### GROUND-004 — Ground processing silently changes after software update

Calibration, geolocation, filtering, compression, and product generation may differ across versions.

HARM: long-term datasets become internally inconsistent without visible break.

OVERLAP TO CHECK: VER-001, DATA-001.

### GROUND-005 — Emergency control path bypasses normal audit and separation

Urgent command may use shared credentials, reduced review, or privileged access.

HARM: recovery capability becomes a persistent security weakness.

OVERLAP TO CHECK: RESTORE-004, AUTHZ-006.

### SPACEACCESS-001 — Space-derived benefits are distributed unequally

Connectivity, weather, imagery, navigation, and data products may favor wealthy regions, firms, or governments.

HARM: public investment and shared orbital resources deepen inequality.

OVERLAP TO CHECK: EDACCESS-001, MOBILITY-005.

### SPACEACCESS-002 — Licensing and spectrum allocation favor established operators

Small nations, communities, researchers, and new entrants may lack access to orbital and radio resources.

HARM: governance locks in existing power and limits plural participation.

OVERLAP TO CHECK: LOCK-001, PLURAL-002.

### SPACEACCESS-003 — Space data is technically public but practically unusable

Large files, specialist formats, processing costs, cloud dependence, and expertise may block access.

HARM: formal openness does not create real public benefit.

OVERLAP TO CHECK: PROV-005, PUBSCI-005.

### SPACEACCESS-004 — Commercial terms can abruptly remove public capability

Pricing, API policy, service region, licensing, or provider shutdown may change after dependence forms.

HARM: essential public functions become hostage to private continuity.

OVERLAP TO CHECK: TERMS-001, LOCK-001.

### SPACEACCESS-005 — Recovery from space-service loss is uneven across users

Large institutions may have terrestrial backups, alternative constellations, and specialist staff while households and small organizations do not.

HARM: the same outage creates unequal safety and economic consequences.

OVERLAP TO CHECK: PUBLICDEP-003, SPACE-004.

## Pass 40 result

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
- Current preserved plus provisional: 1703

NEXT DISCOVERY PASS:
Manufacturing, robotics, machine guarding, quality control, counterfeit components, maintenance, worker-machine interaction, product traceability, and physical product liability.

END PACKET 01.5 — DISCOVERY PASS 40
