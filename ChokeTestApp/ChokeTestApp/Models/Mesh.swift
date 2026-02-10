//
//  Mesh.swift
//  Choke Test Safety Check
//
//  3D mesh representation for analysis
//

import Foundation
import simd

struct Mesh: Hashable {
    var vertices: [SIMD3<Float>]
    var triangles: [Triangle]
    var name: String

    struct Triangle: Hashable {
        let v0: Int
        let v1: Int
        let v2: Int

        func vertices(from mesh: Mesh) -> (SIMD3<Float>, SIMD3<Float>, SIMD3<Float>) {
            (mesh.vertices[v0], mesh.vertices[v1], mesh.vertices[v2])
        }

        func normal(from mesh: Mesh) -> SIMD3<Float> {
            let (v0, v1, v2) = vertices(from: mesh)
            let edge1 = v1 - v0
            let edge2 = v2 - v0
            return normalize(cross(edge1, edge2))
        }
    }

    // Computed properties
    var bounds: BoundingBox {
        guard !vertices.isEmpty else {
            return BoundingBox(min: .zero, max: .zero)
        }

        var minPoint = vertices[0]
        var maxPoint = vertices[0]

        for vertex in vertices {
            minPoint = min(minPoint, vertex)
            maxPoint = max(maxPoint, vertex)
        }

        return BoundingBox(min: minPoint, max: maxPoint)
    }

    var center: SIMD3<Float> {
        let bbox = bounds
        return (bbox.min + bbox.max) * 0.5
    }

    // Transform mesh
    func transformed(by matrix: simd_float4x4) -> Mesh {
        var transformed = self
        transformed.vertices = vertices.map { vertex in
            let v4 = simd_float4(vertex, 1)
            let transformed = matrix * v4
            return SIMD3<Float>(transformed.x, transformed.y, transformed.z)
        }
        return transformed
    }

    // Rotate mesh by given rotation matrix
    func rotated(by rotation: simd_float3x3) -> Mesh {
        var rotated = self
        rotated.vertices = vertices.map { rotation * $0 }
        return rotated
    }
}

struct BoundingBox {
    let min: SIMD3<Float>
    let max: SIMD3<Float>

    var size: SIMD3<Float> { max - min }
    var center: SIMD3<Float> { (min + max) * 0.5 }
}
