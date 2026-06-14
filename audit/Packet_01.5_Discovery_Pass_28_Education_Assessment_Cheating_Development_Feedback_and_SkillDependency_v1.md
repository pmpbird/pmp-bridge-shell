# Packet 01.5 — Discovery Pass 28

STATUS: DISCOVERY IN PROGRESS
PHASE: PROBLEM FINDING ONLY
ROUTING: NOT STARTED
DATE: 2026-06-14

This pass looks for education and learning-integrity failure, invalid assessment, cheating, developmental mismatch, teacher-authority conflict, feedback defects, accommodation boundaries, and long-term loss of independent competence.

## Provisional records

### LEARN-001 — Correct answer is mistaken for demonstrated understanding

A learner may submit accurate text, code, calculations, or explanations without being able to reproduce the reasoning independently.

HARM: performance evidence overstates actual learning.

OVERLAP TO CHECK: TRUST-001, ASSESS-001.

### LEARN-002 — Explanation is matched to the task but not the learner’s prior knowledge

The system may assume vocabulary, concepts, reading level, cultural context, or prerequisite skills the learner does not possess.

HARM: fluent instruction produces confusion or memorized imitation.

OVERLAP TO CHECK: COG-007, MEDINT-006.

### LEARN-003 — Immediate fluency is mistaken for durable retention

A learner may understand during guided interaction but fail after delay, distraction, or removal of prompts.

HARM: short-term assistance is recorded as stable competence.

OVERLAP TO CHECK: TRAIN-001, INTERRUPT-005.

### LEARN-004 — Retrieval practice is replaced by answer exposure

The system may reveal definitions, steps, code, or solutions before the learner attempts recall.

HARM: productive difficulty and memory formation are weakened.

OVERLAP TO CHECK: RELY-002, SKILL-001.

### LEARN-005 — Learning path optimizes completion instead of conceptual structure

Instruction may minimize time, steps, or errors while skipping relationships, causes, transfer, and foundational understanding.

HARM: the learner completes tasks without building a usable mental model.

OVERLAP TO CHECK: FRAME-003, COG-008.

### LEARN-006 — Incorrect learner model persists after evidence changes

The system may continue assuming a learner is advanced, struggling, attentive, fluent, or familiar based on stale history.

HARM: later instruction remains mismatched and reinforces the wrong profile.

OVERLAP TO CHECK: KB-003, HEALTH-004.

### ASSESS-001 — Assessment measures tool access instead of learner ability

A task may be completed through AI, search, templates, calculators, collaborators, or cached material rather than the intended skill.

HARM: the score does not represent the construct being assessed.

OVERLAP TO CHECK: LEARN-001, CHEAT-001.

### ASSESS-002 — Assessment conditions differ across learners

Device quality, network, time zone, language, disability support, account access, and model availability may vary.

HARM: scores reflect environment inequality rather than competence.

OVERLAP TO CHECK: EDACCESS-001, ENV-001.

### ASSESS-003 — Rubric rewards surface form over reasoning quality

Length, formatting, vocabulary, citation count, polished code, or expected phrases may dominate evaluation.

HARM: learners optimize appearance instead of understanding.

OVERLAP TO CHECK: TRUST-001, RANK-004.

### ASSESS-004 — Automated grading accepts one valid-looking path only

Alternative reasoning, notation, language, code structure, cultural examples, and creative solutions may be marked wrong.

HARM: valid competence is rejected because it differs from the grader’s template.

OVERLAP TO CHECK: EVAL-001, MOD-002.

### ASSESS-005 — Assessment item leaks into training or retrieval systems

Questions, answer keys, rubrics, and prior submissions may become searchable or model-accessible.

HARM: future results measure exposure rather than learning.

OVERLAP TO CHECK: KB-001, CHEAT-002.

### ASSESS-006 — Repeated assessment teaches the test rather than the domain

Practice on near-identical prompts may improve scores without improving transfer to new situations.

HARM: test familiarity is mistaken for general competence.

OVERLAP TO CHECK: PERF-007, LEARN-005.

### ASSESS-007 — High-stakes decision relies on one noisy measurement

Placement, certification, progression, discipline, or opportunity may depend on one exam, model score, or timed interaction.

HARM: temporary conditions create durable educational consequences.

OVERLAP TO CHECK: MEAS-002, INCSEV-002.

### CHEAT-001 — Unauthorized assistance is indistinguishable from permitted support

Tutoring, grammar help, accessibility tools, translation, brainstorming, code completion, and answer generation may overlap.

HARM: honest accommodation is punished or prohibited help is accepted.

OVERLAP TO CHECK: CONSENT-001, EDACCESS-002.

### CHEAT-002 — Detection relies on unreliable style or similarity signals

Writing style, perplexity, phrase matching, timing, and code similarity may be influenced by language, disability, templates, or common sources.

HARM: innocent learners are accused while sophisticated misuse passes.

OVERLAP TO CHECK: MOD-002, AUTHENT-005.

### CHEAT-003 — Assignment design makes unauthorized assistance the rational strategy

Excessive workload, unclear instruction, unrealistic deadlines, low relevance, and punitive grading may push learners toward outsourcing.

HARM: system design creates the behavior it later condemns.

OVERLAP TO CHECK: DEAD-005, FRAME-002.

### CHEAT-004 — Shared accounts or devices obscure who completed the work

Family, classmates, tutors, labs, and borrowed devices may use one identity or environment.

HARM: authorship and accountability cannot be established reliably.

OVERLAP TO CHECK: USERPRIV-002, DELEG-003.

### CHEAT-005 — Anti-cheating controls invade privacy or accessibility

Remote proctoring, camera, microphone, screen monitoring, room scans, biometrics, and behavior tracking may collect excessive data or exclude users.

HARM: assessment integrity is pursued through disproportionate surveillance and unequal access.

OVERLAP TO CHECK: MOD-005, ACCESSLAW-003.

### DEV-001 — Content is developmentally inappropriate

Reading level, abstraction, emotional intensity, sexual content, violence, health detail, financial pressure, or legal concepts may exceed the learner’s stage.

HARM: instruction confuses, frightens, or harms the learner.

OVERLAP TO CHECK: COG-007, HEALTH-005.

### DEV-002 — Child or dependent user is treated as able to provide full consent

Data collection, publication, account linking, provider use, and long-term storage may proceed without valid guardian or institutional authority.

HARM: vulnerable-user data is processed without lawful or meaningful permission.

OVERLAP TO CHECK: CONSENT-006, PRIVRIGHT-001.

### DEV-003 — System bypasses healthy struggle and adult guidance

A learner may receive immediate answers, emotional reassurance, conflict advice, or value judgments without space for teacher, parent, or mentor involvement.

HARM: development shifts from supported growth to private machine dependence.

OVERLAP TO CHECK: LEARN-004, RELY-002.

### DEV-004 — Personalized feedback reinforces a fixed identity

Labels such as gifted, weak, slow, advanced, creative, inattentive, or not technical may persist and shape future instruction.

HARM: provisional performance becomes a limiting self-concept.

OVERLAP TO CHECK: LEARN-006, FEED-003.

### DEV-005 — Safety intervention conflicts with developmental context

A child’s joke, fantasy, curiosity, distress, or classroom topic may be interpreted without age, setting, or guardian context.

HARM: real risk is missed or ordinary development is escalated inappropriately.

OVERLAP TO CHECK: CRISIS-002, FRAME-001.

### TEACH-001 — System instruction conflicts with teacher or curriculum authority

The AI may use different definitions, notation, historical framing, methods, standards, or assignment rules.

HARM: the learner receives internally coherent but institutionally incompatible guidance.

OVERLAP TO CHECK: AUTH-005, DOC-005.

### TEACH-002 — Teacher cannot inspect or reproduce the learner’s support path

Personalized prompts, hidden context, model changes, and adaptive responses may not be preserved.

HARM: educators cannot evaluate how the learner arrived at the result.

OVERLAP TO CHECK: PROOFCHAIN-008, RANK-006.

### TEACH-003 — AI becomes a hidden evaluator without institutional approval

Feedback, ranking, placement, misconduct flags, and grading may influence outcomes despite lacking formal authority.

HARM: automated judgment governs learners outside declared policy.

OVERLAP TO CHECK: PRIVRIGHT-005, AUTH-008.

### TEACH-004 — Teacher dependence shifts curriculum toward what the system handles well

Assignments may avoid oral work, hands-on practice, ambiguity, local knowledge, or creative process because automation cannot assess them easily.

HARM: educational goals narrow around machine convenience.

OVERLAP TO CHECK: MEAS-001, LEARN-005.

### TEACH-005 — Institutional policy changes without reaching all educators and learners

Rules for permitted AI use, citation, privacy, accommodations, and assessment may differ by class, term, teacher, or platform.

HARM: the same behavior is treated as acceptable and misconduct in different contexts.

OVERLAP TO CHECK: UPDATE-001, MOD-001.

### FEED-001 — Feedback is correct but arrives too late to guide the next attempt

Batch grading, queue delay, provider outage, or teacher review may return guidance after habits and misconceptions have hardened.

HARM: feedback records error without improving learning.

OVERLAP TO CHECK: SCHED-007, QUEUE-001.

### FEED-002 — Excessive feedback overwhelms the learner

Long corrections, many warnings, multiple rubrics, and simultaneous suggestions may exceed attention and working memory.

HARM: the learner cannot identify the highest-value next change.

OVERLAP TO CHECK: COG-001, NOTIFY-004.

### FEED-003 — Feedback tone changes motivation and self-concept

Overpraise, harshness, certainty, comparison, or impersonal language may alter confidence independently of actual performance.

HARM: the learner becomes dependent, discouraged, or falsely confident.

OVERLAP TO CHECK: TRUST-001, DEV-004.

### FEED-004 — Feedback corrects the product but not the misconception

The system may rewrite the sentence, calculation, proof, or code without identifying the faulty mental step.

HARM: the visible artifact improves while the underlying error persists.

OVERLAP TO CHECK: POST-002, LEARN-001.

### FEED-005 — Feedback loop optimizes for approval rather than truth

Learners may discover that certain phrasing, length, agreement, emotional tone, or style receives better automated responses.

HARM: interaction trains performative compliance instead of honest reasoning.

OVERLAP TO CHECK: ASSESS-003, ADV-005.

### SKILL-001 — Repeated assistance weakens independent recall

The learner may rely on prompts, autocomplete, explanations, and worked examples before attempting unaided thought.

HARM: capability disappears when the system is absent.

OVERLAP TO CHECK: LEARN-004, RELY-003.

### SKILL-002 — Tool skill is mistaken for domain skill

Prompting, searching, editing generated output, and choosing among answers may produce good work without foundational competence.

HARM: the learner cannot verify or repair the result independently.

OVERLAP TO CHECK: ASSESS-001, TRUST-004.

### SKILL-003 — Automation removes error-detection practice

Spelling, arithmetic, coding, citation, planning, and factual checks may be corrected automatically before the learner notices the mistake.

HARM: the learner fails to build internal monitoring skills.

OVERLAP TO CHECK: FEED-004, TOOL-004.

### SKILL-004 — Long-term dependence is hidden by rising output quality

Work products may improve while unaided speed, memory, judgment, and transfer decline.

HARM: external performance masks internal skill loss.

OVERLAP TO CHECK: FAT-006, LEARN-003.

### SKILL-005 — System outage becomes an educational access failure

Assignments, notes, explanations, grading, accommodations, and communication may depend on one provider or device.

HARM: learners cannot continue when the system is unavailable.

OVERLAP TO CHECK: MONO-001, CONT-001.

### SKILL-006 — Learner cannot distinguish when assistance is appropriate

The same tool may be useful for practice, brainstorming, accessibility, translation, answer generation, and high-stakes assessment.

HARM: dependence and misconduct grow because boundaries are not learned.

OVERLAP TO CHECK: CHEAT-001, TRAIN-006.

### EDACCESS-001 — Educational access requires hardware, network, or paid services some learners lack

Device age, bandwidth, accounts, subscriptions, quiet space, and technical support may determine participation.

HARM: educational opportunity follows infrastructure and income rather than learning need.

OVERLAP TO CHECK: ASSESS-002, ECO-003.

### EDACCESS-002 — Accommodation is confused with unfair advantage

Translation, text-to-speech, speech input, extended time, simplified layout, human support, and AI assistance may be judged inconsistently.

HARM: disabled or multilingual learners lose legitimate access or are falsely accused.

OVERLAP TO CHECK: CHEAT-001, ACCESSLAW-001.

### EDACCESS-003 — Accessibility adaptation changes the assessed construct

Reading support, hints, formatting, calculation aids, and generated explanations may help access the task but also perform part of the target skill.

HARM: accommodation either remains insufficient or invalidates the measurement.

OVERLAP TO CHECK: ASSESS-001, ACCESSLAW-002.

## Pass 28 result

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
- Current preserved plus provisional: 1199

NEXT DISCOVERY PASS:
Employment, labor displacement, worker surveillance, hiring and evaluation bias, workplace authority, job-skill erosion, contractor dependence, and employment-record privacy.

END PACKET 01.5 — DISCOVERY PASS 28
