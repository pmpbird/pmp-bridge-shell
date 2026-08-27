'use strict';
const fs=require('fs');
const path=require('path');
const crypto=require('crypto');
const ts=require('/opt/nvm/versions/node/v22.16.0/lib/node_modules/typescript/lib/typescript.js');
function sha(s){return crypto.createHash('sha256').update(s).digest('hex')}
function transpile(source,fileName){
  const result=ts.transpileModule(source,{fileName,reportDiagnostics:true,compilerOptions:{allowJs:true,checkJs:false,target:ts.ScriptTarget.ES2016,module:ts.ModuleKind.None,removeComments:false,newLine:ts.NewLineKind.LineFeed}});
  const errors=(result.diagnostics||[]).filter(d=>d.category===ts.DiagnosticCategory.Error).map(d=>ts.flattenDiagnosticMessageText(d.messageText,'\n'));
  if(errors.length)throw new Error(fileName+': '+errors.join(' | '));
  let output=result.outputText;
  const anchor='        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }\n        function step(result)';
  const insert='        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }\n        fulfilled.__pmpAuthorityFailure=reject;\n        rejected.__pmpAuthorityFailure=reject;\n        function step(result)';
  const count=output.split(anchor).length-1;if(count!==1)throw new Error(fileName+': awaiter settlement anchor count '+count);
  output=output.replace(anchor,insert);
  return output;
}
function asyncCounts(source,fileName){
  const sf=ts.createSourceFile(fileName,source,ts.ScriptTarget.Latest,true,ts.ScriptKind.JS);
  let asyncNodes=0,awaitNodes=0;
  function walk(n){if(n.modifiers&&n.modifiers.some(m=>m.kind===ts.SyntaxKind.AsyncKeyword))asyncNodes++;if(n.kind===ts.SyntaxKind.AwaitExpression)awaitNodes++;ts.forEachChild(n,walk)}
  walk(sf);return{async_nodes:asyncNodes,await_nodes:awaitNodes,parse_diagnostics:sf.parseDiagnostics.map(d=>ts.flattenDiagnosticMessageText(d.messageText,'\n'))};
}
const input=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
const outRoot=process.argv[3];
const report=[];
for(const row of input.records){
  const original=fs.readFileSync(row.source_path,'utf8');
  let transformed,kind=row.kind;
  if(kind==='document-inline'){
    const re=/<script type="application\/pmp-p2c-managed-document"[^>]*>([\s\S]*?)<\/script>/g;
    const matches=[...original.matchAll(re)];
    if(matches.length!==1)throw new Error(row.path+': managed document script count '+matches.length);
    const body=matches[0][1];
    const bodyOut=transpile(body,row.path+'#managed-document');
    transformed=original.slice(0,matches[0].index)+matches[0][0].replace(body,bodyOut.trimEnd())+original.slice(matches[0].index+matches[0][0].length);
  }else{
    transformed=transpile(original,row.path);
  }
  const counts=kind==='document-inline' ? (()=>{const m=transformed.match(/<script type="application\/pmp-p2c-managed-document"[^>]*>([\s\S]*?)<\/script>/);return asyncCounts(m[1],row.path+'#managed-document')})() : asyncCounts(transformed,row.path);
  if(counts.parse_diagnostics.length||counts.async_nodes||counts.await_nodes)throw new Error(row.path+': residual async syntax '+JSON.stringify(counts));
  const dest=path.join(outRoot,row.path);fs.mkdirSync(path.dirname(dest),{recursive:true});fs.writeFileSync(dest,transformed);
  report.push({...row,typescript_version:ts.version,original_sha256:sha(original),transformed_sha256:sha(transformed),original_bytes:Buffer.byteLength(original),transformed_bytes:Buffer.byteLength(transformed),residual_async_nodes:counts.async_nodes,residual_await_nodes:counts.await_nodes});
}
process.stdout.write(JSON.stringify({type:'PMP_REPAIR009_ASYNC_SOURCE_NORMALIZATION_REPORT_002',typescript_version:ts.version,target:'ES2016',records:report},null,2)+'\n');
