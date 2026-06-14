# Packet 01.5 — Discovery Pass 21

STATUS: DISCOVERY IN PROGRESS
PHASE: PROBLEM FINDING ONLY
ROUTING: NOT STARTED
DATE: 2026-06-14

This pass looks for physical-world sensing failure, sensor permission and availability defects, calibration drift, spoofed or stale readings, degraded sensors, and mismatch between digital state and physical reality.

## Provisional records

### SENSE-001 — Sensor reading is treated as direct truth

Location, motion, orientation, proximity, camera, microphone, light, network, and device-state readings may be estimates, filtered values, or inferred states.

HARM: decisions rely on a measurement whose uncertainty is hidden.

OVERLAP TO CHECK: AIH-003, QUAL-002.

### SENSE-002 — Sensor freshness is not recorded

A reading may be cached, delayed, replayed, or obtained before the current action.

HARM: stale physical state is treated as current reality.

OVERLAP TO CHECK: UI-001, REL-009.

### SENSE-003 — Sensor accuracy and confidence are discarded

The system may store only a value while omitting horizontal accuracy, confidence, sample rate, source, and error bounds.

HARM: low-quality readings look equivalent to high-quality readings.

OVERLAP TO CHECK: AIH-004, SEM-004.

### SENSE-004 — Sensor fusion hides disagreement

A combined result may merge GPS, Wi-Fi, cellular, inertial, camera, or network signals without exposing conflict.

HARM: one synthesized answer conceals incompatible physical evidence.

OVERLAP TO CHECK: AGENT-001, RANK-005.

### SENSE-005 — Sensor state changes during one workflow

Orientation, movement, location, lighting, audio, connectivity, or proximity may change between validation and action.

HARM: the final action is based on an earlier physical condition.

OVERLAP TO CHECK: INTENT-002, UI-013.

### SENSE-006 — Unsupported sensor silently falls back to an approximation

A browser or shell may substitute network location, device orientation, cached media, manual entry, or a generic value.

HARM: approximate input is mistaken for actual sensing.

OVERLAP TO CHECK: QUAL-001, PORT-004.

### SENSE-007 — Sensor sampling misses brief events

Low frequency, background suspension, throttling, batching, or dropped frames may miss short movements, sounds, proximity changes, or environmental events.

HARM: absence of a reading is mistaken for absence of the event.

OVERLAP TO CHECK: OBS-003, PERF-006.

### SENSE-008 — Sensor use changes device behavior

Continuous camera, microphone, GPS, motion, or background sensing may increase heat, battery drain, network use, and suspension risk.

HARM: sensing degrades the environment it is meant to observe.

OVERLAP TO CHECK: PERF-004, SCHED-001.

### PERMS-001 — Permission grant is treated as permanent capability

Camera, microphone, location, motion, notification, storage, and Bluetooth permissions may be revoked, limited, reset, or changed by the OS.

HARM: the app assumes capability that is no longer available.

OVERLAP TO CHECK: ENV-003, PLAT-003.

### PERMS-002 — Limited permission is mistaken for full permission

Approximate location, selected photos, one-time access, foreground-only access, or restricted microphone behavior may still appear as granted.

HARM: the system overstates what it can observe or retain.

OVERLAP TO CHECK: AUTHZ-006, UI-003.

### PERMS-003 — Permission request lacks just-in-time explanation

The user may be asked for sensitive sensor access before understanding the exact purpose, duration, and consequence.

HARM: consent is not informed or users deny access needed later.

OVERLAP TO CHECK: CONSENT-001, HUM-002.

### PERMS-004 — Permission denial creates unsafe fallback

The app may continue with guessed location, default orientation, stale media, or cached sensor values.

HARM: a denied capability becomes hidden false data.

OVERLAP TO CHECK: QUAL-001, SENSE-006.

### PERMS-005 — Permission state differs across shell forms

Safari, Home Screen mode, embedded web views, Shortcuts, and restored devices may have separate permission state and prompts.

HARM: the same app identity behaves differently across carriers.

OVERLAP TO CHECK: SHELL-007, PHY-004.

### PERMS-006 — Permission reset is not detected after update or restore

OS updates, reinstall, device replacement, restore, profile change, or privacy reset may silently alter permissions.

HARM: sensing stops or degrades without a visible state transition.

OVERLAP TO CHECK: ENV-005, INCDET-006.

### CALIB-001 — Sensor calibration is assumed rather than verified

Compass, accelerometer, gyroscope, camera, microphone, touch, and environmental sensors may require calibration or known reference conditions.

HARM: systematic bias is mistaken for real-world change.

OVERLAP TO CHECK: MEAS-002, TEST-001.

### CALIB-002 — Calibration drifts over time

Temperature, impact, wear, magnetic interference, component aging, software updates, or case accessories may alter readings.

HARM: once-valid thresholds slowly become wrong.

OVERLAP TO CHECK: MAINT-002, EXP-006.

### CALIB-003 — Calibration data belongs to the wrong device or sensor

Restores, cloned settings, device replacement, accessory changes, or model differences may reuse calibration from another physical unit.

HARM: correction makes readings less accurate.

OVERLAP TO CHECK: REL-001, PHY-004.

### CALIB-004 — Calibration procedure uses an unreliable reference

Manual alignment, network time, map position, ambient silence, screen orientation, or another uncalibrated device may be used as truth.

HARM: calibration locks in a second source’s error.

OVERLAP TO CHECK: TEST-002, TIME-001.

### CALIB-005 — Calibration status is not included in evidence identity

Proof may cite the sensor reading without recording calibration version, date, conditions, or device identity.

HARM: the measurement cannot be reproduced or compared later.

OVERLAP TO CHECK: PROOFCHAIN-001, SEM-004.

### CALIB-006 — Calibration passes in one environment only

Indoor, outdoor, quiet, noisy, stationary, moving, bright, dark, hot, cold, cased, and uncased conditions may produce different behavior.

HARM: a valid laboratory calibration fails in actual use.

OVERLAP TO CHECK: PERF-007, ENV-001.

### SPOOF-001 — Location can be spoofed or relayed

Developer tools, VPNs, network routing, mock-location systems, remote devices, or malicious software may present false position.

HARM: location-based authority or safety decisions are bypassed.

OVERLAP TO CHECK: NET-003, AUTHZ-006.

### SPOOF-002 — Camera input can be replayed or substituted

A stored image, screen, virtual camera, reflected display, or previously captured frame may be accepted as live reality.

HARM: visual presence and state checks are forged.

OVERLAP TO CHECK: REPLAY-001, AIH-001.

### SPOOF-003 — Microphone input can be replayed or injected

Recorded speech, synthetic audio, speaker playback, call routing, or virtual audio paths may imitate a live person or event.

HARM: voice or sound-based evidence is forged.

OVERLAP TO CHECK: AUTH-006, REPLAY-001.

### SPOOF-004 — Motion and orientation can be simulated

Emulators, remote-control tools, scripted events, vibration, mounted movement, or device manipulation may create false inertial readings.

HARM: movement-based state and liveness checks are unreliable.

OVERLAP TO CHECK: ADV-004, TEST-017.

### SPOOF-005 — Sensor metadata can be altered independently of content

Timestamps, orientation tags, coordinates, device model, and capture metadata may be edited without changing the media itself.

HARM: authentic content receives false context.

OVERLAP TO CHECK: AUD-001, FORENSIC-002.

### SPOOF-006 — Cross-sensor consistency is not checked

Location, time, lighting, motion, network, camera, and microphone may tell incompatible stories without triggering review.

HARM: one spoofed channel dominates despite contradictory physical evidence.

OVERLAP TO CHECK: SENSE-004, AGENT-001.

### LOCS-001 — Indoor or dense-area location is too imprecise

GPS, Wi-Fi, cellular, and network location may be inaccurate across rooms, floors, buildings, or nearby properties.

HARM: fine-grained location decisions exceed sensor capability.

OVERLAP TO CHECK: SENSE-003, CALIB-006.

### LOCS-002 — Background location is suspended or delayed

iOS policies, low-power mode, permission scope, app termination, and network conditions may stop or batch updates.

HARM: travel and boundary events are detected late or never.

OVERLAP TO CHECK: PERF-006, SCHED-001.

### LOCS-003 — Geofence behavior differs by platform and condition

Entry, exit, dwell, and region events may depend on OS heuristics, speed, radius, battery, and signal quality.

HARM: a nominal geographic rule is not deterministic.

OVERLAP TO CHECK: PLAT-003, SCHED-007.

### LOCS-004 — Map and coordinate references disagree

Different map providers, datums, address databases, altitude models, and geocoders may represent the same place differently.

HARM: one physical location maps to conflicting digital identities.

OVERLAP TO CHECK: SEM-001, API-001.

### LOCS-005 — Location collection reveals sensitive routines

Even coarse or intermittent points may expose home, work, beliefs, health, relationships, and absence patterns.

HARM: a functional sensor feature creates disproportionate privacy risk.

OVERLAP TO CHECK: PRIV-001, PRIV-002.

### CAM-001 — Lighting and exposure hide important visual detail

Glare, darkness, motion blur, autofocus, compression, occlusion, and camera switching may change what can be seen.

HARM: absence or presence is concluded from an unreadable image.

OVERLAP TO CHECK: SENSE-003, CALIB-006.

### CAM-002 — Camera framing excludes relevant surroundings

A narrow view may omit context, nearby hazards, additional people, scale, or the true source of an object.

HARM: visible evidence is mistaken for complete scene evidence.

OVERLAP TO CHECK: AIH-006, CTX-007.

### CAM-003 — Image processing changes the evidence

HDR, stabilization, sharpening, denoising, portrait effects, automatic rotation, and AI enhancement may alter apparent detail.

HARM: processed pixels are treated as raw observation.

OVERLAP TO CHECK: FORENSIC-003, SEM-004.

### CAM-004 — Camera access exposes unrelated private material

Photo pickers, live preview, background scene, metadata, or accidental capture may reveal people and information outside the task.

HARM: sensing exceeds the intended privacy boundary.

OVERLAP TO CHECK: MIN-001, CONSENT-002.

### MIC-001 — Ambient noise masks or changes meaning

Distance, reverberation, multiple speakers, wind, compression, cancellation, and device position may alter captured sound.

HARM: speech or event interpretation is unreliable.

OVERLAP TO CHECK: SENSE-003, CALIB-006.

### MIC-002 — Automatic audio processing changes evidence

Noise suppression, gain control, echo cancellation, voice isolation, and transcription may remove or invent meaningful detail.

HARM: processed audio is treated as direct physical truth.

OVERLAP TO CHECK: CAM-003, AIH-003.

### MIC-003 — Microphone capture records unintended people or content

Background conversations, media, alerts, and nearby private activity may enter the recording or provider request.

HARM: the project collects data from people who did not consent.

OVERLAP TO CHECK: CONSENT-006, MIN-004.

### REAL-001 — Digital state says an action occurred when the physical action did not

A button press, notification, sensor event, provider response, or automation may record completion without physical-world completion.

HARM: the system trusts an event that never happened outside the screen.

OVERLAP TO CHECK: TOOL-004, UI-004.

### REAL-002 — Physical change occurs without digital acknowledgment

A device may move, disconnect, lose power, change owner, suffer damage, or enter a new environment without updating the app state.

HARM: digital records remain valid after the real-world condition ends.

OVERLAP TO CHECK: PHY-001, STATE-003.

### REAL-003 — Human observation and sensor reading disagree with no resolution rule

The user may see, hear, or know something different from what the device reports.

HARM: either human or sensor evidence is accepted arbitrarily.

OVERLAP TO CHECK: AUTH-005, RANK-005.

### REAL-004 — Physical identity is inferred from device possession

Holding an unlocked phone, using a known location, presenting a camera image, or producing a familiar sound may be treated as proof of the authorized person.

HARM: possession and environmental similarity substitute for identity.

OVERLAP TO CHECK: PHY-003, AUTH-006.

## Pass 21 result

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
- Current preserved plus provisional: 905

NEXT DISCOVERY PASS:
Hardware lifecycle, battery and thermal limits, storage-media health, firmware, peripherals, repair, device replacement, physical tampering, and long-term hardware availability.

END PACKET 01.5 — DISCOVERY PASS 21
