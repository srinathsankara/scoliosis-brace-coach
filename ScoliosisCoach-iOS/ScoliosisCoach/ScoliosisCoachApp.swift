import SwiftUI

@main
struct ScoliosisCoachApp: App {
    @State private var dbReady = false
    @State private var dbError: String?

    var body: some Scene {
        WindowGroup {
            if let error = dbError {
                VStack(spacing: 12) {
                    Image(systemName: "xmark.icloud.fill")
                        .font(.system(size: 48))
                        .foregroundColor(.red)
                    Text("Database Error")
                        .font(.title2).bold()
                    Text(error)
                        .foregroundColor(.secondary)
                        .multilineTextAlignment(.center)
                        .padding(.horizontal)
                    Button("Retry") {
                        Task { await initializeDB() }
                    }
                    .buttonStyle(.borderedProminent)
                }
            } else if !dbReady {
                ProgressView("Initializing...")
            } else {
                ContentView()
            }
        }
        .task {
            await initializeDB()
        }
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
