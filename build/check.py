#!/usr/bin/env python3
"""Validate data/master.yaml. Run after every edit to the master file.

PyYAML silently keeps the LAST of any duplicate mapping key, which can drop an
entire role without raising. This loader rejects duplicates instead.
"""
import sys, yaml

PATH = sys.argv[1] if len(sys.argv) > 1 else 'data/master.yaml'

class Strict(yaml.SafeLoader):
    pass

def no_dup(loader, node, deep=False):
    out = {}
    for k, v in node.value:
        key = loader.construct_object(k, deep=deep)
        if key in out:
            raise ValueError(f"duplicate key {key!r} at line {k.start_mark.line + 1}")
        out[key] = loader.construct_object(v, deep=deep)
    return out

Strict.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, no_dup)

d = yaml.load(open(PATH), Strict)
problems, unverified, needs_metric = [], [], []

for r in d.get('experience', []) + d.get('projects', []):
    label = r.get('id') or r.get('company') or r.get('name') or '<unnamed>'
    if not r.get('id'):
        problems.append(f"{label}: missing id")
    if not (r.get('bullets') or []):
        problems.append(f"{label}: no bullets")
    for b in r.get('bullets') or []:
        if not b.get('text'):
            problems.append(f"{label}: bullet with no text")
        if not b.get('tags'):
            problems.append(f"{label}: untagged bullet — {str(b.get('text'))[:50]}")
        if b.get('verify'):
            unverified.append(f"{label}: {str(b.get('text'))[:60]}")
        if b.get('needs_metric'):
            needs_metric.append(f"{label}: {b['needs_metric']}")

current = [r for r in d.get('experience', []) if str(r.get('end', '')).lower() == 'present']

roles = len(d.get('experience', []))
bullets = sum(len(r.get('bullets') or []) for r in d.get('experience', []) + d.get('projects', []))
skills = sum(len(v) for v in (d.get('skills') or {}).values())
print(f"OK  {roles} roles · {len(d.get('projects', []))} projects · {bullets} bullets · "
      f"{skills} skills · {len(d.get('open_questions', []))} open questions")

if unverified:
    print(f"\nverify:true — NOT renderable until confirmed ({len(unverified)}):")
    for u in unverified:
        print(f"  - {u}")

if needs_metric:
    print(f"\nneeds_metric — renderable, but a number would strengthen it ({len(needs_metric)}):")
    for n in needs_metric:
        print(f"  - {n}")

if len(current) > 1:
    print(f"\nconcurrent 'Present' roles ({len(current)}) — confirm before rendering:")
    for r in current:
        print(f"  - {r['company']}: {r['title']} ({r['start']}-)")

if problems:
    print(f"\nPROBLEMS ({len(problems)}):")
    for p in problems:
        print(f"  - {p}")
    sys.exit(1)
