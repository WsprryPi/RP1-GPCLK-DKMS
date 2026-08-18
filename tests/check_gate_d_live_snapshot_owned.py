#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
from __future__ import annotations
import copy,hashlib,importlib.util,json,os,pathlib,tempfile
ROOT=pathlib.Path(__file__).resolve().parents[1]
def load_module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);assert spec and spec.loader;m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
capture=load_module("capture",ROOT/"scripts/gate_d_live_snapshot_owned.py"); independent=load_module("independent",ROOT/"scripts/gate_d_live_snapshot_owned_validate.py")
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
with tempfile.TemporaryDirectory() as temporary:
 root=pathlib.Path(temporary); kernel="test-kernel"; package=root/"usr/libexec/rp1-gpclk-dkms/tool";package.parent.mkdir(parents=True);package.write_text("current tool\n");package.chmod(0o755)
 link=root/"usr/sbin/tool";link.parent.mkdir(parents=True);link.symlink_to("../libexec/rp1-gpclk-dkms/tool")
 ledger_path=root/"var/lib/rp1-gpclk-dkms/transaction.json";ledger_path.parent.mkdir(parents=True)
 ledger={"status":"complete","release":"0.0.0-current","checkpoint":"commit-state","recoveryRequired":False,"liveOutput":False,"ownedDirectories":[],"ownedFiles":[{"path":"/usr/libexec/rp1-gpclk-dkms/tool","sha256":digest(package)},{"path":"/usr/sbin/tool","symlink":"../libexec/rp1-gpclk-dkms/tool"}],"replacedFiles":[]}
 ledger_path.write_text(json.dumps(ledger,sort_keys=True)+"\n");ledger_path.chmod(0o600)
 header=root/f"usr/src/linux-headers-{kernel}";header.mkdir(parents=True);header.chmod(0o755);(header/"Module.symvers").write_text("symbols\n")
 config=root/f"boot/config-{kernel}";config.parent.mkdir();config.write_text("# CONFIG_MODULE_SIG is not set\n")
 (root/"proc").mkdir();(root/"proc/cmdline").write_text("quiet\n");boot=root/"proc/sys/kernel/random";boot.mkdir(parents=True);(boot/"boot_id").write_text("01234567-89ab-cdef-0123-456789abcdef\n")
 terminal=root/"var/lib/rp1-gpclk-dkms/gate-d/recovery/terminal/transaction.json";terminal.parent.mkdir(parents=True);terminal.write_text(json.dumps({"status":"complete","recoveryRequired":False,"liveOutput":False})+"\n");terminal.chmod(0o400)
 outputs={("uname","-r"):kernel,("uname","-m"):"aarch64",("hostname",):"wspr5",("cc","--version"):"cc test 1",("/usr/bin/dtoverlay","-l"):"No overlays loaded",("/usr/sbin/dkms","status"):""}
 def command(argv,check=True):
  key=tuple(argv)
  if key[:2]==("systemctl","is-active"):return "inactive"
  return outputs[key]
 physical={"si5351Disconnected":True,"si5351Unused":True,"sdrUnused":True,"antennaDisconnected":True}
 snapshot=capture.capture(root=root,command=command,physical=physical,terminal_path="/var/lib/rp1-gpclk-dkms/gate-d/recovery/terminal/transaction.json",expected_owner_uid=os.getuid(),expected_owner_gid=os.getgid())
 snapshot["administratorLedger"].update(ownerUid=0,groupGid=0);snapshot["terminalRecovery"].update(ownerUid=0,groupGid=0);snapshot["kernel"].update(headerOwnerUid=0,headerGroupGid=0)
 assert independent.validate(snapshot)["outputDisabled"] is True
 prior={"path":snapshot["administratorLedger"]["path"],"sha256":snapshot["administratorLedger"]["sha256"],"status":"complete","recoveryRequired":False,"liveOutput":False,"ownerUid":0,"mode":"0600","archivePath":"/var/lib/rp1-gpclk-dkms/history/current.json","archiveMode":"0400"}
 envelope={"priorTerminalState":prior,"installedPackagePaths":snapshot["packagePaths"],"packagePathsSha256":snapshot["packagePathsSha256"]};inventory={"paths":snapshot["packagePaths"]};route={"candidate":{"sourceCommit":"1"*40},"evidence":{"kernelRelease":kernel,"kernelConfigSha256":snapshot["kernel"]["configSha256"]}};build={"candidate":{"sourceCommit":"1"*40},"target":{"terminalRecoveryJournalSha256":snapshot["terminalRecovery"]["sha256"]}}
 assert independent.compare(snapshot,envelope=envelope,inventory=inventory,route=route,build=build)["valid"]
 stale=copy.deepcopy(envelope);stale["priorTerminalState"].update(sha256="2"*64,status="recovered")
 try:independent.compare(snapshot,envelope=stale,inventory=inventory,route=route,build=build)
 except ValueError as error:assert "predecessor ledger differs" in str(error)
 else:raise AssertionError("current package inventory with stale ledger passed")
 changed=copy.deepcopy(snapshot);changed["administratorLedger"]["sha256"]="3"*64
 try:independent.compare(changed,envelope=envelope,inventory=inventory,route=route,build=build)
 except ValueError:pass
 else:raise AssertionError("changed live snapshot passed old controls")
 active_command=lambda argv,check=True:"active" if tuple(argv[:2])==("systemctl","is-active") else command(argv,check)
 try:capture.capture(root=root,command=active_command,physical=physical,terminal_path="/var/lib/rp1-gpclk-dkms/gate-d/recovery/terminal/transaction.json",expected_owner_uid=os.getuid(),expected_owner_gid=os.getgid())
 except ValueError as error:assert "service is not inactive" in str(error)
 else:raise AssertionError("active service entered canonical snapshot")
 bad_package=copy.deepcopy(snapshot);bad_package["packagePaths"][0]["sha256"]="4"*64
 try:independent.validate(bad_package)
 except ValueError as error:assert "package digest differs" in str(error)
 else:raise AssertionError("mutated package identity passed canonical digest")
 config.write_text("CONFIG_MODULE_SIG=y\n")
 try:capture.capture(root=root,command=command,physical=physical,terminal_path="/var/lib/rp1-gpclk-dkms/gate-d/recovery/terminal/transaction.json",expected_owner_uid=os.getuid(),expected_owner_gid=os.getgid())
 except ValueError as error:assert "signing policy" in str(error)
 else:raise AssertionError("unsafe signing state entered canonical snapshot")
print("Gate D ownership-aware live-target snapshot: PASS")
