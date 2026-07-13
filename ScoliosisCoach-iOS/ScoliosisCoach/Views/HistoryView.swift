import SwiftUI

struct HistoryView: View {
    @State private var sessions: [Session] = []
    @State private var isLoading = true
    @State private var showDeleteAll = false

    var body: some View {
        ScrollView {
            VStack(spacing: 0) {
                headerBar

                if isLoading {
                    Spacer().frame(height: 120)
                    ProgressView()
                        .tint(.accentTeal)
                    Spacer()
                } else if sessions.isEmpty {
                    emptyState
                } else {
                    sessionList
                }
            }
            .frame(minHeight: UIScreen.main.bounds.height - 120)
        }
        .scrollDismissesKeyboard(.immediately)
        .background(Color.backgroundPrimary.ignoresSafeArea())
        .task { await loadSessions() }
        .alert("Clear All Sessions?", isPresented: $showDeleteAll) {
            Button("Cancel", role: .cancel) {}
            Button("Delete All", role: .destructive) { clearAllSessions() }
        } message: {
            Text("This will permanently delete all analysis sessions.")
        }
    }

    private var headerBar: some View {
        HStack {
            Text("History")
                .font(.system(size: 30, weight: .bold, design: .rounded))
                .foregroundColor(.textPrimary)

            Spacer()

            if !sessions.isEmpty {
                Button(role: .destructive) {
                    showDeleteAll = true
                } label: {
                    Image(systemName: "trash")
                        .font(.subheadline)
                        .foregroundColor(.statusPoor)
                        .padding(10)
                        .background(Color.statusPoorLight)
                        .clipShape(Circle())
                }
            }
        }
        .padding(.horizontal, 20)
        .padding(.vertical, 16)
    }

    private var emptyState: some View {
        VStack(spacing: 20) {
            Spacer().frame(height: 60)

            ZStack {
                Circle()
                    .fill(Color.accentTealLight)
                    .frame(width: 96, height: 96)
                Image(systemName: "clock.arrow.circlepath")
                    .font(.system(size: 38))
                    .foregroundColor(.accentTeal)
            }

            Text("No Sessions Yet")
                .font(AppFont.title(24))

            Text("Take a posture photo from the Analyze tab to get started")
                .font(.subheadline)
                .foregroundColor(.textSecondary)
                .multilineTextAlignment(.center)
                .padding(.horizontal, 40)

            Spacer()
        }
    }

    private var sessionList: some View {
        LazyVStack(spacing: 10) {
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
                    SessionRow(session: session)
                }
                .buttonStyle(.plain)
            }
        }
        .padding(.horizontal, 20)
    }

    private func loadSessions() async {
        isLoading = true
        sessions = (try? await DatabaseService.shared.getAllSessions(limit: 100)) ?? []
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

// MARK: - Session Row

struct SessionRow: View {
    let session: Session

    private var modeIcon: String {
        if session.mode == "xray" { return "spine" }
        if session.mode.contains("standing") { return "figure.stand" }
        if session.mode.contains("walking") { return "figure.walk" }
        return "figure.core.training"
    }

    private var metrics: MetricsResult? {
        try? JSONDecoder().decode(MetricsResult.self, from: session.metricsJSON)
    }

    var body: some View {
        HStack(spacing: 14) {
            ZStack {
                Circle()
                    .fill(Color.accentTealLight)
                    .frame(width: 44, height: 44)
                Image(systemName: modeIcon)
                    .font(.system(size: 18, weight: .semibold))
                    .foregroundColor(.accentTeal)
            }

            VStack(alignment: .leading, spacing: 3) {
                Text(session.mode
                    .replacingOccurrences(of: "_", with: " ")
                    .capitalized)
                    .font(.subheadline.weight(.semibold))
                    .foregroundColor(.textPrimary)
                Text(DateFormatter.localizedString(
                    from: session.createdAt,
                    dateStyle: .medium,
                    timeStyle: .short))
                    .font(.caption)
                    .foregroundColor(.textSecondary)
            }

            Spacer()

            if session.braceDetected {
                Image(systemName: "shield.fill")
                    .font(.caption)
                    .foregroundColor(.statusGood)
            }

            if let m = metrics {
                riskBadge(value: m.backAsymmetryRisk)
            }
        }
        .padding(14)
        .background(Color.cardBackground)
        .clipShape(RoundedRectangle(cornerRadius: 14))
        .shadow(color: .cardShadow, radius: 6, x: 0, y: 3)
    }

    private func riskBadge(value: Double) -> some View {
        Text("\(Int(value))%")
            .font(.subheadline.weight(.bold))
            .foregroundColor(Color.statusColor(riskStatus(value)))
            .padding(.horizontal, 10)
            .padding(.vertical, 4)
            .background(Color.statusLight(riskStatus(value)))
            .clipShape(Capsule())
    }

    private func riskStatus(_ risk: Double) -> String {
        risk > 30 ? "needs_attention" : risk > 15 ? "fair" : "good"
    }
}
