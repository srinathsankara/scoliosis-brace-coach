import SwiftUI

struct ComplianceView: View {
    @State private var summary: ComplianceSummary?
    @State private var sessions: [ComplianceSession] = []
    @State private var isTracking = false
    @State private var activeSession: ComplianceSession?

    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 16) {
                    // Wear tracker
                    VStack(spacing: 8) {
                        Image(systemName: isTracking ? "clock.badge.checkmark" : "clock.badge.exclamationmark")
                            .font(.system(size: 40))
                            .foregroundColor(isTracking ? .green : .gray)
                        Text(isTracking ? "Tracking Wear Time" : "Not Tracking")
                            .font(.headline)

                        Button(isTracking ? "Stop Tracking" : "Start Tracking") {
                            Task { await toggleTracking() }
                        }
                        .buttonStyle(.borderedProminent)
                        .tint(isTracking ? .red : .green)
                    }
                    .padding()
                    .frame(maxWidth: .infinity)
                    .background(Color(.systemGray6))
                    .cornerRadius(12)
                    .padding(.horizontal)

                    // Summary cards
                    if let summary = summary {
                        LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible()), GridItem(.flexible())], spacing: 12) {
                            StatCard(label: "Today", value: "\(summary.todayMinutes / 60)h \(summary.todayMinutes % 60)m")
                            StatCard(label: "Week", value: "\(summary.weekMinutes / 60)h \(summary.weekMinutes % 60)m")
                            StatCard(label: "Month", value: "\(summary.monthMinutes / 60)h \(summary.monthMinutes % 60)m")
                        }
                        .padding(.horizontal)

                        VStack(alignment: .leading, spacing: 4) {
                            Text("Daily Average: \(Int(summary.averageDailyMinutes)) min")
                            Text("Target Met: \(summary.targetMetDays)/\(summary.totalDays) days")
                                .foregroundColor(.secondary)
                        }
                        .padding()
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .background(Color(.systemGray6))
                        .cornerRadius(10)
                        .padding(.horizontal)
                    }

                    // Recent sessions
                    if !sessions.isEmpty {
                        Text("Recent Sessions")
                            .font(.headline)
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .padding(.horizontal)

                        ForEach(sessions.prefix(10)) { session in
                            HStack {
                                Text(DateFormatter.localizedString(from: session.startTime, dateStyle: .short, timeStyle: .short))
                                Spacer()
                                Text("\(session.wearMinutes) min")
                                    .bold()
                            }
                            .padding(.horizontal)
                        }
                    }
                }
                .padding(.vertical)
            }
            .navigationTitle("Compliance")
        }
        .task { await loadSummary() }
    }

    private func loadSummary() async {
        summary = try? await DatabaseService.shared.getComplianceSummary()
        sessions = (try? await DatabaseService.shared.getAllComplianceSessions()) ?? []
    }

    private func toggleTracking() async {
        if isTracking, let session = activeSession {
            session.endTime = Date()
            let minutes = Int(Date().timeIntervalSince(session.startTime) / 60)
            session.wearMinutes = max(1, minutes)
            try? await DatabaseService.shared.updateComplianceSession(session)
            isTracking = false
            activeSession = nil
        } else {
            let session = ComplianceSession(
                id: UUID().uuidString,
                startTime: Date(),
                endTime: nil,
                wearMinutes: 0,
                skinTempReadings: Data(),
                isActive: true
            )
            try? await DatabaseService.shared.saveComplianceSession(session)
            activeSession = session
            isTracking = true
        }
        await loadSummary()
    }
}

struct StatCard: View {
    let label: String
    let value: String

    var body: some View {
        VStack(spacing: 4) {
            Text(value)
                .font(.title2).bold()
            Text(label)
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .padding()
        .frame(maxWidth: .infinity)
        .background(Color(.systemGray6))
        .cornerRadius(10)
    }
}
