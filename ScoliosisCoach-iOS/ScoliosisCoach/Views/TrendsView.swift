import SwiftUI

struct TrendsView: View {
    @State private var selectedMetric = "backAsymmetryRisk"
    @State private var dataPoints: [(date: Date, value: Double)] = []
    @State private var isLoading = true

    let metrics: [(key: String, label: String, icon: String)] = [
        ("backAsymmetryRisk", "Back Asymmetry", "spine"),
        ("shoulderAsymmetry", "Shoulder", "rectangle.3.group"),
        ("trunkLeanAngle", "Trunk Lean", "arrow.up.and.down"),
        ("rotationRiskScore", "Rotation", "arrow.triangle.2.circlepath"),
        ("ribHumpProxy", "Rib Hump", "person.crop.circle"),
    ]

    var body: some View {
        VStack(spacing: 0) {
            headerBar
            metricPicker

            if isLoading {
                Spacer()
                ProgressView()
                    .tint(.accentTeal)
                Spacer()
            } else if dataPoints.isEmpty {
                emptyState
            } else {
                chartContent
            }
        }
        .background(Color.backgroundPrimary.ignoresSafeArea())
        .task { await loadData() }
        .onChange(of: selectedMetric) { _ in Task { await loadData() } }
    }

    private var headerBar: some View {
        HStack {
            Text("Trends")
                .font(.system(size: 30, weight: .bold, design: .rounded))
                .foregroundColor(.textPrimary)
            Spacer()
        }
        .padding(.horizontal, 20)
        .padding(.vertical, 16)
    }

    private var metricPicker: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 8) {
                ForEach(metrics, id: \.0) { key, label, icon in
                    Button {
                        selectedMetric = key
                    } label: {
                        Label(label, systemImage: icon)
                            .font(.subheadline.weight(.medium))
                            .padding(.horizontal, 14)
                            .padding(.vertical, 8)
                            .background(selectedMetric == key ? Color.accentTeal : Color.cardBackground)
                            .foregroundColor(selectedMetric == key ? .white : .textPrimary)
                            .clipShape(Capsule())
                            .shadow(color: .cardShadow, radius: 4, x: 0, y: 2)
                    }
                }
            }
            .padding(.horizontal, 20)
        }
        .padding(.bottom, 8)
    }

    private var emptyState: some View {
        VStack(spacing: 20) {
            Spacer()
            ZStack {
                Circle()
                    .fill(Color.accentTealLight)
                    .frame(width: 96, height: 96)
                Image(systemName: "chart.line.downtrend.xyaxis")
                    .font(.system(size: 38))
                    .foregroundColor(.accentTeal.opacity(0.5))
            }
            Text("No Trend Data Yet")
                .font(AppFont.title(24))
            Text("Complete a few analyses to see your trends")
                .font(.subheadline)
                .foregroundColor(.textSecondary)
                .multilineTextAlignment(.center)
                .padding(.horizontal, 40)
            Spacer()
        }
    }

    private var chartContent: some View {
        ScrollView {
            VStack(spacing: 16) {
                TrendChart(dataPoints: dataPoints, metricLabel: metricLabel)
                    .padding(.horizontal, 20)
                    .padding(.top, 8)

                summaryCard
                    .padding(.horizontal, 20)
                    .padding(.bottom, 16)
            }
        }
    }

    private var metricLabel: String {
        metrics.first(where: { $0.0 == selectedMetric })?.label ?? selectedMetric
    }

    private var summaryCard: some View {
        let values = dataPoints.map(\.value)
        let avg = values.reduce(0, +) / Double(values.count)
        let min = values.min() ?? 0
        let max = values.max() ?? 0
        let trend = values.count >= 2 ? values.last! - values.first! : 0

        return VStack(spacing: 16) {
            Text("Summary")
                .font(AppFont.headline())
                .foregroundColor(.textPrimary)
                .frame(maxWidth: .infinity, alignment: .leading)

            HStack(spacing: 0) {
                StatItem(label: "Average", value: String(format: "%.0f", avg), icon: "equal")
                Divider().frame(height: 40)
                StatItem(label: "Min", value: String(format: "%.0f", min), icon: "arrow.down")
                Divider().frame(height: 40)
                StatItem(label: "Max", value: String(format: "%.0f", max), icon: "arrow.up")
                Divider().frame(height: 40)
                StatItem(label: "Change",
                         value: "\(trend >= 0 ? "+" : "")\(String(format: "%.0f", trend))",
                         icon: trend >= 0 ? "arrow.up.right" : "arrow.down.right")
            }
        }
        .padding(20)
        .background(Color.cardBackground)
        .clipShape(RoundedRectangle(cornerRadius: 16))
        .shadow(color: .cardShadow, radius: 8, x: 0, y: 4)
    }

    private func loadData() async {
        isLoading = true
        dataPoints = (try? await DatabaseService.shared.getTrendData(metric: selectedMetric, limit: 30)) ?? []
        isLoading = false
    }
}

// MARK: - Stat Item

struct StatItem: View {
    let label: String
    let value: String
    let icon: String

    var body: some View {
        VStack(spacing: 4) {
            Image(systemName: icon)
                .font(.caption)
                .foregroundColor(.textTertiary)
            Text(value)
                .font(.subheadline.weight(.bold))
                .foregroundColor(.textPrimary)
            Text(label)
                .font(.caption2)
                .foregroundColor(.textSecondary)
        }
        .frame(maxWidth: .infinity)
    }
}

// MARK: - Trend Chart

struct TrendChart: View {
    let dataPoints: [(date: Date, value: Double)]
    let metricLabel: String

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(metricLabel)
                .font(AppFont.headline())
                .foregroundColor(.textPrimary)

            let values = dataPoints.map(\.value)
            let minVal = values.min() ?? 0
            let maxVal = values.max() ?? 1
            let range = maxVal - minVal
            let paddedMax = range > 0 ? maxVal + range * 0.15 : maxVal + 1
            let paddedMin = range > 0 ? max(0, minVal - range * 0.15) : 0

            GeometryReader { geo in
                let chartW = geo.size.width
                let chartH = geo.size.height - 40

                ZStack(alignment: .bottomLeading) {
                    ForEach(0..<4) { i in
                        let y = chartH * CGFloat(i) / 3
                        Path { path in
                            path.move(to: CGPoint(x: 0, y: y))
                            path.addLine(to: CGPoint(x: chartW, y: y))
                        }
                        .stroke(Color.dividerColor, lineWidth: 1)

                        let val = paddedMax - (paddedMax - paddedMin) * Double(i) / 3
                        Text("\(Int(val))")
                            .font(.system(size: 9, design: .monospaced))
                            .foregroundColor(.textTertiary)
                            .position(x: -18, y: y)
                    }

                    fillGradient(chartW: chartW, chartH: chartH, values: values,
                                 paddedMin: paddedMin, paddedMax: paddedMax)
                    linePath(chartW: chartW, chartH: chartH, values: values,
                             paddedMin: paddedMin, paddedMax: paddedMax)
                    dataPointCircles(chartW: chartW, chartH: chartH, values: values,
                                     paddedMin: paddedMin, paddedMax: paddedMax)

                    if let firstDate = dataPoints.first?.date,
                       let lastDate = dataPoints.last?.date {
                        Text(firstDate, style: .date)
                            .font(.system(size: 9))
                            .foregroundColor(.textTertiary)
                            .position(x: 0, y: chartH + 16)
                        Text(lastDate, style: .date)
                            .font(.system(size: 9))
                            .foregroundColor(.textTertiary)
                            .position(x: chartW, y: chartH + 16)
                    }
                }
                .padding(.leading, 28)
            }
            .frame(height: 240)
        }
        .padding(20)
        .background(Color.cardBackground)
        .clipShape(RoundedRectangle(cornerRadius: 16))
        .shadow(color: .cardShadow, radius: 8, x: 0, y: 4)
    }

    private func position(index: Int, count: Int, chartW: CGFloat, chartH: CGFloat,
                          value: Double, paddedMin: Double, paddedMax: Double) -> CGPoint {
        let x = count > 1 ? chartW * CGFloat(index) / CGFloat(count - 1) : chartW / 2
        let y = chartH * CGFloat(1 - (value - paddedMin) / (paddedMax - paddedMin))
        return CGPoint(x: x, y: y)
    }

    private func fillGradient(chartW: CGFloat, chartH: CGFloat, values: [Double],
                               paddedMin: Double, paddedMax: Double) -> some View {
        let count = values.count
        return Path { path in
            for (i, val) in values.enumerated() {
                let pt = position(index: i, count: count, chartW: chartW, chartH: chartH,
                                  value: val, paddedMin: paddedMin, paddedMax: paddedMax)
                if i == 0 { path.move(to: pt) }
                else { path.addLine(to: pt) }
            }
            path.addLine(to: CGPoint(x: count > 1 ? chartW : chartW / 2, y: chartH))
            path.addLine(to: CGPoint(x: 0, y: chartH))
            path.closeSubpath()
        }
        .fill(LinearGradient(
            colors: [.accentTeal.opacity(0.2), .accentTeal.opacity(0.01)],
            startPoint: .top, endPoint: .bottom
        ))
    }

    private func linePath(chartW: CGFloat, chartH: CGFloat, values: [Double],
                           paddedMin: Double, paddedMax: Double) -> some View {
        let count = values.count
        return Path { path in
            for (i, val) in values.enumerated() {
                let pt = position(index: i, count: count, chartW: chartW, chartH: chartH,
                                  value: val, paddedMin: paddedMin, paddedMax: paddedMax)
                if i == 0 { path.move(to: pt) }
                else { path.addLine(to: pt) }
            }
        }
        .stroke(Color.accentTeal, style: StrokeStyle(lineWidth: 2.5, lineCap: .round, lineJoin: .round))
    }

    private func dataPointCircles(chartW: CGFloat, chartH: CGFloat, values: [Double],
                                   paddedMin: Double, paddedMax: Double) -> some View {
        let count = values.count
        return ForEach(values.indices, id: \.self) { index in
            let pt = position(index: index, count: count, chartW: chartW, chartH: chartH,
                              value: values[index], paddedMin: paddedMin, paddedMax: paddedMax)
            Circle()
                .fill(Color.cardBackground)
                .overlay(Circle().stroke(Color.accentTeal, lineWidth: 2))
                .frame(width: 8, height: 8)
                .position(pt)
        }
    }
}
