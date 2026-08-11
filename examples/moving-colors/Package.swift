// swift-tools-version: 6.2

import PackageDescription

let package = Package(
    name: "MovingColors",
    products: [
        .executable(name: "MovingColors", targets: ["MovingColors"])
    ],
    targets: [
        .executableTarget(
            name: "MovingColors",
            path: "Sources/MovingColors"
        )
    ]
)
