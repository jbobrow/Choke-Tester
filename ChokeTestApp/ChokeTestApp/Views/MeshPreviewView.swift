//
//  MeshPreviewView.swift
//  Choke Test Safety Check
//
//  3D preview of mesh using SceneKit
//

import SwiftUI
import SceneKit
import AppKit

struct MeshPreviewView: View {
    let result: ChokeTestResult

    var body: some View {
        VStack(spacing: 0) {
            // Header
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text(result.name)
                        .font(.headline)

                    HStack(spacing: 12) {
                        StatusBadge(result: result)

                        if let diameter = result.diameterMM, let height = result.heightMM {
                            Text("Ø\(String(format: "%.1f", diameter))mm × \(String(format: "%.1f", height))mm")
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                    }
                }

                Spacer()
            }
            .padding()
            .background(Color(nsColor: .controlBackgroundColor))

            Divider()

            // 3D View
            SceneKitView(
                mesh: result.mesh,
                showCylinder: result.fits,
                isHazard: result.fits,
                standard: result.standard,
                bestOrientation: result.bestOrientation
            )
            .frame(maxWidth: .infinity, maxHeight: .infinity)
        }
    }
}

struct StatusBadge: View {
    let result: ChokeTestResult

    var body: some View {
        HStack(spacing: 6) {
            Circle()
                .fill(Color(nsColor: result.status.color))
                .frame(width: 8, height: 8)

            Text(result.statusText)
                .font(.caption)
                .fontWeight(.medium)
        }
        .padding(.horizontal, 10)
        .padding(.vertical, 4)
        .background(
            Capsule()
                .fill(Color(nsColor: result.status.color).opacity(0.1))
        )
    }
}

// MARK: - SceneKit View

struct SceneKitView: NSViewRepresentable {
    let mesh: Mesh
    let showCylinder: Bool
    let isHazard: Bool
    let standard: ChokeStandard
    let bestOrientation: simd_float3x3?

    func makeNSView(context: Context) -> SCNView {
        let scnView = SCNView()
        scnView.scene = createScene()
        scnView.allowsCameraControl = true
        scnView.autoenablesDefaultLighting = true
        scnView.backgroundColor = NSColor.textBackgroundColor

        return scnView
    }

    func updateNSView(_ nsView: SCNView, context: Context) {
        nsView.scene = createScene()
    }

    private func createScene() -> SCNScene {
        let scene = SCNScene()

        // Calculate mesh bounds for proper scaling
        let bounds = mesh.bounds
        let meshSize = bounds.size
        let maxDimension = max(meshSize.x, max(meshSize.y, meshSize.z))

        // Add mesh (oriented and colored)
        let meshNode = createMeshNode(from: mesh)

        // Color based on hazard status
        let meshColor = isHazard ? NSColor.systemRed : NSColor.systemGreen
        meshNode.geometry?.firstMaterial?.diffuse.contents = meshColor
        meshNode.geometry?.firstMaterial?.specular.contents = NSColor.white
        meshNode.geometry?.firstMaterial?.shininess = 0.8

        // Apply best orientation if available (for hazards)
        if let orientation = bestOrientation, isHazard {
            let transform = SCNMatrix4(orientation)
            meshNode.transform = transform
        }

        scene.rootNode.addChildNode(meshNode)

        // Add choke cylinder for reference (semi-transparent)
        let cylinderNode = createCylinderNode(standard: standard)
        if showCylinder {
            cylinderNode.geometry?.firstMaterial?.diffuse.contents = NSColor.systemRed.withAlphaComponent(0.15)
        } else {
            cylinderNode.geometry?.firstMaterial?.diffuse.contents = NSColor.systemBlue.withAlphaComponent(0.1)
        }
        cylinderNode.geometry?.firstMaterial?.transparency = 0.25
        cylinderNode.geometry?.firstMaterial?.isDoubleSided = true
        scene.rootNode.addChildNode(cylinderNode)

        // Position camera based on scene bounds
        let cameraDistance = max(maxDimension * 3, 80.0) // Ensure camera is far enough
        let cameraNode = SCNNode()
        cameraNode.camera = SCNCamera()
        cameraNode.camera?.zNear = 1.0
        cameraNode.camera?.zFar = Double(cameraDistance * 3)
        cameraNode.position = SCNVector3(x: Float(cameraDistance) * 0.5,
                                         y: Float(cameraDistance) * 0.3,
                                         z: Float(cameraDistance))
        cameraNode.look(at: SCNVector3(0, 0, 0))
        scene.rootNode.addChildNode(cameraNode)

        return scene
    }

    private func createMeshNode(from mesh: Mesh) -> SCNNode {
        let vertices = mesh.vertices.map { SCNVector3($0.x, $0.y, $0.z) }

        var indices: [Int32] = []
        for triangle in mesh.triangles {
            indices.append(Int32(triangle.v0))
            indices.append(Int32(triangle.v1))
            indices.append(Int32(triangle.v2))
        }

        let vertexSource = SCNGeometrySource(vertices: vertices)
        let indexData = Data(bytes: indices, count: indices.count * MemoryLayout<Int32>.size)
        let element = SCNGeometryElement(
            data: indexData,
            primitiveType: .triangles,
            primitiveCount: indices.count / 3,
            bytesPerIndex: MemoryLayout<Int32>.size
        )

        let geometry = SCNGeometry(sources: [vertexSource], elements: [element])
        return SCNNode(geometry: geometry)
    }

    private func createCylinderNode(standard: ChokeStandard) -> SCNNode {
        // Use actual standard dimensions (convert mm to same scale as mesh)
        let radius = CGFloat(standard.diameterMM / 2.0)
        let height = CGFloat(standard.heightMM)

        let cylinder = SCNCylinder(radius: radius, height: height)
        let node = SCNNode(geometry: cylinder)

        // Rotate cylinder to stand upright (default is lying down)
        node.eulerAngles = SCNVector3(0, 0, 0) // Already upright in SceneKit

        return node
    }
}

// Helper to convert simd matrix to SCNMatrix4
extension SCNMatrix4 {
    init(_ m: simd_float3x3) {
        self.init(
            m11: CGFloat(m[0][0]), m12: CGFloat(m[0][1]), m13: CGFloat(m[0][2]), m14: 0,
            m21: CGFloat(m[1][0]), m22: CGFloat(m[1][1]), m23: CGFloat(m[1][2]), m24: 0,
            m31: CGFloat(m[2][0]), m32: CGFloat(m[2][1]), m33: CGFloat(m[2][2]), m34: 0,
            m41: 0,                m42: 0,                m43: 0,                m44: 1
        )
    }
}

#Preview {
    MeshPreviewView(result: ChokeTestResult(
        name: "test.stl",
        fits: true,
        diameterMM: 28.5,
        heightMM: 45.2,
        standard: .usCPSC,
        mesh: Mesh(vertices: [], triangles: [], name: "test"),
        bestOrientation: nil,
        timestamp: Date()
    ))
    .frame(width: 500, height: 600)
}
