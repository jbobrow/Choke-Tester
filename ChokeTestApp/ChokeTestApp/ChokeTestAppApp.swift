//
//  ChokeTestApp.swift
//  Choke Test Safety Check
//
//  Native SwiftUI macOS application for analyzing 3D models against
//  safety-standard choke test cylinders.
//

import SwiftUI
import UniformTypeIdentifiers

@main
struct ChokeTestApp: App {
    @StateObject private var appState = AppState()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(appState)
                .frame(minWidth: 900, minHeight: 600)
        }
        .windowStyle(.hiddenTitleBar)
        .commands {
            CommandGroup(replacing: .newItem) {
                Button("Open STL...") {
                    appState.openFiles(ofType: [.stl])
                }
                .keyboardShortcut("o", modifiers: .command)

                Button("Open 3MF Project...") {
                    appState.openFiles(ofType: [.threemf])
                }
                .keyboardShortcut("o", modifiers: [.command, .shift])
            }

            CommandGroup(after: .newItem) {
                Divider()

                Button("Export PDF Report...") {
                    appState.exportPDF()
                }
                .keyboardShortcut("e", modifiers: .command)
                .disabled(appState.results.isEmpty)

                Button("Batch Process Folder...") {
                    appState.batchProcess()
                }
            }

            CommandGroup(replacing: .appSettings) {
                Button("Settings...") {
                    appState.showSettings()
                }
                .keyboardShortcut(",", modifiers: .command)
            }
        }
    }
}

// MARK: - App State

class AppState: ObservableObject {
    @Published var results: [ChokeTestResult] = []
    @Published var selectedResult: ChokeTestResult?
    @Published var isProcessing = false
    @Published var processingProgress: Double = 0
    @Published var standard: ChokeStandard = .usCPSC
    @Published var showingSettings = false

    func openFiles(ofType types: [FileType]) {
        let panel = NSOpenPanel()
        panel.allowsMultipleSelection = true
        panel.canChooseDirectories = false
        panel.allowedContentTypes = types.map { $0.contentType }

        panel.begin { response in
            guard response == .OK else { return }
            self.processFiles(panel.urls)
        }
    }

    func processFiles(_ urls: [URL]) {
        isProcessing = true
        processingProgress = 0
        results.removeAll()

        Task {
            let analyzer = ChokeTestAnalyzer(standard: standard)

            for (index, url) in urls.enumerated() {
                do {
                    let mesh = try await MeshLoader.load(from: url)
                    let result = await analyzer.analyze(mesh: mesh, name: url.lastPathComponent)

                    await MainActor.run {
                        results.append(result)
                        processingProgress = Double(index + 1) / Double(urls.count)
                    }
                } catch {
                    print("Error processing \(url.lastPathComponent): \(error)")
                }
            }

            await MainActor.run {
                isProcessing = false
            }
        }
    }

    func exportPDF() {
        let panel = NSSavePanel()
        panel.allowedContentTypes = [.pdf]
        panel.nameFieldStringValue = "choke_test_report.pdf"

        panel.begin { response in
            guard response == .OK, let url = panel.url else { return }
            PDFReportGenerator.generate(results: self.results, standard: self.standard, to: url)
        }
    }

    func batchProcess() {
        let panel = NSOpenPanel()
        panel.canChooseDirectories = true
        panel.canChooseFiles = false

        panel.begin { response in
            guard response == .OK, let url = panel.url else { return }

            let fileManager = FileManager.default
            guard let enumerator = fileManager.enumerator(at: url, includingPropertiesForKeys: nil) else { return }

            let urls = enumerator.compactMap { $0 as? URL }
                .filter { FileType.supported.contains($0.pathExtension.lowercased()) }

            self.processFiles(urls)
        }
    }

    func showSettings() {
        showingSettings = true
    }
}

// MARK: - File Types

enum FileType {
    case stl
    case threemf

    var contentType: UTType {
        switch self {
        case .stl:
            return UTType(filenameExtension: "stl") ?? .data
        case .threemf:
            return UTType(filenameExtension: "3mf") ?? .data
        }
    }

    static let supported = ["stl", "3mf"]
}
