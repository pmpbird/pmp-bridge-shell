# Packet 01.5 — Discovery Pass 62

STATUS: DISCOVERY IN PROGRESS
PHASE: PROBLEM FINDING ONLY
ROUTING: NOT STARTED
COUNT MODE: NATURAL YIELD
DATE: 2026-06-14

This pass looks for natural-hazard and disaster-management failure involving earthquake, tsunami, severe storm, extreme heat, volcanic activity, landslide, warning governance, mass evacuation, sheltering, mutual aid, and long-term recovery.

APPLICABILITY GATE: These are conditional future candidates, not proof of current app defects. They become applicable only if the project stores, interprets, recommends, coordinates, routes, or governs hazard, warning, evacuation, shelter, emergency, recovery, infrastructure, or public-safety information, decisions, or services.

## Provisional records

### EARTH-001 — Earthquake planning relies on mapped fault and shaking assumptions that omit local variation

Soil, fill, basin effects, liquefaction, landslide, building condition, and utility routing may change damage sharply over short distances.

HARM: regional hazard estimates create false confidence at the site level.

OVERLAP TO CHECK: STRUCT-001, GROUNDWATER-002.

### EARTH-002 — Building survival is mistaken for functional habitability

A structure may remain standing while water, power, sanitation, elevators, fire protection, access, and medical support fail.

HARM: people return to a building that cannot safely support life.

OVERLAP TO CHECK: WILDFIRE-003, PUBLICDEP-001.

### EARTH-003 — Aftershock risk is treated as a smaller repeat of the first event

Already damaged structures, slopes, bridges, utilities, and response teams may have much less remaining margin.

HARM: a lower-magnitude event causes disproportionate secondary collapse and injury.

OVERLAP TO CHECK: PERSIST-001, CASCADE-001.

### EARTH-004 — Lifeline restoration priorities conflict across electricity, water, telecom, transport, and healthcare

Each service may need another restored first.

HARM: circular dependencies delay all critical recovery.

OVERLAP TO CHECK: RESTORE-003, WATERGOV-001.

### TSUNAMI-001 — Warning time is consumed by detection, confirmation, authority, and message approval

Source uncertainty, sensor damage, communication delay, and governance layers may narrow the evacuation window.

HARM: an accurate warning arrives too late for people to reach safety.

OVERLAP TO CHECK: NUCEM-001, WILDFIRE-001.

### TSUNAMI-002 — Evacuation maps assume roads and vertical refuges remain usable after the initiating earthquake

Bridges, debris, power, elevators, signage, lighting, and crowd movement may fail simultaneously.

HARM: the designated route or refuge cannot be used during the real event.

OVERLAP TO CHECK: COAST-005, DAM-005.

### TSUNAMI-003 — All-clear communication occurs before later waves and contaminated return conditions are understood

Wave sequences, debris, fire, sewage, hazardous material, and damaged infrastructure may persist.

HARM: people return into a continuing or transformed hazard.

OVERLAP TO CHECK: INCCMD-005, MARCONT-004.

### STORM-001 — Severe-storm forecast precision hides uncertainty in track, intensity, and local impact

Small changes may alter wind, surge, rain, tornado, ice, and outage consequences.

HARM: precise-looking products produce overconfidence in who is safe or endangered.

OVERLAP TO CHECK: FLIGHTOPS-005, FRAME-001.

### STORM-002 — Protective action for one storm hazard increases exposure to another

Evacuating from surge may create wind or traffic risk, while sheltering from wind may increase flood exposure.

HARM: one correct instruction becomes dangerous under a compound event.

OVERLAP TO CHECK: NUCEM-003, CASCADE-001.

### STORM-003 — Generator deployment solves electricity loss while creating fuel, exhaust, fire, and maintenance hazards

Improvised placement, indoor use, scarce fuel, damaged wiring, and prolonged operation may increase risk.

HARM: backup power creates poisoning, fire, or unsafe electrical conditions.

OVERLAP TO CHECK: ENERGYGOV-002, FIRE-005.

### STORM-004 — Debris and access failure delay emergency response after the peak hazard passes

Flooding, trees, wires, damaged bridges, abandoned vehicles, and communication loss may isolate communities.

HARM: survivable injuries and outages become fatal through delayed access.

OVERLAP TO CHECK: EMDISP-003, LOGISTICS-002.

### HEAT-001 — Heat-risk thresholds ignore indoor exposure and nighttime recovery failure

Housing quality, urban heat, humidity, ventilation, power loss, medication, age, and disability may keep bodies from cooling.

HARM: official temperature thresholds understate lethal personal exposure.

OVERLAP TO CHECK: HOUSING-004, PHCOMMS-002.

### HEAT-002 — Cooling-center availability is counted without checking practical access

Distance, transport, hours, pets, disability, language, fear, identification, and capacity may block use.

HARM: nominal refuge exists while high-risk people remain trapped in heat.

OVERLAP TO CHECK: SANACC-001, ACCESSLAW-002.

### HEAT-003 — Grid protection curtails power where cooling dependence is highest

Load shedding, equipment trips, wildfire prevention, and market constraints may remove air conditioning during peak heat.

HARM: system protection transfers life-safety risk to households and care facilities.

OVERLAP TO CHECK: NUC-005, GRID-002.

### HEAT-004 — Worker protection rules fail under piece-rate, informal, and subcontracted labor

Rest, water, shade, acclimatization, reporting, and schedule changes may reduce income or invite retaliation.

HARM: formal protections are bypassed by economic pressure.

OVERLAP TO CHECK: WASTELABOR-001, MINEWORK-001.

### VOLCANO-001 — Volcanic hazard zones are treated as stable despite changing vents and pathways

Topography, snow, water, wind, drainage, eruption style, and new openings may redirect ash, lava, gas, and lahars.

HARM: mapped safety boundaries fail under a different eruption pattern.

OVERLAP TO CHECK: FLOODCTRL-003, NUCEM-005.

### VOLCANO-002 — Ash impact is evaluated mainly as an aviation problem

Water treatment, lungs, crops, machinery, power, roofs, roads, electronics, and livestock may fail across a wide area.

HARM: response underestimates multi-system disruption far from the volcano.

OVERLAP TO CHECK: AIRCARGO-001, PUBLICDEP-001.

### VOLCANO-003 — Long unrest period exhausts trust and preparedness before eruption

Repeated alerts, evacuation, economic loss, school closure, tourism decline, and uncertain timing may create warning fatigue.

HARM: people ignore or resist the warning that eventually matters.

OVERLAP TO CHECK: ALERT-001, TRUST-003.

### LANDSLIDE-001 — Slope stability is inferred from visible surface condition

Groundwater, internal shear, buried layers, drainage, excavation, roots, fire damage, and slow movement may remain hidden.

HARM: apparently stable ground fails without adequate warning.

OVERLAP TO CHECK: PRESSURE-002, DAM-004.

### LANDSLIDE-002 — Protective drainage redirects water into another unstable slope or community

Ditches, culverts, pumps, retaining systems, and road cuts may transfer flow and erosion.

HARM: local stabilization creates remote failure.

OVERLAP TO CHECK: FLOODCTRL-002, WATERSHED-002.

### LANDSLIDE-003 — Closure and evacuation decisions lag because movement is gradual and uncertain

Small cracks, deformation, noise, blocked drains, and sensor changes may be dismissed until acceleration.

HARM: intervention begins after the safe movement window closes.

OVERLAP TO CHECK: INCDET-002, DROUGHT-001.

### WARNGOV-001 — Multiple agencies issue warnings with different boundaries and urgency

Weather, fire, flood, dam, health, police, transport, and local authorities may use incompatible systems.

HARM: the public cannot tell which instruction governs their location and hazard.

OVERLAP TO CHECK: INCCMD-004, EMCOMMS-002.

### WARNGOV-002 — Warning language assumes literacy, hearing, sight, language, cognition, and device access

Sirens, maps, text, apps, television, radio, and social media may exclude different groups.

HARM: equal distribution produces unequal access to lifesaving information.

OVERLAP TO CHECK: LOC-003, BLDACC-002.

### WARNGOV-003 — False-alarm cost is weighted more heavily than missed-event harm

Economic disruption, political criticism, evacuation burden, and trust concerns may delay warning.

HARM: institutions wait for certainty that arrives after useful action time.

OVERLAP TO CHECK: DEAD-005, INCSEV-002.

### WARNGOV-004 — Warning system confirms message delivery but not comprehension or action

Receipt, opening, and device acknowledgment do not prove the person understood, believed, or could comply.

HARM: technical delivery is mistaken for public protection.

OVERLAP TO CHECK: NOTIFY-003, PHCOMMS-002.

### MASSEVAC-001 — Evacuation model assumes households leave together with private vehicles

Caregiving, disability, custody, work, school, pets, fuel, vehicle access, and separated families may produce different movement.

HARM: planned road demand and support needs differ from real evacuation behavior.

OVERLAP TO CHECK: COAST-005, CAREGIVER-001.

### MASSEVAC-002 — Contraflow and route control strand people who need to move toward the hazard area

Responders, caregivers, healthcare workers, family reunification, and supply vehicles may require opposite travel.

HARM: traffic optimization blocks essential movement and support.

OVERLAP TO CHECK: ATC-002, EMROUTE-002.

### MASSEVAC-003 — Evacuation order separates people from medicine, equipment, animals, and support networks

Rapid departure may leave behind prescriptions, oxygen, mobility devices, communication aids, documents, and caregivers.

HARM: escape from the hazard creates a medical or dependency crisis.

OVERLAP TO CHECK: RELEASECUST-001, CARETRANS-001.

### MASSEVAC-004 — Return authorization follows infrastructure status but not household-specific safety

A neighborhood may reopen while individual homes retain contamination, structural damage, mold, heat, or access barriers.

HARM: general reopening directs people into unsafe private conditions.

OVERLAP TO CHECK: DECOMNUC-004, WILDFIRE-003.

### SHELTER-001 — Shelter capacity counts floor space rather than usable support capability

Accessibility, privacy, infection control, medication, behavioral health, electricity, refrigeration, pets, and security may be missing.

HARM: nominal capacity cannot safely serve the arriving population.

OVERLAP TO CHECK: HCAP-001, SANACC-002.

### SHELTER-002 — Congregate sheltering increases violence, exploitation, and family-separation risk

Crowding, poor supervision, shared facilities, stress, missing records, and unequal power may create harm.

HARM: refuge from the disaster becomes a site of new abuse.

OVERLAP TO CHECK: ABUSE-001, FAMILYCUST-001.

### SHELTER-003 — Shelter registration requirements exclude people without documents or trusted identity

Displacement, homelessness, migration status, lost property, and damaged records may prevent verification.

HARM: people most affected by the disaster are denied safe shelter.

OVERLAP TO CHECK: STATELESS-001, BORDER-001.

### SHELTER-004 — Temporary shelter becomes long-term housing without long-term design

Privacy, sanitation, education, healthcare, disability support, employment, and governance may not scale with duration.

HARM: emergency accommodation hardens into prolonged unsafe displacement.

OVERLAP TO CHECK: RADWASTE-003, DISPLACE-005.

### DISREC-001 — Damage assessment favors visible property over lost function and social networks

Care, transport, work, schooling, health, culture, communication, and local businesses may fail without obvious structural destruction.

HARM: recovery funding misses the systems that make the community livable.

OVERLAP TO CHECK: MACROECON-001, RECOVER-003.

### DISREC-002 — Insurance and aid documentation burden excludes those with the greatest loss

Receipts, titles, photos, addresses, bank access, deadlines, language, and internet may be unavailable after disaster.

HARM: assistance follows record quality rather than need.

OVERLAP TO CHECK: DISELIG-003, BENEFIT-001.

### DISREC-003 — Rebuilding restores the pre-disaster vulnerability

Codes, land use, utilities, housing patterns, finance, and political pressure may favor rapid replacement over safer redesign.

HARM: recovery recreates the conditions for the next disaster.

OVERLAP TO CHECK: RESTORE-004, REBOUND-001.

### DISREC-004 — Buyout and relocation programs preserve financial value but destroy community continuity

Eligibility, appraisal, timing, replacement markets, schools, culture, and social ties may not be restored.

HARM: risk reduction is achieved through fragmented displacement and loss of belonging.

OVERLAP TO CHECK: COAST-003, RESERVOIR-004.

### DISREC-005 — Recovery governance ends before health, debt, trauma, and service effects stabilize

Visible debris removal and infrastructure reopening may occur long before household and institutional recovery.

HARM: official closure removes attention and support while long-tail harm continues.

OVERLAP TO CHECK: INCCMD-005, BHREC-001.

## Pass 62 result

Natural-yield provisional records: 38
Routing decisions made: 0
Records closed: 0
Deduplication required later: Yes
Discovery saturation: NOT REACHED

Corrected working total:
- Preserved baseline: 122
- Prior actual provisional headings: 2425
- Pass 62 natural-yield provisional: 38
- Current actual provisional headings: 2463
- Current combined working total: 2585

NEXT DISCOVERY PASS:
Rail systems and mass-freight corridors, including signaling, dispatch, train integrity, grade crossings, track and rolling-stock maintenance, dangerous-goods trains, passenger evacuation, corridor communities, automation, and accident investigation.

END PACKET 01.5 — DISCOVERY PASS 62
