#!/usr/bin/env python3
import subprocess
from dep_platform_common import *
import dep_platform_common as base

_original_allowed = base.allowed

def is_processing_output(name: str) -> bool:
    low = name.lower()
    return 'packet_01.5_' in low or 'packet_01_5_' in low

def allowed(name: str) -> bool:
    if is_processing_output(name):
        return False
    return _original_allowed(name)

def census(repo, names):
    main_names = subprocess.check_output(
        ['git', 'ls-tree', '-r', '--name-only', 'origin/main'],
        cwd=repo,
        text=True,
    ).splitlines()
    records = []
    for name in main_names:
        data = subprocess.check_output(['git', 'show', f'origin/main:{name}'], cwd=repo)
        records.append({'path': name, 'sha256': base.sha(data)})
    digest_input = '\n'.join(f"{item['sha256']}|{item['path']}" for item in records) + '\n'
    return records, base.sha(digest_input.encode())

base.allowed = allowed
base.census = census
