#!/usr/bin/env python3

"""Offline contract tests for the Python public-demo launcher."""

from __future__ import annotations

import base64
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path


REPOSITORY = Path(__file__).resolve().parent.parent
SCRIPT = REPOSITORY / "scripts/swiftps2-demo"
ED25519_SPKI_PREFIX = bytes.fromhex("302a300506032b6570032100")


class TestFailure(Exception):
    """A failed public-demo contract assertion."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise TestFailure(message)


def encoded_json(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


def sign(private_key: Path, message: Path, signature: Path) -> None:
    command = [
        "openssl",
        "pkeyutl",
        "-sign",
        "-inkey",
        str(private_key),
        "-rawin",
        "-in",
        str(message),
        "-out",
        str(signature),
    ]
    result = run(command)
    if result.returncode != 0:
        # Older OpenSSL releases accepted Ed25519 input without -rawin.
        command.remove("-rawin")
        result = run(command)
    if result.returncode != 0:
        raise TestFailure(f"could not sign the test fixture: {result.stdout}")


def write_signature(private_key: Path, document: Path) -> Path:
    raw_signature = document.with_suffix(document.suffix + ".rawsig")
    sign(private_key, document, raw_signature)
    signature = document.with_suffix(document.suffix + ".sig")
    signature.write_bytes(base64.b64encode(raw_signature.read_bytes()) + b"\n")
    return signature


def run_demo(arguments: list[str]) -> subprocess.CompletedProcess[str]:
    return run([str(SCRIPT), *arguments])


def main() -> None:
    require(
        SCRIPT.read_text(encoding="utf-8").startswith("#!/usr/bin/env python3"),
        "public-demo launcher is not a Python script",
    )

    with tempfile.TemporaryDirectory(prefix="swiftps2-demo-tests-") as directory:
        fixture = Path(directory)
        private_key = fixture / "test-private.pem"
        generated = run(["openssl", "genpkey", "-algorithm", "ED25519", "-out", str(private_key)])
        require(generated.returncode == 0, f"could not generate Ed25519 fixture key: {generated.stdout}")
        public_key_der = subprocess.check_output(
            ["openssl", "pkey", "-in", str(private_key), "-pubout", "-outform", "DER"]
        )
        require(
            public_key_der.startswith(ED25519_SPKI_PREFIX) and len(public_key_der) == 44,
            "OpenSSL did not produce an Ed25519 public key",
        )
        public_key = fixture / "test.pub"
        public_key.write_bytes(base64.b64encode(public_key_der[-32:]) + b"\n")

        manifest = fixture / "release-manifest.json"
        manifest.write_bytes(
            encoded_json(
                {
                    "archive": {
                        "bytes": 1,
                        "format": "tar.gz",
                        "sha256": "a" * 64,
                        "url": (fixture / "suite.tar.gz").as_uri(),
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
        manifest_signature = write_signature(private_key, manifest)

        channel = fixture / "testing.json"
        channel.write_bytes(
            encoded_json(
                {
                    "channel": "testing",
                    "generatedAt": "2026-08-11T00:00:00Z",
                    "release": {
                        "manifestSHA256": hashlib.sha256(manifest.read_bytes()).hexdigest(),
                        "manifestSignatureURL": manifest_signature.as_uri(),
                        "manifestURL": manifest.as_uri(),
                        "version": "9.9.9-testing.1",
                    },
                    "schemaVersion": 1,
                    "signingKeyID": "swiftps2-testing-1",
                }
            )
        )
        channel_signature = write_signature(private_key, channel)
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
        require(accepted.returncode == 0, f"signed offline fixture was rejected: {accepted.stdout}")
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

    print("swiftps2-demo Python tests passed")


if __name__ == "__main__":
    try:
        main()
    except (OSError, TestFailure, subprocess.SubprocessError) as error:
        print(f"swiftps2-demo tests failed: {error}", file=sys.stderr)
        sys.exit(1)
