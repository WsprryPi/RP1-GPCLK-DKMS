#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Exact 1.1.1 output-inhibited package and boot-route transaction executor."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tempfile
from typing import Callable

PACKAGE = "rp1-gpclk-dkms"
MODULE = "rp1_gpclk_dkms"
VERSION = "1.1.1"
DEBIAN_VERSION = "1.1.1-1"
HOST = "wspr5"
ARCH = "aarch64"
KERNEL = "6.18.34+rpt-rpi-2712"
FIRMWARE = "69471177"
BASE_DTB_SHA256 = "e67017e5d45b97af478ebc93d651a086f2adcb6a650fe453eb9f1cf47e66473f"
KERNEL_CONFIG_SHA256 = "2a83d4324e9b47d418b4efac18d3af43d15cc956b71c5a8eb074060bf8383801"
PACKAGE_SHA256 = "48d55aa9a906e83b36ed46560c81cd894024bc2d6bf375514b5e1618a43493af"
UAPI_SHA256 = "998ab96d7dbcc0d935c05758c46acba56bbcf92aa1b674b899bdab6932dc8384"
GPIO4_DTBO_SHA256 = "c3e17a685694928468bb18c24f5bb4e25454745d6989e6c9d2c2acf447b908d6"
GPIO20_DTBO_SHA256 = "8eaa8afae7f88a665fc9bec6da1b013be049b2a32c909c729caeff9181bcf3aa"
PREDECESSOR_VERSION = "1.0.1-1"
PREDECESSOR_CONFIG_SHA256 = "8135eb26a52046d042c5f84583cad20d3f519c3753010a5afff063077dcf48f4"
CONFIG = "/boot/firmware/config.txt"
BOOT_ID = "/proc/sys/kernel/random/boot_id"
JOURNAL_DIR = "/var/lib/rp1-gpclk-dkms/route-transactions"
BEGIN = "# BEGIN RP1-GPCLK-DKMS OWNED ROUTE"
END = "# END RP1-GPCLK-DKMS OWNED ROUTE"
LEGACY_BLOCK = (
    "\n\n# RP1-GPCLK-DKMS 1.0.1 GPIO4 clock-disabled validation\n"
    "dtoverlay=rp1-gpclk-gpio4\n"
)
ROUTES = {"gpio4": (1, 4, GPIO4_DTBO_SHA256),
          "gpio20": (2, 20, GPIO20_DTBO_SHA256)}
HEX64 = re.compile(r"[0-9a-f]{64}")
HEX40 = re.compile(r"[0-9a-f]{40}")
OPERATION = re.compile(r"[a-z0-9][a-z0-9-]{7,63}")
Runner = Callable[[list[str]], str]


def digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def digest(path: Path) -> str:
    return digest_bytes(path.read_bytes())


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def rooted(root: Path, absolute: str) -> Path:
    pure = PurePosixPath(absolute)
    if not pure.is_absolute() or ".." in pure.parts:
        raise ValueError("unsafe absolute path")
    result = root / str(pure).lstrip("/")
    current = root
    for part in pure.parts[1:]:
        current = current / part
        if current.is_symlink():
            raise ValueError(f"symlink path rejected: {absolute}")
    return result


def atomic_write(path: Path, payload: bytes, mode: int) -> None:
    path.parent.mkdir(parents=True, mode=0o700, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        os.fchmod(fd, mode)
        with os.fdopen(fd, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass


def load_plan(path: Path) -> dict:
    if path.is_symlink() or not path.is_file():
        raise ValueError("plan is absent or unsafe")
    value = json.loads(path.read_text())
    expected = {
        "schemaVersion", "kind", "operationId", "host", "architecture",
        "kernel", "firmware", "baseDtbSha256", "kernelConfigSha256",
        "sourceCommit", "package", "packageSha256", "qualificationArchiveSha256",
        "uapiSha256", "gpio4DtboSha256", "gpio20DtboSha256",
        "compatibilitySha256", "productInventorySha256", "predecessorVersion",
        "predecessorConfigSha256", "signingPolicy", "physicalTopology",
        "servicePolicy", "planSha256",
    }
    if set(value) != expected:
        raise ValueError("plan fields are incomplete or unknown")
    claimed = value.pop("planSha256")
    if not HEX64.fullmatch(str(claimed)) or digest_bytes(canonical(value)) != claimed:
        raise ValueError("plan digest differs")
    value["planSha256"] = claimed
    fixed = {
        "schemaVersion": 1, "kind": "rp1-gpclk-1.1.1-route-transaction",
        "host": HOST, "architecture": ARCH, "kernel": KERNEL,
        "firmware": FIRMWARE, "baseDtbSha256": BASE_DTB_SHA256,
        "kernelConfigSha256": KERNEL_CONFIG_SHA256,
        "package": f"{PACKAGE}_{DEBIAN_VERSION}_all.deb",
        "packageSha256": PACKAGE_SHA256, "uapiSha256": UAPI_SHA256,
        "gpio4DtboSha256": GPIO4_DTBO_SHA256,
        "gpio20DtboSha256": GPIO20_DTBO_SHA256,
        "predecessorVersion": PREDECESSOR_VERSION,
        "predecessorConfigSha256": PREDECESSOR_CONFIG_SHA256,
        "signingPolicy": "CONFIG_MODULE_SIG=n; unsigned candidate",
        "physicalTopology": "fresh-operator-confirmation-required",
        "servicePolicy": {"wsprrypi.service": "inactive",
                          "soapyremote-server.service": "inactive"},
    }
    for key, expected_value in fixed.items():
        if value.get(key) != expected_value:
            raise ValueError(f"plan identity differs: {key}")
    if not OPERATION.fullmatch(str(value["operationId"])):
        raise ValueError("operation ID is invalid")
    if not HEX40.fullmatch(str(value["sourceCommit"])):
        raise ValueError("invalid source commit")
    for key in ("qualificationArchiveSha256", "compatibilitySha256",
                "productInventorySha256"):
        if not HEX64.fullmatch(str(value[key])):
            raise ValueError(f"invalid hash: {key}")
    return value


def run_command(argv: list[str]) -> str:
    return subprocess.run(argv, check=True, text=True, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT).stdout


def journal_path(root: Path, operation: str) -> Path:
    return rooted(root, f"{JOURNAL_DIR}/{operation}.json")


def journal_write(path: Path, state: dict) -> None:
    atomic_write(path, json.dumps(state, indent=2, sort_keys=True).encode() + b"\n", 0o600)


def read_boot_id(root: Path) -> str:
    value = rooted(root, BOOT_ID).read_text().strip()
    if not re.fullmatch(r"[0-9a-f-]{36}", value):
        raise ValueError("boot ID is malformed")
    return value


def parse_config(payload: bytes) -> str | None:
    text = payload.decode()
    if text.count(BEGIN) != text.count(END) or text.count(BEGIN) > 1:
        raise ValueError("owned route markers are malformed or duplicated")
    routes = re.findall(r"^dtoverlay=rp1-gpclk-(gpio4|gpio20)\s*$", text, re.M)
    if len(routes) > 1:
        raise ValueError("multiple RP1 GPCLK routes are selected")
    if BEGIN in text:
        block = text[text.index(BEGIN):text.index(END) + len(END)]
        block_routes = re.findall(r"^dtoverlay=rp1-gpclk-(gpio4|gpio20)\s*$", block, re.M)
        if len(block_routes) != 1 or routes != block_routes:
            raise ValueError("route exists outside the owned block")
        return block_routes[0]
    if routes:
        if payload.endswith(LEGACY_BLOCK.encode()) and routes == ["gpio4"]:
            return "legacy-gpio4"
        raise ValueError("foreign RP1 GPCLK route selection")
    return None


def system_safety(plan: dict, root: Path, runner: Runner) -> dict:
    dtb = rooted(root, "/boot/firmware/bcm2712-rpi-5-b.dtb")
    kernel_config = rooted(root, f"/usr/src/linux-headers-{KERNEL}/.config")
    if root == Path("/"):
        if not dtb.is_file() or digest(dtb) != plan["baseDtbSha256"]:
            raise ValueError("base DTB identity differs")
        if not kernel_config.is_file() or digest(kernel_config) != plan["kernelConfigSha256"]:
            raise ValueError("kernel configuration identity differs")
        firmware = runner(["/usr/bin/vcgencmd", "version"])
        if plan["firmware"] not in firmware:
            raise ValueError("firmware identity differs")
        states = runner(["/usr/bin/systemctl", "show", "--property=ActiveState",
                         "--value", *plan["servicePolicy"]]).splitlines()
        if states != [plan["servicePolicy"][name] for name in plan["servicePolicy"]]:
            raise ValueError("service policy differs")
        live = Path("/sys/module/rp1_gpclk_dkms/parameters/live_output")
        if live.exists() and live.read_text().strip() not in {"N", "0"}:
            raise ValueError("live output is enabled or unknown")
        summary = Path("/sys/kernel/debug/clk/clk_summary")
        if summary.is_file():
            rows = [line.split() for line in summary.read_text().splitlines()
                    if line.split() and line.split()[0] == "clk_gp0"]
            if len(rows) != 1 or len(rows[0]) < 3 or rows[0][1:3] != ["0", "0"]:
                raise ValueError("GPCLK0 is prepared or enabled")
        endpoint = Path("/dev/rp1-gpclk")
        if endpoint.exists():
            endpoint_stat = endpoint.stat()
            for fd in Path("/proc").glob("[0-9]*/fd/*"):
                try:
                    target = fd.stat()
                except OSError:
                    continue
                if (target.st_dev, target.st_ino) == (endpoint_stat.st_dev, endpoint_stat.st_ino):
                    raise ValueError("endpoint has an open file descriptor")
        for pin in (4, 20):
            line = runner(["/usr/bin/pinctrl", "get", str(pin)]).strip()
            if not re.search(rf"^{pin}:\s+(ip|no)\b", line):
                raise ValueError(f"GPIO{pin} is not in a safe non-output state")
    return {"liveOutput": False, "endpointOpen": False,
            "clockPrepared": False, "clockEnabled": False,
            "gpio4Safe": True, "gpio20Safe": True}


def config_for_route(payload: bytes, route: str) -> bytes:
    current = parse_config(payload)
    if current == "legacy-gpio4":
        payload = payload[:-len(LEGACY_BLOCK.encode())]
    elif current in ROUTES:
        text = payload.decode()
        start = text.index(BEGIN)
        finish = text.index(END) + len(END)
        payload = (text[:start].rstrip() + "\n").encode()
    block = f"\n{BEGIN}\n# version={VERSION} route={route}\ndtoverlay=rp1-gpclk-{route}\n{END}\n"
    return payload.rstrip() + block.encode()


def config_inactive(payload: bytes) -> bytes:
    current = parse_config(payload)
    if current == "legacy-gpio4":
        return payload[:-len(LEGACY_BLOCK.encode())].rstrip() + b"\n"
    if current in ROUTES:
        text = payload.decode()
        return (text[:text.index(BEGIN)].rstrip() + "\n").encode()
    return payload


def preflight(plan: dict, root: Path, runner: Runner = run_command) -> dict:
    if runner(["/bin/hostname"]).strip() != plan["host"]:
        raise ValueError("host identity differs")
    if runner(["/usr/bin/uname", "-m"]).strip() != plan["architecture"]:
        raise ValueError("architecture differs")
    if runner(["/usr/bin/uname", "-r"]).strip() != plan["kernel"]:
        raise ValueError("kernel differs")
    config = rooted(root, CONFIG)
    if config.is_symlink() or not config.is_file():
        raise ValueError("boot configuration is absent or unsafe")
    route = parse_config(config.read_bytes())
    safety = system_safety(plan, root, runner)
    return {"status": "ready", "route": route, "bootId": read_boot_id(root),
            "configSha256": digest(config), "planSha256": plan["planSha256"],
            "safety": safety}


def begin(plan: dict, root: Path, action: str, route: str | None,
          runner: Runner) -> tuple[Path, dict, bytes]:
    path = journal_path(root, plan["operationId"])
    if path.exists() or path.is_symlink():
        raise ValueError("operation journal already exists")
    observed = preflight(plan, root, runner)
    config = rooted(root, CONFIG)
    before = config.read_bytes()
    state = {"schemaVersion": 1, "operationId": plan["operationId"],
             "planSha256": plan["planSha256"], "action": action,
             "sourceCommit": plan["sourceCommit"],
             "qualificationArchiveSha256": plan["qualificationArchiveSha256"],
             "route": route, "status": "prepared", "checkpoint": "journal-created",
             "bootIdBefore": observed["bootId"], "configBeforeSha256": digest_bytes(before),
             "configBefore": before.decode(), "configAfterSha256": None,
             "rebootRequired": False, "reconciled": False}
    journal_write(path, state)
    return path, state, before


def mutate_config(plan: dict, root: Path, action: str, route: str | None,
                  execute: bool, runner: Runner = run_command) -> dict:
    if not execute or os.geteuid() != 0:
        raise ValueError("mutation requires root and --execute")
    path, state, before = begin(plan, root, action, route, runner)
    after = config_inactive(before) if route is None else config_for_route(before, route)
    if after == before:
        raise ValueError("transaction would not change boot configuration")
    config = rooted(root, CONFIG)
    atomic_write(config, after, config.stat().st_mode & 0o777)
    if config.read_bytes() != after:
        raise RuntimeError("boot configuration readback differs")
    state.update({"status": "awaiting-reboot", "checkpoint": "config-committed",
                  "configAfterSha256": digest_bytes(after), "rebootRequired": True})
    journal_write(path, state)
    runner(["/usr/sbin/reboot"])
    return state


def install_inactive(plan: dict, root: Path, package: Path, execute: bool,
                     runner: Runner = run_command) -> dict:
    if not execute or os.geteuid() != 0 or root != Path("/"):
        raise ValueError("installation requires real root and --execute")
    if package.is_symlink() or not package.is_file() or digest(package) != PACKAGE_SHA256:
        raise ValueError("package identity differs")
    observed = preflight(plan, root, runner)
    if observed["route"] is not None:
        raise ValueError("installation requires an inactive boot route")
    modules = Path("/proc/modules").read_text().splitlines()
    if any(line.startswith(f"{MODULE} ") for line in modules) or Path("/dev/rp1-gpclk").exists():
        raise ValueError("installation requires module and endpoint absence")
    path, state, _ = begin(plan, root, "install-inactive", None, runner)
    state["checkpoint"] = "install-started"
    journal_write(path, state)
    runner(["/usr/bin/dpkg", "--install", str(package)])
    status = runner(["/usr/bin/dpkg-query", "-W", "-f=${Status}|${Version}", PACKAGE]).strip()
    if status != f"install ok installed|{DEBIAN_VERSION}":
        raise RuntimeError("installed package identity differs")
    if parse_config(rooted(root, CONFIG).read_bytes()) is not None:
        raise RuntimeError("package installation activated a route")
    state.update({"status": "complete", "checkpoint": "installed-inactive",
                  "rebootRequired": False, "reconciled": True})
    journal_write(path, state)
    return state


def reconcile(plan: dict, root: Path, journal: Path, expected_route: str | None,
              runner: Runner = run_command) -> dict:
    state = json.loads(journal.read_text())
    if state.get("planSha256") != plan["planSha256"] or state.get("status") != "awaiting-reboot":
        raise ValueError("journal is stale, foreign, or not awaiting reboot")
    boot_id = read_boot_id(root)
    if boot_id == state["bootIdBefore"]:
        raise ValueError("expected reboot did not occur")
    config = rooted(root, CONFIG)
    if digest(config) != state["configAfterSha256"]:
        raise ValueError("post-boot configuration differs")
    active = parse_config(config.read_bytes())
    if active != expected_route:
        raise ValueError("configured route differs after reboot")
    state.update({"status": "complete", "checkpoint": "reconciled",
                  "bootIdAfter": boot_id, "rebootRequired": False, "reconciled": True})
    journal_write(journal, state)
    return state


def rollback(plan: dict, root: Path, journal: Path, execute: bool,
             runner: Runner = run_command) -> dict:
    if not execute or os.geteuid() != 0:
        raise ValueError("rollback requires root and --execute")
    state = json.loads(journal.read_text())
    if state.get("planSha256") != plan["planSha256"] or state.get("status") not in {
            "awaiting-reboot", "recovery-required"}:
        raise ValueError("journal is not an owned recoverable transaction")
    config = rooted(root, CONFIG)
    if digest(config) != state.get("configAfterSha256"):
        raise ValueError("rollback refuses changed or foreign boot configuration")
    before = state["configBefore"].encode()
    if digest_bytes(before) != state["configBeforeSha256"]:
        raise ValueError("rollback snapshot identity differs")
    atomic_write(config, before, config.stat().st_mode & 0o777)
    state.update({"status": "rollback-awaiting-reboot", "checkpoint": "rollback-committed",
                  "rollbackConfigSha256": digest(config), "rebootRequired": True})
    journal_write(journal, state)
    runner(["/usr/sbin/reboot"])
    return state


def residue_audit(plan: dict, root: Path) -> dict:
    directory = rooted(root, JOURNAL_DIR)
    if directory.exists():
        for path in directory.iterdir():
            if path.is_symlink() or not path.is_file():
                raise ValueError("journal residue is unsafe")
            state = json.loads(path.read_text())
            if (state.get("sourceCommit") != plan["sourceCommit"] or
                    state.get("qualificationArchiveSha256") != plan["qualificationArchiveSha256"] or
                    state.get("status") != "complete"):
                raise ValueError(f"incomplete or foreign journal: {path.name}")
    return {"status": "clean", "configuredRoute": parse_config(rooted(root, CONFIG).read_bytes())}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("preflight", "deactivate-and-reboot",
                                           "install-inactive", "preflight-route",
                                           "apply-and-reboot", "reconcile", "rollback",
                                           "residue-audit"))
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--root", type=Path, default=Path("/"))
    parser.add_argument("--route", choices=tuple(ROUTES))
    parser.add_argument("--journal", type=Path)
    parser.add_argument("--package", type=Path)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--confirm-physical-topology", action="store_true")
    args = parser.parse_args()
    plan = load_plan(args.plan)
    if args.action in {"deactivate-and-reboot", "install-inactive", "apply-and-reboot",
                       "rollback"} and not args.confirm_physical_topology:
        raise ValueError("mutation requires fresh physical-topology confirmation")
    if args.action in {"preflight", "preflight-route"}:
        result = preflight(plan, args.root)
        if args.action == "preflight-route" and not args.route:
            raise ValueError("--route is required")
    elif args.action == "deactivate-and-reboot":
        result = mutate_config(plan, args.root, args.action, None, args.execute)
    elif args.action == "apply-and-reboot":
        if not args.route:
            raise ValueError("--route is required")
        result = mutate_config(plan, args.root, args.action, args.route, args.execute)
    elif args.action == "install-inactive":
        if not args.package:
            raise ValueError("--package is required")
        result = install_inactive(plan, args.root, args.package, args.execute)
    elif args.action == "reconcile":
        if not args.journal:
            raise ValueError("--journal is required")
        result = reconcile(plan, args.root, args.journal, args.route)
    elif args.action == "rollback":
        if not args.journal:
            raise ValueError("--journal is required")
        result = rollback(plan, args.root, args.journal, args.execute)
    else:
        result = residue_audit(plan, args.root)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError,
            json.JSONDecodeError) as error:
        print(f"release candidate transaction: FAIL: {error}", file=sys.stderr)
        raise SystemExit(1)
