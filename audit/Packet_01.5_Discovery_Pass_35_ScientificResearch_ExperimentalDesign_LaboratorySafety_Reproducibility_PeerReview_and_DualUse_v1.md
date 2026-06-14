# Packet 01.5 — Discovery Pass 35

STATUS: DISCOVERY IN PROGRESS
PHASE: PROBLEM FINDING ONLY
ROUTING: NOT STARTED
DATE: 2026-06-14

This pass looks for scientific-research failure involving experimental design, laboratory safety, reproducibility, data integrity, publication bias, peer review, dual-use knowledge, institutional incentives, and protection of participants and communities.

## Provisional records

### DESIGN-001 — Research question is shaped to fit available data or tools

The study may ask only what existing datasets, instruments, models, funding, or personnel can conveniently measure.

HARM: methodological convenience is mistaken for scientific importance.

OVERLAP TO CHECK: TEACH-004, MEAS-001.

### DESIGN-002 — Comparison group is not truly comparable

Selection, timing, location, baseline condition, prior exposure, or treatment access may differ between groups.

HARM: observed effect is attributed to the intervention rather than group differences.

OVERLAP TO CHECK: ASSESS-002, FRAME-003.

### DESIGN-003 — Outcome measure is a weak proxy for the real phenomenon

A laboratory marker, score, click, survey response, short-term behavior, or model metric may not represent the intended construct.

HARM: the experiment proves improvement in the proxy, not the real outcome.

OVERLAP TO CHECK: MEAS-004, WKEVAL-001.

### DESIGN-004 — Sample excludes the population that will use the result

Research may omit children, elders, disabled people, pregnant people, rural communities, non-native speakers, or complex cases.

HARM: findings are generalized beyond the people actually studied.

OVERLAP TO CHECK: HEALTH-005, ROLLOUT-007.

### DESIGN-005 — Researcher flexibility creates outcome after seeing the data

Hypotheses, exclusions, subgroup definitions, stopping rules, transformations, and models may change during analysis.

HARM: chance patterns are presented as planned findings.

OVERLAP TO CHECK: TEST-004, EVAL-003.

### DESIGN-006 — Short study duration hides delayed or cumulative effects

Benefits may appear quickly while harm, adaptation, rebound, resistance, or degradation emerges later.

HARM: early success is mistaken for durable safety and effectiveness.

OVERLAP TO CHECK: HAZ-006, REBOUND-001.

### DATA-001 — Research dataset contains undocumented transformations

Cleaning, imputation, normalization, aggregation, relabeling, and exclusion may alter meaning without a complete record.

HARM: later analysis cannot reconstruct how raw evidence became the reported result.

OVERLAP TO CHECK: PROV-003, SEM-004.

### DATA-002 — Missing data is treated as random when it is systematic

Dropout, sensor failure, refusal, nonresponse, death, and inaccessible populations may correlate with the outcome.

HARM: the analysis excludes the people or conditions where the method failed most.

OVERLAP TO CHECK: BENEFIT-002, OBS-003.

### DATA-003 — Duplicate or dependent observations are treated as independent

Repeated measures, related participants, reused records, overlapping datasets, and multiple samples from one source may inflate evidence.

HARM: confidence appears stronger than the underlying information supports.

OVERLAP TO CHECK: MISINFO-003, KB-004.

### DATA-004 — Synthetic or augmented data hides unsupported assumptions

Generated records may preserve visible patterns while missing rare events, causal structure, or real-world constraints.

HARM: model performance is validated against data that already reflects the modeler’s assumptions.

OVERLAP TO CHECK: MODEL-003, TEST-005.

### DATA-005 — Data fabrication or falsification is difficult to distinguish from error

Invented values, altered images, copied measurements, selective deletion, and manual correction may resemble ordinary processing mistakes.

HARM: false evidence survives routine review.

OVERLAP TO CHECK: AUTHENT-005, AUD-003.

### DATA-006 — Research data cannot be shared enough to verify but is shared enough to expose people

Privacy, consent, contracts, and community risk may limit openness while partial releases still permit reidentification.

HARM: verification remains weak while participant privacy is still harmed.

OVERLAP TO CHECK: MIN-001, PROV-005.

### LAB-001 — Laboratory procedure assumes the material is correctly identified

Samples, reagents, cultures, chemicals, biological agents, and waste may be mislabeled, contaminated, substituted, or degraded.

HARM: the procedure is safely designed for the wrong substance.

OVERLAP TO CHECK: HAZ-001, IDENT-003.

### LAB-002 — Safety control exists on paper but not at the work surface

Training, ventilation, containment, protective equipment, emergency supplies, and signage may be unavailable, bypassed, or unsuitable.

HARM: formal compliance hides actual exposure risk.

OVERLAP TO CHECK: HAZ-003, ANIMAL-002.

### LAB-003 — Protocol change is not re-evaluated for safety

A different concentration, scale, temperature, organism, pressure, solvent, device, or automation step may alter the hazard.

HARM: an apparently minor research change invalidates the prior safety assessment.

OVERLAP TO CHECK: CHANGE-001, MEDINT-003.

### LAB-004 — Automated laboratory equipment fails outside expected conditions

Robots, pumps, incubators, freezers, sensors, valves, and control software may continue operating after blockage, leakage, drift, or sample mismatch.

HARM: automation scales and prolongs a laboratory failure.

OVERLAP TO CHECK: AUTO-005, COLD-003.

### LAB-005 — Laboratory waste loses identity before disposal

Mixed containers, removed labels, secondary packaging, transfer, outsourcing, and delayed pickup may break the hazard chain.

HARM: waste workers and the environment are exposed to unknown material.

OVERLAP TO CHECK: CONTAM-006, TRACE-002.

### LAB-006 — Near miss is not reported because no harm occurred

Spills, exposure, equipment faults, containment failure, mislabeled samples, and procedural deviations may remain informal.

HARM: the system loses its best warning before a serious incident.

OVERLAP TO CHECK: CARE-006, INCDET-004.

### REPRO-001 — Reproduction uses a method different from the published method

Critical details may be omitted, ambiguous, proprietary, remembered informally, or changed after publication.

HARM: failure to reproduce cannot distinguish false result from incomplete method.

OVERLAP TO CHECK: DOC-005, PROOFCHAIN-008.

### REPRO-002 — Software, model, dependency, or hardware version is not preserved

Results may depend on changing libraries, provider models, random seeds, drivers, compilers, instruments, or firmware.

HARM: the same code and data no longer produce the reported result.

OVERLAP TO CHECK: BUILD-001, VER-001.

### REPRO-003 — Reproduction is attempted only under favorable laboratory conditions

Different operators, sites, devices, populations, climates, and real-world noise may never be tested.

HARM: repeatability in one controlled environment is mistaken for general robustness.

OVERLAP TO CHECK: ENV-001, DESIGN-004.

### REPRO-004 — Negative reproduction is less visible than the original positive result

Failed replications may be unpublished, delayed, framed as incompetence, or excluded from reviews.

HARM: the literature preserves the initial claim after contrary evidence exists.

OVERLAP TO CHECK: PUB-002, MISINFO-004.

### REPRO-005 — Reproducibility package includes data or code that differs from the analyzed version

Late cleanup, privacy edits, file replacement, branch mismatch, and undocumented scripts may produce a polished but inaccurate package.

HARM: verification targets a reconstruction rather than the original analysis.

OVERLAP TO CHECK: PROV-002, DEPLOY-004.

### REPRO-006 — Exact reproduction is mistaken for independent confirmation

The same data, assumptions, software, and pipeline may recreate the result without testing whether the claim is true elsewhere.

HARM: pipeline consistency is mistaken for scientific corroboration.

OVERLAP TO CHECK: TRUST-005, MISINFO-003.

### PUBSCI-001 — Positive and novel results are more likely to be published

Null results, small effects, failed methods, safety concerns, and replications may remain invisible.

HARM: the published literature systematically overstates effectiveness and certainty.

OVERLAP TO CHECK: RANK-002, REPRO-004.

### PUBSCI-002 — Abstract and headline overstate the evidence

Causal, general, safe, effective, proven, and breakthrough language may exceed the actual design and results.

HARM: compressed public communication changes the scientific claim.

OVERLAP TO CHECK: MISINFO-005, PUB-003.

### PUBSCI-003 — Retraction or correction does not propagate through citations and models

Databases, reviews, educational material, clinical tools, media, and training corpora may keep using the original result.

HARM: withdrawn science remains operationally influential.

OVERLAP TO CHECK: GOVREC-002, MISINFO-006.

### PUBSCI-004 — Multiple papers divide one study into apparently independent evidence

Shared participants, datasets, experiments, or analysis plans may be published across several articles without clear linkage.

HARM: reviews and readers count one body of evidence several times.

OVERLAP TO CHECK: DATA-003, MISINFO-003.

### PUBSCI-005 — Proprietary publication access blocks verification and public benefit

Methods, data, corrections, and safety findings may remain behind paywalls, licensing, or institutional access.

HARM: publicly important knowledge cannot be independently checked or widely used.

OVERLAP TO CHECK: PROV-005, EDACCESS-001.

### PEER-001 — Peer reviewer lacks the specialized knowledge needed to detect the central flaw

Complex studies may cross statistics, domain science, software, ethics, hardware, and policy.

HARM: competent review in one area creates false confidence in the whole work.

OVERLAP TO CHECK: WKEVAL-005, BOUND-002.

### PEER-002 — Reviewer conflict of interest is undisclosed or underestimated

Competition, collaboration, funding, ideology, reputation, and institutional relationships may shape judgment.

HARM: supposedly independent review carries hidden incentives.

OVERLAP TO CHECK: GUARD-003, CONTRACT-004.

### PEER-003 — Reviewer anonymity removes accountability without preventing retaliation

Hidden identity may permit weak, biased, obstructive, or exploitative review while editors can still infer or reveal authors.

HARM: power remains asymmetric and difficult to challenge.

OVERLAP TO CHECK: MOD-004, PROV-004.

### PEER-004 — Peer review evaluates the manuscript but not the underlying evidence chain

Raw data, laboratory records, code execution, consent, images, and materials may not be inspected.

HARM: a coherent paper passes despite fabricated or irreproducible foundations.

OVERLAP TO CHECK: DATA-005, PROOFCHAIN-001.

### DUAL-001 — Benign research method can be repurposed for harm

Biological, chemical, cyber, surveillance, behavioral, and autonomous-system knowledge may lower the barrier to misuse.

HARM: dissemination increases harmful capability beyond the intended audience.

OVERLAP TO CHECK: MISUSE-003, ADV-001.

### DUAL-002 — Hazard screening occurs after detailed information is already generated or shared

Drafts, prompts, code, protocols, datasets, and collaboration tools may expose sensitive capability before formal review.

HARM: the control gate activates after transfer has occurred.

OVERLAP TO CHECK: PUB-001, SHARE-003.

### DUAL-003 — Restricting research hides safety information from defenders and affected communities

Secrecy may also block detection methods, protective practices, environmental evidence, and public accountability.

HARM: misuse prevention weakens legitimate protection and oversight.

OVERLAP TO CHECK: PUB-006, CIVIC-004.

### DUAL-004 — Capability assessment ignores combinations of ordinary knowledge

Individually harmless methods, tools, suppliers, datasets, and automation may become dangerous when assembled.

HARM: fragmented review misses the real end-to-end hazard.

OVERLAP TO CHECK: INTERACT-001, AGENT-001.

### INCENT-001 — Funding and career incentives reward claim production over truth correction

Publications, grants, patents, press, citations, and deadlines may outweigh replication, maintenance, data stewardship, and retraction.

HARM: institutional success diverges from scientific reliability.

OVERLAP TO CHECK: LABOR-004, REPUT-004.

### INCENT-002 — Sponsor influence changes question, design, analysis, or publication

Commercial, political, military, philanthropic, or institutional funders may shape scope and visibility.

HARM: sponsor interests are embedded in apparently neutral evidence.

OVERLAP TO CHECK: CONTRACT-004, FRAME-004.

### INCENT-003 — Research competition discourages early risk disclosure and collaboration

Priority, patents, funding, prestige, and fear of being scooped may delay sharing of flaws, incidents, and negative results.

HARM: hazards and false conclusions persist longer than necessary.

OVERLAP TO CHECK: CARE-006, REPUT-004.

### PARTICIP-001 — Participant consent does not cover future data and model uses

Research data, samples, images, genetics, recordings, and derived models may be reused for new questions or commercial products.

HARM: participation expands beyond the choice originally made.

OVERLAP TO CHECK: CONSENT-003, HIRE-007.

### PARTICIP-002 — Community-level harm is missed by individual consent

Research may affect tribes, neighborhoods, families, rare-disease groups, ecosystems, or stigmatized populations even when each participant agreed.

HARM: collective identity and risk are exposed without collective authority or benefit.

OVERLAP TO CHECK: FAMILY-003, CIVIC-004.

## Pass 35 result

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
- Current preserved plus provisional: 1493

NEXT DISCOVERY PASS:
Critical infrastructure, utilities, industrial control, electricity, water, telecommunications, cascading failure, operational technology, public dependency, and recovery under constrained resources.

END PACKET 01.5 — DISCOVERY PASS 35
