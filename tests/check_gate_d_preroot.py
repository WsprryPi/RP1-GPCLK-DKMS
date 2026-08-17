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
    archive=prefix/"staging/rp1-gpclk-dkms-0.0.0-phase5.49.tar.gz"; archive.write_bytes(b"candidate\n")
    sidecars={
        "gpio4Dtbo":prefix/"staging/rp1-gpclk-gpio4.dtbo",
        "gpio20Dtbo":prefix/"staging/rp1-gpclk-gpio20.dtbo",
        "compatibilityManifest":prefix/"staging/rp1-gpclk-compatibility-manifest.json",
        "provenance":prefix/"staging/PROVENANCE.json",
        "releaseMetadata":prefix/"staging/release-metadata.json",
    }
    for role,path in sidecars.items(): path.write_bytes((role+"\n").encode())
    checksums=prefix/"staging/SHA256SUMS"
    release_files={"archive":archive,**sidecars}
    checksums.write_text("".join(f"{sha(path)}  {path.name}\n" for path in sorted(release_files.values(),key=lambda p:p.name)))
    admin=prefix/"staging/admin.py"; admin.write_bytes(b"administrator\n")
    identity=prefix/"staging/qualification.json"; identity.write_bytes(b"identity\n")
    marker={"SPDX-License-Identifier":"MIT","schemaVersion":1,"kind":"gate-d-qualification-root-identity","rootPath":"/qualification/root","candidateRelease":"0.0.0-phase5.49","sourceCommit":"1"*40}
    marker_sha=hashlib.sha256((json.dumps(marker,sort_keys=True,separators=(",",":"))+"\n").encode()).hexdigest()
    payload=b"installed-executor\n"
    release_inputs=[{"role":role,"path":"/"+str(path.relative_to(prefix)),"sha256":sha(path)} for role,path in {**release_files,"checksums":checksums}.items()]
    inputs=[{"path":"/staging/instance.json","sha256":sha(control)},{"path":"/staging/admin.py","sha256":sha(admin)},{"path":"/staging/qualification.json","sha256":sha(identity)},*({"path":item["path"],"sha256":item["sha256"]} for item in release_inputs)]
    return {"SPDX-License-Identifier":"MIT","schemaVersion":2,"kind":"gate-d-pre-root-bootstrap-envelope","operationId":"phase5.25-pre-root","candidate":{"release":"0.0.0-phase5.49","sourceCommit":"1"*40,"archivePath":"/staging/rp1-gpclk-dkms-0.0.0-phase5.49.tar.gz","archiveSha256":sha(archive)},"proposedRoot":{"path":"/qualification/root","ownerUid":os.getuid(),"mode":"0700","marker":marker,"markerSha256":marker_sha},"stagedExecutor":{"path":"/staging/gate_d_outer.py","sha256":sha(executor)},"preRootModule":{"path":"/staging/gate_d_preroot.py","sha256":sha(module)},"administrator":{"path":"/staging/admin.py","sha256":sha(admin)},"qualificationIdentity":{"path":"/staging/qualification.json","sha256":sha(identity)},"inputFiles":inputs,"releaseInputs":release_inputs,"administratorState":{"path":"/admin-transaction.json","absenceBeforeInvocation":True,"recoveryPolicy":"invoke-only-for-real-owned-state"},"transitionFiles":[{"sourcePath":"/staging/instance.json","destination":"release/instance.json","sha256":sha(control),"mode":"0400"}],"installedTools":[{"path":"/installed/gate-d-executor","sha256":hashlib.sha256(payload).hexdigest()}],"argv":["/usr/bin/python3","/staging/admin.py","install","--execute","--qualification-install","--qualification-identity","/staging/qualification.json"],"cleanupArgv":["/usr/libexec/rp1-gpclk-dkms/gate-d-lifecycle","dispatch","complete-removal"],"recoveryArgv":["/usr/bin/python3","/staging/admin.py","recover","--execute"],"journal":"/staging/transaction.json","cleanupPaths":["/runtime/residue"],"deadlineSeconds":1800,"expectedPreState":baseline,"expectedPostState":baseline,"safety":safety}

with tempfile.TemporaryDirectory() as temporary:
    prefix=pathlib.Path(temporary).resolve(); envelope=make_envelope(prefix); installed=prefix/"installed/gate-d-executor"; payload=b"installed-executor\n"
    def runner(argv:list[str])->None:
        state=prefix/"admin-transaction.json"
        if argv==envelope["argv"]: installed.parent.mkdir(parents=True,exist_ok=True); installed.write_bytes(payload); state.write_text('{"status":"complete"}\n')
        elif argv==envelope["cleanupArgv"]: state.unlink(missing_ok=True)
        elif argv==envelope["recoveryArgv"]: installed.unlink(missing_ok=True); state.unlink(missing_ok=True)
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
            state=prefix/"admin-transaction.json"
            if argv==envelope["argv"]: installed.parent.mkdir(parents=True,exist_ok=True); installed.write_bytes(payload); state.write_text('{"status":"complete"}\n')
            elif argv==envelope["cleanupArgv"]: state.unlink(missing_ok=True)
            elif argv==envelope["recoveryArgv"]: installed.unlink(missing_ok=True); state.unlink(missing_ok=True)
        try: tool.execute(envelope,prefix=prefix,runner=runner,probe=lambda:baseline,stop_after=checkpoint)
        except InterruptedError: pass
        else: raise AssertionError("checkpoint interruption absent")
        assert tool.execute(envelope,prefix=prefix,runner=runner,probe=lambda:baseline,recover=True)["status"]=="recovered"
        preserved=prefix/"staging/transaction.failure.json"
        assert preserved.is_file() and not preserved.is_symlink()
        assert json.loads(preserved.read_text())["status"]=="recovery-required"
        assert not (prefix/"qualification/root").exists()

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
            state=prefix/"admin-transaction.json"
            if argv==envelope["argv"]:
                installed.parent.mkdir(parents=True,exist_ok=True)
                installed.write_bytes(b"wrong\n" if failure=="installed-mismatch" else payload)
                state.write_text('{"status":"complete"}\n')
            elif argv==envelope["cleanupArgv"]: state.unlink(missing_ok=True)
            elif argv==envelope["recoveryArgv"]: installed.unlink(missing_ok=True); state.unlink(missing_ok=True)
        changed=dict(baseline); changed["moduleLoaded"]=True
        try: tool.execute(envelope,prefix=prefix,runner=runner,probe=lambda:changed if failure=="baseline" else baseline)
        except (ValueError, OSError): pass
        else: raise AssertionError(f"unsafe pre-root state accepted: {failure}")

for failure in ("missing-sidecar", "swapped-sidecar", "stale-checksums", "symlink-sidecar", "duplicate-role", "wrong-directory"):
    with tempfile.TemporaryDirectory() as temporary:
        prefix=pathlib.Path(temporary).resolve(); envelope=make_envelope(prefix)
        sidecar=prefix/envelope["releaseInputs"][1]["path"].lstrip("/")
        if failure=="missing-sidecar": sidecar.unlink()
        elif failure=="swapped-sidecar": sidecar.write_bytes(b"substituted\n")
        elif failure=="stale-checksums": (prefix/"staging/SHA256SUMS").write_text("0"*64+"  stale\n")
        elif failure=="symlink-sidecar": sidecar.unlink(); sidecar.symlink_to(prefix/"staging/PROVENANCE.json")
        elif failure=="duplicate-role": envelope["releaseInputs"][1]["role"]="archive"
        elif failure=="wrong-directory": envelope["releaseInputs"][1]["path"]="/other/rp1-gpclk-gpio4.dtbo"
        try: tool.execute(envelope,prefix=prefix,runner=lambda argv:None,probe=lambda:baseline)
        except (ValueError,OSError): pass
        else: raise AssertionError(f"unsafe release-input graph accepted: {failure}")

with tempfile.TemporaryDirectory() as temporary:
    prefix=pathlib.Path(temporary).resolve(); envelope=make_envelope(prefix); installed=prefix/"installed/gate-d-executor"; calls=[]
    def fail_before_state_once(argv:list[str])->None:
        calls.append(argv)
        if argv==envelope["argv"]:
            count=sum(item==envelope["argv"] for item in calls)
            if count==1: raise RuntimeError("before administrator state")
            installed.parent.mkdir(parents=True,exist_ok=True); installed.write_bytes(b"installed-executor\n")
            (prefix/"admin-transaction.json").write_text('{"status":"complete"}\n')
        elif argv==envelope["cleanupArgv"]: (prefix/"admin-transaction.json").unlink(missing_ok=True)
    try: tool.execute(envelope,prefix=prefix,runner=fail_before_state_once,probe=lambda:baseline)
    except RuntimeError: pass
    else: raise AssertionError("pre-state administrator failure absent")
    assert tool.execute(envelope,prefix=prefix,runner=fail_before_state_once,probe=lambda:baseline,recover=True)["status"]=="recovered"
    assert envelope["recoveryArgv"] not in calls
    assert calls.count(envelope["argv"])==1

with tempfile.TemporaryDirectory() as temporary:
    prefix=pathlib.Path(temporary).resolve(); envelope=make_envelope(prefix); calls=[]
    try: tool.execute(envelope,prefix=prefix,runner=lambda argv:calls.append(argv),probe=lambda:baseline,stop_after="create-root")
    except InterruptedError: pass
    else: raise AssertionError("partial-root interruption absent")
    marker=prefix/"qualification/root/.gate-d-root.json"; foreign=marker.parent/"foreign"; foreign.write_text("preserve\n")
    try: tool.execute(envelope,prefix=prefix,runner=lambda argv:calls.append(argv),probe=lambda:baseline,recover=True)
    except ValueError: pass
    else: raise AssertionError("foreign partial-root recovery accepted")
    assert marker.is_file() and foreign.read_text()=="preserve\n" and envelope["recoveryArgv"] not in calls

with tempfile.TemporaryDirectory() as temporary:
    prefix=pathlib.Path(temporary).resolve(); envelope=make_envelope(prefix); installed=prefix/"installed/gate-d-executor"; calls=[]
    def recover_then_changed(argv:list[str])->None:
        calls.append(argv); state=prefix/"admin-transaction.json"
        if argv==envelope["argv"]:
            installed.parent.mkdir(parents=True,exist_ok=True); installed.write_bytes(b"installed-executor\n"); state.write_text('{"status":"complete"}\n')
        elif argv==envelope["recoveryArgv"]:
            installed.unlink(); state.unlink()
    try: tool.execute(envelope,prefix=prefix,runner=recover_then_changed,probe=lambda:baseline,stop_after="install")
    except InterruptedError: pass
    else: raise AssertionError("install interruption absent")
    changed=dict(baseline); changed["moduleLoaded"]=True
    try: tool.execute(envelope,prefix=prefix,runner=recover_then_changed,probe=lambda:changed,recover=True)
    except ValueError as error: assert "post-recovery" in str(error)
    else: raise AssertionError("changed post-recovery baseline accepted")
    assert calls.count(envelope["argv"])==1 and calls.count(envelope["recoveryArgv"])==1
    assert (prefix/"staging/transaction.json").is_file()
    assert not (prefix/"staging/transaction.failure.json").exists()

def add_prior_terminal_state(prefix:pathlib.Path,envelope:dict)->tuple[pathlib.Path,pathlib.Path,bytes]:
    state=prefix/"admin-transaction.json"
    payload=(json.dumps({"status":"recovered","recoveryRequired":False,"liveOutput":False},sort_keys=True)+"\n").encode()
    state.write_bytes(payload); state.chmod(0o600)
    envelope["schemaVersion"]=3
    envelope["priorTerminalState"]={
        "path":"/admin-transaction.json","sha256":hashlib.sha256(payload).hexdigest(),
        "status":"recovered","recoveryRequired":False,"liveOutput":False,
        "ownerUid":os.getuid(),"mode":"0600","archivePath":"/history/prior-recovered.json",
        "archiveMode":"0400",
    }
    return state,prefix/"history/prior-recovered.json",payload

with tempfile.TemporaryDirectory() as temporary:
    prefix=pathlib.Path(temporary).resolve(); envelope=make_envelope(prefix)
    state,archive,payload=add_prior_terminal_state(prefix,envelope)
    installed=prefix/"installed/gate-d-executor"
    def archival_runner(argv:list[str])->None:
        if argv==envelope["argv"]:
            assert not state.exists() and archive.read_bytes()==payload
            installed.parent.mkdir(parents=True,exist_ok=True); installed.write_bytes(b"installed-executor\n")
            state.write_text('{"status":"complete"}\n')
        elif argv==envelope["cleanupArgv"]: state.unlink()
    assert tool.validate(envelope)["outputDisabled"] is True
    assert tool.execute(envelope,prefix=prefix,runner=archival_runner,probe=lambda:baseline)["status"]=="complete"
    assert not state.exists() and archive.read_bytes()==payload
    assert archive.stat().st_mode & 0o777==0o400

with tempfile.TemporaryDirectory() as temporary:
    prefix=pathlib.Path(temporary).resolve(); envelope=make_envelope(prefix)
    state,archive,payload=add_prior_terminal_state(prefix,envelope)
    try: tool.execute(envelope,prefix=prefix,runner=lambda argv:None,probe=lambda:baseline,stop_after="archive-prior-state")
    except InterruptedError: pass
    else: raise AssertionError("prior-ledger archive interruption absent")
    assert not state.exists() and archive.read_bytes()==payload
    assert tool.execute(envelope,prefix=prefix,runner=lambda argv:None,probe=lambda:baseline,recover=True)["status"]=="recovered"
    assert state.read_bytes()==payload and state.stat().st_mode & 0o777==0o600
    assert not archive.exists()

with tempfile.TemporaryDirectory() as temporary:
    prefix=pathlib.Path(temporary).resolve(); envelope=make_envelope(prefix)
    state,archive,payload=add_prior_terminal_state(prefix,envelope)
    def fail_before_new_state(argv:list[str])->None:
        if argv==envelope["argv"]: raise RuntimeError("administrator invoked without state")
    try: tool.execute(envelope,prefix=prefix,runner=fail_before_new_state,probe=lambda:baseline)
    except RuntimeError: pass
    else: raise AssertionError("administrator pre-state failure absent")
    try: tool.execute(envelope,prefix=prefix,runner=fail_before_new_state,probe=lambda:baseline,recover=True)
    except ValueError as error: assert "no recoverable transaction state" in str(error)
    else: raise AssertionError("ambiguous invoked-administrator recovery accepted")
    assert not state.exists() and archive.read_bytes()==payload

for failure in ("tampered","nonterminal","wrong-mode","symlink","archive-exists","unsafe-archive-directory"):
    with tempfile.TemporaryDirectory() as temporary:
        prefix=pathlib.Path(temporary).resolve(); envelope=make_envelope(prefix)
        state,archive,payload=add_prior_terminal_state(prefix,envelope)
        if failure=="tampered": state.write_bytes(b"substituted\n")
        elif failure=="nonterminal":
            payload=b'{"liveOutput":false,"recoveryRequired":true,"status":"inactive-recovery-required"}\n'
            state.write_bytes(payload); envelope["priorTerminalState"]["sha256"]=hashlib.sha256(payload).hexdigest()
        elif failure=="wrong-mode": state.chmod(0o644)
        elif failure=="symlink": state.unlink(); state.symlink_to(prefix/"staging/admin.py")
        elif failure=="archive-exists": archive.parent.mkdir(); archive.write_bytes(b"foreign\n")
        elif failure=="unsafe-archive-directory": archive.parent.mkdir(mode=0o755)
        try: tool.execute(envelope,prefix=prefix,runner=lambda argv:None,probe=lambda:baseline)
        except (ValueError,OSError): pass
        else: raise AssertionError(f"unsafe prior terminal state accepted: {failure}")

with tempfile.TemporaryDirectory() as temporary:
    prefix=pathlib.Path(temporary).resolve(); envelope=make_envelope(prefix)
    add_prior_terminal_state(prefix,envelope)
    envelope["priorTerminalState"]["archivePath"]="/history/../escape"
    try: tool.validate(envelope)
    except ValueError: pass
    else: raise AssertionError("unsafe prior terminal archive path accepted")
with tempfile.TemporaryDirectory() as temporary:
    typed_prefix=pathlib.Path(temporary); regular=typed_prefix/"tool"; regular.write_bytes(b"tool\n"); regular.chmod(0o644)
    link=typed_prefix/"command"; link.symlink_to("tool")
    records=[{"path":"/tool","type":"file","sha256":sha(regular),"mode":"0644","ownerUid":regular.stat().st_uid,"groupGid":regular.stat().st_gid},{"path":"/command","type":"symlink","target":"tool","mode":f"{link.lstat().st_mode & 0o777:04o}","ownerUid":link.lstat().st_uid,"groupGid":link.lstat().st_gid}]
    assert tool.validate_package_paths(records)==records
    assert tool.package_paths_digest(records)==hashlib.sha256((json.dumps(records,sort_keys=True,separators=(",",":"))+"\n").encode()).hexdigest()
    for item in records: tool.verify_package_path(typed_prefix,item)
    for mutation in (lambda v:v.append(dict(v[0])),lambda v:v[0].update(sha256="0"*64),lambda v:v[1].update(target="wrong"),lambda v:v[1].update(mode="0644")):
        bad=copy.deepcopy(records); mutation(bad)
        try:
            tool.validate_package_paths(bad)
            for item in bad: tool.verify_package_path(typed_prefix,item)
        except (ValueError,KeyError): pass
        else: raise AssertionError("unsafe typed pre-root package inventory accepted")
print("Gate D pre-root trust transition: PASS")
