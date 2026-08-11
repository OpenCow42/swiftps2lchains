import PS2GS
import PS2Kernel

private enum MovingColorsScene {
    static let width: UInt32 = 320
    static let height: UInt32 = 256
    static let squareSize: UInt32 = 96

    static func frame(index: UInt32) -> (clear: Color, rectangle: Rectangle) {
        let red = UInt8(truncatingIfNeeded: (index &* 29) &+ 32)
        let green = UInt8(truncatingIfNeeded: (index &* 47) &+ 64)
        let blue = UInt8(truncatingIfNeeded: (index &* 61) &+ 96)
        let x = (index &* 23) % (width - squareSize)
        let y = (index &* 17) % (height - squareSize)

        // `draw_clear` historically received B, R, G at six-bit precision.
        let clear = Color(red: blue >> 2, green: red >> 2, blue: green >> 2, alpha: 0)
        let rectangle = Rectangle(
            x: x,
            y: y,
            width: squareSize,
            height: squareSize,
            depth: 0,
            color: .rgb(red, green, blue)
        )
        return (clear, rectangle)
    }
}

/// The original SwiftPS2 hello-world scene. Swift owns its frame progression,
/// color calculation, and rectangle construction; PS2GS owns native submission.
@_cdecl("main")
public func movingColorsMain() -> Int32 {
    guard Kernel.initialize() else {
        Kernel.waitForLoaderReset()
        return 1
    }
    guard let graphics = Graphics(
        width: MovingColorsScene.width,
        height: MovingColorsScene.height
    ) else {
        Kernel.waitForLoaderReset()
        return 2
    }

    var frameIndex: UInt32 = 0
    while true {
        let frame = MovingColorsScene.frame(index: frameIndex)
        guard graphics.drawRectangle(
            clear: frame.clear,
            rectangle: frame.rectangle
        ) != nil else {
            break
        }
        frameIndex &+= 1
    }

    graphics.shutdown()
    Kernel.waitForLoaderReset()
    return 3
}
