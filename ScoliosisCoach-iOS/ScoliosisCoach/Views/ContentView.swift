import SwiftUI

struct ContentView: View {
    @State private var selectedTab = 0

    var body: some View {
        ZStack(alignment: .bottom) {
            TabView(selection: $selectedTab) {
                AnalysisView()
                    .tag(0)
                HistoryView()
                    .tag(1)
                TrendsView()
                    .tag(2)
                ComplianceView()
                    .tag(3)
                SettingsView()
                    .tag(4)
            }
            .toolbar(.hidden, for: .tabBar)

            customTabBar
        }
        .ignoresSafeArea(.keyboard)
        .addDisclaimer()
    }

    private var customTabBar: some View {
        HStack(spacing: 0) {
            ForEach(tabItems.indices, id: \.self) { i in
                let item = tabItems[i]
                let isSelected = selectedTab == i
                Button {
                    withAnimation(.spring(response: 0.35, dampingFraction: 0.7)) {
                        selectedTab = i
                    }
                } label: {
                    VStack(spacing: 3) {
                        Image(systemName: isSelected ? item.selectedIcon : item.icon)
                            .font(.system(size: 22, weight: isSelected ? .semibold : .regular))
                            .symbolEffect(.bounce.up, value: selectedTab)
                        Text(item.label)
                            .font(.system(size: 10, weight: isSelected ? .semibold : .medium))
                    }
                    .foregroundColor(isSelected ? .accentTeal : .textTertiary)
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 6)
                }
            }
        }
        .padding(.horizontal, 8)
        .padding(.top, 8)
        .padding(.bottom, 28)
        .background(
            .regularMaterial,
            in: UnevenRoundedRectangle(
                topLeadingRadius: 24, bottomLeadingRadius: 0,
                bottomTrailingRadius: 0, topTrailingRadius: 24
            )
        )
        .overlay(alignment: .top) {
            Divider().opacity(0.3)
        }
    }
}

private struct TabItemData {
    let icon: String
    let selectedIcon: String
    let label: String
}

private let tabItems: [TabItemData] = [
    TabItemData(icon: "viewfinder", selectedIcon: "viewfinder.fill", label: "Analyze"),
    TabItemData(icon: "clock.arrow.circlepath", selectedIcon: "clock.arrow.circlepath", label: "History"),
    TabItemData(icon: "chart.xyaxis.line", selectedIcon: "chart.xyaxis.line", label: "Trends"),
    TabItemData(icon: "clock.badge.checkmark", selectedIcon: "clock.badge.checkmark.fill", label: "Compliance"),
    TabItemData(icon: "gearshape", selectedIcon: "gearshape.fill", label: "Settings"),
]
