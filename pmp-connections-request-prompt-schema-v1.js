(()=>{
'use strict';
const V='1.0.0-self-defining-request-schema';
function requestPrompt(){return `I need you to create a PMP outside-project transfer packet for the ChatGPT project we are currently inside.

IMPORTANT BOUNDARY
You are the SOURCE project. The PMP app is only the RECEIVER.
Do not make your material official PMP.
Do not claim PMP has accepted, verified, promoted, stored, validated, or made this source official.
Return JSON only. No markdown. No explanation outside JSON.

CREATE OR REUSE ID
Create or reuse a short lowercase project_state_id using letters, numbers, and underscores only.
Use unknown or not_provided when something cannot be known from the current source project. Do not guess.

TOP-LEVEL JSON KEYS REQUIRED
Return one JSON object with exactly these top-level keys:
- type
- packet_version
- project_state_id
- project_name
- project_kind
- source_identity_capture
- transfer_body_capture
- packet_tracks
- quality_truth
- receiver_safe_handoff
- next_move

FIELD DEFINITIONS

type:
Use "PMP_OUTSIDE_PROJECT_TRANSFER_PACKET".

packet_version:
Use "1.0_self_defining_schema" unless you have a reason to mark another compatible version.

project_state_id:
Short stable id for this source project state. Lowercase letters, numbers, underscores only.

project_name:
Human-readable name of the source project or conversation.

project_kind:
What kind of source this is, for example chatgpt_project, app_build_project, research_project, music_project, writing_project, bug_diagnosis_project, or other.

source_identity_capture:
Identify the source without making it official PMP. Include:
- source_is: "current_chatgpt_project"
- source_name
- source_boundary
- owner_or_user_if_known
- current_date_if_known
- what_this_source_can_authoritatively_say
- what_this_source_cannot_authoritatively_say

transfer_body_capture:
The actual source state to transfer. Include:
- concise_summary
- current_goal
- current_state
- important_decisions
- working_rules_or_constraints
- open_questions
- known_risks
- latest_user_intent
- useful_context_for_receiver
- important_exact_phrases_if_any

packet_tracks:
Object with keys A0_kernel through A6_receiver_action. Define and fill each track:

A0_kernel:
The core truth that must survive transfer. The smallest central point of the project.

A1_orientation:
How the receiver should understand the project: purpose, role, scope, and boundary.

A2_shape:
The structure or map of the project: sections, systems, flow, components, or organization.

A3_body:
The actual content/state being transferred: facts, decisions, current work, data, notes, and context.

A4_protection:
Privacy, safety, ownership, do-not-promote rules, do-not-change rules, and what must not be assumed.

A5_quality_truth:
Honest quality status of the transfer: what is complete, partial, uncertain, missing, unverified, stale, or possibly wrong.

A6_receiver_action:
What the PMP receiver should do next with this packet: receive only, store as candidate, ask user, preserve, compare, validate, or hold.

quality_truth:
The honesty layer for the whole packet. Include:
- overall_quality_level: high, medium, low, or unknown
- what_is_known
- what_is_missing
- what_is_uncertain
- what_is_inferred
- what_is_unverified
- freshness_or_staleness
- confidence_notes
- do_not_claim

receiver_safe_handoff:
Rules for the PMP app as receiver. Include:
- receiver_role: "receiver_only"
- safe_to_store_as: candidate_source_packet, reference_only, private_note, or hold_for_user_review
- may_promote_to_official_pmp: false unless explicitly proven and user-approved
- must_not_overwrite_existing_pmp_state: true
- must_preserve_source_boundary: true
- needs_user_confirmation_before_action
- privacy_notes

next_move:
A short object with:
- recommended_next_step_for_user
- recommended_next_step_for_pmp_receiver
- stop_or_continue
- reason

MISSING INFORMATION RULES
If a field cannot be filled, do not omit it. Use one of:
- "unknown"
- "not_provided"
- "not_visible_in_current_context"
- []
Also list missing items inside quality_truth.what_is_missing.

OUTPUT RULE
Return valid JSON only. Do not include comments, markdown fences, or prose outside the JSON.`}
function docs(root,depth,out){out=out||[];depth=depth||0;if(!root||depth>10)return out;try{out.push(root);Array.from(root.querySelectorAll('iframe')).forEach(f=>{try{const d=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(d)docs(d,depth+1,out)}catch(e){}})}catch(e){}return out}
function patchWindow(w,d){if(!w||!d||!d.getElementById)return;w.outsideProjectPrompt=requestPrompt;const mode=d.getElementById('connMode'),box=d.getElementById('connBox');if(mode&&box&&String(mode.value||'')==='request')box.value=requestPrompt();}
function scan(){docs(document).forEach(d=>{try{patchWindow(d.defaultView,d)}catch(e){}})}
window.PMPConnectionsRequestPromptSchemaV1={version:V,requestPrompt,scan};
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',scan);else scan();
window.addEventListener('load',()=>[50,150,400,900,1800].forEach(t=>setTimeout(scan,t)));
setInterval(scan,700);
})();
