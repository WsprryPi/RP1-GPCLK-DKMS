#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Exercise every same-version orchestration interruption boundary."""
import importlib.util,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("same",ROOT/"scripts/gate_d_same_version.py");assert spec and spec.loader
same=importlib.util.module_from_spec(spec);spec.loader.exec_module(same)
product={"product":True,"qualification":False,"liveOutput":False};absent={"product":False,"qualification":False,"liveOutput":False};qualified={"product":True,"qualification":True,"liveOutput":False}
plan={"SPDX-License-Identifier":"MIT","schemaVersion":1,"kind":"gate-d-same-version-transition","productArchiveSha256":"1"*64,"qualificationArchiveSha256":"2"*64,"ledgerSha256":"3"*64,"preState":product,"absentState":absent,"qualifiedState":qualified,"authorization":{"approved":False,"targetExecutionApproved":False,"executionReady":False},"removeArgv":["admin","remove"],"removeRecoveryArgv":["admin","recover-remove"],"qualificationInstallArgv":["admin","install-qualification"],"qualificationRecoveryArgv":["admin","recover-qualification"],"qualificationRemoveArgv":["admin","remove-qualification"],"productRollbackArgv":["admin","install-product"]}
def harness(stop=None,fail=None):
 state=product.copy(); journal=[]
 def run(argv):
  nonlocal state
  if argv==plan["removeArgv"]:
   if fail=="remove": raise RuntimeError("remove failure")
   state=absent.copy()
  elif argv==plan["qualificationInstallArgv"]:
   if fail=="qualification": raise RuntimeError("qualification failure")
   state=qualified.copy()
  elif argv==plan["removeRecoveryArgv"]:state=product.copy()
  elif argv in (plan["qualificationRecoveryArgv"],plan["qualificationRemoveArgv"]):state=absent.copy()
  elif argv==plan["productRollbackArgv"]:state=product.copy()
 def record(value):journal.append(dict(value))
 try:return same.execute(plan,run=run,probe=lambda:state,record=record,stop_after=stop),journal
 except (InterruptedError,RuntimeError):
  recovered=same.recover(plan,journal[-1],run=run,probe=lambda:state,record=record)
  assert state==product and recovered["status"]=="recovered";return recovered,journal
result,_=harness();assert result["status"]=="complete"
for checkpoint in same.CHECKPOINTS[1:]:harness(checkpoint)
for failure in ("remove","qualification"):harness(fail=failure)
contract=json.loads((ROOT/"release/gate-d-same-version-transition-v1.json").read_text());assert contract["sequence"]==list(same.CHECKPOINTS)
bad=dict(plan);bad["authorization"]={"approved":True,"targetExecutionApproved":False,"executionReady":False}
try:same.validate(bad)
except ValueError:pass
else:raise AssertionError("same-version authority leakage accepted")
for field,value in (("preState",absent),("absentState",product),("qualifiedState",absent)):
 bad=dict(plan);bad[field]=value
 try:same.validate(bad)
 except ValueError:pass
 else:raise AssertionError(f"unsafe {field} accepted")
for mutation in ({"checkpoint":"unknown"},{"productRemoved":"yes"},{"qualificationInstalled":True,"productRemoved":False}):
 state={"status":"recovery-required","checkpoint":"remove-product","recoveryRequired":True,"liveOutput":False,"productRemoved":False,"qualificationInstalled":False,**mutation}
 try:same.recover(plan,state,run=lambda argv:None,probe=lambda:product,record=lambda value:None)
 except ValueError:pass
 else:raise AssertionError(f"unsafe journal accepted: {mutation}")
print("Gate D same-version orchestration: PASS")
