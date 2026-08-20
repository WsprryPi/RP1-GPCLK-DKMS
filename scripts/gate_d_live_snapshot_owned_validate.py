#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Independently validate and compare a Gate D live-target snapshot."""
from __future__ import annotations
import argparse, hashlib, json, pathlib, re
SHA=re.compile(r"[0-9a-f]{64}")
SERVICES={"wsprrypi.service","sdrplay.service","sdrconnect-server.service","SoapySDRServer.service","rp1-gpclk-apply.service","rp1-gpclk-watchdog.service"}
def canonical(value:object)->str:return hashlib.sha256((json.dumps(value,sort_keys=True,separators=(",",":"))+"\n").encode()).hexdigest()
def validate(value:dict)->dict:
 required={"SPDX-License-Identifier","schemaVersion","kind","host","boot","kernel","signingPolicy","packagePaths","packagePathsSha256","administratorLedger","terminalRecovery","runtime","services","physicalSafety"}
 if not isinstance(value,dict) or set(value)!=required or value.get("SPDX-License-Identifier")!="MIT" or value.get("schemaVersion")!=1 or value.get("kind")!="gate-d-live-target-snapshot": raise ValueError("snapshot identity differs")
 paths=value["packagePaths"]
 if not isinstance(paths,list) or not paths or paths!=sorted(paths,key=lambda x:x.get("path","")) or len({x.get("path") for x in paths})!=len(paths): raise ValueError("snapshot package inventory differs")
 for item in paths:
  common={"path","type","mode","ownerUid","groupGid"}
  if item.get("type")=="file": expected=common|{"sha256"}; identity=item.get("sha256","")
  elif item.get("type")=="symlink": expected=common|{"target"}; identity=item.get("target","")
  else: raise ValueError("snapshot package type differs")
  if set(item)!=expected or not pathlib.PurePosixPath(item.get("path","")).is_absolute() or not identity or (item["type"]=="file" and not SHA.fullmatch(identity)): raise ValueError("snapshot package record differs")
 if value.get("packagePathsSha256")!=canonical(paths): raise ValueError("snapshot package digest differs")
 ledger=value["administratorLedger"]
 if set(ledger)!={"path","sha256","ownerUid","groupGid","mode","status","release","checkpoint","recoveryRequired","liveOutput"} or ledger.get("path")!="/var/lib/rp1-gpclk-dkms/transaction.json" or not SHA.fullmatch(ledger.get("sha256","")) or ledger.get("mode")!="0600" or ledger.get("ownerUid")!=0 or ledger.get("groupGid")!=0 or ledger.get("status")!="complete" or ledger.get("checkpoint")!="commit-state" or ledger.get("recoveryRequired") is not False or ledger.get("liveOutput") is not False: raise ValueError("snapshot administrator ledger differs")
 terminal=value["terminalRecovery"]
 if set(terminal)!={"path","sha256","ownerUid","groupGid","mode","status","recoveryRequired","liveOutput"} or terminal.get("ownerUid")!=0 or terminal.get("groupGid")!=0 or terminal.get("mode")!="0400" or terminal.get("status")!="complete" or terminal.get("recoveryRequired") is not False or terminal.get("liveOutput") is not False or not SHA.fullmatch(terminal.get("sha256","")): raise ValueError("snapshot terminal recovery differs")
 kernel=value["kernel"]
 if set(kernel)!={"release","headerPath","headerOwnerUid","headerGroupGid","headerMode","configSha256","moduleSymversSha256","compiler"} or kernel.get("headerOwnerUid")!=0 or kernel.get("headerGroupGid")!=0 or kernel.get("headerMode")!="0755" or not SHA.fullmatch(kernel.get("configSha256","")) or not SHA.fullmatch(kernel.get("moduleSymversSha256","")): raise ValueError("snapshot kernel identity differs")
 runtime=value["runtime"]
 if (set(runtime)!={"moduleLoaded","endpointPresent","overlayActive","dkmsTestVersions","liveOutput"} or
     any(type(runtime[key]) is not bool for key in runtime) or
     any(runtime[key] for key in ("moduleLoaded","endpointPresent","overlayActive","liveOutput"))): raise ValueError("snapshot runtime is active")
 if value["physicalSafety"]!={"si5351Disconnected":True,"si5351Unused":True,"sdrUnused":True,"antennaDisconnected":True}: raise ValueError("snapshot physical safety differs")
 if not isinstance(value["services"],dict) or set(value["services"])!=SERVICES or set(value["services"].values())!={"inactive"}: raise ValueError("snapshot service state differs")
 signing=value["signingPolicy"]
 if signing.get("source")!="config-disabled-sysctl-absent" or signing.get("enforced") is not False or signing.get("sysctl") is not None or signing.get("commandLineEnforced") is not False: raise ValueError("snapshot signing policy differs")
 return {"valid":True,"readOnly":True,"outputDisabled":True,"snapshotSha256":canonical(value)}
def compare(value:dict,*,envelope:dict,inventory:dict,route:dict,build:dict)->dict:
 result=validate(value); ledger=value["administratorLedger"]
 prior=envelope.get("priorTerminalState")
 expected_prior={"path":ledger["path"],"sha256":ledger["sha256"],"status":ledger["status"],"recoveryRequired":ledger["recoveryRequired"],"liveOutput":ledger["liveOutput"],"ownerUid":ledger["ownerUid"],"mode":ledger["mode"],"archivePath":prior.get("archivePath") if isinstance(prior,dict) else None,"archiveMode":prior.get("archiveMode") if isinstance(prior,dict) else None}
 if prior!=expected_prior: raise ValueError("control predecessor ledger differs from live snapshot")
 control_paths=envelope.get("predecessorPackagePaths") if envelope.get("schemaVersion") in {5,6} else envelope.get("installedPackagePaths")
 control_digest=envelope.get("predecessorPackagePathsSha256") if envelope.get("schemaVersion") in {5,6} else envelope.get("packagePathsSha256")
 if control_paths!=value["packagePaths"] or inventory.get("paths")!=value["packagePaths"]: raise ValueError("control package inventory differs from live snapshot")
 if control_digest!=value["packagePathsSha256"]: raise ValueError("control package digest differs from live snapshot")
 if envelope.get("schemaVersion") in {5,6} and envelope.get("liveTargetSnapshotSha256")!=result["snapshotSha256"]: raise ValueError("control snapshot identity differs")
 if route.get("candidate",{}).get("sourceCommit")!=build.get("candidate",{}).get("sourceCommit"): raise ValueError("source and build commits differ")
 if route.get("evidence",{}).get("kernelRelease")!=value["kernel"]["release"] or route.get("evidence",{}).get("kernelConfigSha256")!=value["kernel"]["configSha256"]: raise ValueError("control kernel identity differs from live snapshot")
 build_recovery=build.get("target",{}).get("terminalRecoveryJournalSha256")
 if build_recovery is not None and build_recovery!=value["terminalRecovery"]["sha256"]: raise ValueError("build recovery identity differs from live snapshot")
 return result
def main()->None:
 p=argparse.ArgumentParser();p.add_argument("snapshot",type=pathlib.Path);p.add_argument("--envelope",type=pathlib.Path);p.add_argument("--inventory",type=pathlib.Path);p.add_argument("--route",type=pathlib.Path);p.add_argument("--build",type=pathlib.Path);a=p.parse_args(); load=lambda x:json.loads(x.read_text())
 comparison=(a.envelope,a.inventory,a.route,a.build)
 if any(comparison) and not all(comparison):raise SystemExit("comparison requires envelope, inventory, route, and build")
 value=load(a.snapshot); result=compare(value,envelope=load(a.envelope),inventory=load(a.inventory),route=load(a.route),build=load(a.build)) if all(comparison) else validate(value);print(json.dumps(result,indent=2,sort_keys=True))
if __name__=="__main__":main()
