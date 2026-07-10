import Foundation
import GRDB

struct ComplianceSession: Codable, FetchableRecord, PersistableRecord, Identifiable {
    var id: String  // UUID
    var startTime: Date
    var endTime: Date?
    var wearMinutes: Int
    var skinTempReadings: Data?  // JSON array of [timestamp, temp] pairs
    var isActive: Bool

    static let databaseTableName = "complianceSessions"
}

struct PressureReading: Codable, FetchableRecord, PersistableRecord, Identifiable {
    var id: String  // UUID
    var sessionID: String
    var timestamp: Date
    var upperSupport: Double
    var middlePressure: Double
    var lowerSupport: Double
    var skinTemp: Double

    static let databaseTableName = "pressureReadings"
}

struct ComplianceSummary {
    var todayMinutes: Int
    var weekMinutes: Int
    var monthMinutes: Int
    var averageDailyMinutes: Double
    var targetMetDays: Int
    var totalDays: Int

    var targetMetPercentage: Double {
        guard totalDays > 0 else { return 0 }
        return Double(targetMetDays) / Double(totalDays) * 100
    }

    var isOnTrack: Bool {
        averageDailyMinutes >= 780  // 13 hours = BrAIST recommendation
    }
}
