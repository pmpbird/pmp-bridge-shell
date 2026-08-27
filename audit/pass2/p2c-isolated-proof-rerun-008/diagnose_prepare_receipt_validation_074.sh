#!/usr/bin/env bash
set -euo pipefail
rm -rf "$EVIDENCE_DIR"
mkdir -p "$EVIDENCE_DIR"
export P2C_REHEARSAL_SKIP_AUTHORIZATION=1
export P2C_STOP_BEFORE_PREPARATION=1
bash "$AUDIT_DIR/rerun008-controller-main-receipt070.sh"
TARGET="$BUNDLE_DIR/prepare_disposable_proof_002.py"
test -s "$TARGET"
cp "$TARGET" "$EVIDENCE_DIR/prepare_disposable_proof_002.extracted.py"
python3 - "$TARGET" "$EVIDENCE_DIR" <<'PY'
import ast,json,pathlib,re,sys
path=pathlib.Path(sys.argv[1]); out=pathlib.Path(sys.argv[2])
text=path.read_text(); lines=text.splitlines()
patterns=[r'AUTHORIZATION_RECEIPT_INVALID',r'source_repository_commit',r'authorization',r'receipt']
hits=[]
for i,line in enumerate(lines,1):
    if any(re.search(p,line,re.I) for p in patterns):
        start=max(1,i-8); end=min(len(lines),i+8)
        hits.append({'line':i,'text':line,'start':start,'end':end,'context':'\n'.join(f'{n}: {lines[n-1]}' for n in range(start,end+1))})
try:
    tree=ast.parse(text)
    syntax='PASS'
except Exception as e:
    syntax=f'FAIL:{type(e).__name__}:{e}'
summary={'status':'PASS_DIAGNOSTIC_ONLY','proof_executed':False,'production_changed':False,'target':str(path),'line_count':len(lines),'syntax':syntax,'hit_count':len(hits),'hits':hits}
(out/'prepare-receipt-validation-diagnostic-074.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
(out/'prepare-receipt-validation-context-074.txt').write_text('\n\n'.join(h['context'] for h in hits)+'\n')
print(json.dumps({'status':summary['status'],'line_count':len(lines),'hit_count':len(hits),'syntax':syntax},indent=2))
PY
printf '%s\n' 'P2C_DIAGNOSTIC_074_COMPLETE_NO_PROOF_RUN'
