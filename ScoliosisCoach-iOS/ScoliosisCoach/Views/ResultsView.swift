import SwiftUI

struct ResultsView: View {
    let result: AnalysisResult

    var body: some View {
        NavigationView {
            ScrollView {
                VStack(alignment: .leading, spacing: 16) {
                    // Header
                    if result.status == "error", let msg = result.message {
                        VStack(spacing: 8) {
                            Image(systemName: "exclamationmark.triangle.fill")
                                .font(.system(size: 48))
                                .foregroundColor(.orange)
                            Text("Analysis Failed")
                                .font(.title2).bold()
                            Text(msg)
                                .foregroundColor(.secondary)
                        }
                        .frame(maxWidth: .infinity)
                        .padding()
                    } else if let metrics = result.metrics {
                        // Brace status
                        if let brace = result.braceDetected {
                            HStack {
                                Image(systemName: brace ? "checkmark.shield.fill" : "shield.slash")
                                    .foregroundColor(brace ? .green : .orange)
                                Text(brace ? "Brace Detected" : "No Brace Detected")
                                    .font(.headline)
                            }
                            .padding(.horizontal)
                        }

                        // Spinal curvature score
                        ScoreCard(
                            title: "Spinal Curvature Assessment",
                            score: metrics.backAsymmetryRisk,
                            maxScore: 100,
                            status: metrics.backAsymmetryStatus,
                            color: metrics.backAsymmetryRisk > 20 ? .orange : .green,
                            suffix: "%"
                        )

                        // Shoulder & Trunk
                        ScoreCard(
                            title: "Shoulder Asymmetry",
                            score: metrics.shoulderAsymmetry,
                            maxScore: 50,
                            status: metrics.shoulderStatus,
                            color: metrics.shoulderAsymmetry > 15 ? .orange : .green,
                            suffix: " px"
                        )

                        ScoreCard(
                            title: "Trunk Lean",
                            score: metrics.trunkLeanAngle,
                            maxScore: 15,
                            status: metrics.trunkStatus,
                            color: abs(metrics.trunkLeanAngle) > 5 ? .orange : .green,
                            suffix: "°"
                        )

                        // Rotation
                        ScoreCard(
                            title: "Rotation Risk",
                            score: CGFloat(metrics.rotationRiskScore),
                            maxScore: 100,
                            status: metrics.rotationStatus,
                            color: metrics.rotationRiskScore > 20 ? .orange : .green
                        )

                        // Report button
                        NavigationLink(destination: ReportView(sessionID: result.sessionID)) {
                            Label("Generate Report", systemImage: "doc.pdf")
                                .frame(maxWidth: .infinity)
                                .padding()
                                .background(Color.accentColor)
                                .foregroundColor(.white)
                                .cornerRadius(10)
                        }
                        .padding(.horizontal)
                    }
                }
                .padding(.vertical)
            }
            .navigationTitle("Results")
        }
        .addDisclaimer()
    }
}

struct ScoreCard: View {
    let title: String
    let score: CGFloat
    let maxScore: CGFloat
    let status: String
    let color: Color
    var suffix: String = ""

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            HStack {
                Text(title)
                    .font(.headline)
                Spacer()
                Text("\(Int(score))\(suffix)")
                    .font(.title2).bold()
                    .foregroundColor(color)
            }
            ProgressView(value: min(score, maxScore), total: maxScore)
                .tint(color)
            Text(status.replacingOccurrences(of: "_", with: " ").capitalized)
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .padding()
        .background(Color(.systemGray6))
        .cornerRadius(10)
        .padding(.horizontal)
    }
}
