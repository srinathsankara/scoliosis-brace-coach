import SwiftUI

struct TrendsView: View {
    @State private var selectedMetric = "backAsymmetryRisk"
    @State private var dataPoints: [(date: Date, value: Double)] = []
    @State private var isLoading = true

    let metrics = [
        ("backAsymmetryRisk", "Back Asymmetry"),
        ("shoulderAsymmetry", "Shoulder"),
        ("trunkLeanAngle", "Trunk Lean"),
        ("rotationRiskScore", "Rotation"),
        ("ribHumpProxy", "Rib Hump")
    ]

    var body: some View {
        NavigationView {
            VStack {
                Picker("Metric", selection: $selectedMetric) {
                    ForEach(metrics, id: \.0) { key, label in
                        Text(label).tag(key)
                    }
                }
                .pickerStyle(MenuPickerStyle())
                .padding()

                if isLoading {
                    Spacer()
                    ProgressView()
                    Spacer()
                } else if dataPoints.isEmpty {
                    Spacer()
                    VStack(spacing: 8) {
                        Image(systemName: "chart.line.downtrend.xyaxis")
                            .font(.system(size: 48))
                            .foregroundColor(.secondary)
                        Text("No data yet")
                            .foregroundColor(.secondary)
                    }
                    Spacer()
                } else {
                    ChartView(dataPoints: dataPoints)
                        .padding()
                }
            }
            .navigationTitle("Trends")
        }
        .task { await loadData() }
        .onChange(of: selectedMetric) { _ in
            Task { await loadData() }
        }
    }

    private func loadData() async {
        isLoading = true
        dataPoints = (try? await DatabaseService.shared.getTrendData(metric: selectedMetric, limit: 30)) ?? []
        isLoading = false
    }
}

struct ChartView: View {
    let dataPoints: [(date: Date, value: Double)]

    var body: some View {
        GeometryReader { geo in
            let maxVal = dataPoints.map(\.value).max() ?? 1
            let minDate = dataPoints.map(\.date).min() ?? Date()
            let maxDate = dataPoints.map(\.date).max() ?? Date()
            let dateRange = maxDate.timeIntervalSince(minDate)

            ZStack(alignment: .bottomLeading) {
                // Grid lines
                ForEach(0..<5) { i in
                    let y = geo.size.height * CGFloat(i) / 4
                    Path { path in
                        path.move(to: CGPoint(x: 0, y: y))
                        path.addLine(to: CGPoint(x: geo.size.width, y: y))
                    }
                    .stroke(Color.gray.opacity(0.2))
                }

                // Points and lines
                Path { path in
                    for (index, dp) in dataPoints.enumerated() {
                        let x = dateRange > 0
                            ? geo.size.width * CGFloat(dp.date.timeIntervalSince(minDate) / dateRange)
                            : geo.size.width * CGFloat(index) / CGFloat(max(1, dataPoints.count - 1))
                        let y = geo.size.height * CGFloat(1 - dp.value / maxVal)
                        if index == 0 {
                            path.move(to: CGPoint(x: x, y: y))
                        } else {
                            path.addLine(to: CGPoint(x: x, y: y))
                        }
                    }
                }
                .stroke(Color.accentColor, lineWidth: 2)
            }
        }
    }
}
