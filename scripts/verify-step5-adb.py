#!/usr/bin/env python3
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
APPAGENTX_ROOT = REPO_ROOT / "AppAgentX"
SCREENSHOT_DIR = REPO_ROOT / "log" / "step5_screenshots"


def prefer_android_sdk_tools() -> None:
    sdk_root = Path(os.environ.get("ANDROID_SDK_ROOT") or os.environ.get("ANDROID_HOME") or "/home/tiger/android-sdk")
    platform_tools = sdk_root / "platform-tools"
    emulator_tools = sdk_root / "emulator"
    cmdline_tools = sdk_root / "cmdline-tools" / "latest" / "bin"

    paths = [str(path) for path in (platform_tools, emulator_tools, cmdline_tools) if path.exists()]
    if paths:
        os.environ["PATH"] = os.pathsep.join([*paths, os.environ.get("PATH", "")])


def run_command(args: list[str], timeout: int = 30) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=REPO_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
        check=False,
    )


def fail(message: str) -> None:
    print(message)
    raise SystemExit(1)


def parse_devices(output: str) -> list[tuple[str, str]]:
    devices: list[tuple[str, str]] = []
    for line in output.splitlines()[1:]:
        parts = line.split()
        if len(parts) >= 2:
            devices.append((parts[0], parts[1]))
    return devices


def select_device(devices: list[tuple[str, str]]) -> str:
    requested = os.environ.get("APPAGENTX_ADB_DEVICE")
    online = [(device_id, state) for device_id, state in devices if state == "device"]

    if requested:
        matches = [state for device_id, state in devices if device_id == requested]
        if not matches:
            fail(f"requested_device_missing {requested}")
        if matches[0] != "device":
            fail(f"requested_device_not_ready {requested} {matches[0]}")
        return requested

    if not online:
        for device_id, state in devices:
            print(f"adb_device_not_ready {device_id} {state}")
        fail("adb_no_online_device")

    if len(online) > 1:
        print("multiple_online_devices")
        for device_id, _ in online:
            print(f"online_device {device_id}")
        fail("set_APPAGENTX_ADB_DEVICE")

    return online[0][0]


def adb(args: list[str], timeout: int = 30) -> str:
    result = run_command(["adb", *args], timeout=timeout)
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip().splitlines()
        first_line = detail[0] if detail else "unknown adb error"
        fail(f"adb_failed {' '.join(args)}: {first_line}")
    return result.stdout


def parse_screen_size(output: str) -> tuple[int, int]:
    match = re.search(r"(?:Physical|Override) size:\s*(\d+)x(\d+)", output)
    if not match:
        fail(f"screen_size_parse_failed {output.strip()}")
    return int(match.group(1)), int(match.group(2))


def check_adb_binary() -> None:
    adb_path = shutil.which("adb")
    if not adb_path:
        fail("adb_missing")
    print(f"adb_path {adb_path}")

    version = adb(["version"])
    first_line = version.splitlines()[0] if version.splitlines() else "unknown"
    print(f"adb_version_ok {first_line}")

    adb(["start-server"], timeout=20)
    print("adb_server_ok")


def check_adb_device() -> tuple[str, tuple[int, int]]:
    devices_output = adb(["devices"], timeout=20)
    devices = parse_devices(devices_output)
    if not devices:
        fail("adb_no_devices")

    for device_id, state in devices:
        print(f"adb_device {device_id} {state}")

    target = select_device(devices)
    print(f"target_device {target}")

    size_output = adb(["-s", target, "shell", "wm", "size"], timeout=20)
    width, height = parse_screen_size(size_output)
    print(f"adb_wm_size_ok {width}x{height}")

    power = run_command(["adb", "-s", target, "shell", "dumpsys", "power"], timeout=20)
    if power.returncode == 0:
        wakefulness = re.search(r"mWakefulness=([A-Za-z]+)", power.stdout)
        display = re.search(r"Display Power:\s*state=([A-Z]+)", power.stdout)
        state = wakefulness.group(1) if wakefulness else "unknown"
        display_state = display.group(1) if display else "unknown"
        print(f"device_power_state {state} display={display_state}")
    else:
        print("device_power_state_unknown")

    return target, (width, height)


def check_project_tools(target: str, adb_size: tuple[int, int]) -> None:
    sys.path.insert(0, str(APPAGENTX_ROOT))

    from tool.screen_content import get_device_size, list_all_devices, take_screenshot

    project_devices = list_all_devices()
    if target not in project_devices:
        fail(f"project_list_all_devices_missing_target {target}")
    print("project_list_all_devices_ok")

    project_size = get_device_size.invoke({"device": target})
    if not isinstance(project_size, dict):
        fail(f"project_get_device_size_invalid {project_size}")
    width = int(project_size.get("width", 0))
    height = int(project_size.get("height", 0))
    if width <= 0 or height <= 0:
        fail(f"project_get_device_size_invalid {project_size}")
    print(f"project_get_device_size_ok {width}x{height}")
    print(f"screen_size_match {adb_size == (width, height)}")

    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    screenshot = take_screenshot.invoke(
        {
            "device": target,
            "save_dir": str(SCREENSHOT_DIR),
            "app_name": "step5_adb",
            "step": 0,
        }
    )
    screenshot_path = Path(str(screenshot))
    if not screenshot_path.exists() or screenshot_path.stat().st_size <= 0:
        fail(f"project_take_screenshot_failed {screenshot}")
    print(f"project_take_screenshot_ok {screenshot_path}")

    from PIL import Image

    with Image.open(screenshot_path) as image:
        image.verify()
        print(f"screenshot_size {image.width}x{image.height}")


def main() -> int:
    prefer_android_sdk_tools()
    check_adb_binary()
    target, adb_size = check_adb_device()
    check_project_tools(target, adb_size)
    print("step5_adb_device_ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
