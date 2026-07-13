import SwiftUI

struct ComplianceView: View {
    @State private var summary: ComplianceSummary?
    @State private var sessions: [ComplianceSession] = []
    @State private var isTracking = false
    @State private var activeSession: ComplianceSession?
    @Environment(\.scenePhase) private var scenePhase

    var body: some View {
        ScrollView {
            VStack(spacing: 0) {
                headerBar
                VStack(spacing: 20) {
                    trackerCard

                    if let summary = summary {
                        statsGrid(summary)
                        progressCard(summary)
                        recentSessions
                    }
                }
                .padding(.horizontal, 20)
                .padding(.top, 8)
                .padding(.bottom, 32)
            }
        }
        .scrollDismissesKeyboard(.immediately)
        .background(Color.backgroundPrimary.ignoresSafeArea())
        .task { await loadSummary() }
        .onChange(of: scenePhase) { phase in
            guard isTracking, let session = activeSession else { return }
            if phase == .inactive || phase == .background {
                Task {
                    var s = session
                    s.endTime = Date()
                    s.wearMinutes = max(1, Int(Date().timeIntervalSince(s.startTime) / 60))
                    try? await DatabaseService.shared.updateComplianceSession(s)
                    isTracking = false
                    activeSession = nil
                    await loadSummary()
                }
            }
        }
    }

    private var headerBar: some View {
        HStack {
            Text("Compliance")
                .font(.system(size: 30, weight: .bold, design: .rounded))
                .foregroundColor(.textPrimary)
            Spacer()
        }
        .padding(.horizontal, 20)
        .padding(.vertical, 16)
    }

    // MARK: - Tracker

    private var trackerCard: some View {
        VStack(spacing: 16) {
            ZStack {
                Circle()
                    .fill(isTracking ? Color.statusGoodLight : Color.dividerColor)
                    .frame(width: 80, height: 80)

                Image(systemName: isTracking
                    ? "clock.badge.checkmark.fill"
                    : "clock.badge.exclamationmark")
                    .font(.system(size: 34))
                    .foregroundColor(isTracking ? .statusGood : .textTertiary)
            }

            Text(isTracking ? "Tracking Wear Time" : "Not Tracking")
                .font(AppFont.headline())

            Text(isTracking
                 ? "Your brace wear is being monitored"
                 : "Start tracking to log your brace wear time")
                .font(.subheadline)
                .foregroundColor(.textSecondary)

            Button {
                Task { await toggleTracking() }
            } label: {
                Text(isTracking ? "Stop Tracking" : "Start Tracking")
                    .font(.headline.weight(.semibold))
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 14)
                    .background(isTracking ? Color.statusPoor : Color.statusGood)
                    .foregroundColor(.white)
                    .clipShape(RoundedRectangle(cornerRadius: 14))
                    .shadow(color: (isTracking ? Color.statusPoor : Color.statusGood).opacity(0.3),
                            radius: 8, x: 0, y: 4)
            }
            .padding(.top, 4)
        }
        .padding(24)
        .background(Color.cardBackground)
        .clipShape(RoundedRectangle(cornerRadius: 20))
        .shadow(color: .cardShadow, radius: 12, x: 0, y: 6)
    }

    // MARK: - Stats

    private func statsGrid(_ summary: ComplianceSummary) -> some View {
        LazyVGrid(columns: [
            GridItem(.flexible()),
            GridItem(.flexible()),
            GridItem(.flexible())
        ], spacing: 12) {
            StatCard(label: "Today",
                     value: formatMinutes(summary.todayMinutes),
                     icon: "sun.max.fill",
                     color: summary.todayMinutes > 0 ? .statusGood : .textTertiary)
            StatCard(label: "This Week",
                     value: formatMinutes(summary.weekMinutes),
                     icon: "calendar.badge.clock",
                     color: .accentTeal)
            StatCard(label: "This Month",
                     value: formatMinutes(summary.monthMinutes),
                     icon: "calendar",
                     color: .accentBlue)
        }
    }

    // MARK: - Progress

    private func progressCard(_ summary: ComplianceSummary) -> some View {
        VStack(spacing: 12) {
            HStack {
                Text("Daily Average")
                    .font(AppFont.headline())
                    .foregroundColor(.textPrimary)
                Spacer()
                Text(formatMinutes(Int(summary.averageDailyMinutes)))
                    .font(.title3.weight(.bold))
                    .foregroundColor(summary.isOnTrack ? .statusGood : .statusFair)
            }

            ProgressView(value: min(summary.averageDailyMinutes / 780, 1.0))
                .tint(summary.isOnTrack ? .statusGood : .statusFair)

            HStack {
                Label("Target: 13h/day", systemImage: "target")
                    .font(.caption)
                    .foregroundColor(.textSecondary)
                Spacer()
                Text("\(summary.targetMetDays)/\(summary.totalDays) days")
                    .font(.caption.weight(.medium))
                    .foregroundColor(.textSecondary)
            }

            HStack(spacing: 6) {
                Image(systemName: summary.isOnTrack
                    ? "hand.thumbsup.fill" : "info.circle.fill")
                    .font(.caption)
                Text(summary.isOnTrack
                     ? "Great consistency! Keep it up."
                     : "Aim for 13 hours of daily brace wear")
                    .font(.caption)
            }
            .foregroundColor(summary.isOnTrack ? .statusGood : .statusFair)
            .padding(.vertical, 8)
            .padding(.horizontal, 12)
            .background((summary.isOnTrack ? Color.statusGood : Color.statusFair).opacity(0.1))
            .clipShape(RoundedRectangle(cornerRadius: 8))
        }
        .padding(20)
        .background(Color.cardBackground)
        .clipShape(RoundedRectangle(cornerRadius: 16))
        .shadow(color: .cardShadow, radius: 8, x: 0, y: 4)
    }

    // MARK: - Recent Sessions

    private var recentSessions: some View {
        VStack(spacing: 12) {
            if !sessions.isEmpty {
                Text("Recent Sessions")
                    .font(AppFont.headline())
                    .foregroundColor(.textPrimary)
                    .frame(maxWidth: .infinity, alignment: .leading)

                ForEach(sessions.prefix(5)) { session in
                    HStack(spacing: 12) {
                        ZStack {
                            Circle()
                                .fill(Color.accentTealLight)
                                .frame(width: 36, height: 36)
                            Image(systemName: "clock")
                                .font(.caption)
                                .foregroundColor(.accentTeal)
                        }

                        VStack(alignment: .leading, spacing: 2) {
                            Text(DateFormatter.localizedString(
                                from: session.startTime, dateStyle: .short, timeStyle: .short))
                                .font(.subheadline.weight(.medium))
                                .foregroundColor(.textPrimary)
                            if let end = session.endTime {
                                Text("\(formatMinutes(Int(end.timeIntervalSince(session.startTime) / 60)))")
                                    .font(.caption)
                                    .foregroundColor(.textSecondary)
                            }
                        }

                        Spacer()

                        Text(formatMinutes(session.wearMinutes))
                            .font(.subheadline.weight(.bold))
                            .foregroundColor(.accentTeal)
                            .padding(.horizontal, 10)
                            .padding(.vertical, 4)
                            .background(Color.accentTealLight)
                            .clipShape(Capsule())
                    }
                    .padding(14)
                    .background(Color.cardBackground)
                    .clipShape(RoundedRectangle(cornerRadius: 12))
                    .shadow(color: .cardShadow, radius: 4, x: 0, y: 2)
                }
            }
        }
    }

    // MARK: - Helpers

    private func loadSummary() async {
        summary = try? await DatabaseService.shared.getComplianceSummary()
        sessions = (try? await DatabaseService.shared.getAllComplianceSessions()) ?? []
    }

    private func toggleTracking() async {
        if isTracking, var session = activeSession {
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

    private func formatMinutes(_ minutes: Int) -> String {
        let h = minutes / 60
        let m = minutes % 60
        return "\(h)h \(m)m"
    }
}

// MARK: - Stat Card

struct StatCard: View {
    let label: String
    let value: String
    let icon: String
    let color: Color

    var body: some View {
        VStack(spacing: 8) {
            Image(systemName: icon)
                .font(.title3)
                .foregroundColor(color)
            Text(value)
                .font(.title3.weight(.bold))
                .foregroundColor(.textPrimary)
                .minimumScaleFactor(0.7)
                .lineLimit(1)
            Text(label)
                .font(.caption2)
                .foregroundColor(.textSecondary)
        }
        .padding(14)
        .frame(maxWidth: .infinity)
        .background(Color.cardBackground)
        .clipShape(RoundedRectangle(cornerRadius: 14))
        .shadow(color: .cardShadow, radius: 4, x: 0, y: 2)
    }
}
