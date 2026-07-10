import SwiftUI

@main
struct ScoliosisCoachApp: App {
    init() {
        Task { await DatabaseService.shared.initialize() }
    }

    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}
