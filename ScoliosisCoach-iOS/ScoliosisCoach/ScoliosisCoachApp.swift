import SwiftUI

@main
struct ScolioTrackApp: App {
    @State private var dbReady = false
    @State private var dbError: String?

    var body: some Scene {
        WindowGroup {
            Group {
                if let error = dbError {
                    errorView(error)
                } else if !dbReady {
                    loadingView
                } else {
                    ContentView()
                }
            }
            .task {
                await initializeDB()
            }
        }
    }

    private var loadingView: some View {
        VStack(spacing: 24) {
            Image(systemName: "spine")
                .font(.system(size: 52))
                .foregroundStyle(Color.gradientTeal)

            Text("ScolioTrack")
                .font(.system(size: 30, weight: .bold, design: .rounded))
                .foregroundColor(.textPrimary)

            Text("AI-Powered Posture Screening")
                .font(.subheadline)
                .foregroundColor(.textSecondary)

            ProgressView()
                .tint(.accentTeal)
                .padding(.top, 8)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(Color.backgroundPrimary.ignoresSafeArea())
    }

    private func errorView(_ error: String) -> some View {
        VStack(spacing: 16) {
            Image(systemName: "xmark.icloud.fill")
                .font(.system(size: 48))
                .foregroundColor(.statusPoor)

            Text("Database Error")
                .font(.title2.weight(.semibold))

            Text(error)
                .font(.subheadline)
                .foregroundColor(.textSecondary)
                .multilineTextAlignment(.center)
                .padding(.horizontal, 40)

            Button("Retry") {
                dbError = nil
                Task { await initializeDB() }
            }
            .buttonStyle(.borderedProminent)
            .tint(.accentTeal)
            .controlSize(.large)
        }
        .padding()
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(Color.backgroundPrimary.ignoresSafeArea())
    }

    private func initializeDB() async {
        do {
            try await DatabaseService.shared.initialize()
            dbReady = true
        } catch {
            dbError = error.localizedDescription
        }
    }
}
