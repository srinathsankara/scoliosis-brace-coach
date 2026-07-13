import SwiftUI

struct ResultsView: View {
    let result: AnalysisResult
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        ScrollView {
            VStack(spacing: 20) {
                headerBar
                if result.status == "error", let msg = result.message {
                    errorState(msg)
                } else if let metrics = result.metrics {
                    successContent(metrics)
                }
            }
            .padding(.vertical, 16)
        }
        .scrollDismissesKeyboard(.immediately)
        .background(Color.backgroundPrimary.ignoresSafeArea())
        .addDisclaimer()
    }

    // MARK: - Header

    private var headerBar: some View {
        HStack {
            Button {
                dismiss()
            } label: {
                HStack(spacing: 6) {
                    Image(systemName: "chevron.left")
                        .font(.caption.weight(.semibold))
                    Text("Back")
                        .font(.subheadline.weight(.semibold))
                }
                .foregroundColor(.accentTeal)
            }

            Spacer()

            if let sessionID = result.sessionID {
                ShareLink(item: "ScolioTrack Analysis: \(sessionID)") {
                    Image(systemName: "square.and.arrow.up")
                        .font(.subheadline)
                        .foregroundColor(.accentTeal)
                }
            }
        }
        .padding(.horizontal, 20)
    }

    // MARK: - Error

    private func errorState(_ msg: String) -> some View {
        VStack(spacing: 20) {
            Spacer().frame(height: 24)

            ZStack {
                Circle()
                    .fill(Color.statusPoorLight)
                    .frame(width: 96, height: 96)
                Image(systemName: "exclamationmark.triangle.fill")
                    .font(.system(size: 38, weight: .semibold))
                    .foregroundColor(.statusPoor)
            }

            Text("Analysis Failed")
                .font(AppFont.title(24))

            Text(msg)
                .font(.subheadline)
                .foregroundColor(.textSecondary)
                .multilineTextAlignment(.center)
                .padding(.horizontal, 32)

            Button {
                dismiss()
            } label: {
                Text("Try Again")
                    .font(.headline.weight(.semibold))
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 16)
                    .background(Color.accentTeal)
                    .foregroundColor(.white)
                    .clipShape(RoundedRectangle(cornerRadius: 14))
            }
            .padding(.horizontal, 40)
            .padding(.top, 8)
        }
    }

    // MARK: - Success

    private func successContent(_ metrics: MetricsResult) -> some View {
        VStack(spacing: 20) {
            headerBadge

            if let msg = result.message, !msg.isEmpty {
                HStack(spacing: 6) {
                    Image(systemName: "info.circle.fill")
                        .font(.caption)
                    Text(msg)
                        .font(.caption.weight(.medium))
                }
                .foregroundColor(.textSecondary)
                .padding(.horizontal, 14)
                .padding(.vertical, 8)
                .background(Color.cardBackground)
                .clipShape(Capsule())
                .shadow(color: .cardShadow, radius: 4, x: 0, y: 2)
            }

            overallScoreCard(metrics)
            metricsGrid(metrics)
            reportButton
        }
    }

    private var headerBadge: some View {
        HStack(spacing: 8) {
            if let brace = result.braceDetected {
                Label(brace ? "Brace On" : "No Brace", systemImage: brace ? "checkmark.shield.fill" : "shield.slash")
                    .font(.caption.weight(.semibold))
            }
            if let mode = result.mode {
                Text("•")
                    .foregroundColor(.textTertiary)
                Text(mode.replacingOccurrences(of: "_", with: " ").capitalized)
                    .font(.caption)
            }
        }
        .foregroundColor(.textSecondary)
        .padding(.horizontal, 16)
        .padding(.vertical, 8)
        .background(Color.cardBackground)
        .clipShape(Capsule())
        .shadow(color: .cardShadow, radius: 4, x: 0, y: 2)
    }

    // MARK: - Score Ring

    private func overallScoreCard(_ metrics: MetricsResult) -> some View {
        VStack(spacing: 16) {
            Text("Overall Assessment")
                .font(AppFont.headline())
                .foregroundColor(.textPrimary)

            ZStack {
                Circle()
                    .stroke(Color.dividerColor, lineWidth: 12)
                    .frame(width: 160, height: 160)

                Circle()
                    .trim(from: 0, to: CGFloat(min(metrics.backAsymmetryRisk, 100)) / 100)
                    .stroke(
                        AngularGradient(
                            colors: riskGradientColors(metrics.backAsymmetryRisk),
                            center: .center,
                            startAngle: .degrees(-90),
                            endAngle: .degrees(270)
                        ),
                        style: StrokeStyle(lineWidth: 12, lineCap: .round)
                    )
                    .frame(width: 160, height: 160)
                    .rotationEffect(.degrees(-90))

                VStack(spacing: 2) {
                    Text("\(Int(metrics.backAsymmetryRisk))")
                        .font(.system(size: 44, weight: .bold, design: .rounded))
                        .foregroundColor(.textPrimary)
                    Text("out of 100")
                        .font(.system(size: 11, weight: .medium, design: .rounded))
                        .foregroundColor(.textTertiary)
                }
            }

            Text(riskLabel(metrics.backAsymmetryRisk))
                .font(.title3.weight(.bold))
                .foregroundColor(Color.statusColor(riskStatus(metrics.backAsymmetryRisk)))

            if !metrics.backAsymmetryStatus.isEmpty {
                Text(metrics.backAsymmetryStatus
                    .replacingOccurrences(of: "_", with: " ").capitalized)
                    .font(.subheadline)
                    .foregroundColor(.textSecondary)
            }
        }
        .padding(.vertical, 28)
        .padding(.horizontal, 20)
        .frame(maxWidth: .infinity)
        .background(Color.cardBackground)
        .clipShape(RoundedRectangle(cornerRadius: 24))
        .shadow(color: .cardShadow, radius: 12, x: 0, y: 6)
        .padding(.horizontal, 20)
    }

    // MARK: - Metrics Grid

    private func metricsGrid(_ metrics: MetricsResult) -> some View {
        VStack(spacing: 12) {
            Text("Detailed Metrics")
                .font(AppFont.headline())
                .foregroundColor(.textPrimary)
                .frame(maxWidth: .infinity, alignment: .leading)
                .padding(.horizontal, 20)

            LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 12) {
                MetricCard(title: "Shoulder Asym.", value: "\(Int(metrics.shoulderAsymmetry)) px",
                           status: metrics.shoulderStatus, icon: "rectangle.3.group")
                MetricCard(title: "Trunk Lean", value: "\(Int(metrics.trunkLeanAngle))°",
                           status: metrics.trunkStatus, icon: "arrow.up.and.down")
                MetricCard(title: "Hip Asymmetry", value: "\(Int(metrics.hipAsymmetry)) px",
                           status: metrics.hipAsymmetry > 10 ? "needs_improvement" : "good", icon: "square.on.square")
                MetricCard(title: "Spine Deviation", value: "\(Int(metrics.spineDeviation)) px",
                           status: metrics.spineDeviation > 8 ? "needs_improvement" : "good", icon: "spine")
                MetricCard(title: "Rib Hump", value: "\(Int(metrics.ribHumpProxy))°",
                           status: metrics.ribHumpStatus, icon: "person.crop.circle")
                MetricCard(title: "Rotation Risk", value: "\(Int(metrics.rotationRiskScore))/100",
                           status: metrics.rotationStatus, icon: "arrow.triangle.2.circlepath")
            }
            .padding(.horizontal, 20)
        }
    }

    // MARK: - Report

    private var reportButton: some View {
        NavigationLink(destination: ReportView(sessionID: result.sessionID)) {
            Label("Generate PDF Report", systemImage: "doc.text.fill")
                .font(.headline.weight(.semibold))
                .frame(maxWidth: .infinity)
                .padding(.vertical, 16)
                .background(Color.cardBackground)
                .foregroundColor(.accentTeal)
                .clipShape(RoundedRectangle(cornerRadius: 14))
                .overlay(
                    RoundedRectangle(cornerRadius: 14)
                        .stroke(Color.accentTeal, lineWidth: 1.5)
                )
                .shadow(color: .cardShadow, radius: 4, x: 0, y: 2)
        }
        .padding(.horizontal, 20)
    }

    // MARK: - Helpers

    private func riskLabel(_ risk: Double) -> String {
        risk > 30 ? "Needs Attention" : risk > 15 ? "Monitor Closely" : "Looks Good"
    }

    private func riskStatus(_ risk: Double) -> String {
        risk > 30 ? "needs_attention" : risk > 15 ? "fair" : "good"
    }

    private func riskGradientColors(_ risk: Double) -> [Color] {
        risk > 30 ? [.statusPoor, .statusFair] : risk > 15 ? [.statusFair, .statusGood] : [.statusGood, .accentTeal]
    }
}

// MARK: - Metric Card

struct MetricCard: View {
    let title: String
    let value: String
    let status: String
    let icon: String

    var body: some View {
        VStack(spacing: 10) {
            ZStack {
                Circle()
                    .fill(Color.statusLight(status))
                    .frame(width: 40, height: 40)
                Image(systemName: icon)
                    .font(.system(size: 16, weight: .semibold))
                    .foregroundColor(Color.statusColor(status))
            }

            Text(title)
                .font(.caption.weight(.medium))
                .foregroundColor(.textSecondary)

            Text(value)
                .font(.title3.weight(.bold))
                .foregroundColor(.textPrimary)
        }
        .padding(.vertical, 16)
        .frame(maxWidth: .infinity)
        .background(Color.cardBackground)
        .clipShape(RoundedRectangle(cornerRadius: 14))
        .shadow(color: .cardShadow, radius: 6, x: 0, y: 3)
    }
}
