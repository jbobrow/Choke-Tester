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

    // Welzl's algorithm for minimum enclosing circle
    private func minimumEnclosingCircle(points: [SIMD2<Float>]) -> Circle {
        guard !points.isEmpty else { return Circle(center: .zero, radius: 0) }

        return welzl(points: points, boundary: [])
    }

    private func welzl(points: [SIMD2<Float>], boundary: [SIMD2<Float>]) -> Circle {
        // Base cases
        if boundary.count == 3 {
            return circleFromThreePoints(boundary[0], boundary[1], boundary[2])
        }

        if points.isEmpty {
            if boundary.isEmpty { return Circle(center: .zero, radius: 0) }
            if boundary.count == 1 { return Circle(center: boundary[0], radius: 0) }
            if boundary.count == 2 {
                let center = (boundary[0] + boundary[1]) * 0.5
                let radius = distance(boundary[0], boundary[1]) * 0.5
                return Circle(center: center, radius: radius)
            }
        }

        guard !points.isEmpty else {
            return circleFromThreePoints(boundary[0], boundary[1], boundary[2])
        }

        // Recursive case
        var remainingPoints = points
        let p = remainingPoints.removeFirst()
        let circle = welzl(points: remainingPoints, boundary: boundary)

        // Check if point is inside circle
        if distance(p, circle.center) <= circle.radius {
            return circle
        }

        // Point is outside, must be on boundary
        var newBoundary = boundary
        newBoundary.append(p)
        return welzl(points: remainingPoints, boundary: newBoundary)
    }

    private func circleFromThreePoints(_ p1: SIMD2<Float>, _ p2: SIMD2<Float>, _ p3: SIMD2<Float>) -> Circle {
        // Calculate circumcircle of three points
        let ax = p1.x; let ay = p1.y
        let bx = p2.x; let by = p2.y
        let cx = p3.x; let cy = p3.y

        let d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))

        guard abs(d) > 1e-6 else {
            // Points are collinear, use diameter of farthest points
            let center = (p1 + p2 + p3) / 3
            let r1 = distance(p1, center)
            let r2 = distance(p2, center)
            let r3 = distance(p3, center)
            return Circle(center: center, radius: max(r1, max(r2, r3)))
        }

        let ux = ((ax * ax + ay * ay) * (by - cy) + (bx * bx + by * by) * (cy - ay) + (cx * cx + cy * cy) * (ay - by)) / d
        let uy = ((ax * ax + ay * ay) * (cx - bx) + (bx * bx + by * by) * (ax - cx) + (cx * cx + cy * cy) * (bx - ax)) / d

        let center = SIMD2<Float>(ux, uy)
        let radius = distance(center, p1)

        return Circle(center: center, radius: radius)
    }

    struct Circle {
        let center: SIMD2<Float>
        let radius: Float
    }
}
