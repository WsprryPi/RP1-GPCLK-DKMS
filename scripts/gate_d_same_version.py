#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Fail-closed same-version product-to-qualification transition model."""
from __future__ import annotations
import copy

CHECKPOINTS=("preflight","remove-product","verify-absent","install-qualification","verify-qualified","commit")
ARGV_FIELDS=("removeArgv","removeRecoveryArgv","qualificationInstallArgv","qualificationRecoveryArgv","qualificationRemoveArgv","productRollbackArgv")

def validate(plan:dict)->dict:
 required={"SPDX-License-Identifier","schemaVersion","kind","productArchiveSha256","qualificationArchiveSha256","ledgerSha256","preState","absentState","qualifiedState","authorization",*ARGV_FIELDS}
 if not isinstance(plan,dict) or set(plan)!=required or plan.get("SPDX-License-Identifier")!="MIT" or plan.get("schemaVersion")!=1 or plan.get("kind")!="gate-d-same-version-transition": raise ValueError("same-version plan identity differs")
 if plan["authorization"]!={"approved":False,"targetExecutionApproved":False,"executionReady":False}: raise ValueError("same-version plan inherited authority")
 for field in ("productArchiveSha256","qualificationArchiveSha256","ledgerSha256"):
  value=plan[field]
  if not isinstance(value,str) or len(value)!=64 or any(c not in "0123456789abcdef" for c in value): raise ValueError("same-version identity differs")
 for field in ARGV_FIELDS:
  argv=plan[field]
  if not isinstance(argv,list) or not argv or not all(isinstance(x,str) and x for x in argv) or any(x in " ".join(argv) for x in ("--force","/dev/mem","live_output=1")): raise ValueError("unsafe same-version argv")
 states=(plan["preState"],plan["absentState"],plan["qualifiedState"])
 if any(not isinstance(state,dict) or state.get("liveOutput") is not False for state in states): raise ValueError("unsafe same-version state")
 if states[0].get("product") is not True or states[0].get("qualification") is not False: raise ValueError("same-version prestate differs")
 if states[1].get("product") is not False or states[1].get("qualification") is not False: raise ValueError("same-version absent state differs")
 if states[2].get("product") is not True or states[2].get("qualification") is not True: raise ValueError("same-version qualified state differs")
 return copy.deepcopy(plan)

def execute(plan:dict,*,run,probe,record,stop_after:str|None=None)->dict:
 value=validate(plan); state={"status":"in-progress","checkpoint":"preflight","recoveryRequired":True,"liveOutput":False,"productRemoved":False,"qualificationInstalled":False}; record(state)
 try:
  if probe()!=value["preState"]: raise ValueError("same-version prestate differs")
  actions={"remove-product":value["removeArgv"],"install-qualification":value["qualificationInstallArgv"]}
  expectations={"verify-absent":value["absentState"],"verify-qualified":value["qualifiedState"]}
  for checkpoint in CHECKPOINTS[1:]:
   state["checkpoint"]=checkpoint; record(state)
   if checkpoint in actions:
    run(actions[checkpoint])
    if checkpoint=="remove-product": state["productRemoved"]=True
    if checkpoint=="install-qualification": state["qualificationInstalled"]=True
    record(state)
   elif checkpoint in expectations and probe()!=expectations[checkpoint]: raise ValueError(f"{checkpoint} differs")
   if stop_after==checkpoint: raise InterruptedError(checkpoint)
  state.update(status="complete",recoveryRequired=False); record(state); return state
 except BaseException as error:
  state.update(status="recovery-required",failure=type(error).__name__); record(state); raise

def recover(plan:dict,state:dict,*,run,probe,record)->dict:
 value=validate(plan)
 if state.get("status")!="recovery-required" or state.get("liveOutput") is not False: raise ValueError("same-version state is not recoverable")
 checkpoint=state.get("checkpoint")
 if checkpoint not in CHECKPOINTS or type(state.get("productRemoved")) is not bool or type(state.get("qualificationInstalled")) is not bool: raise ValueError("same-version journal differs")
 if state["qualificationInstalled"] and not state["productRemoved"]: raise ValueError("same-version journal is inconsistent")
 if checkpoint=="remove-product" and not state.get("productRemoved"): run(value["removeRecoveryArgv"])
 if checkpoint in {"install-qualification","verify-qualified","commit"}:
  run(value["qualificationRemoveArgv"] if state.get("qualificationInstalled") else value["qualificationRecoveryArgv"])
 if state.get("productRemoved"): run(value["productRollbackArgv"])
 if probe()!=value["preState"]: raise ValueError("same-version rollback did not restore product")
 state=dict(state); state.update(status="recovered",checkpoint="rollback-product",recoveryRequired=False,productRemoved=False,qualificationInstalled=False); record(state); return state
