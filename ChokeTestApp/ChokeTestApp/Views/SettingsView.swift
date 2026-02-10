//
//  SettingsView.swift
//  Choke Test Safety Check
//
//  Settings panel for selecting safety standard
//

import SwiftUI

struct SettingsView: View {
    @EnvironmentObject var appState: AppState
    @Environment(\.dismiss) var dismiss

    var body: some View {
        VStack(spacing: 0) {
            // Header
            HStack {
                Text("Settings")
                    .font(.title2)
                    .fontWeight(.semibold)

                Spacer()

                Button("Done") {
                    dismiss()
                }
                .keyboardShortcut(.defaultAction)
            }
            .padding()

            Divider()

            // Content
            Form {
                Section {
                    Picker("Safety Standard", selection: $appState.standard) {
                        ForEach(ChokeStandard.all) { standard in
                            VStack(alignment: .leading, spacing: 4) {
                                Text(standard.name)
                                    .font(.body)

                                Text(standard.description)
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                            }
                            .tag(standard)
                        }
                    }
                    .pickerStyle(.radioGroup)
                } header: {
                    Text("Choke Cylinder Standard")
                        .font(.headline)
                }

                Section {
                    VStack(alignment: .leading, spacing: 8) {
                        HStack {
                            Text("Diameter:")
                                .fontWeight(.medium)
                            Spacer()
                            Text("\(String(format: "%.2f", appState.standard.diameterMM))mm (\(String(format: "%.2f", appState.standard.diameterInches))\")")
                                .foregroundColor(.secondary)
                        }

                        HStack {
                            Text("Height:")
                                .fontWeight(.medium)
                            Spacer()
                            Text("\(String(format: "%.2f", appState.standard.heightMM))mm (\(String(format: "%.2f", appState.standard.heightInches))\")")
                                .foregroundColor(.secondary)
                        }
                    }
                } header: {
                    Text("Current Standard Dimensions")
                        .font(.headline)
                }

                Section {
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Objects that can fit entirely within the choke cylinder in any orientation are flagged as potential choking hazards.")
                            .font(.caption)
                            .foregroundColor(.secondary)

                        Text("This tool is for informational purposes only. Always follow official safety guidelines when creating products for children.")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                } header: {
                    Text("About")
                        .font(.headline)
                }
            }
            .formStyle(.grouped)
            .padding()
        }
        .frame(width: 500, height: 500)
    }
}

#Preview {
    SettingsView()
        .environmentObject(AppState())
}
