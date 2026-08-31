#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Hardware-free source-development workflow contract tests."""

import bz2, gzip, importlib.util, json, lzma, os, pathlib, platform, shutil, subprocess, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("development_workflow", ROOT / "scripts/development_workflow.py")
DEV = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(DEV)


def command(*args, cwd=None, env=None):
    return subprocess.run(args, cwd=cwd, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)


def fixture_repo(base: pathlib.Path) -> pathlib.Path:
    source = base / "source"; shutil.copytree(ROOT, source, ignore=shutil.ignore_patterns(".git", "__pycache__"))
    command("git", "init", "-q", cwd=source); command("git", "config", "user.email", "test@example.invalid", cwd=source)
    command("git", "config", "user.name", "test", cwd=source); command("git", "add", ".", cwd=source)
    assert command("git", "commit", "-qm", "fixture", cwd=source).returncode == 0
    return source


def test_render() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        base = pathlib.Path(temporary); source = fixture_repo(base); output = base / "rendered"
        result = command(str(source / "scripts/render-development-tree"), "--source", str(source), "--output", str(output), "--module-version", "0.9.0", cwd=source)
        assert result.returncode == 0, result.stderr
        manifest = json.loads((output / "DEVELOPMENT_MANIFEST.json").read_text())
        assert manifest["classification"] == "source-development" and manifest["qualification"] is False
        assert manifest["moduleName"] == "rp1_gpclk_dkms"
        assert [item["operation"] for item in manifest["transformations"]] == ["replace-module-version-placeholder","relax-development-kernel-name-filter"]
        assert manifest["changedFiles"] == ["dkms.conf"]
        assert 'PACKAGE_VERSION="0.9.0"' in (output / "dkms.conf").read_text()
        assert 'BUILD_EXCLUSIVE_KERNEL=".*"' in (output / "dkms.conf").read_text()
        assert 'PACKAGE_VERSION="#MODULE_VERSION#"' not in (output / "dkms.conf").read_text()
        assert not (source / "DEVELOPMENT_MANIFEST.json").exists()
        again = command(str(source / "scripts/render-development-tree"), "--source", str(source), "--output", str(output), "--module-version", "0.9.0", cwd=source)
        assert again.returncode == 2 and "already exists" in again.stderr
        (source / "README.md").write_text((source / "README.md").read_text() + "\ndirty\n")
        rejected = command(str(source / "scripts/render-development-tree"), "--source", str(source), "--output", str(base / "dirty"), "--module-version", "0.9.0", cwd=source)
        assert rejected.returncode == 2 and "dirty" in rejected.stderr
        allowed = command(str(source / "scripts/render-development-tree"), "--source", str(source), "--output", str(base / "allowed"), "--module-version", "0.9.0", "--allow-dirty", cwd=source)
        assert allowed.returncode == 0 and json.loads((base / "allowed/DEVELOPMENT_MANIFEST.json").read_text())["sourceState"] == "dirty-explicitly-allowed"


def test_forbidden_transform() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        base = pathlib.Path(temporary); source = fixture_repo(base)
        (source / "README.md").write_text((source / "README.md").read_text() + '\nPACKAGE_VERSION="#OTHER_VERSION#"\n')
        command("git", "add", "README.md", cwd=source); command("git", "commit", "-qm", "forbidden", cwd=source)
        result = command(str(source / "scripts/render-development-tree"), "--source", str(source), "--output", str(base / "output"), "--module-version", "0.9.0", cwd=source)
        assert result.returncode == 2 and "unresolved" in result.stderr and not (base / "output").exists()


def test_compression() -> None:
    elf = b"\x7fELF" + bytes(range(256))
    with tempfile.TemporaryDirectory() as temporary:
        base = pathlib.Path(temporary)
        variants = {"module.ko": elf, "module.ko.xz": lzma.compress(elf), "module.ko.gz": gzip.compress(elf), "module.ko.bz2": bz2.compress(elf)}
        for name, payload in variants.items():
            path = base / name; path.write_bytes(payload)
            assert DEV.decompressed(path) == elf
            assert DEV.sha256_bytes(DEV.decompressed(path)) == DEV.sha256_bytes(elf)
    assert DEV.CANONICAL_MODULE == "rp1_gpclk_dkms" and DEV.CANONICAL_MODULE != "rp1_gpclk"


def test_false_qualification_and_cli() -> None:
    source = (ROOT / "scripts/development_workflow.py").read_text()
    assert '"releaseQualified": False' in source and '"classification": "Experimental"' in source
    for script in ("development-preflight", "development-install", "development-enroll", "development-module",
                   "development-status", "development-endpoint", "development-route", "development-overlay", "development-rollback"):
        result = command(str(ROOT / "scripts" / script), "--help")
        assert result.returncode == 0, (script, result.stderr)


def executable(path: pathlib.Path, body: str) -> None:
    path.write_text("#!/bin/sh\nset -eu\n" + body); path.chmod(0o755)


def test_controlled_lifecycle() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        base=pathlib.Path(temporary); source=fixture_repo(base); fake_root=base/"root"; tools=base/"tools"; tools.mkdir()
        kernel=platform.release(); (fake_root/f"lib/modules/{kernel}/build").mkdir(parents=True)
        executable(tools/"dkms", '''
case "$1" in
 install) mkdir -p "$RP1_GPCLK_DEVELOPMENT_ROOT/lib/modules/$7/updates/dkms"; printf '\\177ELFfake-development-module' >"$RP1_GPCLK_DEVELOPMENT_ROOT/lib/modules/$7/updates/dkms/rp1_gpclk_dkms.ko" ;;
 remove) rm -f "$RP1_GPCLK_DEVELOPMENT_ROOT/lib/modules/$RP1_TEST_KERNEL/updates/dkms/rp1_gpclk_dkms.ko" ;;
 status) [ -d "$RP1_GPCLK_DEVELOPMENT_ROOT/usr/src/rp1-gpclk-dkms-0.9.0" ] || exit 0; printf 'rp1-gpclk-dkms/0.9.0, %s, installed\\n' "$RP1_TEST_KERNEL" ;;
esac
''')
        executable(tools/"modinfo", '''
field=$2
case "$field" in name) echo rp1_gpclk_dkms;; version) echo 0.9.0;; vermagic) echo "$RP1_TEST_KERNEL SMP mod_unload aarch64";; signer|sig_key|sig_hashalgo) :;; esac
''')
        executable(tools/"depmod", ":\n")
        executable(tools/"modprobe", '''
if [ "${1:-}" = -r ]; then rm -rf "$RP1_GPCLK_DEVELOPMENT_ROOT/sys/module/rp1_gpclk_dkms"; exit 0; fi
mkdir -p "$RP1_GPCLK_DEVELOPMENT_ROOT/sys/module/rp1_gpclk_dkms/parameters"
echo 0.9.0 >"$RP1_GPCLK_DEVELOPMENT_ROOT/sys/module/rp1_gpclk_dkms/version"
case "$2" in live_output=1) echo Y;; *) echo N;; esac >"$RP1_GPCLK_DEVELOPMENT_ROOT/sys/module/rp1_gpclk_dkms/parameters/live_output"
''')
        environment={**os.environ,"RP1_GPCLK_DEVELOPMENT_ROOT":str(fake_root),"RP1_GPCLK_DEVELOPMENT_TEST_ROOT":"1","RP1_TEST_KERNEL":kernel,
            "RP1_GPCLK_TOOL_DKMS":str(tools/"dkms"),"RP1_GPCLK_TOOL_MODINFO":str(tools/"modinfo"),
            "RP1_GPCLK_TOOL_DEPMOD":str(tools/"depmod"),"RP1_GPCLK_TOOL_MODPROBE":str(tools/"modprobe")}
        evidence=base/"evidence"
        result=command(str(source/"scripts/development-install"),"--source",str(source),"--kernel",kernel,"--module-version","0.9.0","--route","gpio4","--live-output","0","--load","--evidence-directory",str(evidence),cwd=source,env=environment)
        assert result.returncode==0,result.stderr
        manifest=evidence/"rendered-source/DEVELOPMENT_MANIFEST.json"; value=json.loads(manifest.read_text())
        assert value["developmentState"]=="development-loaded" and value["installedModule"]["moduleName"]=="rp1_gpclk_dkms"
        replacement=base/"replacement-evidence"
        replaced=command(str(source/"scripts/development-install"),"--source",str(source),"--kernel",kernel,"--module-version","0.9.0","--route","gpio4","--live-output","0","--load","--evidence-directory",str(replacement),cwd=source,env=environment)
        assert replaced.returncode==0,replaced.stderr
        assert (replacement/"dkms-remove.log").is_file() and (replacement/"module-unload-for-replace.log").is_file()
        backup = json.loads((replacement/"ROLLBACK.json").read_text())
        assert (pathlib.Path(backup["priorSource"])/"DEVELOPMENT_MANIFEST.json").is_file()
        for item in backup["prior"]["installedArtifacts"]:
            assert DEV.sha256(pathlib.Path(item["backup"])) == item["sha256"]
        stale=command(str(source/"scripts/development-rollback"),"--record",str(evidence/"ROLLBACK.json"),env=environment)
        assert stale.returncode==2 and "another instance" in stale.stderr
        assert (fake_root/"sys/module/rp1_gpclk_dkms").exists()
        manifest=replacement/"rendered-source/DEVELOPMENT_MANIFEST.json"
        assert (replacement.stat().st_mode & 0o777)==0o755
        status=command(str(source/"scripts/development-status"),"--manifest",str(manifest),"--json",env=environment)
        assert status.returncode==0 and json.loads(status.stdout)["developmentState"]=="development-loaded"
        enrolled=command(str(source/"scripts/development-enroll"),"--manifest",str(manifest),"--route","gpio4","--kernel",kernel,env=environment)
        assert enrolled.returncode==0,enrolled.stderr
        enrollment=json.loads(enrolled.stdout)
        assert enrollment["record"]["moduleVersion"]=="0.9.0" and enrollment["record"]["qualification"] is False
        removed=command(str(source/"scripts/development-enroll"),"--remove","--manifest",str(manifest),"--route","gpio4","--kernel",kernel,env=environment)
        assert removed.returncode==0,removed.stderr
        unloaded=command(str(source/"scripts/development-module"),"unload","--manifest",str(manifest),env=environment)
        assert unloaded.returncode==0,unloaded.stderr
        rolled=command(str(source/"scripts/development-rollback"),"--record",str(replacement/"ROLLBACK.json"),env=environment)
        assert rolled.returncode==0,rolled.stderr
        assert not (fake_root/f"usr/src/rp1-gpclk-dkms-0.9.0").exists()


def main() -> None:
    test_render(); test_forbidden_transform(); test_compression(); test_false_qualification_and_cli(); test_controlled_lifecycle()
    print("development workflow checks passed")


if __name__ == "__main__": main()
