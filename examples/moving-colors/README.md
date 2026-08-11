# Moving Colors

This is the original SwiftPS2 hello-world scene. Swift owns the PlayStation 2
entry point, frame progression, color calculation, and foreground-rectangle
construction through the public `PS2Kernel` and `PS2GS` overlays. The native
boundary retains GS lifecycle, GIF packet encoding, DMA submission, and vsync.

This source-only branch requires a matching unreleased SwiftPS2 SDK containing
the bounded `Color`, `Rectangle`, and `Graphics.drawRectangle` API. It is not
compatible with the currently published Testing SDK and must be released with
that SDK change.

Build it from a local checkout of the matching SwiftPS2 SDK. Rebuild its local
artifact bundle so it includes the unreleased `PS2GS` overlay API:

```sh
/path/to/ps2swift/scripts/swiftps2 build \
  --rebuild-toolchain \
  --package /path/to/swiftps2lchains/examples/moving-colors \
  --profile debug-emulator \
  --output /tmp/moving-colors
```

The resulting ELF and build manifest are written below `/tmp/moving-colors`.
After the coordinated SDK is published, this example can return to the
repository's signed `./scripts/swiftps2-demo` quick-start flow.
