# swiftps2lchains

Signed SwiftPS2 SDK channel metadata and immutable release assets for
swiftPlay2ground. Compiler binaries belong in GitHub Releases, not Git history.

The `stable` channel remains empty until the exact retained SDK, compiler, and
ELF suite complete physical Gate 12. The `preview` channel may only reference
an emulator-qualified Gate 12 result without a failed compiler-quality policy.

Channel and release manifests are signed as their exact UTF-8 bytes with the
Ed25519 key identified by `swiftps2-release-1`.

`channels/stable.json` and `channels/preview.json` are the only mutable release
pointers. Their detached signatures use the adjacent `.sig` filename. The
schemas under `schemas/` define the accepted channel and release documents.
Every referenced archive and release manifest is an immutable GitHub Release
asset.

This bootstrap tree intentionally contains unsigned empty channels until the
protected release key is created and pinned in ps2swift/swiftPlay2ground. Do
not publish this template as a live update source before both empty channel
files have valid detached signatures.
