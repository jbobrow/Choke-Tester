//
//  MeshPreviewView.swift
//  Choke Test Safety Check
//
//  3D preview of mesh using SceneKit
//

import SwiftUI
import SceneKit

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
            SceneKitView(mesh: result.mesh, showCylinder: result.fits)
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

        // Add mesh
        let meshNode = createMeshNode(from: mesh)
        meshNode.geometry?.firstMaterial?.diffuse.contents = NSColor.systemBlue
        meshNode.geometry?.firstMaterial?.specular.contents = NSColor.white
        scene.rootNode.addChildNode(meshNode)

        // Add choke cylinder if object is a hazard
        if showCylinder {
            let cylinderNode = createCylinderNode()
            cylinderNode.geometry?.firstMaterial?.diffuse.contents = NSColor.systemRed.withAlphaComponent(0.2)
            cylinderNode.geometry?.firstMaterial?.transparency = 0.3
            scene.rootNode.addChildNode(cylinderNode)
        }

        // Add camera
        let cameraNode = SCNNode()
        cameraNode.camera = SCNCamera()
        cameraNode.position = SCNVector3(x: 0, y: 0, z: 100)
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

    private func createCylinderNode() -> SCNNode {
        let cylinder = SCNCylinder(radius: 15, height: 30) // Approximate visualization
        return SCNNode(geometry: cylinder)
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
