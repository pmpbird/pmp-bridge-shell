# Packet 01.5 — Discovery Pass 31

STATUS: DISCOVERY IN PROGRESS
PHASE: PROBLEM FINDING ONLY
ROUTING: NOT STARTED
DATE: 2026-06-14

This pass looks for housing, credit, insurance, lending, pricing, fraud-scoring, allocation, consumer-appeal, and essential-service access failures.

## Provisional records

### HOUSING-001 — Tenant screening reuses disputed or outdated records

Evictions, criminal records, addresses, debts, complaints, income, and identity data may remain inaccurate or incomplete across screening vendors.

HARM: housing is denied using records the applicant cannot meaningfully correct in time.

OVERLAP TO CHECK: COURT-006, EMPREC-002.

### HOUSING-002 — Proxy variables recreate prohibited housing discrimination

ZIP code, language, family size, disability-related history, source of income, device, schedule, and neighborhood may correlate with protected traits.

HARM: discriminatory selection reappears through indirect scoring.

OVERLAP TO CHECK: HIRE-002, INFER-001.

### HOUSING-003 — Automated application ranking hides landlord discretion

A score or recommendation may appear objective while landlords choose thresholds, exceptions, weights, and override rules.

HARM: human policy is concealed behind automated output.

OVERLAP TO CHECK: WKAUTH-002, DUE-001.

### HOUSING-004 — Informal or unstable housing history is treated as risk

Homelessness, shared housing, sublets, family stays, domestic violence, migration, and missing rental records may not fit standard forms.

HARM: people with the greatest housing instability are penalized for that instability.

OVERLAP TO CHECK: BENEFIT-003, HIRE-004.

### HOUSING-005 — Smart-home or building telemetry becomes tenancy evidence

Entry logs, utility use, noise sensors, cameras, access systems, maintenance requests, and connected devices may influence fees, renewal, or eviction.

HARM: ordinary living behavior becomes continuous landlord surveillance.

OVERLAP TO CHECK: SURV-001, USERPRIV-004.

### HOUSING-006 — Housing appeal is slower than the available unit

A screening or identity error may be correctable only after the property is rented to someone else.

HARM: formal correction cannot restore the lost housing opportunity.

OVERLAP TO CHECK: DUE-002, DUE-006.

### CREDIT-001 — Credit record merges people with similar identities

Names, family relationships, reused identifiers, addresses, and data-broker matching may combine separate individuals.

HARM: one person inherits another person’s debt or risk history.

OVERLAP TO CHECK: IDENT-003, TENANT-003.

### CREDIT-002 — Credit score compresses incompatible obligations into one number

Medical debt, rent, utilities, loans, identity theft, disputed charges, and temporary hardship may be aggregated without causal context.

HARM: unlike events produce the same durable judgment.

OVERLAP TO CHECK: FRAME-003, WKEVAL-003.

### CREDIT-003 — Lack of credit history is treated as bad credit

Young people, immigrants, cash users, low-income households, and privacy-conscious people may have sparse records.

HARM: absence of data becomes adverse evidence.

OVERLAP TO CHECK: BENEFIT-002, HEALTH-002.

### CREDIT-004 — Credit correction does not propagate before new decisions

A bureau may fix its file while lenders, landlords, insurers, employers, and cached vendor systems retain the old result.

HARM: corrected information continues causing exclusion.

OVERLAP TO CHECK: GOVREC-002, PRIVRIGHT-002.

### CREDIT-005 — Alternative credit data expands surveillance

Phone use, shopping, location, device behavior, rent, social connections, and online activity may be used to score thin-file consumers.

HARM: access to credit is exchanged for broad behavioral monitoring.

OVERLAP TO CHECK: SURV-004, PRIV-002.

### CREDIT-006 — Score improvement advice conflicts with actual financial wellbeing

Actions that improve a score may increase fees, debt exposure, account complexity, or risky borrowing.

HARM: metric optimization is mistaken for economic health.

OVERLAP TO CHECK: FEED-005, MEAS-004.

### LEND-001 — Affordability model ignores unstable real expenses

Healthcare, caregiving, disability, transportation, housing volatility, variable income, and local prices may be absent or simplified.

HARM: approved loans become predictably unaffordable.

OVERLAP TO CHECK: HEALTH-005, BILL-005.

### LEND-002 — Loan explanation hides total cost and downside scenarios

Rate changes, compounding, fees, penalties, refinancing risk, collateral loss, and payment timing may be presented separately.

HARM: the borrower cannot understand the full obligation.

OVERLAP TO CHECK: BILL-003, FRAME-002.

### LEND-003 — Automated underwriting rejects nonstandard but valid income

Seasonal work, self-employment, cash income, caregiving payments, benefits, and multiple small sources may not fit expected patterns.

HARM: viable borrowers are excluded by representational limits.

OVERLAP TO CHECK: BENEFIT-003, HIRE-004.

### LEND-004 — Dynamic preapproval becomes a behavioral pressure tool

Apps may adjust offers, urgency, limits, or recommendations using browsing, spending, timing, or location signals.

HARM: personalization manipulates borrowing decisions when users are vulnerable.

OVERLAP TO CHECK: FRAME-004, SURV-004.

### LEND-005 — Adverse-action notice names a broad category instead of the real cause

A lender may cite credit history, risk, affordability, or verification without identifying the specific record, rule, or model factor.

HARM: the borrower cannot correct or contest the denial.

OVERLAP TO CHECK: DUE-003, HIRE-005.

### INSUR-001 — Insurance pricing uses proxies unrelated to the insured hazard

Credit, ZIP code, occupation, device data, purchase behavior, and online activity may influence premiums or coverage.

HARM: social and economic status is converted into insurance cost.

OVERLAP TO CHECK: HIRE-002, PRICE-002.

### INSUR-002 — Telematics data changes coverage beyond the user’s understanding

Driving, movement, health, home, wearable, and device telemetry may affect price, eligibility, claim review, and renewal.

HARM: surveillance becomes a hidden condition of protection.

OVERLAP TO CHECK: HOUSING-005, SURV-001.

### INSUR-003 — Claim automation mistakes incomplete evidence for fraud

Missing receipts, delayed care, inconsistent memories, damaged devices, unusual timelines, and language differences may trigger suspicion.

HARM: legitimate claims are delayed or denied.

OVERLAP TO CHECK: BENEFIT-002, FRAUDSCORE-001.

### INSUR-004 — Policy summary omits exclusions that control the real outcome

Coverage may appear broad while definitions, riders, limits, deductibles, location rules, and procedural deadlines narrow it.

HARM: the insured discovers the true protection only after loss.

OVERLAP TO CHECK: DOC-005, TERMS-001.

### INSUR-005 — Model-driven catastrophe repricing removes coverage from entire communities

Wildfire, flood, heat, storm, crime, and climate models may rapidly increase premiums or nonrenewals by region.

HARM: essential protection disappears where collective risk is rising.

OVERLAP TO CHECK: ENVRES-002, PRICE-003.

### INSUR-006 — Corrected claim decision does not repair secondary harm

Late payment or wrongful denial may already cause debt, eviction, missed care, business failure, or credit damage.

HARM: successful appeal restores the claim but not the consequences.

OVERLAP TO CHECK: DUE-006, CREDIT-004.

### PRICE-001 — Personalized pricing is hidden from the consumer

Different users may receive different prices based on location, device, history, urgency, account, or inferred willingness to pay.

HARM: consumers cannot compare offers or know whether they are being treated fairly.

OVERLAP TO CHECK: LEND-004, SURV-004.

### PRICE-002 — Price model uses protected-trait proxies

Neighborhood, language, browsing, device, payment method, time, and household data may correlate with race, disability, age, or income.

HARM: discriminatory pricing is implemented indirectly.

OVERLAP TO CHECK: HOUSING-002, INSUR-001.

### PRICE-003 — Dynamic pricing exploits emergencies or scarcity

Housing, transport, utilities, medicine, insurance, food, and communications may become more expensive during crisis.

HARM: people with the greatest immediate need face the highest price.

OVERLAP TO CHECK: FRAME-002, ENVRES-002.

### PRICE-004 — Comparison interface omits materially different terms

Displayed monthly price may hide fees, renewal changes, deductibles, cancellation rules, usage limits, and bundled obligations.

HARM: the cheapest-looking option is not the least costly.

OVERLAP TO CHECK: BILL-005, SUB-005.

### PRICE-005 — Algorithmic price response creates feedback loops

Competitors, marketplaces, landlords, insurers, or sellers may react to one another’s automated prices.

HARM: prices rise, oscillate, or coordinate without explicit human agreement.

OVERLAP TO CHECK: AGENT-001, REBOUND-005.

### FRAUDSCORE-001 — Fraud model treats unusual legitimate behavior as deception

Travel, disability, account recovery, family assistance, migration, crisis, device replacement, and irregular income may appear anomalous.

HARM: vulnerable users are blocked precisely when circumstances change.

OVERLAP TO CHECK: FRAUD-005, INCDET-002.

### FRAUDSCORE-002 — Fraud label propagates across unrelated services

A disputed flag from payment, banking, housing, benefits, insurance, or identity systems may be shared or inferred elsewhere.

HARM: one uncertain suspicion becomes broad exclusion.

OVERLAP TO CHECK: GOVREC-001, PUBID-001.

### FRAUDSCORE-003 — Fraud controls reveal the detection strategy to attackers but not users

Systems may give vague reasons to legitimate users while adversaries learn thresholds through repeated probing.

HARM: honest users cannot recover, while attackers adapt.

OVERLAP TO CHECK: ADV-005, DUE-003.

### FRAUDSCORE-004 — Manual review inherits the model’s suspicion framing

Reviewers may see a fraud score, red flag, or risk narrative before examining original evidence.

HARM: human review confirms rather than independently tests the allegation.

OVERLAP TO CHECK: DUE-004, COG-002.

### FRAUDSCORE-005 — Fraud prevention blocks essential funds or services without emergency release

Accounts, cards, claims, housing, benefits, and identity may be frozen while review takes days or weeks.

HARM: protective controls create immediate material hardship.

OVERLAP TO CHECK: PAY-001, ESSENTIAL-001.

### ALLOC-001 — Scarce-resource ranking hides value judgments

Housing, credit, insurance, aid, appointments, energy, and emergency support may be allocated by scores whose priorities are not public.

HARM: political and ethical choices appear as technical optimization.

OVERLAP TO CHECK: CIVIC-003, RANK-001.

### ALLOC-002 — Allocation data reflects past unequal access

Historical utilization may show who received services, not who needed them.

HARM: prior exclusion is used to justify future underallocation.

OVERLAP TO CHECK: POLICE-001, HIRE-001.

### ALLOC-003 — Queue position is lost after identity or documentation failure

A user may restart the process after address, account, upload, biometric, or verification errors.

HARM: technical problems erase accumulated waiting time.

OVERLAP TO CHECK: QUEUE-003, PUBID-002.

### ALLOC-004 — Allocation optimizes throughput by excluding complex cases

Systems may favor applicants who are easy to verify, serve, price, or automate.

HARM: people with complex needs wait longer or disappear from success metrics.

OVERLAP TO CHECK: ROLLOUT-007, BENEFIT-003.

### ALLOC-005 — Allocation appeal cannot preserve the scarce opportunity

A corrected score may arrive after the unit, loan, appointment, policy, or benefit window is gone.

HARM: procedural success cannot restore the lost resource.

OVERLAP TO CHECK: HOUSING-006, DUE-006.

### ESSENTIAL-001 — Essential service is suspended before dispute resolution

Electricity, water, communications, banking, insurance, housing, transport, or healthcare access may stop while billing, identity, or fraud issues remain contested.

HARM: administrative uncertainty creates immediate safety and livelihood risk.

OVERLAP TO CHECK: FRAUDSCORE-005, PAY-001.

### ESSENTIAL-002 — Digital-only service recovery excludes people in crisis

Restoration may require a charged phone, email, app, stable address, documents, payment, or biometric verification.

HARM: users cannot recover service because the outage removed the recovery tools.

OVERLAP TO CHECK: CIVIC-006, EMSAFE-005.

### ESSENTIAL-003 — Bundled essential services create cascading exclusion

One account, credit flag, identity error, or payment problem may affect phone, internet, banking, housing, transport, and utilities together.

HARM: a single administrative failure becomes systemic personal exclusion.

OVERLAP TO CHECK: PUBID-001, MONO-001.

### ESSENTIAL-004 — Consumer appeal lacks an independent human decision maker

Chatbots, scripts, outsourced support, and model-assisted reviewers may repeat the same policy and data source.

HARM: escalation appears available but no independent reconsideration occurs.

OVERLAP TO CHECK: DUE-004, SUP-004.

## Pass 31 result

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
- Current preserved plus provisional: 1325

NEXT DISCOVERY PASS:
Family, intimate relationships, domestic abuse, guardianship, caregiving, child welfare, reproductive autonomy, vulnerable dependents, and household power asymmetry.

END PACKET 01.5 — DISCOVERY PASS 31
