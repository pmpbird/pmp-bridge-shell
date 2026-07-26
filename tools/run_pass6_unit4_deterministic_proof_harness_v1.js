#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');
const childProcess = require('child_process');
const harness = require('./pass6_deterministic_browser_frame_event_harness_v1.js');

const ROOT = path.resolve(__dirname, '..');

function args(argv) {
  const out = {
    catalog: 'audit/pass6/pass6-cross-system-invariant-catalog-v1.json',
    scenario: 'audit/pass6/fixtures/pass6-unit4-deterministic-proof-harness-positive-v1.json',
    output: null,
  };
  for (let index = 2; index < argv.length; index += 1) {
    const key = argv[index];
    if (!['--catalog', '--scenario', '--output'].includes(key) || index + 1 >= argv.length) {
      throw new Error(`unknown or incomplete argument: ${key}`);
    }
    out[key.slice(2)] = argv[++index];
  }
  return out;
}

function readTracked(relative) {
  const full = path.resolve(ROOT, relative);
  if (!full.startsWith(ROOT + path.sep)) throw new Error(`path escapes repository: ${relative}`);
  if (fs.existsSync(full)) return fs.readFileSync(full, 'utf8');
  return childProcess.execFileSync('git', ['show', `HEAD:${relative}`], {
    cwd: ROOT,
    encoding: 'utf8',
  });
}

function main() {
  const options = args(process.argv);
  const catalog = JSON.parse(readTracked(options.catalog));
  const scenario = JSON.parse(readTracked(options.scenario));
  const result = harness.runScenario({
    catalog,
    scenario,
    adapter: harness.createDeterministicAdapter(),
  });
  const payload = JSON.stringify(result, null, 2) + '\n';
  if (options.output) fs.writeFileSync(path.resolve(options.output), payload);
  process.stdout.write(payload);
  if (result.status !== 'PASS') process.exitCode = 1;
}

main();
