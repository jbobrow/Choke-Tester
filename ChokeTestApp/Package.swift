// swift-tools-version: 5.9
// The swift-tools-version declares the minimum version of Swift required to build this package.

import PackageDescription

let package = Package(
    name: "ChokeTestApp",
    platforms: [
        .macOS(.v13)
    ],
    products: [
        .executable(
            name: "ChokeTestApp",
            targets: ["ChokeTestApp"]
        ),
    ],
    targets: [
        .executableTarget(
            name: "ChokeTestApp",
            dependencies: [],
            path: "ChokeTestApp",
            exclude: [
                "Info.plist",
                "ChokeTestApp.entitlements"
            ],
            resources: [
                .process("Resources")
            ]
        ),
    ]
)
