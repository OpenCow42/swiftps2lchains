import PS2GS
import PS2Kernel

/// The original SwiftPS2 hello-world scene: Swift owns `main` and advances
/// the frame index while the PS2GS overlay animates the background and square.
@_cdecl("main")
public func movingColorsMain() -> Int32 {
    guard Kernel.initialize() else {
        Kernel.waitForLoaderReset()
        return 1
    }
    guard let graphics = Graphics(width: 320, height: 256) else {
        Kernel.waitForLoaderReset()
        return 2
    }

    var frameIndex: UInt32 = 0
    while true {
        guard let frame = graphics.drawFrame(index: frameIndex) else {
            break
        }
        frameIndex = frame.index &+ 1
    }

    graphics.shutdown()
    Kernel.waitForLoaderReset()
    return 3
}
