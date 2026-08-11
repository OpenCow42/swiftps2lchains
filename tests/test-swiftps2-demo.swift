import CryptoKit
import Foundation

enum TestFailure: Error, CustomStringConvertible {
    case message(String)

    var description: String {
        switch self {
        case let .message(text): text
        }
    }
}

func encodedJSON(_ object: Any) throws -> Data {
    var data = try JSONSerialization.data(withJSONObject: object, options: [.prettyPrinted, .sortedKeys])
    data.append(0x0a)
    return data
}

func hexDigest(_ data: Data) -> String {
    SHA256.hash(data: data).map { String(format: "%02x", $0) }.joined()
}

func write(_ data: Data, to url: URL) throws {
    try data.write(to: url, options: .atomic)
}

func run(_ script: URL, arguments: [String]) throws -> (status: Int32, output: String) {
    let process = Process()
    let pipe = Pipe()
    process.executableURL = URL(fileURLWithPath: "/usr/bin/swift")
    process.arguments = [script.path] + arguments
    process.standardOutput = pipe
    process.standardError = pipe
    try process.run()
    process.waitUntilExit()
    let data = pipe.fileHandleForReading.readDataToEndOfFile()
    return (process.terminationStatus, String(data: data, encoding: .utf8) ?? "")
}

func require(_ condition: @autoclosure () -> Bool, _ message: String) throws {
    guard condition() else { throw TestFailure.message(message) }
}

let manager = FileManager.default
let repository = URL(fileURLWithPath: #filePath)
    .deletingLastPathComponent()
    .deletingLastPathComponent()
let script = repository.appendingPathComponent("scripts/swiftps2-demo")
let fixture = manager.temporaryDirectory.appendingPathComponent("swiftps2-demo-tests-\(UUID().uuidString)")
try manager.createDirectory(at: fixture, withIntermediateDirectories: true)
defer { try? manager.removeItem(at: fixture) }

do {
    let privateKey = Curve25519.Signing.PrivateKey()
    let publicKey = fixture.appendingPathComponent("test.pub")
    try Data(privateKey.publicKey.rawRepresentation.base64EncodedString().utf8).write(to: publicKey)

    let manifestURL = fixture.appendingPathComponent("release-manifest.json")
    let manifestSignatureURL = fixture.appendingPathComponent("release-manifest.sig")
    let manifest = try encodedJSON([
        "archive": [
            "bytes": 1,
            "format": "tar.gz",
            "sha256": String(repeating: "a", count: 64),
            "url": fixture.appendingPathComponent("suite.tar.gz").absoluteString,
        ],
        "channel": "testing",
        "hostTriples": ["arm64-apple-macosx13.0"],
        "packageManifestSha256": String(repeating: "b", count: 64),
        "qualification": [
            "caveat": "Offline fixture",
            "hardwareQualified": false,
            "status": "candidate-unqualified",
        ],
        "releaseVersion": "9.9.9-testing.1",
        "schemaVersion": 2,
        "signingKeyID": "swiftps2-testing-1",
        "target": [
            "abi": "n32",
            "cpu": "r5900",
            "elfClass": "ELF32",
            "triple": "mips64el-scei-ps2",
        ],
    ])
    try write(manifest, to: manifestURL)
    try write(
        Data(privateKey.signature(for: manifest).base64EncodedString().utf8),
        to: manifestSignatureURL
    )

    let channelURL = fixture.appendingPathComponent("testing.json")
    let channelSignatureURL = fixture.appendingPathComponent("testing.json.sig")
    let channel = try encodedJSON([
        "channel": "testing",
        "generatedAt": "2026-08-11T00:00:00Z",
        "release": [
            "manifestSHA256": hexDigest(manifest),
            "manifestSignatureURL": manifestSignatureURL.absoluteString,
            "manifestURL": manifestURL.absoluteString,
            "version": "9.9.9-testing.1",
        ],
        "schemaVersion": 1,
        "signingKeyID": "swiftps2-testing-1",
    ])
    try write(channel, to: channelURL)
    try write(
        Data(privateKey.signature(for: channel).base64EncodedString().utf8),
        to: channelSignatureURL
    )

    let accepted = try run(
        script,
        arguments: [
            "--channel", "testing",
            "--channel-url", channelURL.absoluteString,
            "--trust-root", publicKey.path,
            "--resolve-only",
        ]
    )
    try require(accepted.status == 0, "signed offline fixture was rejected: \(accepted.output)")
    try require(
        accepted.output.contains("Resolved 9.9.9-testing.1"),
        "resolved release identity was not printed"
    )
    try require(
        accepted.output.contains("candidate-unqualified"),
        "qualification warning was not printed"
    )

    try write(Data("AAAA\n".utf8), to: channelSignatureURL)
    let rejected = try run(
        script,
        arguments: [
            "--channel", "testing",
            "--channel-url", channelURL.absoluteString,
            "--trust-root", publicKey.path,
            "--resolve-only",
        ]
    )
    try require(rejected.status != 0, "corrupted channel signature was accepted")
    try require(rejected.output.contains("signature is invalid"), "signature rejection was not explicit")

    let unsafeOverride = try run(script, arguments: ["--trust-root", publicKey.path, "--resolve-only"])
    try require(unsafeOverride.status != 0, "trust-root override without channel override was accepted")
    print("swiftps2-demo tests passed")
} catch {
    fputs("swiftps2-demo tests failed: \(error)\n", stderr)
    exit(1)
}
