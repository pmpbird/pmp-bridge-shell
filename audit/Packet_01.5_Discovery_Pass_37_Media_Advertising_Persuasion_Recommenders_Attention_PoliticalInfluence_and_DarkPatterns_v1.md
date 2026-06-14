# Packet 01.5 — Discovery Pass 37

STATUS: DISCOVERY IN PROGRESS
PHASE: PROBLEM FINDING ONLY
ROUTING: NOT STARTED
DATE: 2026-06-14

This pass looks for media, advertising, persuasion, recommender-system, attention-capture, political-influence, dark-pattern, consumer-autonomy, and manipulation-resistant communication failure.

## Provisional records

### MEDIA-001 — Editorial judgment is hidden behind automated ranking

Placement, visibility, order, and prominence may appear neutral while reflecting platform goals, engagement signals, and unpublished rules.

HARM: distribution power is exercised without visible accountability.

OVERLAP TO CHECK: RANK-001, CIVIC-003.

### MEDIA-002 — Repetition is mistaken for independent confirmation

The same report may be syndicated, summarized, reposted, translated, and quoted across many outlets.

HARM: one source appears to become broad corroboration.

OVERLAP TO CHECK: MISINFO-003, DATA-003.

### MEDIA-003 — Correction receives less prominence than the original error

Updated headlines, appended notes, quiet edits, and later articles may not reach the original audience.

HARM: the false version remains the dominant public record.

OVERLAP TO CHECK: MISINFO-004, REPUT-003.

### MEDIA-004 — Breaking-news speed outruns verification

Competitive pressure may reward publication before identity, source, location, chronology, and context are confirmed.

HARM: early error shapes public understanding before evidence stabilizes.

OVERLAP TO CHECK: DEAD-005, PUBSCI-002.

### MEDIA-005 — Visual evidence is trusted without source context

Video, image, graph, screenshot, map, and audio may be cropped, edited, old, synthetic, or unrelated to the claimed event.

HARM: persuasive media overrides provenance and uncertainty.

OVERLAP TO CHECK: AUTHENT-002, AUTHENT-005.

### MEDIA-006 — Archive and search systems preserve superseded reporting

Old headlines, cached pages, clips, and summaries may remain more discoverable than later corrections.

HARM: obsolete public claims continue shaping decisions.

OVERLAP TO CHECK: MISINFO-006, PUB-005.

### ADS-001 — Advertising is not clearly distinguishable from editorial content

Sponsored articles, native ads, influencer posts, affiliate links, and promoted recommendations may mimic ordinary content.

HARM: commercial persuasion is mistaken for independent judgment.

OVERLAP TO CHECK: AUTHENT-001, PROV-001.

### ADS-002 — Advertiser targeting infers sensitive traits

Health, religion, politics, sexuality, income, family status, addiction, and vulnerability may be inferred from behavior.

HARM: intimate characteristics become inputs to persuasion without explicit disclosure.

OVERLAP TO CHECK: INFER-001, REPRO-001.

### ADS-003 — Vulnerable state increases persuasive pressure

Grief, crisis, debt, illness, loneliness, fear, urgency, and sleep deprivation may be detected or inferred.

HARM: the user is targeted when decision quality is weakest.

OVERLAP TO CHECK: STRESS-001, LEND-004.

### ADS-004 — Advertiser exclusion creates discriminatory access

Housing, jobs, credit, education, and services may be shown or withheld based on audience segmentation.

HARM: opportunity inequality occurs before application or formal decision.

OVERLAP TO CHECK: HIRE-002, HOUSING-002.

### ADS-005 — Measurement system rewards misleading creative content

Click-through, conversion, watch time, and recall may improve when ads exaggerate, frighten, or obscure terms.

HARM: optimization systematically favors manipulation.

OVERLAP TO CHECK: FEED-005, PRICE-004.

### ADS-006 — Ad delivery reveals private interests to nearby people

Lock screens, shared devices, family accounts, connected televisions, and public displays may expose sensitive targeting.

HARM: inferred private information is disclosed through the advertisement itself.

OVERLAP TO CHECK: FAMILY-002, USERPRIV-001.

### PERSUADE-001 — Persuasive intent is hidden behind helpful framing

Advice, summaries, defaults, reminders, education, and personalization may steer the user toward a preferred outcome.

HARM: influence occurs without informed awareness.

OVERLAP TO CHECK: FRAME-004, ADS-001.

### PERSUADE-002 — Emotional arousal substitutes for evidence

Fear, outrage, disgust, hope, belonging, and urgency may drive acceptance independently of claim quality.

HARM: decision strength exceeds evidentiary strength.

OVERLAP TO CHECK: STRESS-002, MEDIA-004.

### PERSUADE-003 — Social proof is manufactured or selectively displayed

Ratings, testimonials, follower counts, trending labels, endorsements, and purchase activity may be fake, filtered, or context-free.

HARM: perceived consensus manipulates user judgment.

OVERLAP TO CHECK: TRUST-007, PROV-004.

### PERSUADE-004 — Personalization creates different persuasive realities

Users may receive different facts, emphasis, prices, urgency, or arguments without knowing alternatives exist.

HARM: people cannot compare the basis of their decisions.

OVERLAP TO CHECK: PRICE-001, POL-002.

### PERSUADE-005 — Repeated exposure changes familiarity into perceived truth

A claim may feel more credible simply because it is encountered often.

HARM: platform repetition manufactures belief without new evidence.

OVERLAP TO CHECK: MISINFO-003, MEDIA-002.

### PERSUADE-006 — Opt-out language itself is persuasive or confusing

Privacy, subscription, tracking, and recommendation controls may frame refusal as loss, danger, or inconvenience.

HARM: the user’s nominal choice is steered toward acceptance.

OVERLAP TO CHECK: CONSENT-005, DARK-001.

### RECOMMEND-001 — Recommender objective differs from user wellbeing

Engagement, revenue, retention, or growth may dominate safety, diversity, accuracy, and long-term benefit.

HARM: the system optimizes behavior that is profitable but harmful.

OVERLAP TO CHECK: MEAS-001, ATTN-001.

### RECOMMEND-002 — Recommendation history traps the user in a narrowed identity

Past clicks, searches, purchases, or watch behavior may repeatedly reinforce one interest, mood, ideology, or vulnerability.

HARM: temporary behavior becomes a persistent informational cage.

OVERLAP TO CHECK: DEV-004, LEARN-006.

### RECOMMEND-003 — Exploration exposes users to escalating harmful material

The system may test increasingly extreme, sensational, sexual, violent, conspiratorial, or self-destructive content.

HARM: experimentation by the system becomes risk borne by the user.

OVERLAP TO CHECK: MOD-003, CRISIS-001.

### RECOMMEND-004 — Recommendation quality is evaluated only by immediate response

Long-term regret, polarization, sleep loss, compulsive use, and changed beliefs may not be measured.

HARM: short-term engagement hides delayed harm.

OVERLAP TO CHECK: DESIGN-006, REBOUND-001.

### RECOMMEND-005 — User cannot understand why a recommendation appeared

Source signals, sponsorship, similarity, social influence, inferred traits, and ranking factors may remain hidden.

HARM: users cannot correct or resist the system’s assumptions.

OVERLAP TO CHECK: DUE-003, HIRE-005.

### RECOMMEND-006 — Shared account recommendations reveal one person to another

Household members may infer searches, purchases, relationships, health concerns, or private interests from recommendations.

HARM: personalization becomes indirect surveillance.

OVERLAP TO CHECK: HOUSE-002, ADS-006.

### ATTN-001 — Infinite feeds remove natural stopping cues

Autoplay, endless scroll, variable refresh, streaks, and continuous recommendations may prevent reflective disengagement.

HARM: time and attention are captured beyond deliberate choice.

OVERLAP TO CHECK: COG-006, REBOUND-001.

### ATTN-002 — Notification timing exploits interruption vulnerability

Alerts may be scheduled around inactivity, bedtime, emotional events, location, or predicted availability.

HARM: the system repeatedly overrides the user’s intended focus.

OVERLAP TO CHECK: NOTIFY-004, INTERRUPT-001.

### ATTN-003 — Variable rewards encourage compulsive checking

Uncertain likes, messages, offers, matches, and new content may reinforce repeated return behavior.

HARM: behavioral conditioning replaces intentional use.

OVERLAP TO CHECK: FEED-003, NUTRI-003.

### ATTN-004 — Attention capture displaces sleep, care, work, and offline relationships

Usage metrics may improve while essential activities degrade.

HARM: platform success hides life-level cost.

OVERLAP TO CHECK: FAT-001, LABOR-004.

### ATTN-005 — User controls are too weak to counter learned habits

Timers, mute settings, and limits may be easy to override, buried, or undermined by re-engagement prompts.

HARM: formal controls do not restore practical autonomy.

OVERLAP TO CHECK: CONSENT-005, DARK-004.

### POL-001 — Political advertising source and funding are obscured

Intermediaries, nonprofits, foreign entities, influencers, issue campaigns, and shell organizations may hide who paid.

HARM: voters cannot evaluate the interests behind persuasion.

OVERLAP TO CHECK: PROV-001, PEER-002.

### POL-002 — Microtargeted political messages avoid public scrutiny

Different groups may receive contradictory claims, fears, promises, and turnout messages.

HARM: democratic debate fragments into invisible personalized persuasion.

OVERLAP TO CHECK: PERSUADE-004, CIVIC-001.

### POL-003 — Political recommendation systems amplify conflict because it engages

Outrage, identity threat, and adversarial framing may outperform nuance and compromise.

HARM: platform incentives increase polarization and social instability.

OVERLAP TO CHECK: RECOMMEND-001, PERSUADE-002.

### POL-004 — Synthetic political media spreads faster than authentication

Generated voice, video, images, and documents may circulate before verification or correction.

HARM: false events influence civic action in the critical time window.

OVERLAP TO CHECK: IMPERSON-003, MEDIA-004.

### POL-005 — Voter suppression messages target procedural confusion

False deadlines, eligibility claims, polling locations, document requirements, and intimidation may be personalized.

HARM: people lose participation through manipulated uncertainty.

OVERLAP TO CHECK: VOTE-001, MISINFO-001.

### DARK-001 — Interface makes acceptance easier than refusal

Consent, purchase, subscription, tracking, and sharing may use prominent approval and hidden rejection paths.

HARM: interface friction substitutes for genuine choice.

OVERLAP TO CHECK: CONSENT-005, PERSUADE-006.

### DARK-002 — Cancellation or deletion is intentionally harder than enrollment

Multiple screens, calls, delays, retention offers, identity loops, and warnings may obstruct exit.

HARM: users remain in relationships they attempted to end.

OVERLAP TO CHECK: SUB-002, PRIVRIGHT-002.

### DARK-003 — Scarcity and urgency signals are fabricated or unverifiable

Countdowns, limited stock, expiring prices, waitlists, and “others are viewing” messages may be artificial.

HARM: time pressure suppresses comparison and reflection.

OVERLAP TO CHECK: PRICE-003, PERSUADE-002.

### DARK-004 — Defaults reactivate after updates or account changes

Tracking, sharing, notifications, subscriptions, and recommendations may return after software change or migration.

HARM: earlier refusal does not remain effective.

OVERLAP TO CHECK: REMOTE-003, CONSENT-001.

### AUTON-001 — System presents one path while hiding meaningful alternatives

Interface order, defaults, summaries, and recommendations may conceal lower-cost, safer, slower, or less profitable options.

HARM: the user chooses within an artificially narrowed field.

OVERLAP TO CHECK: FRAME-002, PRICE-004.

### AUTON-002 — Explanation arrives after the user has already committed

Terms, sponsorship, personalization, risk, and data use may be disclosed only after click, purchase, upload, or enrollment.

HARM: awareness occurs too late to guide consent.

OVERLAP TO CHECK: DUAL-002, CONSENT-002.

### AUTON-003 — Manipulation-resistant mode is unavailable during vulnerability

Users may lack a low-stimulation, chronological, ad-free, nonpersonalized, or delay-based interface when distressed or fatigued.

HARM: the system remains most persuasive when resistance is weakest.

OVERLAP TO CHECK: STRESS-001, EDACCESS-003.

### AUTON-004 — User preference is inferred from behavior produced by prior manipulation

Clicks, time spent, purchases, and returns may reflect pressure, habit, confusion, or lack of alternatives.

HARM: coerced behavior is used to justify further personalization.

OVERLAP TO CHECK: RECOMMEND-002, CONSENT-005.

## Pass 37 result

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
- Current preserved plus provisional: 1577

NEXT DISCOVERY PASS:
Culture, religion, language preservation, identity, heritage, representation, community norms, pluralism, sacred knowledge, and cross-cultural interpretation.

END PACKET 01.5 — DISCOVERY PASS 37
