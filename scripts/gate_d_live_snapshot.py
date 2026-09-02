#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Capture one canonical, read-only Gate D target-state snapshot."""
from __future__ import annotations
import argparse, hashlib, json, os, pathlib, stat, subprocess

LEDGER="/var/lib/rp1-gpclk-dkms/transaction.json"
SERVICES=("wsprrypi.service","sdrplay.service","sdrconnect-server.service","SoapySDRServer.service","rp1-gpclk-apply.service","rp1-gpclk-watchdog.service")
def sha(path:pathlib.Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()
def rooted(root:pathlib.Path,raw:str)->pathlib.Path:
 p=pathlib.PurePosixPath(raw)
 if not p.is_absolute() or ".." in p.parts: raise ValueError("unsafe snapshot path")
 current=root
 for part in p.parts[1:]:
  current/=part
  if current.is_symlink() and part!=p.parts[-1]: raise ValueError("symlink in snapshot path")
 return current
def canonical_digest(value:object)->str:
 return hashlib.sha256((json.dumps(value,sort_keys=True,separators=(",",":"))+"\n").encode()).hexdigest()
def run(argv:list[str])->str:return subprocess.run(argv,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,check=True).stdout.strip()
def capture(*,root:pathlib.Path,command,physical:dict,terminal_path:str,expected_owner_uid:int=0,expected_owner_gid:int=0)->dict:
 if physical!={"si5351Disconnected":True,"si5351Unused":True,"sdrUnused":True,"antennaDisconnected":True}: raise ValueError("physical safety declaration differs")
 ledger_path=rooted(root,LEDGER); st=ledger_path.lstat()
 if ledger_path.is_symlink() or not ledger_path.is_file() or stat.S_IMODE(st.st_mode)!=0o600 or st.st_uid!=expected_owner_uid or st.st_gid!=expected_owner_gid: raise ValueError("administrator ledger is unsafe")
 ledger=json.loads(ledger_path.read_text()); replaced=ledger.get("replacedFiles")
 if ledger.get("status")!="complete" or ledger.get("checkpoint")!="commit-state" or ledger.get("recoveryRequired") is not False or ledger.get("outputActive") is not False or not isinstance(ledger.get("release"),str): raise ValueError("administrator ledger is not terminal complete")
 if not isinstance(replaced,list) or not replaced: raise ValueError("administrator ledger lacks committed package inventory")
 records=[]
 for record in replaced:
  if record.get("status")!="committed" or not isinstance(record.get("path"),str): raise ValueError("uncommitted package transition")
  path=rooted(root,record["path"]); meta=path.lstat(); common={"path":record["path"],"mode":f"0{stat.S_IMODE(meta.st_mode):03o}","ownerUid":meta.st_uid,"groupGid":meta.st_gid}
  if path.is_symlink(): records.append({**common,"type":"symlink","target":os.readlink(path)})
  elif path.is_file(): records.append({**common,"type":"file","sha256":sha(path)})
  else: raise ValueError("package path is absent or special")
 records.sort(key=lambda x:x["path"])
 if len({x["path"] for x in records})!=len(records): raise ValueError("duplicate package transition")
 kernel=command(["uname","-r"]); header=f"/usr/src/linux-headers-{kernel}"; header_path=rooted(root,header)
 if header_path.is_symlink() or not header_path.is_dir(): raise ValueError("kernel headers are unsafe")
 hs=header_path.stat()
 if hs.st_uid!=expected_owner_uid or hs.st_gid!=expected_owner_gid or stat.S_IMODE(hs.st_mode)!=0o755: raise ValueError("kernel header ownership differs")
 config=rooted(root,f"/boot/config-{kernel}"); cmdline_path=rooted(root,"/proc/cmdline")
 if config.is_symlink() or not config.is_file() or cmdline_path.is_symlink() or not cmdline_path.is_file(): raise ValueError("kernel policy evidence is unsafe")
 lines=config.read_text().splitlines(); cmdline=cmdline_path.read_text().split()
 sysctl=rooted(root,"/proc/sys/kernel/module_sig_enforce"); lockdown=rooted(root,"/sys/kernel/security/lockdown")
 if "# CONFIG_MODULE_SIG is not set" not in lines or sysctl.exists() or "module.sig_enforce=1" in cmdline: raise ValueError("signing policy is not reviewed non-enforcing state")
 lockdown_value=lockdown.read_text().strip() if lockdown.exists() else None
 if lockdown_value is not None and "[none]" not in lockdown_value: raise ValueError("lockdown is enforcing")
 terminal=rooted(root,terminal_path)
 if terminal.is_symlink() or not terminal.is_file(): raise ValueError("terminal recovery is unsafe")
 terminal_stat=terminal.stat();terminal_value=json.loads(terminal.read_text())
 if terminal_stat.st_uid!=expected_owner_uid or terminal_stat.st_gid!=expected_owner_gid or stat.S_IMODE(terminal_stat.st_mode)!=0o400: raise ValueError("terminal recovery metadata differs")
 if terminal_value.get("status")!="complete" or terminal_value.get("recoveryRequired") is not False or terminal_value.get("outputActive") is not False: raise ValueError("terminal recovery differs")
 overlays=command(["/usr/bin/dtoverlay","-l"]); dkms=command(["/usr/sbin/dkms","status"])
 services={}
 for name in SERVICES:
  state=command(["systemctl","is-active",name],False)
  if state!="inactive": raise ValueError(f"service is not inactive: {name}")
  services[name]="inactive"
 return {"SPDX-License-Identifier":"MIT","schemaVersion":1,"kind":"gate-d-live-target-snapshot","host":{"hostname":command(["hostname"]),"architecture":command(["uname","-m"])},"boot":{"bootId":rooted(root,"/proc/sys/kernel/random/boot_id").read_text().strip()},"kernel":{"release":kernel,"headerPath":header,"headerOwnerUid":hs.st_uid,"headerGroupGid":hs.st_gid,"headerMode":f"0{stat.S_IMODE(hs.st_mode):03o}","configSha256":sha(config),"moduleSymversSha256":sha(header_path/"Module.symvers"),"compiler":command(["cc","--version"]).splitlines()[0]},"signingPolicy":{"source":"config-disabled-sysctl-absent","enforced":False,"sysctl":None,"commandLineEnforced":False,"lockdown":lockdown_value},"packagePaths":records,"packagePathsSha256":canonical_digest(records),"administratorLedger":{"path":LEDGER,"sha256":sha(ledger_path),"ownerUid":st.st_uid,"groupGid":st.st_gid,"mode":"0600","status":ledger.get("status"),"release":ledger.get("release"),"checkpoint":ledger.get("checkpoint"),"recoveryRequired":ledger.get("recoveryRequired"),"outputActive":ledger.get("outputActive")},"terminalRecovery":{"path":terminal_path,"sha256":sha(terminal),"ownerUid":terminal_stat.st_uid,"groupGid":terminal_stat.st_gid,"mode":f"0{stat.S_IMODE(terminal_stat.st_mode):03o}","status":terminal_value["status"],"recoveryRequired":False,"outputActive":False},"runtime":{"moduleLoaded":rooted(root,"/sys/module/rp1_gpclk_dkms").exists(),"endpointPresent":rooted(root,"/dev/rp1-gpclk").exists(),"overlayActive":"rp1-gpclk" in overlays,"dkmsTestVersions":"rp1-gpclk-dkms/" in dkms,"outputActive":False},"services":services,"physicalSafety":physical}
def main()->None:
 p=argparse.ArgumentParser();p.add_argument("--physical-declarations",type=pathlib.Path,required=True);p.add_argument("--terminal-recovery-journal",required=True);a=p.parse_args()
 value=capture(root=pathlib.Path("/"),command=lambda argv,check=True:run(argv) if check else subprocess.run(argv,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,check=False).stdout.strip(),physical=json.loads(a.physical_declarations.read_text()),terminal_path=a.terminal_recovery_journal)
 print(json.dumps(value,sort_keys=True,separators=(",",":")))
if __name__=="__main__":main()
