(()=>{
'use strict';
const V='2.0.0-pure-normalizer';
function clean(value){return String(value||'').replace(/\s+/g,' ').trim()}
function typeOf(row){return clean(row&&row.type||row&&row.kind||row&&row.problem||row&&row.check||'Unknown helper problem type')}
function normalizeList(list){
  const map={};
  (Array.isArray(list)?list:[]).filter(Boolean).forEach((row,index)=>{
    const type=typeOf(row),key=type.toLowerCase(),old=map[key]||{};
    map[key]={
      id:old.id||row.id||('type_'+index),
      type,
      signature:'type:'+key,
      where:old.where||clean(row.where||'helper memory'),
      severity:old.severity||row.severity||'medium',
      how_it_happens:old.how_it_happens||clean(row.how_it_happens||row.why||''),
      fix_rule:old.fix_rule||clean(row.fix_rule||''),
      seen:Number(old.seen||0)+Math.max(Number(row.seen||1),1)
    };
  });
  return Object.keys(map).sort().map(key=>map[key]).slice(-60);
}
window.PMPHelperProblemTypeOnlyV1={
  version:V,
  owner:'diagnostics_owner',
  role:'pure_data_normalizer',
  normalizeList,
  rule:'Caller supplies and stores data. This helper never monkeypatches Storage and never reads or writes persisted state.'
};
})();
