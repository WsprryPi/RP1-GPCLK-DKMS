#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Bounded, read-only RP1-GPCLK-DKMS diagnostics."""

from __future__ import annotations
import argparse, fcntl, grp, hashlib, json, os, pathlib, platform, pwd, stat, struct, subprocess
from typing import Callable

PACKAGE, MODULE, VERSION = "rp1-gpclk-dkms", "rp1_gpclk_dkms", "0.0.0-phase5.25"
DEVICE = "/dev/rp1-gpclk"
FILE_LIMIT, LOG_LIMIT, COMMAND_LIMIT, TIMEOUT = 4096, 16384, 8192, 5
QUERY_FORMAT = "<HHIHHIIIIQIIIIIIQQ64s64s64s4Q"
QUERY_SIZE = struct.calcsize(QUERY_FORMAT)
QUERY_IOCTL = 0xC0000000 | (QUERY_SIZE << 16) | (0xB8 << 8) | 0x20
STATES = {1:"Qualified",2:"Experimental",3:"Compatible-unqualified",4:"Unavailable",5:"Rejected"}
REASONS = {0:"none",1:"manifest-missing",2:"identity-unknown",3:"identity-mismatch",4:"build-unsupported",5:"signature-rejected",6:"resource-unavailable",7:"resource-conflict",8:"self-test-failed",9:"cleanup-latched",10:"administrator-enrollment-required"}
ROUTES = {1:"GPIO4",2:"GPIO20"}
CAPS = {0:"submit-wspr",1:"submit-events",2:"stop-drain",3:"stable-state",4:"route-identity",5:"compat-identity",6:"cleanup-fault-latch",7:"live-eligible"}

def sha256(path: pathlib.Path) -> str | None:
    try:
        if path.is_symlink() or not path.is_file(): return None
        digest = hashlib.sha256()
        with path.open("rb") as source:
            while chunk := source.read(65536): digest.update(chunk)
        return digest.hexdigest()
    except OSError: return None

class Collector:
    """Collector supports a synthetic root/runner solely for hardware-free tests."""
    def __init__(self, root=pathlib.Path("/"), runner: Callable[[list[str]],dict]|None=None,
                 kernel: str|None=None, architecture: str|None=None):
        self.root, self.runner = pathlib.Path(root), runner or self._run
        self.kernel, self.architecture = kernel or platform.release(), architecture or platform.machine()
    def path(self, absolute: str) -> pathlib.Path: return self.root / absolute.lstrip("/")
    @staticmethod
    def _run(args: list[str]) -> dict:
        try:
            result = subprocess.run(args, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, text=True, timeout=TIMEOUT, check=False,
                env={"PATH":"/usr/sbin:/usr/bin:/sbin:/bin","LC_ALL":"C"})
            return {"status":"ok" if result.returncode == 0 else "error", "exitStatus":result.returncode,
                    "stdout":result.stdout[:COMMAND_LIMIT], "stderr":result.stderr[:COMMAND_LIMIT],
                    "truncated":len(result.stdout)>COMMAND_LIMIT or len(result.stderr)>COMMAND_LIMIT}
        except FileNotFoundError: return {"status":"unavailable","reason":"command-not-found"}
        except subprocess.TimeoutExpired: return {"status":"indeterminate","reason":"command-timeout"}
    def read(self, absolute: str, limit=FILE_LIMIT) -> dict:
        try:
            path=self.path(absolute)
            if path.is_symlink() or not path.is_file(): return {"status":"absent"}
            data=path.read_bytes()
            return {"status":"ok","value":data[:limit].decode(errors="replace").rstrip("\0\n"),"truncated":len(data)>limit}
        except PermissionError: return {"status":"indeterminate","reason":"permission-denied"}
        except OSError as error: return {"status":"indeterminate","reason":type(error).__name__}
    def metadata(self, absolute: str) -> dict:
        try:
            value=self.path(absolute).lstat()
            kind="symlink" if stat.S_ISLNK(value.st_mode) else "character" if stat.S_ISCHR(value.st_mode) else "file" if stat.S_ISREG(value.st_mode) else "other"
            return {"status":"ok","present":True,"type":kind,"uid":value.st_uid,"gid":value.st_gid,
                    "owner":pwd.getpwuid(value.st_uid).pw_name,"group":grp.getgrgid(value.st_gid).gr_name,
                    "mode":f"{stat.S_IMODE(value.st_mode):04o}"}
        except FileNotFoundError: return {"status":"ok","present":False}
        except PermissionError: return {"status":"indeterminate","reason":"permission-denied"}
        except (OSError,KeyError) as error: return {"status":"indeterminate","reason":type(error).__name__}
    def json_file(self, absolute: str) -> dict:
        item=self.read(absolute)
        if item["status"]!="ok": return item
        try: return {"status":"ok","value":json.loads(item["value"]),"sha256":sha256(self.path(absolute))}
        except json.JSONDecodeError: return {"status":"rejected","reason":"malformed-json"}
    def query(self) -> dict:
        if self.root != pathlib.Path("/"):
            fixture=self.json_file("/run/rp1-gpclk-dkms/query-fixture.json")
            return fixture.get("value",fixture) if fixture.get("status")=="ok" else fixture
        try:
            payload=bytearray(QUERY_SIZE); struct.pack_into("<HHI",payload,0,QUERY_SIZE,1,0)
            descriptor=os.open(self.path(DEVICE),os.O_RDONLY|os.O_CLOEXEC|os.O_NONBLOCK)
            try: fcntl.ioctl(descriptor,QUERY_IOCTL,payload,True)
            finally: os.close(descriptor)
            values=struct.unpack(QUERY_FORMAT,payload); bits=values[9]
            reason=REASONS.get(values[7],f"unknown-{values[7]}")
            return {"status":"ok","abiMin":values[3],"abiMax":values[4],"route":ROUTES.get(values[5],f"unknown-{values[5]}"),
                "compatibilityState":STATES.get(values[6],f"unknown-{values[6]}"),"compatibilityReason":REASONS.get(values[7],f"unknown-{values[7]}"),
                "cleanupFault":reason=="cleanup-latched",
                "capabilityMask":f"0x{bits:016x}","capabilities":[name for bit,name in CAPS.items() if bits&(1<<bit)],
                "unknownCapabilityMask":f"0x{bits&~0xff:016x}","moduleId":values[18].split(b"\0",1)[0].decode(errors="replace"),
                "buildId":values[19].split(b"\0",1)[0].decode(errors="replace"),"compatibilityId":values[20].split(b"\0",1)[0].decode(errors="replace")}
        except PermissionError: return {"status":"indeterminate","reason":"permission-denied"}
        except FileNotFoundError: return {"status":"unavailable","reason":"endpoint-absent"}
        except OSError as error: return {"status":"rejected","reason":f"query-failed-{error.errno}"}
    def collect(self, release_directory: pathlib.Path|None=None) -> dict:
        module_path=f"/lib/modules/{self.kernel}/updates/dkms/{MODULE}.ko"
        kernels=sorted(p.name for p in self.path("/lib/modules").glob("*") if p.is_dir())
        module_file=self.metadata(module_path); module_file["sha256"]=sha256(self.path(module_path))
        modinfo={name:self.runner(["modinfo","-F",field,module_path]) for name,field in
            (("version","version"),("vermagic","vermagic"),("signer","signer"),("signatureKeyId","sig_key"),("signatureAlgorithm","sig_id"),("signatureHashAlgorithm","sig_hashalgo"))}
        transaction=self.json_file(f"/var/lib/{PACKAGE}/transaction.json")
        enrollment=self.json_file(f"/etc/{PACKAGE}/enrollment.json")
        query=self.query(); release=self._release(release_directory)
        selected=select_manifest_entry(release.get("manifest"),query)
        endpoint=self.metadata(DEVICE); driver=self.path("/sys/bus/platform/drivers/rp1-gpclk-dkms")
        endpoint["boundDevices"]=sorted(p.name for p in driver.glob("*") if p.name not in {"bind","unbind","module","uevent"})[:8]
        endpoint["bound"]=bool(endpoint["boundDevices"])
        return {"SPDX-License-Identifier":"MIT","schemaVersion":1,"readOnly":True,
            "collectionLimits":{"commandSeconds":TIMEOUT,"commandStreamBytes":COMMAND_LIMIT,"fileBytes":FILE_LIMIT,"kernelLogBytes":LOG_LIMIT,"kernelLogScope":"current boot, matching rp1_gpclk or rp1-gpclk only"},
            "summary":classify(query,selected,transaction,enrollment),
            "package":{"version":VERSION,"manager":self.runner(["dpkg-query","-W","-f=${Status} ${Version}",PACKAGE]),"dkms":self.runner(["dkms","status","-m",PACKAGE])},
            "kernels":{"running":self.kernel,"installed":kernels,"headers":{k:self.metadata(f"/lib/modules/{k}/build") for k in kernels}},
            "build":{"transaction":transaction,"logs":self._build_logs()},
            "module":{"installedPath":module_path,"file":module_file,"metadata":modinfo,
                      "signatureStatus":self._signature_status(modinfo),"loaded":self.path(f"/sys/module/{MODULE}").is_dir(),"liveGate":self.read(f"/sys/module/{MODULE}/parameters/live_output"),"taint":self.read("/proc/sys/kernel/tainted")},
            "endpoint":endpoint,"uapi":query,"release":release,"compatibility":selected,"enrollment":enrollment,
            "cleanupFaultLatch":query.get("cleanupFault","not-exposed-by-QUERY-v1") if query.get("status")=="ok" else query,
            "routeOverlay":self._route_overlay(query),"hardwareIdentity":self._hardware(),
            "kernelDiagnostics":self.runner(["journalctl","-k","-b","--no-pager","-g","rp1[_-]gpclk","--output=short-monotonic"]),
            "residue":self._residue(transaction),"assurance":"A clean report does not prove absence of competing or direct-MMIO software."}
    def _release(self,supplied):
        base=pathlib.Path(supplied) if supplied else self.path(f"/usr/share/{PACKAGE}/{VERSION}")
        result={"path":str(base),"status":"ok" if base.is_dir() and not base.is_symlink() else "absent"}
        for name in ("release-metadata.json","rp1-gpclk-compatibility-manifest.json","SHA256SUMS"):
            digest=sha256(base/name); result[name]={"status":"ok","sha256":digest} if digest else {"status":"absent"}
        try:
            path=base/"rp1-gpclk-compatibility-manifest.json"
            if path.is_file() and not path.is_symlink(): result["manifest"]=json.loads(path.read_text())
        except (OSError,json.JSONDecodeError): result["manifest"]={"status":"rejected","reason":"malformed-or-unreadable"}
        return result
    def _build_logs(self):
        logs=[]
        for path in sorted(self.path(f"/var/lib/dkms/{PACKAGE}").glob("*/*/*/log/make.log"))[:8]:
            try:
                data=path.read_bytes(); logs.append({"path":str(path.relative_to(self.root)),"tail":data[-LOG_LIMIT:].decode(errors="replace"),"truncated":len(data)>LOG_LIMIT})
            except OSError: logs.append({"path":str(path),"status":"indeterminate","reason":"permission-denied-or-read-error"})
        return logs
    def _route_overlay(self,query):
        route=query.get("route") if query.get("status")=="ok" else None
        name={"GPIO4":"rp1-gpclk-gpio4.dtbo","GPIO20":"rp1-gpclk-gpio20.dtbo"}.get(route)
        return {"selectedRoute":route or "indeterminate","selectedArtifact":name,"artifactSha256":sha256(self.path(f"/boot/firmware/overlays/{name}")) if name else None,
                "persistentConfiguration":self.read("/boot/firmware/config.txt",LOG_LIMIT),"runtimeRoute":self.read("/proc/device-tree/rp1-gpclk/route")}
    def _hardware(self):
        result={name:self.read(path) for name,path in {"model":"/proc/device-tree/model","revision":"/proc/device-tree/system/linux,revision","clockProvider":"/proc/device-tree/rp1/clocks/compatible","clockId":"/proc/device-tree/rp1-gpclk/clock-id","dmaController":"/proc/device-tree/rp1-gpclk/dmas","pinctrl":"/proc/device-tree/rp1-gpclk/pinctrl-names"}.items()}
        result["baseDeviceTreeSha256"]=sha256(self.path("/sys/firmware/fdt"))
        return result
    @staticmethod
    def _signature_status(modinfo):
        signer=modinfo["signer"]
        if signer.get("status")!="ok": return {"status":"indeterminate","reason":"modinfo-signer-unavailable"}
        return {"status":"signed" if signer.get("stdout","").strip() else "unsigned",
                "reason":"metadata-present" if signer.get("stdout","").strip() else "no-signer-metadata"}
    def _residue(self,transaction):
        if transaction.get("status")!="ok" or not isinstance(transaction.get("value"),dict): return {"status":"indeterminate" if transaction.get("status")=="indeterminate" else "none-recorded","paths":[]}
        journal=transaction["value"]; paths=[]
        for item in journal.get("ownedFiles",[]):
            candidate=item.get("path") if isinstance(item,dict) else None
            if candidate and self.path(candidate).exists(): paths.append(candidate)
        for candidate in journal.get("ownedDirectories",[]):
            if isinstance(candidate,str) and self.path(candidate).exists(): paths.append(candidate)
        interrupted=journal.get("status") not in {"complete","recovered"}; unique=sorted(set(paths))
        return {"status":"interrupted-operation-residue" if interrupted and unique else "none-detected","transactionStatus":journal.get("status","unknown"),"paths":unique[:128],"truncated":len(unique)>128}

def select_manifest_entry(manifest,query):
    if not isinstance(manifest,dict) or not isinstance(manifest.get("entries"),list): return {"status":"Unavailable","reason":"manifest-missing-or-malformed","selectedEntry":None}
    if query.get("status")!="ok": return {"status":"indeterminate","reason":"UAPI-query-unavailable","selectedEntry":None,"manifestId":manifest.get("manifestId")}
    matches=[e for e in manifest["entries"] if e.get("id")==query.get("compatibilityId") and e.get("route")==query.get("route")]
    if len(matches)!=1: return {"status":"Unavailable","reason":"no-unique-exact-manifest-entry","selectedEntry":None,"manifestId":manifest.get("manifestId")}
    entry=matches[0]; return {"status":entry.get("state","Rejected"),"reason":entry.get("reason","missing-reason"),"selectedEntry":entry.get("id"),"manifestId":manifest.get("manifestId"),"liveEligible":entry.get("liveEligible",False)}

def classify(query,selected,transaction,enrollment):
    if transaction.get("status")=="ok" and transaction.get("value",{}).get("status") not in {"complete","recovered"}: return {"category":"rejected","compatibilityState":"Rejected","reason":"interrupted-operation-requires-recovery"}
    if any(x.get("status")=="indeterminate" for x in (query,selected,enrollment)): return {"category":"indeterminate-because-inspection-lacked-privileges","compatibilityState":"indeterminate","reason":"required-read-denied-or-query-unavailable"}
    state=query.get("compatibilityState") if query.get("status")=="ok" else selected.get("status","Unavailable")
    if query.get("cleanupFault") is True or state=="Rejected": return {"category":"rejected","compatibilityState":"Rejected","reason":query.get("compatibilityReason",selected.get("reason"))}
    if selected.get("status")=="Unavailable": return {"category":"unavailable","compatibilityState":"Unavailable","reason":selected.get("reason")}
    if selected.get("status") not in {state,"indeterminate"}: return {"category":"rejected","compatibilityState":"Rejected","reason":"UAPI-and-manifest-state-mismatch"}
    categories={"Qualified":"healthy-and-qualified","Experimental":"healthy-but-experimental","Compatible-unqualified":"build-compatible-but-live-disabled"}
    if state in categories: return {"category":categories[state],"compatibilityState":state,"reason":selected.get("reason")}
    return {"category":"unavailable","compatibilityState":"Unavailable","reason":selected.get("reason",query.get("reason","required-identity-unavailable"))}

def main():
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument("--release-directory",type=pathlib.Path); args=parser.parse_args()
    print(json.dumps(Collector().collect(args.release_directory),indent=2,sort_keys=True))
if __name__=="__main__": main()
