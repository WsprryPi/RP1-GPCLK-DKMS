#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Hardware-free fixtures for the installed route-manager contract."""
import copy, importlib.util, json, pathlib, tempfile

ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("route_manager",ROOT/"scripts/rp1-gpclk-route-manager.py")
manager=importlib.util.module_from_spec(spec); spec.loader.exec_module(manager)

def rejected(action,contains=None):
    try: action()
    except manager.ContractError as error:
        if contains: assert contains in str(error),str(error)
    else: raise AssertionError("unsafe fixture was accepted")

def request(operation,route=None,number=1):
    value={"schemaVersion":1,"operation":operation}
    if route is not None: value["route"]=route
    if operation in manager.MUTATIONS: value.update(execute=True,requestId=f"wsprrypi-{number:08d}",actor="wsprrypi.service")
    return value

class Fixture:
    def __init__(self,root):
        self.root=root; self.calls=[]; self.services={name:"inactive" for name in manager.SERVICES}; self.fail_stop=None; self.fail_reboot=False
        self.uapi=b"fixture uapi\n"; self.overlays={"gpio4":b"fixture gpio4\n","gpio20":b"fixture gpio20\n"}
        self.place("/boot/firmware/config.txt",b"# base configuration\n")
        self.place(manager.BOOT_ID,b"11111111-2222-3333-4444-555555555555\n")
        self.place(manager.UAPI,self.uapi)
        for route,payload in self.overlays.items(): self.place(f"{manager.OVERLAY_DIR}/rp1-gpclk-{route}.dtbo",payload)
        (self.root/"proc").mkdir(exist_ok=True); (self.root/"sys/firmware/devicetree/base").mkdir(parents=True)
        manager.UAPI_SHA256=manager.sha256_bytes(self.uapi)
        manager.OVERLAY_SHA256={key:manager.sha256_bytes(value) for key,value in self.overlays.items()}
    def place(self,path,payload):
        target=self.root/path.lstrip("/"); target.parent.mkdir(parents=True,exist_ok=True); target.write_bytes(payload)
    def runner(self,argv):
        self.calls.append(argv)
        if argv[:3]==["/usr/bin/dpkg-query","-W","-f=${Status}|${Version}"]: return "install ok installed|1.1.2-1\n"
        if argv[:4]==["/usr/sbin/modinfo","-F","version",manager.MODULE]: return "1.1.2\n"
        if argv[:3]==["/usr/bin/systemctl","show","--property=ActiveState"]: return self.services[argv[-1]]+"\n"
        if argv[:2]==["/usr/bin/systemctl","stop"]:
            if argv[-1]==self.fail_stop: raise OSError("injected stop failure")
            self.services[argv[-1]]="inactive"; return ""
        if argv[:2]==["/usr/bin/systemctl","start"]: self.services[argv[-1]]="active"; return ""
        if argv==["/usr/bin/systemctl","reboot"]:
            if self.fail_reboot: raise OSError("injected reboot failure")
            return ""
        raise AssertionError(argv)
    def env(self,root=True): return manager.Environment(self.root,self.runner,(lambda:0 if root else 1000))
    def activate(self,route):
        node=self.root/"sys/firmware/devicetree/base/rp1/rp1-gpclk-dkms"; node.mkdir(parents=True,exist_ok=True)
        (node/"compatible").write_bytes(b"wsprrypi,rp1-gpclk-dkms-v1\0"); (node/"status").write_bytes(b"okay\0")
        (node/"wsprrypi,route").write_bytes(manager.ROUTE_ID[route].to_bytes(4,"big")); (self.root/f"sys/module/{manager.MODULE}").mkdir(parents=True,exist_ok=True)
    def reboot(self): self.place(manager.BOOT_ID,b"aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee\n")

with tempfile.TemporaryDirectory() as temporary:
    fixture=Fixture(pathlib.Path(temporary)); env=fixture.env()
    assert manager.dispatch(request("query"),env)["state"]["configuredRoute"] is None
    fixture.services["wsprrypi.service"]="active"
    running=manager.dispatch(request("preflight","gpio4"),env)
    assert running["status"]=="ok" and running["state"]["safety"]["services"]["wsprrypi.service"]=="active"
    assert running["state"]["safety"]["servicesQuiesced"] is False
    for route in manager.ROUTE_ID:
        assert manager.dispatch(request("preflight",route),env)["state"]["requestedRoute"]==route
        result=manager.dispatch(request("apply-and-reboot",route,10+manager.ROUTE_ID[route]),env,reboot=False)
        assert result["status"]=="reboot-requested" and manager.parse_config(env.path(manager.CONFIG).read_bytes())==route
        assert fixture.services["wsprrypi.service"]=="inactive"
        fixture.activate(route); fixture.reboot()
        assert manager.dispatch(request("reconcile"),env)["status"]=="complete"
        # Reset active fixture and boot identity for the independent second route.
        active=fixture.root/"sys/firmware/devicetree/base/rp1/rp1-gpclk-dkms"
        for child in active.iterdir(): child.unlink()
        active.rmdir(); (fixture.root/f"sys/module/{manager.MODULE}").rmdir()
        fixture.place(manager.BOOT_ID,b"11111111-2222-3333-4444-555555555555\n")
        fixture.services["wsprrypi.service"]="active"

with tempfile.TemporaryDirectory() as temporary:
    fixture=Fixture(pathlib.Path(temporary)); env=fixture.env()
    applied=manager.dispatch(request("apply-and-reboot","gpio4",20),env,reboot=False)
    assert applied["state"]["transaction"]["initialActor"]=="wsprrypi.service"
    assert manager.dispatch(request("rollback",number=21),env,reboot=False)["state"]["configuredRoute"] is None
    fixture.reboot(); assert manager.dispatch(request("reconcile"),env)["status"]=="rolled-back"

with tempfile.TemporaryDirectory() as temporary:
    fixture=Fixture(pathlib.Path(temporary)); env=fixture.env(); config=env.path(manager.CONFIG)
    original=manager.atomic_write
    def interrupted(path,payload,mode):
        if path==config: raise OSError("injected interruption")
        return original(path,payload,mode)
    manager.atomic_write=interrupted
    try:
        try: manager.dispatch(request("apply-and-reboot","gpio20",30),env,reboot=False)
        except OSError: pass
        else: raise AssertionError("interrupted transaction succeeded")
    finally: manager.atomic_write=original
    journal=manager.load_journals(env)[0][1]
    assert journal["status"]=="recovery-required" and config.read_bytes()==b"# base configuration\n"
    assert manager.dispatch(request("rollback",number=31),env,reboot=False)["status"]=="rolled-back"

with tempfile.TemporaryDirectory() as temporary:
    fixture=Fixture(pathlib.Path(temporary)); env=fixture.env()
    fixture.services={name:"active" for name in manager.SERVICES}; fixture.fail_stop="soapyremote-server.service"
    try: manager.dispatch(request("apply-and-reboot","gpio4",35),env,reboot=False)
    except OSError: pass
    else: raise AssertionError("partial service quiescence succeeded")
    assert fixture.services=={name:"active" for name in manager.SERVICES}
    assert manager.load_journals(env)[0][1]["status"]=="recovery-required"

with tempfile.TemporaryDirectory() as temporary:
    fixture=Fixture(pathlib.Path(temporary)); env=fixture.env(); fixture.services["wsprrypi.service"]="active"; fixture.fail_reboot=True
    try: manager.dispatch(request("apply-and-reboot","gpio20",36),env,reboot=True)
    except OSError: pass
    else: raise AssertionError("failed reboot request succeeded")
    journal=manager.load_journals(env)[0][1]
    assert journal["status"]=="recovery-required" and journal["servicesOwned"] is False
    assert fixture.services["wsprrypi.service"]=="active"

with tempfile.TemporaryDirectory() as temporary:
    fixture=Fixture(pathlib.Path(temporary)); env=fixture.env(); config=env.path(manager.CONFIG)
    manager.dispatch(request("apply-and-reboot","gpio4",40),env,reboot=False); config.write_bytes(config.read_bytes()+b"# foreign change\n")
    rejected(lambda:manager.dispatch(request("rollback",number=41),env,reboot=False),"refuses changed")

for payload in (
    f"{manager.BEGIN}\ndtoverlay=rp1-gpclk-gpio4\n".encode(),
    b"dtoverlay=rp1-gpclk-gpio4\n",
    b"dtoverlay=rp1-gpclk-gpio4\ndtoverlay=rp1-gpclk-gpio20\n",
    (f"{manager.BEGIN}\n# contract={manager.CONTRACT} package={manager.DEBIAN_VERSION} route=gpio4\n"
     f"dtoverlay=rp1-gpclk-gpio4\n{manager.END}\n{manager.BEGIN}\n# duplicate\n{manager.END}\n").encode(),
): rejected(lambda payload=payload:manager.parse_config(payload))

legacy=(f"{manager.BEGIN}\n# version=1.1.1 route=gpio4\n"
        f"dtoverlay=rp1-gpclk-gpio4\n{manager.END}\n").encode()
assert manager.parse_config(legacy)=="gpio4" and manager.config_ownership(legacy)=="historical-package-owned"

predecessor=(f"{manager.BEGIN}\n# contract={manager.CONTRACT} package=1.1.1-1 route=gpio20\n"
             f"dtoverlay=rp1-gpclk-gpio20\n{manager.END}\n").encode()
assert manager.parse_config(predecessor)=="gpio20"
assert manager.config_ownership(predecessor)=="historical-package-owned"
upgraded=manager.config_for_route(b"# base\n\n"+predecessor,"gpio4")
assert manager.parse_config(upgraded)=="gpio4" and manager.config_ownership(upgraded)=="current"
assert b"package=1.1.1-1" not in upgraded and b"package=1.1.2-1" in upgraded

with tempfile.TemporaryDirectory() as temporary:
    fixture=Fixture(pathlib.Path(temporary)); env=fixture.env(); env.path(manager.CONFIG).write_bytes(b"# base\n\n"+legacy)
    journal_dir=env.path(manager.JOURNAL_DIR); journal_dir.mkdir(parents=True)
    before="# historical before\n"
    historical={"schemaVersion":1,"operationId":"wspr5-1-1-1-old-select-gpio4","planSha256":"1"*64,
                "qualificationArchiveSha256":"2"*64,"sourceCommit":"3"*40,"action":"apply-and-reboot",
                "status":"complete","checkpoint":"reconciled","rebootRequired":False,"reconciled":True,
                "route":"gpio4","configBefore":before,"configBeforeSha256":manager.sha256_bytes(before.encode()),
                "configAfterSha256":"4"*64}
    historical_path=journal_dir/f"{historical['operationId']}.json"; historical_path.write_text(json.dumps(historical,sort_keys=True)+"\n")
    original=historical_path.read_bytes(); state=manager.dispatch(request("preflight","gpio20"),env)["state"]
    assert state["bootOwnership"]=="historical-package-owned" and len(state["historicalJournals"])==1
    assert state["pendingTransaction"] is None and historical_path.read_bytes()==original
    historical["status"]="awaiting-reboot"; historical_path.write_text(json.dumps(historical))
    rejected(lambda:manager.dispatch(request("query"),env),"incomplete")

with tempfile.TemporaryDirectory() as temporary:
    fixture=Fixture(pathlib.Path(temporary)); env=fixture.env(); journal_dir=env.path(manager.JOURNAL_DIR); journal_dir.mkdir(parents=True)
    (journal_dir/"stale.json").write_text(json.dumps({"schemaVersion":0}))
    rejected(lambda:manager.dispatch(request("query"),env),"stale")

with tempfile.TemporaryDirectory() as temporary:
    fixture=Fixture(pathlib.Path(temporary)); env=fixture.env(); manager.dispatch(request("apply-and-reboot","gpio20",50),env,reboot=False)
    fixture.reboot(); result=manager.dispatch(request("reconcile"),env)
    assert result["status"]=="mismatch" and result["state"]["configuredRoute"]=="gpio20" and result["state"]["activeRoute"] is None

for bad in (
    {"schemaVersion":1,"operation":"query","route":"gpio4"},
    {"schemaVersion":1,"operation":"preflight","route":"gpio5"},
    {"schemaVersion":1,"operation":"apply-and-reboot","route":"gpio4","execute":False,"requestId":"wsprrypi-00000001","actor":"app"},
    {"schemaVersion":1,"operation":"rollback","execute":True,"requestId":"short","actor":"app"},
): rejected(lambda bad=bad:manager.parse_request(bad))

source=(ROOT/"scripts/rp1-gpclk-route-manager.py").read_text()
for prohibited in ("shell=True","/dev/mem","live_output=1","release_candidate_transaction","sudo","/bin/sh"):
    assert prohibited not in source
for required in ("os.replace","os.fsync","O_DIRECTORY","/usr/bin/systemctl\",\"reboot","rollback refuses changed"):
    assert required in source
print("Installed route manager hardware-free contract: PASS")
