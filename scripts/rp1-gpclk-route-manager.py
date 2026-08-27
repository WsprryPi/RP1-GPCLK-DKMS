#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Stable, fail-closed RP1 GPCLK boot-route manager for applications."""
from __future__ import annotations
import hashlib, json, os, re, stat, subprocess, sys, tempfile, uuid
from pathlib import Path, PurePosixPath
from typing import Callable

SCHEMA_VERSION=1; CONTRACT="rp1-gpclk-route-manager-v1"; PACKAGE="rp1-gpclk-dkms"
VERSION="1.1.2"; DEBIAN_VERSION="1.1.2-1"; MODULE="rp1_gpclk_dkms"
PREDECESSOR_VERSION="1.1.1"; PREDECESSOR_DEBIAN_VERSION="1.1.1-1"
CONFIG="/boot/firmware/config.txt"; BOOT_ID="/proc/sys/kernel/random/boot_id"
JOURNAL_DIR="/var/lib/rp1-gpclk-dkms/route-transactions"
UAPI=f"/usr/src/{PACKAGE}-{VERSION}/include/uapi/linux/rp1_gpclk.h"
OVERLAY_DIR="/boot/firmware/overlays"
BEGIN="# BEGIN RP1-GPCLK-DKMS OWNED ROUTE"; END="# END RP1-GPCLK-DKMS OWNED ROUTE"
UAPI_SHA256="f0af5ffda91f4ba82285dc278452eae28b2eeffa635ebd6ee473bf7393a6a54e"
SOURCE_DEVELOPMENT_BINDING_ENV="RP1_GPCLK_SOURCE_DEVELOPMENT_BINDING"
OVERLAY_SHA256={"gpio4":"c3e17a685694928468bb18c24f5bb4e25454745d6989e6c9d2c2acf447b908d6","gpio20":"8eaa8afae7f88a665fc9bec6da1b013be049b2a32c909c729caeff9181bcf3aa"}
ROUTE_ID={"gpio4":1,"gpio20":2}; OPERATIONS={"query","preflight","apply-and-reboot","rollback","reconcile"}
MUTATIONS={"apply-and-reboot","rollback","reconcile"}; SERVICES=("wsprrypi.service","soapyremote-server.service")
REQUEST_ID=re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{7,63}"); ACTOR=re.compile(r"[A-Za-z0-9][A-Za-z0-9._:@/-]{1,127}")
BOOT_ID_RE=re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
Runner=Callable[[list[str]],str]

class ContractError(Exception): pass
def sha256_bytes(payload:bytes)->str: return hashlib.sha256(payload).hexdigest()
def sha256(path:Path)->str: return sha256_bytes(path.read_bytes())
def canonical(value:object)->bytes: return (json.dumps(value,sort_keys=True,separators=(",",":"))+"\n").encode()
def run(argv:list[str])->str: return subprocess.run(argv,check=True,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT).stdout

class Environment:
    """Fixed production paths; overrides are internal fixture seams, not CLI."""
    def __init__(self,root:Path=Path("/"),runner:Runner=run,euid:Callable[[],int]=os.geteuid): self.root=root; self.runner=runner; self.euid=euid
    def path(self,absolute:str)->Path:
        pure=PurePosixPath(absolute)
        if not pure.is_absolute() or ".." in pure.parts: raise ContractError("unsafe fixed path")
        current=self.root
        for part in pure.parts[1:]:
            current/=part
            if current.is_symlink(): raise ContractError(f"symlink rejected at fixed path: {absolute}")
        return current

def atomic_write(path:Path,payload:bytes,mode:int)->None:
    path.parent.mkdir(parents=True,mode=0o700,exist_ok=True); fd,temporary=tempfile.mkstemp(prefix=f".{path.name}.",dir=path.parent)
    try:
        os.fchmod(fd,mode)
        with os.fdopen(fd,"wb") as stream: stream.write(payload); stream.flush(); os.fsync(stream.fileno())
        os.replace(temporary,path); directory=os.open(path.parent,os.O_RDONLY|os.O_DIRECTORY)
        try: os.fsync(directory)
        finally: os.close(directory)
    finally:
        try: os.unlink(temporary)
        except FileNotFoundError: pass

def parse_request(value:object)->dict:
    if not isinstance(value,dict): raise ContractError("request must be an object")
    allowed={"schemaVersion","operation","route","execute","requestId","actor"}
    if set(value)-allowed: raise ContractError("request contains unknown fields")
    if value.get("schemaVersion")!=1 or value.get("operation") not in OPERATIONS: raise ContractError("request schema or operation is unsupported")
    operation=value["operation"]; expected={"schemaVersion","operation"}
    if operation in {"preflight","apply-and-reboot"}:
        expected.add("route")
        if value.get("route") not in ROUTE_ID: raise ContractError("route must be gpio4 or gpio20")
    if operation in MUTATIONS:
        expected.update({"execute","requestId","actor"})
        if value.get("execute") is not True: raise ContractError("mutation requires execute=true")
        if not REQUEST_ID.fullmatch(str(value.get("requestId",""))): raise ContractError("requestId is invalid")
        if not ACTOR.fullmatch(str(value.get("actor",""))): raise ContractError("actor is invalid")
    if set(value)!=expected: raise ContractError("request fields do not exactly match the operation")
    return value

def parse_config(payload:bytes)->str|None:
    try: text=payload.decode("utf-8")
    except UnicodeDecodeError as error: raise ContractError("boot configuration is not UTF-8") from error
    begins,ends=text.count(BEGIN),text.count(END)
    if begins!=ends or begins>1: raise ContractError("owned route markers are malformed or duplicated")
    all_routes=re.findall(r"^\s*dtoverlay=rp1-gpclk-(gpio4|gpio20)\s*$",text,re.M)
    if begins==0:
        if all_routes: raise ContractError("foreign RP1 GPCLK route selection")
        return None
    start,finish=text.index(BEGIN),text.index(END)+len(END)
    if finish<start: raise ContractError("owned route marker order is malformed")
    block=text[start:finish]; block_routes=re.findall(r"^dtoverlay=rp1-gpclk-(gpio4|gpio20)$",block,re.M); lines=block.splitlines()
    current_line=f"# contract={CONTRACT} package={DEBIAN_VERSION} route={block_routes[0]}" if block_routes else ""
    historical_lines=({
        f"# version={PREDECESSOR_VERSION} route={block_routes[0]}",
        f"# contract={CONTRACT} package={PREDECESSOR_DEBIAN_VERSION} route={block_routes[0]}",
    } if block_routes else set())
    if (len(block_routes)!=1 or all_routes!=block_routes or len(lines)!=4 or lines[0]!=BEGIN or lines[3]!=END or lines[1] not in {current_line,*historical_lines} or lines[2]!=f"dtoverlay=rp1-gpclk-{block_routes[0]}"): raise ContractError("owned route block is malformed or ambiguous")
    return block_routes[0]

def config_ownership(payload:bytes)->str:
    route=parse_config(payload)
    if route is None: return "absent"
    return "current" if f"# contract={CONTRACT} package={DEBIAN_VERSION} route={route}" in payload.decode() else "historical-package-owned"

def config_for_route(payload:bytes,route:str)->bytes:
    current=parse_config(payload); text=payload.decode()
    if current:
        start,finish=text.index(BEGIN),text.index(END)+len(END); text=text[:start].rstrip()+text[finish:].lstrip("\n")
    block=f"{BEGIN}\n# contract={CONTRACT} package={DEBIAN_VERSION} route={route}\ndtoverlay=rp1-gpclk-{route}\n{END}\n"
    return (text.rstrip()+"\n\n"+block).encode()

def boot_id(env:Environment)->str:
    value=env.path(BOOT_ID).read_text().strip()
    if not BOOT_ID_RE.fullmatch(value): raise ContractError("boot ID is malformed")
    return value

def source_development_identity(env:Environment,binding_name:str)->dict:
    binding_path=env.path(binding_name)
    if binding_path.is_symlink() or not binding_path.is_file(): raise ContractError("source-development binding is absent or unsafe")
    try: binding=json.loads(binding_path.read_text())
    except (OSError,json.JSONDecodeError) as error: raise ContractError("source-development binding is malformed") from error
    required={"schema","classification","qualification","sourceCommit","moduleSourceCommit","sourceManifest","sourceManifestSha256","executable","executableSha256","module","moduleVersion","uapiSha256","kernel","route","compatibilityId"}
    if (set(binding)!=required or binding["schema"]!="rp1-gpclk-route-manager-source-development-v1" or
            binding["classification"]!="Experimental/source-development" or binding["qualification"] is not False or
            not re.fullmatch(r"[0-9a-f]{40}",str(binding["sourceCommit"])) or
            not re.fullmatch(r"[0-9a-f]{40}",str(binding["moduleSourceCommit"])) or
            binding["module"]!=MODULE or binding["moduleVersion"]!=VERSION or
            binding["route"] not in ROUTE_ID or not re.fullmatch(r"[0-9a-f]{64}",str(binding["uapiSha256"]))):
        raise ContractError("source-development binding identity differs")
    executable=env.path(binding["executable"]); manifest=env.path(binding["sourceManifest"])
    if executable.is_symlink() or not executable.is_file() or sha256(executable)!=binding["executableSha256"]: raise ContractError("source-development executable identity differs")
    if manifest.is_symlink() or not manifest.is_file() or sha256(manifest)!=binding["sourceManifestSha256"]: raise ContractError("source-development manifest identity differs")
    try: manifest_value=json.loads(manifest.read_text())
    except (OSError,json.JSONDecodeError) as error: raise ContractError("source-development manifest is malformed") from error
    if (manifest_value.get("schema")!="rp1-gpclk-source-development-manifest-v1" or
            manifest_value.get("classification")!="source-development" or manifest_value.get("qualification") is not False or
            manifest_value.get("sourceCommit")!=binding["moduleSourceCommit"] or manifest_value.get("renderedVersion")!=VERSION or
            manifest_value.get("targetKernel")!=binding["kernel"] or manifest_value.get("route")!=binding["route"] or
            manifest_value.get("uapiIdentity",{}).get("sha256")!=binding["uapiSha256"]):
        raise ContractError("source-development manifest binding differs")
    if env.runner(["/usr/sbin/modinfo","-F","version",MODULE]).strip()!=VERSION: raise ContractError("module identity differs")
    if env.root==Path("/") and os.uname().release!=binding["kernel"]: raise ContractError("target kernel differs")
    return {"package":PACKAGE,"debianVersion":"installed-package-not-authoritative","module":MODULE,"moduleVersion":VERSION,
            "uapiSha256":binding["uapiSha256"],"sourceDevelopment":{"classification":binding["classification"],
            "qualification":False,"sourceCommit":binding["sourceCommit"],"moduleSourceCommit":binding["moduleSourceCommit"],"manifestSha256":binding["sourceManifestSha256"],
            "executable":binding["executable"],"executableSha256":binding["executableSha256"],"kernel":binding["kernel"],
            "route":binding["route"],"compatibilityId":binding["compatibilityId"]}}

def fixed_identity(env:Environment)->dict:
    binding=os.environ.get(SOURCE_DEVELOPMENT_BINDING_ENV)
    if binding: return source_development_identity(env,binding)
    package=env.runner(["/usr/bin/dpkg-query","-W","-f=${Status}|${Version}",PACKAGE]).strip()
    if package!=f"install ok installed|{DEBIAN_VERSION}": raise ContractError("package identity differs")
    module=env.runner(["/usr/sbin/modinfo","-F","version",MODULE]).strip()
    if module!=VERSION: raise ContractError("module identity differs")
    uapi=env.path(UAPI)
    if not uapi.is_file() or sha256(uapi)!=UAPI_SHA256: raise ContractError("UAPI identity differs")
    overlays={}
    for route,expected in OVERLAY_SHA256.items():
        path=env.path(f"{OVERLAY_DIR}/rp1-gpclk-{route}.dtbo")
        if not path.is_file() or sha256(path)!=expected: raise ContractError(f"{route} overlay identity differs")
        overlays[route]=expected
    return {"package":PACKAGE,"debianVersion":DEBIAN_VERSION,"module":MODULE,"moduleVersion":VERSION,"uapiSha256":UAPI_SHA256,"overlaySha256":overlays}

def service_safety(env:Environment,require_quiesced:bool=False)->dict:
    observed={}
    for service in SERVICES:
        active=env.runner(["/usr/bin/systemctl","show","--property=ActiveState","--value",service]).strip()
        if active not in {"active","inactive","failed"}: raise ContractError(f"service state is unknown: {service}")
        if require_quiesced and active not in {"inactive","failed"}: raise ContractError(f"service is not quiesced: {service}")
        observed[service]=active
    endpoint=env.path("/dev/rp1-gpclk")
    if endpoint.exists():
        endpoint_stat=endpoint.stat()
        if not stat.S_ISCHR(endpoint_stat.st_mode) or endpoint_stat.st_uid!=0 or endpoint_stat.st_gid!=0 or stat.S_IMODE(endpoint_stat.st_mode)!=0o600: raise ContractError("endpoint ownership or mode differs")
        for fd in env.path("/proc").glob("[0-9]*/fd/*"):
            try: opened=fd.stat()
            except OSError: continue
            if (opened.st_dev,opened.st_ino)==(endpoint_stat.st_dev,endpoint_stat.st_ino): raise ContractError("RP1 GPCLK endpoint is open")
    live=env.path(f"/sys/module/{MODULE}/parameters/live_output")
    if live.exists() and live.read_text().strip() not in {"N","0"}: raise ContractError("live_output is enabled or unknown")
    return {"services":observed,"servicesQuiesced":all(value in {"inactive","failed"} for value in observed.values()),"endpointOwned":True,"endpointOpen":False,"liveOutput":False}

def active_route(env:Environment)->str|None:
    matches=[]; of_root=env.path("/sys/firmware/devicetree/base")
    if of_root.is_dir():
        for compatible in of_root.rglob("compatible"):
            try:
                if b"wsprrypi,rp1-gpclk-dkms-v1" not in compatible.read_bytes().split(b"\0"): continue
                status_path=compatible.parent/"status"
                if status_path.exists() and status_path.read_bytes().rstrip(b"\0")!=b"okay": continue
                raw=(compatible.parent/"wsprrypi,route").read_bytes()
                if len(raw)!=4: raise ContractError("active route property is malformed")
                number=int.from_bytes(raw,"big"); route=next((name for name,value in ROUTE_ID.items() if value==number),None)
                if not route: raise ContractError("active route is unsupported")
                matches.append(route)
            except OSError as error: raise ContractError("active route could not be inspected") from error
    if len(matches)>1: raise ContractError("active route is duplicated or ambiguous")
    if matches and not env.path(f"/sys/module/{MODULE}").is_dir(): raise ContractError("active route exists without exact module")
    return matches[0] if matches else None

JOURNAL_FIELDS={"schemaVersion","contract","transactionId","initialRequestId","initialActor","lastRequestId","lastActor","operation","route","status","bootIdBefore","configBefore","configBeforeSha256","configAfterSha256","createdBootId","serviceBefore","servicesOwned"}
HISTORICAL_REQUIRED={"schemaVersion","operationId","planSha256","qualificationArchiveSha256","sourceCommit","action","status","checkpoint","rebootRequired","reconciled"}
HISTORICAL_ALLOWED=HISTORICAL_REQUIRED|{"route","bootIdBefore","bootIdAfter","configBefore","configBeforeSha256","configIntendedSha256","configAfterSha256","serviceBefore","serviceAfter","serviceAfterRestore","serviceRestorePolicy"}

def historical_journal(path:Path,value:dict,payload:bytes)->dict|None:
    if "contract" in value or "transactionId" in value: return None
    if not HISTORICAL_REQUIRED<=set(value) or not set(value)<=HISTORICAL_ALLOWED: raise ContractError("historical journal schema is stale, foreign, or malformed")
    if (value["schemaVersion"]!=1 or path.name!=f"{value['operationId']}.json" or
            not re.fullmatch(r"[a-z0-9][a-z0-9-]{7,127}",str(value["operationId"])) or
            not re.fullmatch(r"[0-9a-f]{40}",str(value["sourceCommit"])) or
            not all(re.fullmatch(r"[0-9a-f]{64}",str(value[key])) for key in ("planSha256","qualificationArchiveSha256")) or
            value["action"] not in {"quiesce-services","deactivate-and-reboot","install-inactive","apply-and-reboot"} or
            value["status"]!="complete" or value["rebootRequired"] is not False or value["reconciled"] is not True): raise ContractError("historical journal is incomplete, foreign, or unsafe")
    if "configBefore" in value:
        if not re.fullmatch(r"[0-9a-f]{64}",str(value.get("configBeforeSha256",""))) or sha256_bytes(value["configBefore"].encode())!=value["configBeforeSha256"]: raise ContractError("historical journal boot payload differs")
    if value.get("route") not in {None,"gpio4","gpio20"}: raise ContractError("historical journal route is invalid")
    return {"name":path.name,"sha256":sha256_bytes(payload),"schemaVersion":1,"operationId":value["operationId"],"sourceCommit":value["sourceCommit"],"qualificationArchiveSha256":value["qualificationArchiveSha256"],"status":"complete","preservation":"in-place-byte-exact"}

def load_journals(env:Environment)->list[tuple[Path,dict]]:
    directory=env.path(JOURNAL_DIR)
    if not directory.exists(): return []
    if not directory.is_dir(): raise ContractError("journal path is not a directory")
    if env.root==Path("/"):
        metadata=directory.stat()
        if metadata.st_uid!=0 or stat.S_IMODE(metadata.st_mode)!=0o700: raise ContractError("journal directory is not root-owned mode 0700")
    result=[]
    for path in sorted(directory.iterdir()):
        if path.is_symlink() or not path.is_file() or path.suffix!=".json": raise ContractError("foreign journal entry exists")
        try:
            payload=path.read_bytes(); value=json.loads(payload)
        except (OSError,json.JSONDecodeError) as error: raise ContractError("journal is malformed") from error
        if not isinstance(value,dict): raise ContractError("journal schema is stale, foreign, or malformed")
        metadata=path.stat()
        if env.root==Path("/") and (metadata.st_uid!=0 or stat.S_IMODE(metadata.st_mode)!=0o600): raise ContractError("journal is not root-owned mode 0600")
        historical=historical_journal(path,value,payload)
        if historical is not None:
            value={"status":"complete","historical":historical}; result.append((path,value)); continue
        if set(value)!=JOURNAL_FIELDS: raise ContractError("journal schema is stale, foreign, or malformed")
        try: canonical_id=str(uuid.UUID(str(value["transactionId"])))
        except ValueError as error: raise ContractError("journal transaction ID is invalid") from error
        if value["schemaVersion"]!=1 or value["contract"]!=CONTRACT or value["transactionId"]!=canonical_id or path.name!=f"{canonical_id}.json" or not REQUEST_ID.fullmatch(str(value["initialRequestId"])) or not ACTOR.fullmatch(str(value["initialActor"])) or not REQUEST_ID.fullmatch(str(value["lastRequestId"])) or not ACTOR.fullmatch(str(value["lastActor"])): raise ContractError("journal attribution is invalid")
        if (value["route"] not in ROUTE_ID or value["operation"] not in MUTATIONS or
                set(value["serviceBefore"])!=set(SERVICES) or
                any(state not in {"active","inactive","failed"} for state in value["serviceBefore"].values()) or
                not isinstance(value["servicesOwned"],bool) or
                value["status"] not in {"prepared","quiescing-services","services-quiesced","awaiting-reboot","rollback-prepared","rollback-awaiting-reboot","recovery-required","service-restore-failed","complete","rolled-back"} or
                not all(re.fullmatch(r"[0-9a-f]{64}",str(value[key])) for key in ("configBeforeSha256","configAfterSha256")) or
                sha256_bytes(str(value["configBefore"]).encode())!=value["configBeforeSha256"]): raise ContractError("journal state is stale, foreign, or malformed")
        result.append((path,value))
    pending=[item for item in result if item[1]["status"] not in {"complete","rolled-back"}]
    if len(pending)>1: raise ContractError("multiple pending route transactions exist")
    return result

def inspect(env:Environment,observe_safety:bool=False,require_quiesced:bool=False)->dict:
    config=env.path(CONFIG)
    if config.is_symlink() or not config.is_file() or not stat.S_ISREG(config.stat().st_mode): raise ContractError("boot configuration is absent or unsafe")
    payload=config.read_bytes(); journals=load_journals(env); pending=next((v for _,v in journals if v["status"] not in {"complete","rolled-back"}),None)
    historical=[value["historical"] for _,value in journals if "historical" in value]
    result={"identity":fixed_identity(env),"configuredRoute":parse_config(payload),"bootOwnership":config_ownership(payload),"activeRoute":active_route(env),"bootId":boot_id(env),"configSha256":sha256_bytes(payload),"pendingTransaction":pending,"journalCount":len(journals),"historicalJournals":historical}
    if observe_safety: result["safety"]=service_safety(env,require_quiesced)
    return result
def response(operation:str,status:str,state:dict)->dict: return {"schemaVersion":1,"contract":CONTRACT,"operation":operation,"status":status,"state":state}
def journal_write(path:Path,value:dict)->None: atomic_write(path,json.dumps(value,indent=2,sort_keys=True).encode()+b"\n",0o600)

def set_service_activity(env:Environment,service_before:dict,stop:bool)->None:
    if stop:
        for service in SERVICES: env.runner(["/usr/bin/systemctl","stop",service])
    else:
        for service in SERVICES:
            if service_before[service]=="active": env.runner(["/usr/bin/systemctl","start",service])

def quiesce_services(env:Environment,path:Path,journal:dict)->dict:
    journal["status"]="quiescing-services"; journal["servicesOwned"]=True; journal_write(path,journal)
    try:
        set_service_activity(env,journal["serviceBefore"],True)
        observed=service_safety(env,True)
        journal["status"]="services-quiesced"; journal_write(path,journal)
        return observed
    except BaseException:
        try:
            set_service_activity(env,journal["serviceBefore"],False)
            journal["servicesOwned"]=False; journal["status"]="recovery-required"; journal_write(path,journal)
        except BaseException:
            journal["status"]="service-restore-failed"; journal_write(path,journal)
        raise

def restore_services_after_failure(env:Environment,path:Path,journal:dict)->None:
    try:
        set_service_activity(env,journal["serviceBefore"],False)
        journal["servicesOwned"]=False; journal["status"]="recovery-required"; journal_write(path,journal)
    except BaseException as error:
        journal["status"]="service-restore-failed"; journal_write(path,journal)
        raise ContractError("boot mutation failed and service restoration failed") from error

def apply(request:dict,env:Environment,*,reboot:bool=True)->dict:
    if env.euid()!=0: raise ContractError("mutation requires root")
    before_state=inspect(env,True,False)
    if before_state["pendingTransaction"] is not None: raise ContractError("a route transaction is already pending")
    config=env.path(CONFIG); before=config.read_bytes(); after=config_for_route(before,request["route"]); transaction_id=str(uuid.uuid4()); path=env.path(f"{JOURNAL_DIR}/{transaction_id}.json")
    journal={"schemaVersion":1,"contract":CONTRACT,"transactionId":transaction_id,"initialRequestId":request["requestId"],"initialActor":request["actor"],"lastRequestId":request["requestId"],"lastActor":request["actor"],"operation":"apply-and-reboot","route":request["route"],"status":"prepared","bootIdBefore":before_state["bootId"],"configBefore":before.decode(),"configBeforeSha256":sha256_bytes(before),"configAfterSha256":sha256_bytes(after),"createdBootId":before_state["bootId"],"serviceBefore":before_state["safety"]["services"],"servicesOwned":False}
    journal_write(path,journal)
    quiesce_services(env,path,journal)
    try:
        atomic_write(config,after,config.stat().st_mode&0o777)
        if config.read_bytes()!=after or parse_config(after)!=request["route"]: raise ContractError("atomic boot update readback differs")
        journal["status"]="awaiting-reboot"; journal_write(path,journal)
    except BaseException:
        restore_services_after_failure(env,path,journal); raise
    if reboot:
        try: env.runner(["/usr/bin/systemctl","reboot"])
        except BaseException:
            restore_services_after_failure(env,path,journal); raise
    return response(request["operation"],"reboot-requested",{**before_state,"configuredRoute":request["route"],"transaction":journal})

def rollback(request:dict,env:Environment,*,reboot:bool=True)->dict:
    if env.euid()!=0: raise ContractError("mutation requires root")
    current=inspect(env,True,False); pending=current["pendingTransaction"]
    if pending is None: raise ContractError("no pending transaction can be rolled back")
    path=env.path(f"{JOURNAL_DIR}/{pending['transactionId']}.json"); config=env.path(CONFIG); payload=config.read_bytes()
    before=pending["configBefore"].encode()
    if sha256_bytes(before)!=pending["configBeforeSha256"]: raise ContractError("journaled rollback payload differs")
    current_sha=sha256_bytes(payload)
    if current_sha not in {pending["configAfterSha256"],pending["configBeforeSha256"]}: raise ContractError("rollback refuses changed boot configuration")
    pending.update(operation="rollback",status="rollback-prepared",lastRequestId=request["requestId"],lastActor=request["actor"],serviceBefore=current["safety"]["services"],servicesOwned=False); journal_write(path,pending)
    quiesce_services(env,path,pending)
    if current_sha==pending["configBeforeSha256"]:
        set_service_activity(env,pending["serviceBefore"],False); pending["servicesOwned"]=False; pending["status"]="rolled-back"; journal_write(path,pending)
        return response(request["operation"],"rolled-back",{**current,"pendingTransaction":None,"configuredRoute":parse_config(before),"transaction":pending})
    try:
        atomic_write(config,before,config.stat().st_mode&0o777)
        if config.read_bytes()!=before: raise ContractError("rollback readback differs")
        parse_config(before); pending["status"]="rollback-awaiting-reboot"; journal_write(path,pending)
    except BaseException:
        restore_services_after_failure(env,path,pending); raise
    if reboot:
        try: env.runner(["/usr/bin/systemctl","reboot"])
        except BaseException:
            restore_services_after_failure(env,path,pending); raise
    return response(request["operation"],"reboot-requested",{**current,"configuredRoute":parse_config(before),"transaction":pending})

def reconcile(request:dict,env:Environment)->dict:
    if env.euid()!=0: raise ContractError("reconciliation requires root")
    current=inspect(env); pending=current["pendingTransaction"]
    if pending is None: return response(request["operation"],"ok",current)
    if current["bootId"]==pending["bootIdBefore"]: return response(request["operation"],"awaiting-reboot",current)
    configured,active=current["configuredRoute"],current["activeRoute"]
    if pending["status"]=="awaiting-reboot":
        if configured!=pending["route"] or active!=pending["route"]: return response(request["operation"],"mismatch",current)
        pending["status"]="complete"
    elif pending["status"]=="rollback-awaiting-reboot":
        if configured!=active: return response(request["operation"],"mismatch",current)
        pending["status"]="rolled-back"
    else: return response(request["operation"],"recovery-required",current)
    pending["lastRequestId"]=request["requestId"]; pending["lastActor"]=request["actor"]; pending["servicesOwned"]=False
    journal_write(env.path(f"{JOURNAL_DIR}/{pending['transactionId']}.json"),pending); current["pendingTransaction"]=None; current["reconciledTransaction"]=pending
    return response(request["operation"],pending["status"],current)

def dispatch(value:object,env:Environment=Environment(),*,reboot:bool=True)->dict:
    request=parse_request(value); operation=request["operation"]
    if os.environ.get(SOURCE_DEVELOPMENT_BINDING_ENV) and operation!="query":
        raise ContractError("source-development route-manager integration is passive-query-only")
    if operation in {"query","preflight"}:
        result=response(operation,"ok",inspect(env,operation=="preflight",False))
        if operation=="preflight": result["state"]["requestedRoute"]=request["route"]
        return result
    if operation=="apply-and-reboot": return apply(request,env,reboot=reboot)
    if operation=="rollback": return rollback(request,env,reboot=reboot)
    return reconcile(request,env)

def main()->int:
    try:
        if len(sys.argv)!=1: raise ContractError("the executor accepts JSON on stdin and no arguments")
        sys.stdout.buffer.write(canonical(dispatch(json.load(sys.stdin)))); return 0
    except (ContractError,OSError,subprocess.CalledProcessError,json.JSONDecodeError) as error:
        sys.stdout.buffer.write(canonical({"schemaVersion":1,"contract":CONTRACT,"operation":None,"status":"error","error":{"code":"fail-closed","message":str(error)}})); return 2
if __name__=="__main__": raise SystemExit(main())
