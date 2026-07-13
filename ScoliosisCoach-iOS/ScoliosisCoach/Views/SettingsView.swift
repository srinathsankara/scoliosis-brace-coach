import SwiftUI

struct SettingsView: View {
    @AppStorage("dailyWearTarget") private var dailyWearTarget: Double = 780
    @AppStorage("notificationsEnabled") private var notificationsEnabled = true
    @AppStorage("reminderInterval") private var reminderInterval = 60
    @AppStorage("temperatureUnit") private var temperatureUnit = 0
    @State private var showDisclaimer = false
    @State private var showClearConfirm = false

    let reminderOptions = [30, 60, 120, 240]

    var body: some View {
        ScrollView {
            VStack(spacing: 0) {
                headerBar
                VStack(spacing: 16) {
                    wearTargetCard
                    notificationsCard
                    unitsCard
                    aboutCard
                    dangerCard
                }
                .padding(.horizontal, 20)
                .padding(.top, 8)
                .padding(.bottom, 32)
            }
        }
        .scrollDismissesKeyboard(.immediately)
        .background(Color.backgroundPrimary.ignoresSafeArea())
        .alert("Clear All Data?", isPresented: $showClearConfirm) {
            Button("Cancel", role: .cancel) {}
            Button("Delete All", role: .destructive) {
                Task { try? await DatabaseService.shared.deleteAllSessions() }
            }
        } message: {
            Text("All analysis sessions and compliance data will be permanently deleted.")
        }
        .alert("Medical Disclaimer", isPresented: $showDisclaimer) {
            Button("OK") {}
        } message: {
            Text("ScolioTrack is for educational and monitoring purposes only. It is not a medical device and does not provide diagnosis or treatment recommendations. Always consult a qualified healthcare provider for medical decisions.")
        }
    }

    private var headerBar: some View {
        HStack {
            Text("Settings")
                .font(.system(size: 30, weight: .bold, design: .rounded))
                .foregroundColor(.textPrimary)
            Spacer()
        }
        .padding(.horizontal, 20)
        .padding(.vertical, 16)
    }

    // MARK: - Cards

    private func sectionHeader(_ title: String, icon: String) -> some View {
        Label(title, systemImage: icon)
            .font(.caption.weight(.semibold))
            .foregroundColor(.textSecondary)
            .textCase(.uppercase)
            .frame(maxWidth: .infinity, alignment: .leading)
            .padding(.leading, 4)
    }

    private var wearTargetCard: some View {
        VStack(spacing: 12) {
            sectionHeader("Brace Wear", icon: "figure.stand")

            VStack(spacing: 10) {
                HStack {
                    ZStack {
                        Circle()
                            .fill(Color.accentTealLight)
                            .frame(width: 36, height: 36)
                        Image(systemName: "clock.badge.checkmark")
                            .foregroundColor(.accentTeal)
                    }
                    Text("Daily Wear Target")
                        .font(.subheadline.weight(.semibold))
                        .foregroundColor(.textPrimary)
                    Spacer()
                }

                Text("\(Int(dailyWearTarget) / 60)h \(Int(dailyWearTarget) % 60)m")
                    .font(.system(size: 36, weight: .bold, design: .rounded))
                    .foregroundColor(.accentTeal)

                Slider(value: $dailyWearTarget, in: 300...960, step: 30)
                    .tint(.accentTeal)

                Label("BrAIST study recommends 13h/day", systemImage: "book.closed")
                    .font(.caption)
                    .foregroundColor(.textSecondary)
            }
        }
        .padding(20)
        .background(Color.cardBackground)
        .clipShape(RoundedRectangle(cornerRadius: 16))
        .shadow(color: .cardShadow, radius: 8, x: 0, y: 4)
    }

    private var notificationsCard: some View {
        VStack(spacing: 12) {
            sectionHeader("Notifications", icon: "bell")

            VStack(spacing: 12) {
                Toggle(isOn: $notificationsEnabled) {
                    Label("Reminders", systemImage: "bell.badge.fill")
                        .foregroundColor(.textPrimary)
                }
                .tint(.accentTeal)

                if notificationsEnabled {
                    Picker("Interval", selection: $reminderInterval) {
                        ForEach(reminderOptions, id: \.self) { mins in
                            Text("Every \(mins) min").tag(mins)
                        }
                    }
                    .pickerStyle(.segmented)
                }
            }
        }
        .padding(20)
        .background(Color.cardBackground)
        .clipShape(RoundedRectangle(cornerRadius: 16))
        .shadow(color: .cardShadow, radius: 8, x: 0, y: 4)
    }

    private var unitsCard: some View {
        VStack(spacing: 12) {
            sectionHeader("Units", icon: "ruler")

            Picker("Temperature", selection: $temperatureUnit) {
                Label("Celsius", systemImage: "thermometer.sun").tag(0)
                Label("Fahrenheit", systemImage: "thermometer.sun.fill").tag(1)
            }
            .pickerStyle(.segmented)
        }
        .padding(20)
        .background(Color.cardBackground)
        .clipShape(RoundedRectangle(cornerRadius: 16))
        .shadow(color: .cardShadow, radius: 8, x: 0, y: 4)
    }

    private var aboutCard: some View {
        VStack(spacing: 12) {
            sectionHeader("About", icon: "info.circle")

            VStack(spacing: 10) {
                row("Version", "1.0.0")
                Divider()
                row("Developer", "Srinath Sankara")
                Divider()
                Button {
                    showDisclaimer = true
                } label: {
                    HStack {
                        Label("Medical Disclaimer", systemImage: "info.circle.fill")
                            .foregroundColor(.accentTeal)
                        Spacer()
                        Image(systemName: "chevron.right")
                            .font(.caption)
                            .foregroundColor(.textTertiary)
                    }
                }
            }
        }
        .padding(20)
        .background(Color.cardBackground)
        .clipShape(RoundedRectangle(cornerRadius: 16))
        .shadow(color: .cardShadow, radius: 8, x: 0, y: 4)
    }

    private var dangerCard: some View {
        Button(role: .destructive) {
            showClearConfirm = true
        } label: {
            HStack {
                Image(systemName: "trash")
                    .font(.subheadline)
                Text("Clear All Data")
                    .font(.subheadline.weight(.semibold))
                Spacer()
                Image(systemName: "chevron.right")
                    .font(.caption)
            }
            .foregroundColor(.statusPoor)
            .padding(20)
            .background(Color.cardBackground)
            .clipShape(RoundedRectangle(cornerRadius: 16))
            .shadow(color: .cardShadow, radius: 8, x: 0, y: 4)
        }
    }

    private func row(_ label: String, _ value: String) -> some View {
        HStack {
            Text(label)
                .font(.subheadline)
                .foregroundColor(.textPrimary)
            Spacer()
            Text(value)
                .font(.subheadline)
                .foregroundColor(.textSecondary)
        }
    }
}
