# swiftps2lchains

Public SwiftPS2 toolchain-suite releases, signed channel metadata, and a
command-line hello-world workflow. Compiler binaries belong in GitHub
Releases, not Git history.

## Build the first Swift demo

On Apple Silicon with macOS 13 or newer, Python 3, and the Xcode Command Line
Tools:

```sh
git clone https://github.com/OpenCow42/swiftps2lchains.git
cd swiftps2lchains
./scripts/swiftps2-demo
```

The Python launcher does not invoke the host Swift interpreter. It verifies the
Testing channel and release Ed25519 signatures,
downloads and hashes the published self-contained SDK, validates its complete
internal package manifest, runs its doctor checks, and compiles
[`examples/moving-colors`](examples/moving-colors). It publishes the audited
result as `artifacts/moving-colors.elf` with its build manifest beside it.
The SDK and download cache stay under the ignored `.swiftps2/` directory.

PCSX2 and a legally obtained PS2 BIOS remain separate. After configuring the
BIOS in PCSX2, build and launch the demo with:

```sh
./scripts/swiftps2-demo --run
```

Use `--pcsx2 /path/to/PCSX2.app` when auto-discovery cannot find it. Run
`./scripts/swiftps2-demo --help` for channel, profile, output, and fullscreen
options.

The current default is the Testing channel because Stable and Preview are
empty. Testing is deliberately labeled `candidate-unqualified`; it is useful
for public compiler consumption but makes no emulator, hardware, or
production-qualification claim.

swiftPlay2ground is a separate private GUI application. This public repository
does not contain or require its source code.

## Distribution contract

The downloadable suite contains matching Swift, Clang, LLVM, Rust, Cargo,
Embedded Swift and Rust target runtimes, a locked PS2DEV/PS2SDK/gsKit install,
`ps2client`, a pinned host Python runtime, licenses, and an SPDX SBOM. PCSX2,
Sony BIOS images, and proprietary Sony SDK material are not redistributed.

The `stable` channel remains empty until the exact retained suite, compilers,
and ELF corpus complete physical Gate 12 v2. The `preview` channel may only
reference an emulator-qualified Gate 12 v2 result without a failed
compiler-quality policy.

The `testing` channel exists for public compiler-consumer and private updater
integration testing. It may reference a functional but
`candidate-unqualified` suite and never represents emulator or hardware
qualification. Testing releases use the separate `swiftps2-testing-1` trust
root and are published as GitHub prereleases. The private GUI hides this
channel unless its developer mode is enabled; the public command line labels
the qualification caveat on every invocation.

Stable and Preview channel and release manifests are signed as their exact
UTF-8 bytes with the Ed25519 key identified by `swiftps2-release-1`. Testing
metadata is signed with `swiftps2-testing-1`, so a testing credential cannot
publish a trusted Stable or Preview pointer.

`channels/stable.json`, `channels/preview.json`, and `channels/testing.json` are
the only mutable release pointers. Their detached signatures use the adjacent
`.sig` filename. The schemas under `schemas/` define the accepted channel and
release documents. Every referenced archive and release manifest is an
immutable GitHub Release asset. Each binary release also carries checksums,
qualification evidence or an explicit unqualified-testing notice, license
notices, and the corresponding locked source/patch material required to
reconstruct redistributed compiler components.

The empty channel pointers are signed as well. This lets clients distinguish
an authentic “no release yet” response from unsigned or substituted metadata.
`scripts/verify-channel-signatures.mjs` binds both files to the public key under
`keys/` on every pull request and default-branch push.
