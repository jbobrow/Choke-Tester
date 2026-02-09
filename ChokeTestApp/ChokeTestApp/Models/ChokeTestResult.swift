//
//  ChokeTestResult.swift
//  Choke Test Safety Check
//
//  Result of a choke test analysis
//

import Foundation

struct ChokeTestResult: Identifiable, Equatable {
    let id = UUID()
    let name: String
    let fits: Bool
    let diameterMM: Double?
    let heightMM: Double?
    let standard: ChokeStandard
    let mesh: Mesh
    let bestOrientation: simd_float3x3?
    let timestamp: Date

    var status: Status {
        fits ? .hazard : .safe
    }

    var statusText: String {
        fits ? "CHOKING HAZARD" : "SAFE"
    }

    enum Status {
        case hazard
        case safe

        var color: NSColor {
            switch self {
            case .hazard: return .systemRed
            case .safe: return .systemGreen
            }
        }
    }

    static func == (lhs: ChokeTestResult, rhs: ChokeTestResult) -> Bool {
        lhs.id == rhs.id
    }
}
