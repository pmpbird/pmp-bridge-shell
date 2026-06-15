#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import re
from pathlib import Path

import runtime_source_rules as base
from runtime_source_git import main_text

_original_evaluate = base.evaluate


def balanced_function_body(text: str, name: str) -> str:
    escaped_name = re.escape(name)
    patterns = (
        rf"(?:async\s+)?function\s+{escaped_name}\s*\([^)]*\)\s*\{{",
        rf"(?:const|let|var)\s+{escaped_name}\s*=\s*(?:async\s*)?\([^)]*\)\s*=>\s*\{{",
        rf"{escaped_name}\s*=\s*(?:async\s*)?function\s*\([^)]*\)\s*\{{",
    )
    match = None
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            break
    if not match:
        return ""

    brace = text.find("{", match.start())
    if brace < 0:
        return ""

    depth = 0
    quote = ""
    escaped = False
    line_comment = False
    block_comment = False
    index = brace
    while index < len(text):
        char = text[index]
        next_char = text[index + 1] if index + 1 < len(text) else ""

        if line_comment:
            if char == "\n":
                line_comment = False
            index += 1
            continue
        if block_comment:
            if char == "*" and next_char == "/":
                block_comment = False
                index += 2
                continue
            index += 1
            continue
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = ""
            index += 1
            continue

        if char == "/" and next_char == "/":
            line_comment = True
            index += 2
            continue
        if char == "/" and next_char == "*":
            block_comment = True
            index += 2
            continue
        if char in ("'", '"', "`"):
            quote = char
            index += 1
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[brace + 1:index]
        index += 1
    return ""


def evaluate(identifier: str, repo: Path, graph, core_text: str):
    if identifier == "DATA-011":
        wall_clocks = [term for term in ("Date.now(", "new Date(", "toISOString(") if term in core_text]
        local_monotonic = [term for term in ("performance.now(",) if term in core_text]
        trusted_order = [
            term
            for term in (
                "event_sequence",
                "eventSequence",
                "sequence_id",
                "sequenceId",
                "trusted timestamp authority",
                "trusted order",
                "append sequence",
                "monotonic event",
            )
            if term.lower() in core_text.lower()
        ]
        detail = {
            "wall_clock_calls": wall_clocks,
            "local_monotonic_clock_calls": local_monotonic,
            "trusted_receipt_or_event_order_sources": trusted_order,
        }
        return ("SUPPORTED" if wall_clocks and not trusted_order else "UNRESOLVED"), detail, []

    if identifier == "RUN-001":
        home = main_text(repo, "pmp-home-single-v6.html")
        body = balanced_function_body(home, "residentRun")
        network_terms = [
            term
            for term in (
                "fetch(",
                "xmlhttprequest",
                "websocket",
                "openai",
                "anthropic",
                "model.call",
                "provider",
            )
            if term in body.lower()
        ]
        detail = {
            "resident_run_found": bool(body),
            "network_or_provider_terms": network_terms,
            "body_sha256": hashlib.sha256(body.encode()).hexdigest() if body else None,
        }
        return ("SUPPORTED" if body and not network_terms else "UNRESOLVED"), detail, ["pmp-home-single-v6.html"]

    return _original_evaluate(identifier, repo, graph, core_text)


base.function_body = balanced_function_body
base.evaluate = evaluate
