(()=>{
'use strict';
const V='1.1.0-complete-field-lock-copyable-json-block';
function addendum(){return [
'',
'--- COMPLETE FIELD LOCK START ---',
'The returned JSON must contain every older v2 field plus the memory-deposit fields. Do not choose between them. Include all of them in one object.',
'',
'Top-level required order:',
'type, packet_version, project_state_id, project_name, project_kind, packet_built_at, source_identity_capture, transfer_body_capture, memory_deposit_layer, packet_tracks, quality_truth, search_surface, receiver_safe_handoff, next_move.',
'',
'source_identity_capture required fields:',
'what_this_project_is, what_this_project_is_not, kernel, core_purpose, main_subject, active_goal, source_chat_title_if_known, source_project_name_if_known, locked_identity_rules, do_not_confuse_with.',
'',
'transfer_body_capture required fields:',
'core_definitions, locked_decisions, active_structure, important_boundaries, current_state, open_questions, important_history, outputs_or_artifacts, exact_or_locked_material, reconstructed_or_uncertain_material.',
'',
'memory_deposit_layer required sections:',
'source_access_truth, full_memory_recovery, pmp_storage_instruction, future_chat_read_protocol, multipart_control.',
'',
'source_access_truth required fields:',
'can_pmp_app_directly_read_source_chat, access_method_available, source_pointer, what_requires_returning_to_original_chat, what_is_fully_captured_inside_this_packet.',
'source_pointer required fields: chat_title, project_name, date_or_time, manual_route, link_if_user_provides_one.',
'',
'full_memory_recovery required fields:',
'core_kernel, exact_rules, locked_decisions, current_state, current_goal, working_structure, important_history, important_exact_phrases, files_or_artifacts, bugs_or_fixes, unresolved_questions, next_move, do_not_forget, do_not_change, what_is_not_captured.',
'',
'pmp_storage_instruction required fields:',
'store_as, storage_key, official_status, may_promote_to_official_pmp, must_not_overwrite_existing_memory, should_merge_with_existing_packet, merge_rule.',
'',
'future_chat_read_protocol required fields:',
'how_future_chat_should_use_this_packet, what_future_chat_must_trust, what_future_chat_must_not_assume, first_question_if_memory_is_incomplete, continuation_instruction.',
'',
'multipart_control required fields:',
'is_multipart, part_number, total_parts, continuation_key, if_more_memory_exists_return_next_part_instruction.',
'',
'packet_tracks required fields:',
'A0_kernel, A1_orientation, A2_shape, A3_body, A4_protection, A5_quality_truth, A6_receiver_action. Each A track must include meaning, evidence, and confidence.',
'',
'quality_truth required fields:',
'quality_level, quality_claim, what_is_well_preserved, known_gaps, known_risks, confidence_notes, not_lossless_if, next_quality_move.',
'',
'search_surface required fields:',
'primary_lookup_key, keywords, aliases, tags, section_anchors, restore_pointer.',
'',
'receiver_safe_handoff required fields:',
'packet_role, receiver_role, store_under, safe_receiver_path, do_not_overwrite, do_not_promote_directly, official_boundary.',
'',
'Memory truth rule: the app cannot read old chat memory unless the source places it in the packet, a transcript/export is pasted/imported, or a user-provided link/source is used. Therefore the full_memory_recovery section must be as complete as the source chat can make it.',
'',
'Missing rule: if any field cannot be filled, keep the field and use unknown, not_provided, not_visible_in_current_context, or an empty list. Record the gap in quality_truth.known_gaps and memory_deposit_layer.full_memory_recovery.what_is_not_captured.',
'--- COMPLETE FIELD LOCK END ---',
'',
'FINAL COPY FORMAT RULE: Return the completed packet inside one copyable markdown code block labeled json. Put no prose before or after the code block. Inside the code block, include valid JSON only.'
].join('\n')}
function docs(root,depth,out){out=out||[];depth=depth||0;if(!root||depth>10)return out;try{out.push(root);Array.from(root.querySelectorAll('iframe')).forEach(f=>{try{const d=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(d)docs(d,depth+1,out)}catch(e){}})}catch(e){}return out}
function patchWindow(w,d){if(!w||!d||!d.getElementById)return;if(w.__pmpRequestPromptCompleteV1===V)return;const prior=typeof w.outsideProjectPrompt==='function'?w.outsideProjectPrompt.bind(w):null;w.__pmpRequestPromptCompleteV1=V;w.pmpConnectionsRequestCompleteFieldLock=addendum;w.outsideProjectPrompt=function(){const base=prior?prior():'';return String(base||'')+addendum()};const mode=d.getElementById('connMode'),box=d.getElementById('connBox');if(mode&&box&&String(mode.value||'')==='request')box.value=w.outsideProjectPrompt();}
function scan(){docs(document).forEach(d=>{try{patchWindow(d.defaultView,d)}catch(e){}})}
window.PMPConnectionsRequestPromptCompleteV1={version:V,addendum,scan};
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',scan);else scan();
window.addEventListener('load',()=>[50,150,400,900,1800].forEach(t=>setTimeout(scan,t)));
setInterval(scan,700);
})();