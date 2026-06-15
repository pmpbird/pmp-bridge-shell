#!/usr/bin/env python3
import json

import runtime_source_rules_v2
import verify_packet_01_5_runtime_source_v1 as checker

original_compute = checker.compute


def normalized_compute():
    result = original_compute()
    result["matrix"] = json.loads(json.dumps(result["matrix"]))
    return result


checker.compute = normalized_compute
print(json.dumps(checker.verify(), indent=2))
