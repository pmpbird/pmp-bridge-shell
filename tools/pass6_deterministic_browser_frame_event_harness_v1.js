'use strict';

const crypto = require('crypto');

const CONTRACT_TYPE = 'PMP_PASS6_DETERMINISTIC_BROWSER_FRAME_EVENT_HARNESS_V1';
const RESULT_TYPE = 'PMP_PASS6_DETERMINISTIC_BROWSER_FRAME_EVENT_PROOF_RESULT_V1';
const SCENARIO_TYPE = 'PMP_PASS6_DETERMINISTIC_BROWSER_FRAME_EVENT_SCENARIO_V1';
const CATALOG_TYPE = 'PMP_PASS6_CROSS_SYSTEM_INVARIANT_CATALOG_V1';
const VERSION = '1.0.0';
const ID = /^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$/;
const ALLOWED_EVENTS = new Set([
  'browser_started',
  'page_created',
  'frame_attached',
  'frame_navigated',
  'domcontentloaded',
  'load',
  'console',
  'page_error',
  'request_failed',
  'frame_detached',
  'page_closed',
  'browser_closed',
]);
const EFFECT_KEYS = Object.freeze([
  'network_requests',
  'storage_writes',
  'persisted_user_data_writes',
  'route_changes',
  'repairs',
  'live_observations',
  'formal_proofs',
  'production_files_changed',
]);

class HarnessFailure extends Error {
  constructor(code, message, evidence) {
    super(message);
    this.name = 'HarnessFailure';
    this.code = code;
    this.evidence = evidence === undefined ? null : evidence;
  }
}

function fail(code, message, evidence) {
  throw new HarnessFailure(code, message, evidence);
}

function canonical(value) {
  if (Array.isArray(value)) return value.map(canonical);
  if (value && typeof value === 'object') {
    return Object.fromEntries(
      Object.keys(value).sort().map(key => [key, canonical(value[key])])
    );
  }
  return value;
}

function stableJson(value) {
  return JSON.stringify(canonical(value));
}

function digest(value) {
  const payload = Buffer.isBuffer(value)
    ? value
    : Buffer.from(typeof value === 'string' ? value : stableJson(value));
  return crypto.createHash('sha256').update(payload).digest('hex');
}

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

function requireObject(value, code, label) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) {
    fail(code, `${label} must be an object`);
  }
}

function requireId(value, code, label) {
  if (typeof value !== 'string' || !ID.test(value)) {
    fail(code, `${label} must be a stable identifier`, { value });
  }
  return value;
}

function requireArray(value, code, label, nonempty = true) {
  if (!Array.isArray(value) || (nonempty && value.length === 0)) {
    fail(code, `${label} must be ${nonempty ? 'a non-empty' : 'an'} array`);
  }
  return value;
}

function exactUniqueStrings(values, code, label, nonempty = true) {
  requireArray(values, code, label, nonempty);
  const seen = new Set();
  for (const value of values) {
    requireId(value, code, `${label} entry`);
    if (seen.has(value)) fail(code, `${label} contains a duplicate`, { value });
    seen.add(value);
  }
  return seen;
}

function validateCatalog(catalog) {
  requireObject(catalog, 'CATALOG_MALFORMED', 'catalog');
  if (catalog.type !== CATALOG_TYPE || catalog.version !== VERSION) {
    fail('CATALOG_IDENTITY_INVALID', 'catalog type or version is not supported', {
      type: catalog.type,
      version: catalog.version,
    });
  }
  const requiredSubsystems = exactUniqueStrings(
    catalog.required_subsystems,
    'CATALOG_SUBSYSTEMS_INVALID',
    'catalog.required_subsystems'
  );
  const requiredScenarios = exactUniqueStrings(
    catalog.required_scenarios,
    'CATALOG_SCENARIOS_INVALID',
    'catalog.required_scenarios'
  );
  const invariants = requireArray(
    catalog.invariants,
    'CATALOG_INVARIANTS_INVALID',
    'catalog.invariants'
  );
  const byId = new Map();
  for (const invariant of invariants) {
    requireObject(invariant, 'CATALOG_INVARIANT_MALFORMED', 'catalog invariant');
    const id = requireId(invariant.id, 'CATALOG_INVARIANT_ID_INVALID', 'invariant.id');
    if (byId.has(id)) fail('CATALOG_INVARIANT_DUPLICATE', 'duplicate invariant id', { id });
    requireId(invariant.subsystem, 'CATALOG_INVARIANT_SUBSYSTEM_INVALID', 'invariant.subsystem');
    if (!requiredSubsystems.has(invariant.subsystem)) {
      fail('CATALOG_INVARIANT_SUBSYSTEM_UNKNOWN', 'invariant subsystem is not required', {
        id,
        subsystem: invariant.subsystem,
      });
    }
    requireId(invariant.owner, 'CATALOG_INVARIANT_OWNER_INVALID', 'invariant.owner');
    if (typeof invariant.statement !== 'string' || invariant.statement.trim() === '') {
      fail('CATALOG_INVARIANT_STATEMENT_MISSING', 'invariant statement is required', { id });
    }
    const scenarios = exactUniqueStrings(
      invariant.scenarios,
      'CATALOG_INVARIANT_SCENARIOS_INVALID',
      `${id}.scenarios`
    );
    for (const scenario of scenarios) {
      if (!requiredScenarios.has(scenario)) {
        fail('CATALOG_INVARIANT_SCENARIO_UNKNOWN', 'invariant scenario is unknown', {
          id,
          scenario,
        });
      }
    }
    requireArray(
      invariant.evidence_paths,
      'CATALOG_INVARIANT_EVIDENCE_MISSING',
      `${id}.evidence_paths`
    );
    requireArray(
      invariant.deterministic_test_paths,
      'CATALOG_INVARIANT_TEST_MISSING',
      `${id}.deterministic_test_paths`
    );
    byId.set(id, invariant);
  }
  return {
    byId,
    requiredSubsystems: [...requiredSubsystems],
    requiredScenarios: [...requiredScenarios],
    sha256: digest(catalog),
  };
}

function validateScenario(scenario, catalogState) {
  requireObject(scenario, 'SCENARIO_MALFORMED', 'scenario');
  if (scenario.type !== SCENARIO_TYPE || scenario.version !== VERSION) {
    fail('SCENARIO_IDENTITY_INVALID', 'scenario type or version is not supported', {
      type: scenario.type,
      version: scenario.version,
    });
  }
  requireId(scenario.id, 'SCENARIO_ID_INVALID', 'scenario.id');
  const invariantIds = exactUniqueStrings(
    scenario.invariant_ids,
    'SCENARIO_INVARIANTS_INVALID',
    'scenario.invariant_ids'
  );
  for (const id of invariantIds) {
    if (!catalogState.byId.has(id)) {
      fail('SCENARIO_INVARIANT_UNKNOWN', 'scenario references an unknown invariant', { id });
    }
  }
  const requiredEvents = exactUniqueStrings(
    scenario.required_events,
    'SCENARIO_REQUIRED_EVENTS_INVALID',
    'scenario.required_events'
  );
  for (const event of requiredEvents) {
    if (!ALLOWED_EVENTS.has(event)) {
      fail('SCENARIO_REQUIRED_EVENT_UNKNOWN', 'scenario requires an unknown event', { event });
    }
  }
  if (
    !Number.isInteger(scenario.timeout_ticks)
    || scenario.timeout_ticks < 1
    || scenario.timeout_ticks > 100000
  ) {
    fail('SCENARIO_TIMEOUT_INVALID', 'timeout_ticks must be an integer from 1 through 100000');
  }
  requireArray(scenario.steps, 'SCENARIO_STEPS_INVALID', 'scenario.steps');
  return {
    invariantIds,
    requiredEvents,
    sha256: digest(scenario),
  };
}

function normalizeEffects(raw) {
  requireObject(raw, 'EFFECTS_MALFORMED', 'adapter effects');
  const unknown = Object.keys(raw).filter(key => !EFFECT_KEYS.includes(key));
  if (unknown.length) fail('EFFECT_KEY_UNKNOWN', 'adapter reported an unknown effect', { unknown });
  const effects = {};
  for (const key of EFFECT_KEYS) {
    const value = raw[key] === undefined ? 0 : raw[key];
    if (!Number.isInteger(value) || value < 0) {
      fail('EFFECT_COUNT_INVALID', 'effect counts must be non-negative integers', { key, value });
    }
    effects[key] = value;
  }
  return effects;
}

class State {
  constructor(catalog, scenario, catalogState, scenarioState) {
    this.catalog = catalog;
    this.scenario = scenario;
    this.catalogState = catalogState;
    this.scenarioState = scenarioState;
    this.tick = 0;
    this.stepIndex = -1;
    this.browserOpen = false;
    this.pages = new Map();
    this.frames = new Map();
    this.events = [];
    this.assertions = new Map();
  }

  snapshot() {
    return {
      tick: this.tick,
      browser_open: this.browserOpen,
      pages: [...this.pages.values()].map(clone).sort((a, b) => a.page_id.localeCompare(b.page_id)),
      frames: [...this.frames.values()].map(clone).sort((a, b) => a.frame_id.localeCompare(b.frame_id)),
      assertions: [...this.assertions.values()].map(clone).sort((a, b) => a.invariant_id.localeCompare(b.invariant_id)),
      event_count: this.events.length,
    };
  }

  stepTick() {
    this.tick += 1;
    if (this.tick > this.scenario.timeout_ticks) {
      fail('SCENARIO_TIMEOUT', 'scenario exceeded its deterministic timeout', {
        tick: this.tick,
        timeout_ticks: this.scenario.timeout_ticks,
      });
    }
  }

  emit(kind, details = {}) {
    if (!ALLOWED_EVENTS.has(kind)) fail('EVENT_KIND_UNKNOWN', 'event kind is not supported', { kind });
    requireObject(details, 'EVENT_DETAILS_MALFORMED', 'event details');
    if (details.frame_id !== undefined) {
      const frame = this.frames.get(details.frame_id);
      if (!frame || !frame.active) {
        fail('EVENT_FRAME_NOT_ACTIVE', 'event frame is missing or inactive', {
          frame_id: details.frame_id,
          kind,
        });
      }
    }
    const invariantIds = details.invariant_ids === undefined
      ? []
      : [...exactUniqueStrings(
        details.invariant_ids,
        'EVENT_INVARIANTS_INVALID',
        'event.invariant_ids',
        false
      )];
    for (const id of invariantIds) {
      if (!this.scenarioState.invariantIds.has(id)) {
        fail('EVENT_INVARIANT_OUT_OF_SCOPE', 'event references an invariant outside the scenario', {
          id,
          kind,
        });
      }
    }
    this.stepTick();
    const event = {
      event_id: `E${String(this.events.length + 1).padStart(4, '0')}`,
      monotonic_tick: this.tick,
      step_index: this.stepIndex,
      kind,
      page_id: details.page_id || null,
      frame_id: details.frame_id || null,
      frame_generation: details.frame_generation === undefined ? null : details.frame_generation,
      invariant_ids: invariantIds.sort(),
      payload: clone(details.payload === undefined ? {} : details.payload),
    };
    event.event_sha256 = digest({
      ...event,
      event_sha256: undefined,
    });
    this.events.push(event);
    return event;
  }

  requirePage(pageId, active = true) {
    requireId(pageId, 'PAGE_ID_INVALID', 'page_id');
    const page = this.pages.get(pageId);
    if (!page || (active && !page.active)) {
      fail('PAGE_NOT_ACTIVE', 'page is missing or inactive', { page_id: pageId });
    }
    return page;
  }

  requireFrame(frameId, active = true) {
    requireId(frameId, 'FRAME_ID_INVALID', 'frame_id');
    const frame = this.frames.get(frameId);
    if (!frame || (active && !frame.active)) {
      fail('FRAME_NOT_ACTIVE', 'frame is missing or inactive', { frame_id: frameId });
    }
    return frame;
  }

  execute(step) {
    requireObject(step, 'STEP_MALFORMED', 'scenario step');
    const op = step.op;
    if (typeof op !== 'string') fail('STEP_OPERATION_MISSING', 'step.op is required');
    switch (op) {
      case 'launch_browser': {
        if (this.browserOpen) fail('BROWSER_ALREADY_OPEN', 'browser is already open');
        this.browserOpen = true;
        this.emit('browser_started', { payload: { engine: step.engine || 'adapter' } });
        return;
      }
      case 'open_page': {
        if (!this.browserOpen) fail('BROWSER_NOT_OPEN', 'cannot open a page before the browser');
        const pageId = requireId(step.page_id, 'PAGE_ID_INVALID', 'page_id');
        const frameId = requireId(step.main_frame_id, 'FRAME_ID_INVALID', 'main_frame_id');
        if (this.pages.has(pageId)) fail('DUPLICATE_PAGE_ID', 'page id already exists', { page_id: pageId });
        if (this.frames.has(frameId)) fail('DUPLICATE_FRAME_ID', 'frame id already exists', { frame_id: frameId });
        if (typeof step.url !== 'string' || step.url.trim() === '') {
          fail('FRAME_URL_INVALID', 'page URL is required');
        }
        this.pages.set(pageId, { page_id: pageId, main_frame_id: frameId, active: true });
        this.frames.set(frameId, {
          frame_id: frameId,
          page_id: pageId,
          parent_frame_id: null,
          generation: 0,
          url: step.url,
          active: true,
        });
        this.emit('page_created', {
          page_id: pageId,
          frame_id: frameId,
          frame_generation: 0,
          payload: { url: step.url },
        });
        return;
      }
      case 'attach_frame': {
        const page = this.requirePage(step.page_id);
        const frameId = requireId(step.frame_id, 'FRAME_ID_INVALID', 'frame_id');
        const parent = this.requireFrame(step.parent_frame_id);
        if (parent.page_id !== page.page_id) {
          fail('FRAME_PARENT_PAGE_MISMATCH', 'parent frame belongs to another page', {
            frame_id: frameId,
            parent_frame_id: parent.frame_id,
          });
        }
        if (frameId === parent.frame_id) fail('FRAME_PARENT_SELF', 'frame cannot parent itself', { frame_id: frameId });
        if (this.frames.has(frameId)) fail('DUPLICATE_FRAME_ID', 'frame id already exists', { frame_id: frameId });
        if (typeof step.url !== 'string' || step.url.trim() === '') {
          fail('FRAME_URL_INVALID', 'frame URL is required');
        }
        this.frames.set(frameId, {
          frame_id: frameId,
          page_id: page.page_id,
          parent_frame_id: parent.frame_id,
          generation: 0,
          url: step.url,
          active: true,
        });
        this.emit('frame_attached', {
          page_id: page.page_id,
          frame_id: frameId,
          frame_generation: 0,
          payload: { parent_frame_id: parent.frame_id, url: step.url },
        });
        return;
      }
      case 'navigate_frame': {
        const frame = this.requireFrame(step.frame_id);
        if (!Number.isInteger(step.expected_generation) || step.expected_generation !== frame.generation) {
          fail('FRAME_GENERATION_STALE', 'frame generation does not match', {
            frame_id: frame.frame_id,
            expected: frame.generation,
            actual: step.expected_generation,
          });
        }
        if (typeof step.url !== 'string' || step.url.trim() === '') {
          fail('FRAME_URL_INVALID', 'navigation URL is required');
        }
        frame.generation += 1;
        frame.url = step.url;
        this.emit('frame_navigated', {
          page_id: frame.page_id,
          frame_id: frame.frame_id,
          frame_generation: frame.generation,
          payload: { url: step.url },
        });
        return;
      }
      case 'emit_event': {
        this.emit(step.kind, {
          page_id: step.page_id,
          frame_id: step.frame_id,
          frame_generation: step.frame_generation,
          invariant_ids: step.invariant_ids || [],
          payload: step.payload || {},
        });
        return;
      }
      case 'expect_event': {
        if (!ALLOWED_EVENTS.has(step.kind)) {
          fail('EXPECTED_EVENT_KIND_UNKNOWN', 'expected event kind is not supported', { kind: step.kind });
        }
        const found = this.events.some(event => (
          event.kind === step.kind
          && (step.frame_id === undefined || event.frame_id === step.frame_id)
          && (step.invariant_id === undefined || event.invariant_ids.includes(step.invariant_id))
        ));
        if (!found) {
          fail('REQUIRED_EVENT_MISSING', 'expected event was not observed', {
            kind: step.kind,
            frame_id: step.frame_id || null,
            invariant_id: step.invariant_id || null,
          });
        }
        return;
      }
      case 'assert_invariant': {
        const id = requireId(step.invariant_id, 'ASSERTION_INVARIANT_INVALID', 'invariant_id');
        if (!this.scenarioState.invariantIds.has(id)) {
          fail('ASSERTION_INVARIANT_OUT_OF_SCOPE', 'assertion invariant is outside the scenario', { id });
        }
        if (this.assertions.has(id)) {
          fail('ASSERTION_DUPLICATE', 'invariant was asserted more than once', { id });
        }
        if (step.outcome !== 'PASS') {
          fail('INVARIANT_ASSERTION_FAILED', 'invariant assertion did not pass', {
            id,
            outcome: step.outcome,
          });
        }
        const evidenceIds = exactUniqueStrings(
          step.evidence_event_ids,
          'ASSERTION_EVIDENCE_INVALID',
          'evidence_event_ids'
        );
        for (const eventId of evidenceIds) {
          const event = this.events.find(item => item.event_id === eventId);
          if (!event) {
            fail('ASSERTION_EVIDENCE_MISSING', 'assertion references a missing event', {
              id,
              event_id: eventId,
            });
          }
          if (!event.invariant_ids.includes(id)) {
            fail('ASSERTION_EVIDENCE_UNBOUND', 'evidence event is not bound to the invariant', {
              id,
              event_id: eventId,
            });
          }
        }
        this.assertions.set(id, {
          invariant_id: id,
          outcome: 'PASS',
          evidence_event_ids: [...evidenceIds].sort(),
        });
        return;
      }
      case 'advance_ticks': {
        if (!Number.isInteger(step.ticks) || step.ticks < 1) {
          fail('ADVANCE_TICKS_INVALID', 'advance_ticks requires a positive integer');
        }
        this.tick += step.ticks;
        if (this.tick > this.scenario.timeout_ticks) {
          fail('SCENARIO_TIMEOUT', 'scenario exceeded its deterministic timeout', {
            tick: this.tick,
            timeout_ticks: this.scenario.timeout_ticks,
          });
        }
        return;
      }
      case 'detach_frame': {
        const frame = this.requireFrame(step.frame_id);
        if (frame.parent_frame_id === null) {
          fail('MAIN_FRAME_DETACH_FORBIDDEN', 'main frame cannot be detached independently', {
            frame_id: frame.frame_id,
          });
        }
        const activeChild = [...this.frames.values()].find(
          item => item.active && item.parent_frame_id === frame.frame_id
        );
        if (activeChild) {
          fail('ACTIVE_CHILD_FRAME_REMAINS', 'cannot detach a frame with an active child', {
            frame_id: frame.frame_id,
            child_frame_id: activeChild.frame_id,
          });
        }
        this.emit('frame_detached', {
          page_id: frame.page_id,
          frame_id: frame.frame_id,
          frame_generation: frame.generation,
          payload: { url: frame.url },
        });
        frame.active = false;
        return;
      }
      case 'close_page': {
        const page = this.requirePage(step.page_id);
        const activeChild = [...this.frames.values()].find(
          item => item.active && item.page_id === page.page_id && item.parent_frame_id !== null
        );
        if (activeChild) {
          fail('ACTIVE_CHILD_FRAME_REMAINS', 'cannot close a page with an active child frame', {
            page_id: page.page_id,
            child_frame_id: activeChild.frame_id,
          });
        }
        const main = this.requireFrame(page.main_frame_id);
        this.emit('page_closed', {
          page_id: page.page_id,
          frame_id: main.frame_id,
          frame_generation: main.generation,
          payload: {},
        });
        main.active = false;
        page.active = false;
        return;
      }
      case 'close_browser': {
        if (!this.browserOpen) fail('BROWSER_NOT_OPEN', 'browser is not open');
        const activePage = [...this.pages.values()].find(page => page.active);
        if (activePage) {
          fail('ACTIVE_PAGE_REMAINS', 'cannot close browser with an active page', {
            page_id: activePage.page_id,
          });
        }
        this.emit('browser_closed', { payload: {} });
        this.browserOpen = false;
        return;
      }
      default:
        fail('STEP_OPERATION_UNKNOWN', 'step operation is not supported', { op });
    }
  }

  finalize(effects) {
    if (this.browserOpen) fail('BROWSER_LEFT_OPEN', 'scenario finished with browser open');
    const activePage = [...this.pages.values()].find(page => page.active);
    if (activePage) fail('PAGE_LEFT_OPEN', 'scenario finished with an active page', { page_id: activePage.page_id });
    const activeFrame = [...this.frames.values()].find(frame => frame.active);
    if (activeFrame) fail('FRAME_LEFT_ACTIVE', 'scenario finished with an active frame', { frame_id: activeFrame.frame_id });
    for (const kind of this.scenarioState.requiredEvents) {
      if (!this.events.some(event => event.kind === kind)) {
        fail('REQUIRED_EVENT_MISSING', 'required scenario event was not observed', { kind });
      }
    }
    for (const id of this.scenarioState.invariantIds) {
      if (!this.assertions.has(id)) {
        fail('INVARIANT_ASSERTION_MISSING', 'scenario omitted an invariant assertion', { id });
      }
    }
    const observed = Object.entries(effects).filter(([, count]) => count !== 0);
    if (observed.length) {
      fail('FORBIDDEN_EFFECT_OBSERVED', 'proof harness observed a forbidden effect', {
        effects: Object.fromEntries(observed),
      });
    }
  }
}

function createDeterministicAdapter(options = {}) {
  const effects = Object.assign(Object.fromEntries(EFFECT_KEYS.map(key => [key, 0])), options.effects || {});
  let teardownCalls = 0;
  return {
    contract_type: 'PMP_PASS6_DETERMINISTIC_BROWSER_ADAPTER_V1',
    perform(step, api) {
      if (options.fail_step_index === api.step_index) {
        fail('ADAPTER_OPERATION_FAILED', 'adapter failed at the requested deterministic step', {
          step_index: api.step_index,
        });
      }
      api.execute(step);
    },
    effects() {
      return clone(effects);
    },
    teardown(api) {
      teardownCalls += 1;
      if (options.teardown_error) throw new Error(String(options.teardown_error));
      return {
        status: 'PASS',
        calls: teardownCalls,
        final_tick: api.tick,
      };
    },
  };
}

function buildResult({
  catalog,
  scenario,
  catalogState,
  scenarioState,
  state,
  effects,
  status,
  failure,
  secondaryFailures,
  teardown,
}) {
  const selected = scenarioState
    ? [...scenarioState.invariantIds].sort().map(id => {
      const invariant = catalogState.byId.get(id);
      return {
        id,
        subsystem: invariant.subsystem,
        owner: invariant.owner,
        enforcement: invariant.enforcement,
        failure_behavior: invariant.failure_behavior,
      };
    })
    : [];
  const result = {
    type: RESULT_TYPE,
    version: VERSION,
    harness: {
      type: CONTRACT_TYPE,
      version: VERSION,
      deterministic_clock: 'MONOTONIC_INTEGER_TICKS',
      adapter_contract: 'PMP_PASS6_DETERMINISTIC_BROWSER_ADAPTER_V1',
    },
    status,
    scenario_id: scenario && typeof scenario.id === 'string' ? scenario.id : null,
    catalog_sha256: catalogState ? catalogState.sha256 : digest(catalog || null),
    scenario_sha256: scenarioState ? scenarioState.sha256 : digest(scenario || null),
    selected_invariants: selected,
    events: state ? clone(state.events) : [],
    frames: state
      ? [...state.frames.values()].map(clone).sort((a, b) => a.frame_id.localeCompare(b.frame_id))
      : [],
    assertions: state
      ? [...state.assertions.values()].map(clone).sort((a, b) => a.invariant_id.localeCompare(b.invariant_id))
      : [],
    effects: effects || Object.fromEntries(EFFECT_KEYS.map(key => [key, 0])),
    teardown,
    failure,
    secondary_failures: secondaryFailures,
    summary: {
      invariants_required: scenarioState ? scenarioState.invariantIds.size : 0,
      invariants_passed: state ? state.assertions.size : 0,
      events_captured: state ? state.events.length : 0,
      frames_observed: state ? state.frames.size : 0,
      final_tick: state ? state.tick : 0,
      failures: failure ? 1 + secondaryFailures.length : 0,
    },
    claim_ceiling: 'Deterministic harness contract and supplied adapter evidence only; no live-app, production, later-pass, repair, migration, or formal-proof outcome is implied.',
  };
  result.result_sha256 = digest(result);
  return result;
}

function runScenario({ catalog, scenario, adapter }) {
  let catalogState = null;
  let scenarioState = null;
  let state = null;
  let effects = Object.fromEntries(EFFECT_KEYS.map(key => [key, 0]));
  let failure = null;
  const secondaryFailures = [];
  let teardown = { status: 'NOT_STARTED', calls: 0, final_tick: 0 };
  const activeAdapter = adapter || createDeterministicAdapter();
  try {
    catalogState = validateCatalog(catalog);
    scenarioState = validateScenario(scenario, catalogState);
    if (!activeAdapter || typeof activeAdapter.perform !== 'function') {
      fail('ADAPTER_CONTRACT_INVALID', 'adapter.perform must be a function');
    }
    if (typeof activeAdapter.effects !== 'function' || typeof activeAdapter.teardown !== 'function') {
      fail('ADAPTER_CONTRACT_INVALID', 'adapter.effects and adapter.teardown must be functions');
    }
    state = new State(catalog, scenario, catalogState, scenarioState);
    for (let index = 0; index < scenario.steps.length; index += 1) {
      state.stepIndex = index;
      activeAdapter.perform(scenario.steps[index], {
        step_index: index,
        tick: state.tick,
        execute: step => state.execute(step),
        emit: (kind, details) => state.emit(kind, details),
        snapshot: () => state.snapshot(),
      });
    }
    effects = normalizeEffects(activeAdapter.effects());
    state.finalize(effects);
  } catch (error) {
    const normalized = error instanceof HarnessFailure
      ? error
      : new HarnessFailure('UNEXPECTED_HARNESS_ERROR', String(error && error.message || error));
    failure = {
      code: normalized.code,
      message: normalized.message,
      step_index: state ? state.stepIndex : null,
      evidence: clone(normalized.evidence),
      state: state ? state.snapshot() : null,
    };
  } finally {
    if (activeAdapter && typeof activeAdapter.teardown === 'function') {
      try {
        const raw = activeAdapter.teardown({
          step_index: state ? state.stepIndex : null,
          tick: state ? state.tick : 0,
          snapshot: () => state ? state.snapshot() : null,
        });
        requireObject(raw, 'TEARDOWN_RESULT_MALFORMED', 'teardown result');
        teardown = {
          status: raw.status === 'PASS' ? 'PASS' : 'FAIL',
          calls: raw.calls,
          final_tick: raw.final_tick,
        };
        if (teardown.status !== 'PASS' || teardown.calls !== 1) {
          fail('TEARDOWN_INCOMPLETE', 'adapter teardown must pass exactly once', teardown);
        }
      } catch (error) {
        const item = {
          code: error instanceof HarnessFailure ? error.code : 'TEARDOWN_FAILED',
          message: String(error && error.message || error),
          evidence: error instanceof HarnessFailure ? clone(error.evidence) : null,
        };
        teardown = {
          status: 'FAIL',
          calls: teardown.calls || null,
          final_tick: state ? state.tick : 0,
        };
        if (failure) secondaryFailures.push(item);
        else {
          failure = {
            ...item,
            step_index: state ? state.stepIndex : null,
            state: state ? state.snapshot() : null,
          };
        }
      }
    } else if (!failure) {
      failure = {
        code: 'ADAPTER_CONTRACT_INVALID',
        message: 'adapter teardown is unavailable',
        step_index: null,
        evidence: null,
        state: null,
      };
    }
  }
  return buildResult({
    catalog,
    scenario,
    catalogState,
    scenarioState,
    state,
    effects,
    status: failure ? 'FAIL' : 'PASS',
    failure,
    secondaryFailures,
    teardown,
  });
}

function verifyResultHash(result) {
  if (!result || typeof result.result_sha256 !== 'string') return false;
  const copy = clone(result);
  const expected = copy.result_sha256;
  delete copy.result_sha256;
  return digest(copy) === expected;
}

module.exports = Object.freeze({
  CONTRACT_TYPE,
  RESULT_TYPE,
  SCENARIO_TYPE,
  CATALOG_TYPE,
  VERSION,
  ALLOWED_EVENTS: Object.freeze([...ALLOWED_EVENTS]),
  EFFECT_KEYS,
  HarnessFailure,
  canonical,
  stableJson,
  digest,
  validateCatalog,
  validateScenario,
  createDeterministicAdapter,
  runScenario,
  verifyResultHash,
});
