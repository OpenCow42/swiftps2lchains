# Moving Colors

This is the original SwiftPS2 hello-world scene. Swift owns the PlayStation 2
entry point and drives an infinite animation through the public `PS2Kernel`
and `PS2GS` overlays. The background color and foreground square move every
frame.

Build it with the signed compiler suite published by this repository:

```sh
./scripts/swiftps2-demo
```

The audited ELF and its build manifest are written to `artifacts/`. To launch
the ELF after building, configure a BIOS in PCSX2 and run:

```sh
./scripts/swiftps2-demo --run
```

The current Testing SDK is a public consumer fixture marked
`candidate-unqualified`; using this example does not promote it to Preview or
Stable.
