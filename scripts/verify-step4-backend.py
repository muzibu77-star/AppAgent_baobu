#!/usr/bin/env python3
from __future__ import annotations

import json
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw


REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = REPO_ROOT / "AppAgentX" / "backend"
OMNI_ROOT = BACKEND_ROOT / "OmniParser"
IMAGE_ROOT = BACKEND_ROOT / "ImageEmbedding"


def fail(message: str) -> None:
    print(message)
    raise SystemExit(1)


def check_file(path: Path) -> None:
    if not path.is_file() or path.stat().st_size == 0:
        fail(f"missing_or_empty_file: {path}")


def check_dir(path: Path) -> None:
    if not path.is_dir():
        fail(f"missing_dir: {path}")


def check_preflight() -> None:
    check_file(BACKEND_ROOT / "docker-compose.yml")
    check_dir(IMAGE_ROOT)
    check_dir(OMNI_ROOT)
    check_file(IMAGE_ROOT / "image_embedding.py")
    check_file(OMNI_ROOT / "omni.py")
    check_file(IMAGE_ROOT / "Dockerfile")
    check_file(OMNI_ROOT / "Dockerfile")
    check_file(IMAGE_ROOT / "requirements.txt")
    check_file(OMNI_ROOT / "requirements.txt")

    check_file(OMNI_ROOT / "weights" / "icon_detect_v1_5" / "best.pt")
    caption_dir = OMNI_ROOT / "weights" / "icon_caption_florence"
    check_dir(caption_dir)
    if not any(caption_dir.iterdir()):
        fail(f"empty_caption_weights_dir: {caption_dir}")

    print("backend_preflight_ok")


def check_tcp(host: str, port: int) -> None:
    with socket.create_connection((host, port), timeout=5):
        print(f"tcp_ok {host}:{port}")


def request_json(req: urllib.request.Request, timeout: int = 30) -> dict:
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            body = response.read().decode("utf-8")
            return json.loads(body)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        fail(f"http_error {exc.code}: {detail[:300]}")


def get_json(url: str, timeout: int = 30) -> dict:
    return request_json(urllib.request.Request(url), timeout=timeout)


def post_json(url: str, payload: dict, timeout: int = 120) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    return request_json(req, timeout=timeout)


def post_multipart(url: str, file_path: Path, field_name: str = "file", timeout: int = 180) -> dict:
    boundary = f"----appagentx{int(time.time() * 1000)}"
    file_bytes = file_path.read_bytes()
    body = b"".join(
        [
            f"--{boundary}\r\n".encode(),
            (
                f'Content-Disposition: form-data; name="{field_name}"; '
                f'filename="{file_path.name}"\r\n'
            ).encode(),
            b"Content-Type: image/png\r\n\r\n",
            file_bytes,
            b"\r\n",
            f"--{boundary}--\r\n".encode(),
        ]
    )
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    return request_json(req, timeout=timeout)


def make_test_image() -> Path:
    temp_dir = Path(tempfile.mkdtemp(prefix="appagentx-step4-"))
    image_path = temp_dir / "test_screen.png"
    image = Image.new("RGB", (360, 640), "white")
    draw = ImageDraw.Draw(image)
    draw.rectangle((50, 80, 310, 150), outline="black", width=3)
    draw.text((85, 105), "Settings", fill="black")
    draw.rectangle((70, 220, 290, 300), outline="blue", width=3)
    draw.text((120, 250), "OK", fill="blue")
    image.save(image_path)
    return image_path


def check_compose_services() -> None:
    result = subprocess.run(
        ["docker", "compose", "ps", "--format", "json"],
        cwd=BACKEND_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        print(f"docker_compose_ps_skipped: {result.stderr.strip()}")
        return
    output = result.stdout.strip()
    if not output:
        print("docker_compose_ps_empty_local_mode")
        return
    print("docker_compose_ps_ok")


def check_image_embedding(image_path: Path) -> None:
    models = get_json("http://127.0.0.1:8001/available_models")
    if "recommended_models" not in models:
        fail("image_embedding_available_models_missing_recommended_models")
    print("image_embedding_available_models_ok")

    set_model = post_json("http://127.0.0.1:8001/set_model", {"model_name": "resnet50"})
    if set_model.get("status") != "success":
        fail(f"image_embedding_set_model_failed: {set_model}")
    print("image_embedding_set_model_ok")

    model_info = get_json("http://127.0.0.1:8001/model_info")
    if model_info.get("model_name") != "resnet50":
        fail(f"image_embedding_model_info_unexpected: {model_info}")
    print("image_embedding_model_info_ok")

    features = post_multipart("http://127.0.0.1:8001/extract_single/", image_path)
    if features.get("model_name") != "resnet50" or "shape" not in features:
        fail(f"image_embedding_extract_single_failed: {features.keys()}")
    print("image_embedding_extract_single_ok")
    print("image_embedding_shape", features.get("shape"))


def check_omni_parser(image_path: Path) -> None:
    parsed = post_multipart("http://127.0.0.1:8000/process_image/", image_path, timeout=240)
    if parsed.get("status") != "success":
        fail(f"omni_parser_process_failed: {parsed}")
    for key in ("parsed_content", "labeled_image", "e_time"):
        if key not in parsed:
            fail(f"omni_parser_missing_key: {key}")
    print("omni_parser_process_image_ok")
    print("omni_parser_elements", len(parsed.get("parsed_content") or []))
    print("omni_parser_e_time", parsed.get("e_time"))


def main() -> int:
    check_preflight()
    check_compose_services()
    check_tcp("127.0.0.1", 8001)
    check_tcp("127.0.0.1", 8000)
    image_path = make_test_image()
    check_image_embedding(image_path)
    check_omni_parser(image_path)
    print("step4_backend_services_ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
