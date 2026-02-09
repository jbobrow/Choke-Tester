//
//  ContentView.swift
//  Choke Test Safety Check
//
//  Main application view with minimalist design
//

import SwiftUI

struct ContentView: View {
    @EnvironmentObject var appState: AppState

    var body: some View {
        ZStack {
            if appState.results.isEmpty && !appState.isProcessing {
                DropZoneView()
            } else {
                MainWorkspaceView()
            }

            if appState.isProcessing {
                ProcessingOverlay()
            }
        }
        .sheet(isPresented: $appState.showingSettings) {
            SettingsView()
        }
    }
}

// MARK: - Drop Zone

struct DropZoneView: View {
    @EnvironmentObject var appState: AppState

    var body: some View {
        VStack(spacing: 24) {
            Image(systemName: "cube.transparent")
                .font(.system(size: 80))
                .foregroundColor(.secondary)

            VStack(spacing: 8) {
                Text("Drop 3D Models Here")
                    .font(.title2)
                    .fontWeight(.medium)

                Text("Supports .stl and .3mf files")
                    .font(.subheadline)
                    .foregroundColor(.secondary)
            }

            HStack(spacing: 16) {
                Button("Open STL...") {
                    appState.openFiles(ofType: [.stl])
                }
                .buttonStyle(.borderedProminent)

                Button("Open 3MF...") {
                    appState.openFiles(ofType: [.threemf])
                }
                .buttonStyle(.bordered)
            }
            .controlSize(.large)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(Color(nsColor: .windowBackgroundColor))
        .onDrop(of: ["public.file-url"], isTargeted: nil) { providers in
            handleDrop(providers)
        }
    }

    private func handleDrop(_ providers: [NSItemProvider]) -> Bool {
        for provider in providers {
            _ = provider.loadObject(ofClass: URL.self) { url, _ in
                guard let url = url else { return }
                DispatchQueue.main.async {
                    appState.processFiles([url])
                }
            }
        }
        return true
    }
}

// MARK: - Main Workspace

struct MainWorkspaceView: View {
    @EnvironmentObject var appState: AppState

    var body: some View {
        HSplitView {
            ResultsListView()
                .frame(minWidth: 300, idealWidth: 400)

            if let result = appState.selectedResult {
                MeshPreviewView(result: result)
                    .frame(minWidth: 400)
            } else {
                EmptyPreviewView()
            }
        }
    }
}

// MARK: - Results List

struct ResultsListView: View {
    @EnvironmentObject var appState: AppState

    var body: some View {
        VStack(spacing: 0) {
            // Header
            HStack {
                Text("Results")
                    .font(.headline)

                Spacer()

                Text("\(appState.results.count) objects")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            .padding()
            .background(Color(nsColor: .controlBackgroundColor))

            Divider()

            // List
            List(appState.results, selection: $appState.selectedResult) { result in
                ResultRow(result: result)
                    .tag(result)
            }
            .listStyle(.plain)
        }
    }
}

struct ResultRow: View {
    let result: ChokeTestResult

    var body: some View {
        HStack(spacing: 12) {
            // Status indicator
            Circle()
                .fill(Color(nsColor: result.status.color))
                .frame(width: 10, height: 10)

            VStack(alignment: .leading, spacing: 4) {
                Text(result.name)
                    .font(.body)
                    .lineLimit(1)

                HStack(spacing: 8) {
                    if let diameter = result.diameterMM {
                        Label("Ø\(String(format: "%.1f", diameter))mm", systemImage: "circle")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }

                    if let height = result.heightMM {
                        Label("\(String(format: "%.1f", height))mm", systemImage: "arrow.up.and.down")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
            }

            Spacer()

            Text(result.statusText)
                .font(.caption)
                .fontWeight(.medium)
                .foregroundColor(Color(nsColor: result.status.color))
        }
        .padding(.vertical, 4)
    }
}

// MARK: - Empty Preview

struct EmptyPreviewView: View {
    var body: some View {
        VStack(spacing: 16) {
            Image(systemName: "cube.transparent")
                .font(.system(size: 60))
                .foregroundColor(.secondary)

            Text("Select an object to preview")
                .font(.subheadline)
                .foregroundColor(.secondary)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(Color(nsColor: .textBackgroundColor))
    }
}

// MARK: - Processing Overlay

struct ProcessingOverlay: View {
    @EnvironmentObject var appState: AppState

    var body: some View {
        ZStack {
            Color.black.opacity(0.3)
                .ignoresSafeArea()

            VStack(spacing: 20) {
                ProgressView(value: appState.processingProgress) {
                    Text("Analyzing Models...")
                        .font(.headline)
                }
                .progressViewStyle(.linear)
                .frame(width: 300)

                Text("\(Int(appState.processingProgress * 100))%")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            .padding(30)
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(Color(nsColor: .windowBackgroundColor))
                    .shadow(radius: 20)
            )
        }
    }
}

#Preview {
    ContentView()
        .environmentObject(AppState())
        .frame(width: 900, height: 600)
}
