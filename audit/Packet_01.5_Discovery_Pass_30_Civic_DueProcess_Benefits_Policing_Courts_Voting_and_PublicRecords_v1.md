# Packet 01.5 — Discovery Pass 30

STATUS: DISCOVERY IN PROGRESS
PHASE: PROBLEM FINDING ONLY
ROUTING: NOT STARTED
DATE: 2026-06-14

This pass looks for civic and public-sector failure involving due process, public benefits, policing, courts, voting, identity systems, administrative appeal, public records, and unequal access to government services.

## Provisional records

### CIVIC-001 — Public-service automation hides the responsible authority

Residents may interact with a portal, chatbot, contractor, model, or vendor without knowing which agency or official owns the decision.

HARM: accountability and escalation become unclear.

OVERLAP TO CHECK: WKAUTH-002, AUTH-007.

### CIVIC-002 — Digital access becomes a practical condition of citizenship

Benefits, permits, taxes, records, voting information, hearings, and public communication may require devices, accounts, connectivity, and technical skill.

HARM: people without reliable digital access lose practical access to public rights and services.

OVERLAP TO CHECK: EDACCESS-001, ACCESSLAW-001.

### CIVIC-003 — Contractor policy becomes undeclared government policy

Vendor defaults, moderation rules, ranking logic, identity requirements, and risk thresholds may shape public decisions without formal adoption.

HARM: private system design exercises public authority without public process.

OVERLAP TO CHECK: CONTRACT-003, REMOTE-001.

### CIVIC-004 — Public transparency exposes vulnerable individuals

Open records, meeting materials, incident maps, court data, permits, and benefit records may reveal addresses, health, family, immigration, or safety information.

HARM: transparency duties create privacy, stalking, retaliation, or discrimination risk.

OVERLAP TO CHECK: PUB-006, USERPRIV-004.

### CIVIC-005 — Service availability differs by language, disability, and region

One portal or automation may work well for standard English, modern devices, urban addresses, and common documents but fail elsewhere.

HARM: public access is unequal even when the nominal service is universal.

OVERLAP TO CHECK: LOC-003, ASSESS-002.

### CIVIC-006 — Public system failure lacks a non-digital fallback

When identity, portal, payment, upload, or scheduling systems fail, there may be no reachable human office or paper route.

HARM: technical outage becomes denial of public service.

OVERLAP TO CHECK: LABOR-006, CONT-001.

### DUE-001 — Affected person is not told that automation influenced the decision

A denial, flag, priority, investigation, or sanction may appear fully human even when a model or rule engine materially shaped it.

HARM: people cannot challenge the actual decision process.

OVERLAP TO CHECK: PRIVRIGHT-005, WKAUTH-002.

### DUE-002 — Notice arrives after the response window begins or expires

Mail delay, inaccessible portals, wrong addresses, notification failure, detention, illness, or account problems may prevent timely awareness.

HARM: a person loses rights without a meaningful chance to respond.

OVERLAP TO CHECK: DEAD-003, NOTIFY-001.

### DUE-003 — Explanation states the rule but not the evidence

A decision may cite eligibility, risk, policy, or inconsistency without revealing the records, calculations, or inferences used.

HARM: the person cannot identify factual or logical error.

OVERLAP TO CHECK: WKEVAL-005, PROOFCHAIN-008.

### DUE-004 — Appeal reviews the same automated output rather than the underlying case

The reviewer may see the original score, recommendation, or summary and inherit its framing.

HARM: appeal reproduces the first error instead of independently reconsidering it.

OVERLAP TO CHECK: COG-002, TRUST-005.

### DUE-005 — Appeal requires resources unavailable to the affected person

Forms, legal knowledge, records, translation, transportation, time off, fees, and digital access may be necessary to contest a decision.

HARM: formal appeal exists but is not practically usable.

OVERLAP TO CHECK: PROV-005, EDACCESS-001.

### DUE-006 — Corrected decision does not repair downstream consequences

Restored eligibility, dismissed charges, corrected identity, or reversed findings may not update housing, employment, credit, records, fees, or watchlists.

HARM: successful appeal leaves the real harm in place.

OVERLAP TO CHECK: EMPREC-002, PRIVRIGHT-002.

### BENEFIT-001 — Eligibility rule is implemented differently from the governing policy

Code, data mappings, thresholds, household rules, and document logic may simplify or misread the actual standard.

HARM: lawful eligibility is denied by implementation drift.

OVERLAP TO CHECK: SEM-001, TEACH-001.

### BENEFIT-002 — Missing data is interpreted as disqualifying data

Unreported income, unavailable records, incomplete identity history, or absent documents may be treated as evidence against the applicant.

HARM: administrative gaps become adverse facts.

OVERLAP TO CHECK: HEALTH-002, INFER-001.

### BENEFIT-003 — Automation cannot represent unstable or informal living conditions

Homelessness, shared households, caregiving, cash work, migration, domestic violence, and temporary housing may not fit standard forms.

HARM: people with the greatest need are least representable.

OVERLAP TO CHECK: HIRE-004, DEV-001.

### BENEFIT-004 — Benefit cliffs are hidden from the applicant

A small change in income, household, work hours, or reporting may cause a large loss of aid or debt.

HARM: people cannot make informed choices about work and reporting.

OVERLAP TO CHECK: FRAME-002, BILL-003.

### BENEFIT-005 — Verification burden is repeatedly shifted to the applicant

Agencies may request the same documents, identities, and explanations across programs or renewal cycles.

HARM: administrative repetition creates attrition and wrongful loss of benefits.

OVERLAP TO CHECK: COG-001, RECORDLAW-001.

### BENEFIT-006 — Overpayment recovery assumes recipient fault

Agency delay, rule complexity, data mismatch, or system error may create debt that is later charged to the recipient.

HARM: public-system mistakes become personal financial harm.

OVERLAP TO CHECK: BILL-004, DUE-003.

### POLICE-001 — Predictive system amplifies historically concentrated enforcement

Past arrests, calls, stops, and reports may reflect where policing occurred rather than where harm actually existed.

HARM: prior enforcement concentration justifies future concentration.

OVERLAP TO CHECK: HIRE-001, KB-002.

### POLICE-002 — Identity match is treated as probable guilt

Face, plate, device, location, name, association, or database matches may be noisy, stale, or shared.

HARM: investigative lead becomes coercive action without sufficient verification.

OVERLAP TO CHECK: REAL-004, IDENT-003.

### POLICE-003 — Officer reliance on system output is invisible in the record

Reports may describe an independent observation while omitting alert, score, query, or model influence.

HARM: courts and oversight cannot examine the real basis of action.

OVERLAP TO CHECK: DUE-001, PROV-003.

### POLICE-004 — Public-safety data is reused beyond the original purpose

License plates, faces, location, emergency calls, witnesses, victims, and intelligence may enter immigration, employment, benefits, or private databases.

HARM: safety reporting creates broad surveillance consequences.

OVERLAP TO CHECK: SURV-004, CONSENT-001.

### POLICE-005 — Sensor or body-camera absence is treated as evidence of no event

Device failure, obstruction, activation delay, missing upload, or limited view may leave no record.

HARM: missing evidence favors the system or official account unfairly.

OVERLAP TO CHECK: SENSE-007, CAM-002.

### POLICE-006 — Automated alert escalates faster than human correction

A false match or threat signal may trigger dispatch, pursuit, detention, or force before context can be reviewed.

HARM: low-confidence data produces immediate physical risk.

OVERLAP TO CHECK: STRESS-002, MEDINT-005.

### COURT-001 — Legal research system omits controlling authority

Ranking, access limits, jurisdiction filters, unpublished decisions, and stale databases may hide the most relevant source.

HARM: arguments and rulings rely on incomplete law.

OVERLAP TO CHECK: RETR-004, INDEX-002.

### COURT-002 — Generated citation or quotation is not verified against the record

A model may fabricate, misquote, or misapply cases, statutes, testimony, exhibits, or docket entries.

HARM: false authority enters legal proceedings.

OVERLAP TO CHECK: MISINFO-001, PROV-001.

### COURT-003 — Automated risk score influences liberty without individual explanation

Bail, sentencing, supervision, diversion, and release decisions may use group-level patterns or hidden features.

HARM: a person’s liberty turns on an opaque statistical proxy.

OVERLAP TO CHECK: WKEVAL-003, PRIVRIGHT-005.

### COURT-004 — Digital evidence loses chain-of-custody meaning

Copies, exports, screenshots, cloud processing, AI enhancement, transcription, and format conversion may alter or detach evidence context.

HARM: persuasive material is admitted without reliable provenance.

OVERLAP TO CHECK: AUTHENT-005, PROV-003.

### COURT-005 — Remote hearing conditions affect perceived credibility

Audio delay, camera quality, lighting, language access, disability, device failure, and private-space limits may shape how testimony is judged.

HARM: technical conditions influence legal credibility and outcome.

OVERLAP TO CHECK: HIRE-006, ASSESS-002.

### COURT-006 — Sealed, expunged, or corrected records remain in downstream systems

Search indexes, commercial databases, police systems, news archives, and background checks may retain old court information.

HARM: legal relief does not remove practical punishment.

OVERLAP TO CHECK: PUB-005, DUE-006.

### VOTE-001 — Voter information system gives stale or location-inappropriate instructions

Registration rules, deadlines, polling places, identification, accessibility, and ballot procedures may change by jurisdiction and date.

HARM: a voter follows accurate-looking instructions that do not apply.

OVERLAP TO CHECK: CRISIS-003, MISINFO-006.

### VOTE-002 — Registration matching removes eligible voters through data error

Names, addresses, citizenship records, death records, duplicates, and moves may be matched incorrectly.

HARM: eligible voters lose access before correction is possible.

OVERLAP TO CHECK: IDENT-003, DUE-002.

### VOTE-003 — Accessibility or language support changes ballot secrecy

A voter may require assistance, accessible equipment, remote tools, or translation that exposes choices to others.

HARM: access is gained at the cost of privacy or independence.

OVERLAP TO CHECK: EDACCESS-003, ACCESSLAW-004.

### VOTE-004 — Election-result automation obscures uncertainty and correction

Preliminary counts, reporting gaps, rejected ballots, audits, recounts, and certification status may be compressed into one number.

HARM: incomplete results are treated as final or manipulated.

OVERLAP TO CHECK: MISINFO-005, FRAME-003.

### PUBID-001 — Government identity record becomes a single point of exclusion

A wrong name, date, status, address, biometric, or identifier may block benefits, voting, travel, healthcare, taxes, and employment.

HARM: one record error propagates across civic life.

OVERLAP TO CHECK: MONO-001, PRIVRIGHT-002.

### PUBID-002 — Strong identity proof excludes people with weak documentation

Homeless people, migrants, abuse survivors, elders, rural residents, and people with name or gender changes may lack standard evidence.

HARM: fraud prevention denies legitimate existence and access.

OVERLAP TO CHECK: BENEFIT-003, AUTHN-009.

### PUBID-003 — Biometric identity cannot be safely reissued after compromise

Faces, fingerprints, voice, and behavioral patterns are persistent and may be copied or misclassified.

HARM: identity theft or false match becomes difficult to recover from.

OVERLAP TO CHECK: AUTHN-004, SPOOF-003.

### PUBID-004 — Cross-agency identity linking exceeds the original purpose

Identifiers may connect tax, health, policing, education, benefits, voting, and immigration records.

HARM: administrative convenience creates pervasive government profiling.

OVERLAP TO CHECK: SURV-004, TENANT-002.

### GOVREC-001 — Government record stores inference as verified fact

Risk, intent, household, fraud, association, identity, or eligibility may be inferred and later treated as observed truth.

HARM: speculation gains official durability.

OVERLAP TO CHECK: EMPREC-001, INFER-001.

### GOVREC-002 — Public-record correction lacks propagation and audit

An agency may fix its source while contractors, other agencies, courts, search systems, and commercial databases keep the error.

HARM: corrected public truth remains practically false elsewhere.

OVERLAP TO CHECK: DUE-006, EMPREC-002.

### GOVREC-003 — Record-retention policy destroys evidence needed for accountability

Routine deletion, migration, vendor shutdown, or classification changes may remove logs and records before complaint, investigation, or appeal.

HARM: official action becomes impossible to reconstruct.

OVERLAP TO CHECK: RET-001, RECORDLAW-001.

### GOVREC-004 — Public-record system cannot distinguish official, draft, and superseded material

Meeting notes, policy drafts, preliminary findings, old forms, and corrected records may remain equally discoverable.

HARM: nonfinal government material is mistaken for operative truth.

OVERLAP TO CHECK: PUB-001, MISINFO-006.

## Pass 30 result

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
- Current preserved plus provisional: 1283

NEXT DISCOVERY PASS:
Housing, credit, insurance, lending, pricing, fraud scoring, allocation, consumer appeal, and essential-service access.

END PACKET 01.5 — DISCOVERY PASS 30
