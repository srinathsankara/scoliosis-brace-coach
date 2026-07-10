import SwiftUI

struct SettingsView: View {
    @State private var dailyWearTarget: Double = 780
    @State private var notificationsEnabled = true
    @State private var reminderInterval = 60
    @State private var temperatureUnit = 0
    @State private var showDisclaimer = false

    let reminderOptions = [30, 60, 120, 240]

    var body: some View {
        NavigationView {
            Form {
                Section("Brace Wear Target") {
                    VStack {
                        Text("\(Int(dailyWearTarget) / 60)h \(Int(dailyWearTarget) % 60)m daily")
                            .font(.title2).bold()
                        Slider(value: $dailyWearTarget, in: 300...960, step: 30)
                    }
                }

                Section("Notifications") {
                    Toggle("Reminders", isOn: $notificationsEnabled)
                    if notificationsEnabled {
                        Picker("Remind every", selection: $reminderInterval) {
                            ForEach(reminderOptions, id: \.self) { mins in
                                Text("\(mins) min").tag(mins)
                            }
                        }
                    }
                }

                Section("Units") {
                    Picker("Temperature", selection: $temperatureUnit) {
                        Text("°C").tag(0)
                        Text("°F").tag(1)
                    }
                    .pickerStyle(SegmentedPickerStyle())
                }

                Section {
                    Button("Clear All Data") {
                        Task {
                            try? await DatabaseService.shared.deleteAllSessions()
                        }
                    }
                    .foregroundColor(.red)
                }

                Section("About") {
                    HStack {
                        Text("Version")
                        Spacer()
                        Text("1.0.0").foregroundColor(.secondary)
                    }
                    HStack {
                        Text("Created by")
                        Spacer()
                        Text("Srinath Sankara").foregroundColor(.secondary)
                    }
                    Button("Medical Disclaimer") {
                        showDisclaimer = true
                    }
                    .foregroundColor(.orange)
                }
            }
            .navigationTitle("Settings")
        }
        .alert("Medical Disclaimer", isPresented: $showDisclaimer) {
            Button("OK") {}
        } message: {
            Text("""
            Scoliosis Brace Coach is for educational and monitoring purposes only. \
            It is not a medical device and does not provide diagnosis or treatment \
            recommendations. Always consult a qualified healthcare provider for \
            medical decisions. The creator, Srinath Sankara, assumes no responsibility \
            for any medical decisions made based on this application.
            """)
        }
        .addDisclaimer()
    }
}
