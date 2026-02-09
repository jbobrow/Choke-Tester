//
//  ChokeStandard.swift
//  Choke Test Safety Check
//
//  Defines safety standards for choke test cylinders
//

import Foundation

struct ChokeStandard: Identifiable, Equatable {
    let id = UUID()
    let name: String
    let diameterMM: Double
    let heightMM: Double
    let description: String

    // Standard definitions
    static let usCPSC = ChokeStandard(
        name: "US CPSC",
        diameterMM: 31.75, // 1.25 inches
        heightMM: 57.15,   // 2.25 inches
        description: "US Consumer Product Safety Commission standard"
    )

    static let euEN71 = ChokeStandard(
        name: "EU EN-71",
        diameterMM: 31.2,  // ~1.23 inches
        heightMM: 52.3,    // ~2.06 inches
        description: "European toy safety standard"
    )

    static let all: [ChokeStandard] = [.usCPSC, .euEN71]

    var diameterInches: Double { diameterMM / 25.4 }
    var heightInches: Double { heightMM / 25.4 }
}
