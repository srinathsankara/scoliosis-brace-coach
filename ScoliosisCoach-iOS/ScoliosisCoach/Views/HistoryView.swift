import SwiftUI

struct HistoryView: View {
    @State private var sessions: [Session] = []
    @State private var isLoading = true
    @State private var selectedMode: String?
    @State private var showingFilter = false
    @State private var showDeleteAll = false

    var body: some View {
        NavigationView {
            Group {
                if isLoading {
                    ProgressView("Loading...")
                } else if sessions.isEmpty {
                    VStack(spacing: 12) {
                        Image(systemName: "tray")
                            .font(.system(size: 48))
                            .foregroundColor(.secondary)
                        Text("No sessions yet")
                            .font(.title2)
                        Text("Take a photo from the Analyze tab to get started")
                            .foregroundColor(.secondary)
                    }
                } else {
                    List {
                        ForEach(sessions) { session in
                            NavigationLink(destination: ResultsView(
                                result: AnalysisResult(
                                    status: "success",
                                    mode: session.mode,
                                    braceDetected: session.braceDetected,
                                    metrics: try? JSONDecoder().decode(MetricsResult.self, from: session.metricsJSON),
                                    sessionID: session.id
                                )
                            )) {
                                HStack {
                                    VStack(alignment: .leading) {
                                        Text(session.mode.replacingOccurrences(of: "_", with: " ").capitalized)
                                            .font(.headline)
                                        Text(DateFormatter.localizedString(from: session.createdAt, dateStyle: .medium, timeStyle: .short))
                                            .font(.caption)
                                            .foregroundColor(.secondary)
                                    }
                                    Spacer()
                                    if session.braceDetected {
                                        Image(systemName: "shield.fill")
                                            .foregroundColor(.green)
                                    }
                                    if let metrics = try? JSONDecoder().decode(MetricsResult.self, from: session.metricsJSON) {
                                        Text("\(Int(metrics.backAsymmetryRisk))%")
                                            .font(.subheadline).bold()
                                            .foregroundColor(metrics.backAsymmetryRisk > 20 ? .orange : .green)
                                    }
                                }
                            }
                        }
                        .onDelete(perform: deleteSessions)
                    }
                    .toolbar {
                        ToolbarItem(placement: .navigationBarTrailing) {
                            Button("Clear All") { showDeleteAll = true }
                        }
                    }
                    .alert("Clear All Sessions?", isPresented: $showDeleteAll) {
                        Button("Cancel", role: .cancel) {}
                        Button("Delete All", role: .destructive) { clearAllSessions() }
                    }
                }
            }
            .navigationTitle("History")
        }
        .task { await loadSessions() }
    }

    private func loadSessions() async {
        isLoading = true
        sessions = try! await DatabaseService.shared.getAllSessions(limit: 100)
        isLoading = false
    }

    private func deleteSessions(at offsets: IndexSet) {
        Task {
            for index in offsets {
                try? await DatabaseService.shared.deleteSession(id: sessions[index].id)
            }
            sessions.remove(atOffsets: offsets)
        }
    }

    private func clearAllSessions() {
        Task {
            try? await DatabaseService.shared.deleteAllSessions()
            sessions = []
        }
    }
}
