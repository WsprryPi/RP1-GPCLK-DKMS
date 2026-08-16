#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
from __future__ import annotations
import copy, hashlib, importlib.util, json, os, pathlib, tempfile

ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("gate_d_preroot",ROOT/"scripts/gate_d_preroot.py"); assert spec and spec.loader
tool=importlib.util.module_from_spec(spec); spec.loader.exec_module(tool)
baseline={"moduleLoaded":False,"endpointPresent":False,"overlayActive":False,"dkmsTestVersions":False,"liveOutput":False}
safety={"outputDisabled":True,"liveOutput":False,"gpioAccess":False,"clockEnabled":False,"dmaActive":False,"sdrActive":False,"rf":False}
def sha(path:pathlib.Path)->str: return hashlib.sha256(path.read_bytes()).hexdigest()
def make_envelope(prefix:pathlib.Path)->dict:
    (prefix/"qualification").mkdir(); (prefix/"staging").mkdir()
    control=prefix/"staging/instance.json"; control.write_text("{}\n")
    executor=prefix/"staging/gate_d_outer.py"; executor.write_bytes((ROOT/"scripts/gate_d_outer.py").read_bytes())
    module=prefix/"staging/gate_d_preroot.py"; module.write_bytes((ROOT/"scripts/gate_d_preroot.py").read_bytes())
    archive=prefix/"staging/candidate.tar.gz"; archive.write_bytes(b"candidate\n")
    admin=prefix/"staging/admin.py"; admin.write_bytes(b"administrator\n")
    identity=prefix/"staging/qualification.json"; identity.write_bytes(b"identity\n")
    marker={"SPDX-License-Identifier":"MIT","schemaVersion":1,"kind":"gate-d-qualification-root-identity","rootPath":"/qualification/root","candidateRelease":"0.0.0-phase5.23","sourceCommit":"1"*40}
    marker_sha=hashlib.sha256((json.dumps(marker,sort_keys=True,separators=(",",":"))+"\n").encode()).hexdigest()
    payload=b"installed-executor\n"
    return {"SPDX-License-Identifier":"MIT","schemaVersion":1,"kind":"gate-d-pre-root-bootstrap-envelope","operationId":"phase5.23-pre-root","candidate":{"release":"0.0.0-phase5.23","sourceCommit":"1"*40,"archivePath":"/staging/candidate.tar.gz","archiveSha256":sha(archive)},"proposedRoot":{"path":"/qualification/root","ownerUid":os.getuid(),"mode":"0700","marker":marker,"markerSha256":marker_sha},"stagedExecutor":{"path":"/staging/gate_d_outer.py","sha256":sha(executor)},"preRootModule":{"path":"/staging/gate_d_preroot.py","sha256":sha(module)},"administrator":{"path":"/staging/admin.py","sha256":sha(admin)},"qualificationIdentity":{"path":"/staging/qualification.json","sha256":sha(identity)},"inputFiles":[{"path":"/staging/instance.json","sha256":sha(control)},{"path":"/staging/candidate.tar.gz","sha256":sha(archive)},{"path":"/staging/admin.py","sha256":sha(admin)},{"path":"/staging/qualification.json","sha256":sha(identity)}],"transitionFiles":[{"sourcePath":"/staging/instance.json","destination":"release/instance.json","sha256":sha(control),"mode":"0400"}],"installedTools":[{"path":"/installed/gate-d-executor","sha256":hashlib.sha256(payload).hexdigest()}],"argv":["/usr/bin/python3","/staging/admin.py","install","--execute","--qualification-install","--qualification-identity","/staging/qualification.json"],"cleanupArgv":["/usr/libexec/rp1-gpclk-dkms/gate-d-lifecycle","dispatch","complete-removal"],"recoveryArgv":["/usr/bin/python3","/staging/admin.py","recover","--execute"],"journal":"/staging/transaction.json","cleanupPaths":["/runtime/residue"],"deadlineSeconds":1800,"expectedPreState":baseline,"expectedPostState":baseline,"safety":safety}

with tempfile.TemporaryDirectory() as temporary:
    prefix=pathlib.Path(temporary).resolve(); envelope=make_envelope(prefix); installed=prefix/"installed/gate-d-executor"; payload=b"installed-executor\n"
    def runner(argv:list[str])->None:
        if argv==envelope["argv"]: installed.parent.mkdir(parents=True,exist_ok=True); installed.write_bytes(payload)
        elif argv==envelope["recoveryArgv"]: installed.unlink(missing_ok=True)
    assert tool.validate(envelope)["outputDisabled"] is True
    assert tool.execute(envelope,prefix=prefix,runner=runner,probe=lambda:baseline)["status"]=="complete"
    assert (prefix/"qualification/root/release/instance.json").read_text()=="{}\n"
    try: tool.execute(envelope,prefix=prefix,runner=runner,probe=lambda:baseline)
    except ValueError: pass
    else: raise AssertionError("pre-root replay accepted")
    for mutation in (lambda v:v["candidate"].update(archiveSha256="0"*63),lambda v:v["proposedRoot"].update(mode="0755"),lambda v:v["proposedRoot"]["marker"].update(candidateRelease="swapped"),lambda v:v["inputFiles"][0].update(sha256="4"*64),lambda v:v["transitionFiles"][0].update(destination="../escape"),lambda v:v["argv"].append("live_output=1")):
        bad=copy.deepcopy(envelope); mutation(bad)
        try: tool.validate(bad)
        except ValueError: pass
        else: raise AssertionError("unsafe pre-root envelope accepted")

for checkpoint in tool.CHECKPOINTS[1:-1]:
    with tempfile.TemporaryDirectory() as temporary:
        prefix=pathlib.Path(temporary).resolve(); envelope=make_envelope(prefix); installed=prefix/"installed/gate-d-executor"; payload=b"installed-executor\n"
        def runner(argv:list[str])->None:
            if argv==envelope["argv"]: installed.parent.mkdir(parents=True,exist_ok=True); installed.write_bytes(payload)
            elif argv==envelope["recoveryArgv"]: installed.unlink(missing_ok=True)
        try: tool.execute(envelope,prefix=prefix,runner=runner,probe=lambda:baseline,stop_after=checkpoint)
        except InterruptedError: pass
        else: raise AssertionError("checkpoint interruption absent")
        assert tool.execute(envelope,prefix=prefix,runner=runner,probe=lambda:baseline,recover=True)["status"]=="complete"

for failure in ("missing", "symlink", "substituted", "preexisting-root", "unsafe-parent", "installed-mismatch", "residue", "baseline"):
    with tempfile.TemporaryDirectory() as temporary:
        prefix=pathlib.Path(temporary).resolve(); envelope=make_envelope(prefix); installed=prefix/"installed/gate-d-executor"; payload=b"installed-executor\n"
        source=prefix/"staging/instance.json"
        if failure=="missing": source.unlink()
        elif failure=="symlink": source.unlink(); source.symlink_to(prefix/"staging/admin.py")
        elif failure=="substituted": source.write_text("changed\n")
        elif failure=="preexisting-root": (prefix/"qualification/root").mkdir()
        elif failure=="unsafe-parent": (prefix/"qualification").chmod(0o777)
        elif failure=="residue": residue=prefix/"runtime/residue"; residue.parent.mkdir(); residue.write_text("owned\n")
        def runner(argv:list[str])->None:
            if argv==envelope["argv"]:
                installed.parent.mkdir(parents=True,exist_ok=True)
                installed.write_bytes(b"wrong\n" if failure=="installed-mismatch" else payload)
            elif argv==envelope["recoveryArgv"]: installed.unlink(missing_ok=True)
        changed=dict(baseline); changed["moduleLoaded"]=True
        try: tool.execute(envelope,prefix=prefix,runner=runner,probe=lambda:changed if failure=="baseline" else baseline)
        except (ValueError, OSError): pass
        else: raise AssertionError(f"unsafe pre-root state accepted: {failure}")
print("Gate D pre-root trust transition: PASS")
