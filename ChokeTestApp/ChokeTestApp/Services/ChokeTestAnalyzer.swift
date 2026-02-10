//
//  ChokeTestAnalyzer.swift
//  Choke Test Safety Check
//
//  Core algorithm for analyzing if a 3D mesh fits in a choke cylinder
//

import Foundation
import simd

actor ChokeTestAnalyzer {
    let standard: ChokeStandard
    private let testOrientations: Int = 360 // Number of orientations to test

    init(standard: ChokeStandard) {
        self.standard = standard
    }

    func analyze(mesh: Mesh, name: String) async -> ChokeTestResult {
        // Center the mesh at origin
        let centered = centerMesh(mesh)

        // Test various orientations
        var bestFit: (fits: Bool, diameter: Double, height: Double, rotation: simd_float3x3)?

        for i in 0..<testOrientations {
            let angle = (2.0 * .pi * Double(i)) / Double(testOrientations)
            let rotation = rotationMatrix(angle: Float(angle))
            let rotated = centered.rotated(by: rotation)

            // Project to 2D (looking down Z-axis)
            let projection = projectTo2D(rotated)

            // Calculate minimum enclosing circle
            let enclosingCircle = minimumEnclosingCircle(points: projection)

            // Get height (Z-axis extent)
            let height = getHeight(rotated)

            let diameterMM = Double(enclosingCircle.radius * 2)
            let heightMM = Double(height)

            // Check if it fits
            let fits = diameterMM <= standard.diameterMM && heightMM <= standard.heightMM

            if bestFit == nil || fits {
                bestFit = (fits, diameterMM, heightMM, rotation)
                if fits { break } // Found a hazardous orientation, stop
            }
        }

        guard let result = bestFit else {
            return ChokeTestResult(
                name: name,
                fits: false,
                diameterMM: nil,
                heightMM: nil,
                standard: standard,
                mesh: mesh,
                bestOrientation: nil,
                timestamp: Date()
            )
        }

        return ChokeTestResult(
            name: name,
            fits: result.fits,
            diameterMM: result.diameter,
            heightMM: result.height,
            standard: standard,
            mesh: mesh,
            bestOrientation: result.rotation,
            timestamp: Date()
        )
    }

    // MARK: - Helper Methods

    private func centerMesh(_ mesh: Mesh) -> Mesh {
        let center = mesh.center
        var centered = mesh
        centered.vertices = mesh.vertices.map { $0 - center }
        return centered
    }

    private func rotationMatrix(angle: Float) -> simd_float3x3 {
        // Rotate around Y-axis
        let cos = cosf(angle)
        let sin = sinf(angle)
        return simd_float3x3(
            SIMD3<Float>(cos, 0, sin),
            SIMD3<Float>(0, 1, 0),
            SIMD3<Float>(-sin, 0, cos)
        )
    }

    private func projectTo2D(_ mesh: Mesh) -> [SIMD2<Float>] {
        // Project vertices onto XY plane
        return mesh.vertices.map { SIMD2<Float>($0.x, $0.y) }
    }

    private func getHeight(_ mesh: Mesh) -> Float {
        guard !mesh.vertices.isEmpty else { return 0 }

        var minZ = mesh.vertices[0].z
        var maxZ = mesh.vertices[0].z

        for vertex in mesh.vertices {
            minZ = min(minZ, vertex.z)
            maxZ = max(maxZ, vertex.z)
        }

        return maxZ - minZ
    }

    // Simple iterative minimum enclosing circle algorithm
    // More robust than recursive Welzl's algorithm for large meshes
    private func minimumEnclosingCircle(points: [SIMD2<Float>]) -> Circle {
        guard !points.isEmpty else { return Circle(center: .zero, radius: 0) }
        guard points.count > 1 else { return Circle(center: points[0], radius: 0) }

        // Start with centroid as initial center
        var center = points.reduce(SIMD2<Float>.zero, +) / Float(points.count)

        // Find the farthest point from center
        var maxDist: Float = 0
        for point in points {
            let dist = distance(point, center)
            if dist > maxDist {
                maxDist = dist
            }
        }

        // Iteratively improve the circle
        for _ in 0..<10 {  // Limit iterations
            var farthestPoint = center
            var maxDistance: Float = 0

            // Find farthest point from current center
            for point in points {
                let dist = distance(point, center)
                if dist > maxDistance {
                    maxDistance = dist
                    farthestPoint = point
                }
            }

            // Move center slightly toward farthest point
            let direction = farthestPoint - center
            let moveAmount = maxDistance * 0.1
            center = center + normalize(direction) * moveAmount
            maxDist = max(maxDist, maxDistance)
        }

        // Final pass to ensure all points are inside
        var radius = maxDist
        for point in points {
            radius = max(radius, distance(point, center))
        }

        // Add small margin for floating point safety
        radius *= 1.01

        return Circle(center: center, radius: radius)
    }

    struct Circle {
        let center: SIMD2<Float>
        let radius: Float
    }
}
