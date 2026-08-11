#!/usr/bin/env python3

"""Offline contract tests for the Python public-demo launcher."""

from __future__ import annotations

import base64
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path


REPOSITORY = Path(__file__).resolve().parent.parent
SCRIPT = REPOSITORY / "scripts/swiftps2-demo"
FIXTURE = Path("/tmp/swiftps2-demo-python-fixture")
PUBLIC_KEY = "BxNNtE5E2tgRLx484WzH8n6SryrkX20R4VsLjgxAiZM="
MANIFEST_SIGNATURE = (
    "7E+0fguu5QtR6zIViJcW5kCQ3Bp3azbbDkXOEQ6zBIZtg1vsfRJR1uLGE7j+bhwkwax"
    "KyWDIYYMC1yoVepFSCw=="
)
CHANNEL_SIGNATURE = (
    "W4zTLTVOZgACM+ml5KSclokoLPzQbNK0ANsX4lP4/Y7OJxyq53lxUAh/D3PM6yEk/Dxq"
    "nYBilIOgbpuoeyQXAw=="
)
MANIFEST_SHA256 = "a2291ccdb109ab322c3e7cbbd46843759dcc7a157ddf42da35fd790f7fb02d30"


class TestFailure(Exception):
    """A failed public-demo contract assertion."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise TestFailure(message)


def encoded_json(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def run_demo(arguments: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(SCRIPT), *arguments],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )


def write_signature(path: Path, signature: str) -> None:
    path.write_bytes(signature.encode("ascii") + b"\n")


def main() -> None:
    require(
        SCRIPT.read_text(encoding="utf-8").startswith("#!/usr/bin/env python3"),
        "public-demo launcher is not a Python script",
    )

    if FIXTURE.exists():
        shutil.rmtree(FIXTURE)
    FIXTURE.mkdir()
    try:
        public_key = FIXTURE / "test.pub"
        public_key.write_bytes(PUBLIC_KEY.encode("ascii") + b"\n")

        manifest = FIXTURE / "release-manifest.json"
        manifest.write_bytes(
            encoded_json(
                {
                    "archive": {
                        "bytes": 1,
                        "format": "tar.gz",
                        "sha256": "a" * 64,
                        "url": (FIXTURE / "suite.tar.gz").as_uri(),
                    },
                    "channel": "testing",
                    "hostTriples": ["arm64-apple-macosx13.0"],
                    "packageManifestSha256": "b" * 64,
                    "qualification": {
                        "caveat": "Offline fixture",
                        "hardwareQualified": False,
                        "status": "candidate-unqualified",
                    },
                    "releaseVersion": "9.9.9-testing.1",
                    "schemaVersion": 2,
                    "signingKeyID": "swiftps2-testing-1",
                    "target": {
                        "abi": "n32",
                        "cpu": "r5900",
                        "elfClass": "ELF32",
                        "triple": "mips64el-scei-ps2",
                    },
                }
            )
        )
        require(
            hashlib.sha256(manifest.read_bytes()).hexdigest() == MANIFEST_SHA256,
            "offline manifest no longer matches its independent signature",
        )
        write_signature(
            FIXTURE / "release-manifest.json.sig",
            MANIFEST_SIGNATURE,
        )

        channel = FIXTURE / "testing.json"
        channel.write_bytes(
            encoded_json(
                {
                    "channel": "testing",
                    "generatedAt": "2026-08-11T00:00:00Z",
                    "release": {
                        "manifestSHA256": MANIFEST_SHA256,
                        "manifestSignatureURL": (
                            FIXTURE / "release-manifest.json.sig"
                        ).as_uri(),
                        "manifestURL": (FIXTURE / "release-manifest.json").as_uri(),
                        "version": "9.9.9-testing.1",
                    },
                    "schemaVersion": 1,
                    "signingKeyID": "swiftps2-testing-1",
                }
            )
        )
        channel_signature = FIXTURE / "testing.json.sig"
        write_signature(channel_signature, CHANNEL_SIGNATURE)
        arguments = [
            "--channel",
            "testing",
            "--channel-url",
            channel.as_uri(),
            "--trust-root",
            str(public_key),
            "--resolve-only",
        ]
        accepted = run_demo(arguments)
        require(
            accepted.returncode == 0,
            f"signed offline fixture was rejected: {accepted.stdout}",
        )
        require(
            "Resolved 9.9.9-testing.1" in accepted.stdout,
            "resolved release identity was not printed",
        )
        require(
            "candidate-unqualified" in accepted.stdout,
            "qualification warning was not printed",
        )

        channel_signature.write_text("AAAA\n", encoding="utf-8")
        rejected = run_demo(arguments)
        require(rejected.returncode != 0, "corrupted channel signature was accepted")
        require(
            "signature is invalid" in rejected.stdout,
            "signature rejection was not explicit",
        )

        unsafe_override = run_demo(["--trust-root", str(public_key), "--resolve-only"])
        require(
            unsafe_override.returncode != 0,
            "trust-root override without channel override was accepted",
        )
    finally:
        shutil.rmtree(FIXTURE, ignore_errors=True)

    print("swiftps2-demo Python tests passed")


if __name__ == "__main__":
    try:
        main()
    except (OSError, TestFailure, subprocess.SubprocessError) as error:
        print(f"swiftps2-demo tests failed: {error}", file=sys.stderr)
        sys.exit(1)
