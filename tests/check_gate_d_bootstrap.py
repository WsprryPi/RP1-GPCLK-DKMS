#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
import copy, hashlib, importlib.util, json, pathlib, tempfile

ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("gate_d_bootstrap",ROOT/"scripts/gate_d_bootstrap.py"); tool=importlib.util.module_from_spec(spec); spec.loader.exec_module(tool)

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
with tempfile.TemporaryDirectory() as temporary:
    root=pathlib.Path(temporary); (root/"inputs").mkdir(); (root/"source").mkdir()
    archive=root/"inputs/candidate.tar.gz"; archive.write_bytes(b"archive")
    identity=root/"inputs/identity.json"; identity.write_text("{}")
    admin=root/"source/admin.py"; admin.write_text("admin")
    installed="/usr/libexec/rp1-gpclk-dkms/rp1-gpclk-admin"
    tool_path="/usr/libexec/rp1-gpclk-dkms/gate-d-executor"
    plan={"SPDX-License-Identifier":"MIT","schemaVersion":1,"kind":"gate-d-qualification-bootstrap-plan","operationId":"phase5.18-bootstrap","hostId":"wspr5-stock","predecessorVersion":"0.0.0-phase5.2","kernelRelease":"kernel","stagingDirectory":"/var/lib/rp1-gpclk-dkms/gate-d/bootstrap","candidate":{"release":"0.0.0-phase5.38","sourceCommit":"1"*40,"archive":"/inputs/candidate.tar.gz","archiveSha256":sha(archive)},"qualificationIdentity":{"path":"/inputs/identity.json","sha256":sha(identity)},"administrator":{"sourcePath":"source/admin.py","sourceSha256":sha(admin),"bootstrapPath":"/inputs/extracted/scripts/rp1-gpclk-admin.py","installedPath":installed,"installedSha256":sha(admin)},"argv":["/usr/bin/python3","/inputs/extracted/scripts/rp1-gpclk-admin.py","install","--execute","--release-directory","/inputs","--route","gpio4","--qualification-install","--qualification-identity","/inputs/identity.json"],"cleanupArgv":["/usr/libexec/rp1-gpclk-dkms/gate-d-lifecycle","dispatch","complete-removal","0.0.0-phase5.2","0.0.0-phase5.38","kernel","/var/lib/rp1-gpclk-dkms/gate-d/bootstrap","--execute"],"recoveryArgv":["/usr/bin/python3","/inputs/extracted/scripts/rp1-gpclk-admin.py","recover","--execute"],"journal":"/state/bootstrap.json","deadlineSeconds":1800,"expectedPreState":{"moduleLoaded":False,"endpointPresent":False,"overlayActive":False,"dkmsTestVersions":False,"liveOutput":False},"expectedPostState":{"moduleLoaded":False,"endpointPresent":False,"overlayActive":False,"dkmsTestVersions":False,"liveOutput":False},"retainedTools":[{"path":tool_path,"sha256":hashlib.sha256(b"executor").hexdigest()}],"cleanupPaths":["/var/lib/rp1-gpclk-dkms/gate-d/bootstrap"],"safety":{"outputDisabled":True,"liveOutput":False,"gpioAccess":False,"clockEnabled":False,"dmaActive":False,"sdrActive":False,"rf":False}}
    assert tool.validate(plan,root=root,verify_files=True)["outputDisabled"]
    calls=[]
    def runner(argv):
        calls.append(argv)
        if argv==plan["argv"]:
            p=root/tool_path.lstrip("/"); p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(b"executor")
    probe=lambda: copy.deepcopy(plan["expectedPostState"])
    assert tool.execute(plan,root=root,runner=runner,probe=probe)["status"]=="complete"
    failed=copy.deepcopy(plan); failed["operationId"]="phase5.18-bootstrap-interrupted"; failed["journal"]="/state/interrupted.json"
    def interrupt(argv):
        if argv==failed["argv"]: raise InterruptedError("partial install")
    try: tool.execute(failed,root=root,runner=interrupt,probe=probe)
    except InterruptedError: pass
    else: raise AssertionError("interrupted bootstrap completed")
    assert json.loads((root/"state/interrupted.json").read_text())["status"]=="recovery-required"
    recovered=[]
    def recover_runner(argv): recovered.append(argv)
    assert tool.execute(failed,root=root,runner=recover_runner,probe=probe,recover=True)["status"]=="complete"
    assert failed["recoveryArgv"] in recovered and failed["argv"] in recovered
    link=root/"inputs/identity-link.json"; link.symlink_to(identity)
    bad=copy.deepcopy(plan); bad["qualificationIdentity"]={"path":"/inputs/identity-link.json","sha256":sha(identity)}; bad["argv"][-1]="/inputs/identity-link.json"
    try: tool.validate(bad,root=root,verify_files=True)
    except ValueError: pass
    else: raise AssertionError("symlinked bootstrap identity accepted")
    cleanup_failed=copy.deepcopy(plan); cleanup_failed["operationId"]="phase5.18-cleanup-failed"; cleanup_failed["journal"]="/state/cleanup-failed.json"
    def fail_cleanup(argv):
        if argv==cleanup_failed["cleanupArgv"]: raise RuntimeError("cleanup failed")
    try: tool.execute(cleanup_failed,root=root,runner=fail_cleanup,probe=probe)
    except RuntimeError: pass
    else: raise AssertionError("cleanup failure completed")
    assert json.loads((root/"state/cleanup-failed.json").read_text())["status"]=="recovery-required"
    residue=copy.deepcopy(plan); residue["operationId"]="phase5.18-residue"; residue["journal"]="/state/residue.json"
    residue_path=root/residue["cleanupPaths"][0].lstrip("/"); residue_path.mkdir(parents=True)
    try: tool.execute(residue,root=root,runner=runner,probe=probe)
    except ValueError as error: assert "residue remains" in str(error)
    else: raise AssertionError("bootstrap residue accepted")
    __import__("shutil").rmtree(residue_path)
    for mutation in (lambda x:x["qualificationIdentity"].update(sha256="0"*64),lambda x:x["administrator"].update(installedSha256="2"*64),lambda x:x["argv"].append("--force"),lambda x:x["safety"].update(gpioAccess=True),lambda x:x["cleanupPaths"].append("/../etc")):
        bad=copy.deepcopy(plan); mutation(bad)
        try: tool.validate(bad,root=root,verify_files=True)
        except ValueError: pass
        else: raise AssertionError("unsafe bootstrap accepted")
with tempfile.TemporaryDirectory() as temporary:
    root=pathlib.Path(temporary); (root/"inputs").mkdir(); (root/"source").mkdir()
    (root/"inputs/candidate.tar.gz").write_bytes(b"archive"); (root/"inputs/identity.json").write_text("{}")
    (root/"source/admin.py").write_text("admin")
    interrupted=copy.deepcopy(plan); interrupted["retainedTools"]=[]
    try: tool.validate(interrupted,root=root)
    except ValueError: pass
    else: raise AssertionError("missing retained tools accepted")
print("Gate D qualification bootstrap: PASS")
