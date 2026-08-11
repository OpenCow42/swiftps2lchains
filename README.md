# swiftps2lchains

Signed SwiftPS2 toolchain-suite channel metadata and immutable release assets
for swiftPlay2ground. Compiler binaries belong in GitHub Releases, not Git
history.

The downloadable suite contains matching Swift, Clang, LLVM, Rust, Cargo,
Embedded Swift and Rust target runtimes, a locked PS2DEV/PS2SDK/gsKit install,
`ps2client`, a pinned host Python runtime, licenses, and an SPDX SBOM. PCSX2,
Sony BIOS images, and proprietary Sony SDK material are not redistributed.

The `stable` channel remains empty until the exact retained suite, compilers,
and ELF corpus complete physical Gate 12 v2. The `preview` channel may only
reference an emulator-qualified Gate 12 v2 result without a failed
compiler-quality policy.

The opt-in `testing` channel exists only for end-to-end swiftPlay2ground update
testing. It may reference a functional but `candidate-unqualified` suite and
never represents emulator or hardware qualification. Testing releases use the
separate `swiftps2-testing-1` trust root, are published as GitHub prereleases,
and are hidden unless swiftPlay2ground developer mode is enabled.

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
