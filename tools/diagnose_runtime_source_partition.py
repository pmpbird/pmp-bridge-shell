#!/usr/bin/env python3
import json
import runtime_source_evaluate as evaluator

original_need=evaluator.need
def diagnostic_need(value,message):
    if message=='expected partition':return
    original_need(value,message)
evaluator.need=diagnostic_need
result=evaluator.compute()
print(json.dumps({
  'decisions':len(result['decisions']),
  'queued':len(result['remaining']),
  'outcomes':[{
    'identifier':item['original_identifier'],
    'outcome':item['outcome'],
    'expected':item['expected_outcome'],
    'result':item['result'],
    'detail':item['detail']
  } for item in result['matrix']]
},indent=2))
