//
//  MeshLoader.swift
//  Choke Test Safety Check
//
//  Loads 3D meshes from STL and 3MF files
//

import Foundation

enum MeshLoader {
    static func load(from url: URL) async throws -> Mesh {
        let ext = url.pathExtension.lowercased()

        switch ext {
        case "stl":
            return try await loadSTL(from: url)
        case "3mf":
            return try await load3MF(from: url)
        default:
            throw MeshError.unsupportedFormat
        }
    }

    // MARK: - STL Loading

    private static func loadSTL(from url: URL) async throws -> Mesh {
        let data = try Data(contentsOf: url)

        // Check if binary or ASCII
        if data.count >= 5, String(data: data.prefix(5), encoding: .ascii) == "solid" {
            return try loadASCIISTL(data: data, name: url.lastPathComponent)
        } else {
            return try loadBinarySTL(data: data, name: url.lastPathComponent)
        }
    }

    private static func loadBinarySTL(data: Data, name: String) throws -> Mesh {
        guard data.count >= 84 else { throw MeshError.invalidSTL }

        // Read triangle count (at bytes 80-83)
        let triangleCount: UInt32 = data.subdata(in: 80..<84).withUnsafeBytes { buffer in
            buffer.loadUnaligned(as: UInt32.self)
        }

        guard data.count >= 84 + Int(triangleCount) * 50 else {
            throw MeshError.invalidSTL
        }

        var vertices: [SIMD3<Float>] = []
        var triangles: [Mesh.Triangle] = []
        var vertexMap: [SIMD3<Float>: Int] = [:]

        // Each triangle is 50 bytes: normal(12) + vertex1(12) + vertex2(12) + vertex3(12) + attribute(2)
        for i in 0..<Int(triangleCount) {
            let baseOffset = 84 + i * 50

            // Skip normal (first 12 bytes of triangle data)
            let vertexOffset = baseOffset + 12

            // Read 3 vertices (12 bytes each)
            var triangleIndices: [Int] = []

            for v in 0..<3 {
                let vOffset = vertexOffset + v * 12

                // Read x, y, z as Float (4 bytes each)
                let x = data.subdata(in: vOffset..<vOffset+4).withUnsafeBytes { buffer in
                    buffer.loadUnaligned(as: Float.self)
                }
                let y = data.subdata(in: vOffset+4..<vOffset+8).withUnsafeBytes { buffer in
                    buffer.loadUnaligned(as: Float.self)
                }
                let z = data.subdata(in: vOffset+8..<vOffset+12).withUnsafeBytes { buffer in
                    buffer.loadUnaligned(as: Float.self)
                }

                let vertex = SIMD3<Float>(x, y, z)

                if let index = vertexMap[vertex] {
                    triangleIndices.append(index)
                } else {
                    let index = vertices.count
                    vertices.append(vertex)
                    vertexMap[vertex] = index
                    triangleIndices.append(index)
                }
            }

            triangles.append(Mesh.Triangle(
                v0: triangleIndices[0],
                v1: triangleIndices[1],
                v2: triangleIndices[2]
            ))
        }

        return Mesh(vertices: vertices, triangles: triangles, name: name)
    }

    private static func loadASCIISTL(data: Data, name: String) throws -> Mesh {
        guard let content = String(data: data, encoding: .utf8) else {
            throw MeshError.invalidSTL
        }

        var vertices: [SIMD3<Float>] = []
        var triangles: [Mesh.Triangle] = []
        var vertexMap: [SIMD3<Float>: Int] = [:]
        var currentTriangleVertices: [Int] = []

        let lines = content.components(separatedBy: .newlines)

        for line in lines {
            let trimmed = line.trimmingCharacters(in: .whitespaces)
            let parts = trimmed.components(separatedBy: .whitespaces).filter { !$0.isEmpty }

            guard !parts.isEmpty else { continue }

            if parts[0] == "vertex", parts.count >= 4 {
                guard let x = Float(parts[1]),
                      let y = Float(parts[2]),
                      let z = Float(parts[3]) else { continue }

                let vertex = SIMD3<Float>(x, y, z)

                if let index = vertexMap[vertex] {
                    currentTriangleVertices.append(index)
                } else {
                    let index = vertices.count
                    vertices.append(vertex)
                    vertexMap[vertex] = index
                    currentTriangleVertices.append(index)
                }

                if currentTriangleVertices.count == 3 {
                    triangles.append(Mesh.Triangle(
                        v0: currentTriangleVertices[0],
                        v1: currentTriangleVertices[1],
                        v2: currentTriangleVertices[2]
                    ))
                    currentTriangleVertices.removeAll()
                }
            }
        }

        return Mesh(vertices: vertices, triangles: triangles, name: name)
    }

    // MARK: - 3MF Loading

    private static func load3MF(from url: URL) async throws -> Mesh {
        // 3MF is a ZIP archive with XML
        let fileManager = FileManager.default
        let tempDir = fileManager.temporaryDirectory.appendingPathComponent(UUID().uuidString)

        try fileManager.createDirectory(at: tempDir, withIntermediateDirectories: true)

        defer {
            try? fileManager.removeItem(at: tempDir)
        }

        // Unzip (using system unzip for simplicity)
        let process = Process()
        process.executableURL = URL(fileURLWithPath: "/usr/bin/unzip")
        process.arguments = ["-q", url.path, "-d", tempDir.path]
        try process.run()
        process.waitUntilExit()

        // Parse 3D/3dmodel.model XML
        let modelPath = tempDir.appendingPathComponent("3D/3dmodel.model")
        let xmlData = try Data(contentsOf: modelPath)

        return try parse3MFModel(xmlData: xmlData, name: url.lastPathComponent)
    }

    private static func parse3MFModel(xmlData: Data, name: String) throws -> Mesh {
        let parser = ThreeMFParser()
        let parseResult = try parser.parse(xmlData)

        return Mesh(
            vertices: parseResult.vertices,
            triangles: parseResult.triangles,
            name: name
        )
    }
}

// MARK: - 3MF XML Parser

private class ThreeMFParser: NSObject, XMLParserDelegate {
    var vertices: [SIMD3<Float>] = []
    var triangles: [Mesh.Triangle] = []

    private var currentElement = ""

    func parse(_ data: Data) throws -> (vertices: [SIMD3<Float>], triangles: [Mesh.Triangle]) {
        let parser = XMLParser(data: data)
        parser.delegate = self

        guard parser.parse() else {
            throw MeshError.invalid3MF
        }

        return (vertices, triangles)
    }

    func parser(_ parser: XMLParser, didStartElement elementName: String, namespaceURI: String?, qualifiedName qName: String?, attributes attributeDict: [String : String] = [:]) {
        currentElement = elementName

        if elementName == "vertex" {
            guard let xStr = attributeDict["x"],
                  let yStr = attributeDict["y"],
                  let zStr = attributeDict["z"],
                  let x = Float(xStr),
                  let y = Float(yStr),
                  let z = Float(zStr) else { return }

            vertices.append(SIMD3<Float>(x, y, z))
        }
        else if elementName == "triangle" {
            guard let v1Str = attributeDict["v1"],
                  let v2Str = attributeDict["v2"],
                  let v3Str = attributeDict["v3"],
                  let v1 = Int(v1Str),
                  let v2 = Int(v2Str),
                  let v3 = Int(v3Str) else { return }

            triangles.append(Mesh.Triangle(v0: v1, v1: v2, v2: v3))
        }
    }
}

// MARK: - Errors

enum MeshError: LocalizedError {
    case unsupportedFormat
    case invalidSTL
    case invalid3MF
    case fileNotFound

    var errorDescription: String? {
        switch self {
        case .unsupportedFormat:
            return "Unsupported file format. Only STL and 3MF files are supported."
        case .invalidSTL:
            return "Invalid STL file format."
        case .invalid3MF:
            return "Invalid 3MF file format."
        case .fileNotFound:
            return "File not found."
        }
    }
}
