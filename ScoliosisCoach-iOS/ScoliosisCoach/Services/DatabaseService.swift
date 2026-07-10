import Foundation
import GRDB

enum DatabaseError: LocalizedError {
    case notInitialized
    case migrationFailed(String)

    var errorDescription: String? {
        switch self {
        case .notInitialized:
            return "Database not initialized. Please restart the app."
        case .migrationFailed(let msg):
            return "Database migration failed: \(msg)"
        }
    }
}

actor DatabaseService {
    static let shared = DatabaseService()

    private var dbWriter: DatabaseWriter?

    private let schemaVersion: Int = 1

    func initialize() throws {
        let documentsPath = FileManager.default.urls(
            for: .documentDirectory, in: .userDomainMask
        ).first!
        let dbPath = documentsPath.appendingPathComponent("scoliosis_coach.db").path
        dbWriter = try DatabaseQueue(path: dbPath)
        try createTables()
    }

    private func createTables() throws {
        try dbWriter?.write { db in
            // FIX #15: schema versioning for future migrations
            let currentVersion = try Int.fetchOne(db, sql: "PRAGMA user_version") ?? 0

            try db.create(table: "sessions", ifNotExists: true) { t in
                t.column("id", .text).primaryKey()
                t.column("createdAt", .datetime).notNull()
                t.column("mode", .text).notNull()
                t.column("ageGroup", .text).notNull()
                t.column("braceDetected", .boolean).notNull()
                t.column("imagePath", .text)
                t.column("metricsJSON", .blob).notNull()
                t.column("status", .text).notNull()
                t.column("errorMessage", .text)
            }

            try db.create(table: "complianceSessions", ifNotExists: true) { t in
                t.column("id", .text).primaryKey()
                t.column("startTime", .datetime).notNull()
                t.column("endTime", .datetime)
                t.column("wearMinutes", .integer).notNull()
                t.column("skinTempReadings", .blob)
                t.column("isActive", .boolean).notNull()
            }

            try db.create(table: "pressureReadings", ifNotExists: true) { t in
                t.column("id", .text).primaryKey()
                t.column("sessionID", .text).notNull()
                t.column("timestamp", .datetime).notNull()
                t.column("upperSupport", .double).notNull()
                t.column("middlePressure", .double).notNull()
                t.column("lowerSupport", .double).notNull()
                t.column("skinTemp", .double).notNull()
            }

            if currentVersion < schemaVersion {
                try db.execute(sql: "PRAGMA user_version = \(schemaVersion)")
            }
        }
    }

    private func requireDB() throws -> DatabaseWriter {
        guard let dbWriter = dbWriter else {
            throw DatabaseError.notInitialized
        }
        return dbWriter
    }

    // MARK: - Sessions

    func saveSession(_ session: Session) async throws {
        let db = try requireDB()
        try await db.write { db in
            try session.insert(db)
        }
    }

    func getAllSessions(limit: Int = 50) async throws -> [Session] {
        let db = try requireDB()
        return try await db.read { db in
            try Session
                .order(Column("createdAt").desc)
                .limit(limit)
                .fetchAll(db)
        }
    }

    func getSessions(mode: String, limit: Int = 50) async throws -> [Session] {
        let db = try requireDB()
        return try await db.read { db in
            try Session
                .filter(Column("mode") == mode)
                .order(Column("createdAt").desc)
                .limit(limit)
                .fetchAll(db)
        }
    }

    func getSession(id: String) async throws -> Session? {
        let db = try requireDB()
        return try await db.read { db in
            try Session.fetchOne(db, key: id)
        }
    }

    func deleteSession(id: String) async throws {
        let db = try requireDB()
        try await db.write { db in
            try Session.deleteOne(db, key: id)
        }
    }

    func deleteAllSessions() async throws {
        let db = try requireDB()
        try await db.write { db in
            try Session.deleteAll(db)
        }
    }

    // MARK: - Compliance

    func saveComplianceSession(_ session: ComplianceSession) async throws {
        let db = try requireDB()
        try await db.write { db in
            try session.insert(db)
        }
    }

    func updateComplianceSession(_ session: ComplianceSession) async throws {
        let db = try requireDB()
        try await db.write { db in
            try session.update(db)
        }
    }

    func getAllComplianceSessions() async throws -> [ComplianceSession] {
        let db = try requireDB()
        return try await db.read { db in
            try ComplianceSession
                .order(Column("startTime").desc)
                .fetchAll(db)
        }
    }

    func getComplianceSummary() async throws -> ComplianceSummary {
        let sessions = try await getAllComplianceSessions()
        let calendar = Calendar.current
        let now = Date()

        let todaySessions = sessions.filter { calendar.isDate($0.startTime, inSameDayAs: now) }

        let weekStart = calendar.date(from: calendar.dateComponents([.yearForWeekOfYear, .weekOfYear], from: now))!
        let monthStart = calendar.date(from: calendar.dateComponents([.year, .month], from: now))!
        let daysSinceMonthStart = calendar.dateComponents([.day], from: monthStart, to: now).day.map { max(1, $0 + 1) } ?? 1

        let todayMinutes = todaySessions.reduce(0) { $0 + $1.wearMinutes }
        let weekMinutes = sessions.filter { $0.startTime >= weekStart }.reduce(0) { $0 + $1.wearMinutes }
        let monthMinutes = sessions.filter { $0.startTime >= monthStart }.reduce(0) { $0 + $1.wearMinutes }

        // FIX #7: correct daily average = week / 7 (rolling weekly average)
        let avgDaily = Double(weekMinutes) / 7.0

        let dailyMinutesThreshold = 13 * 60
        let uniqueDays = Set(sessions.map { calendar.startOfDay(for: $0.startTime) })
        let targetMetDays = uniqueDays.filter { day in
            let dayTotal = sessions.filter { calendar.isDate($0.startTime, inSameDayAs: day) }
                .reduce(0) { $0 + $1.wearMinutes }
            return dayTotal >= dailyMinutesThreshold
        }.count

        // FIX #7: totalDays uses month range for more meaningful percentage
        let totalDays = min(uniqueDays.count, daysSinceMonthStart)

        return ComplianceSummary(
            todayMinutes: todayMinutes,
            weekMinutes: weekMinutes,
            monthMinutes: monthMinutes,
            averageDailyMinutes: avgDaily,
            targetMetDays: targetMetDays,
            totalDays: totalDays
        )
    }

    // MARK: - Pressure Readings

    func savePressureReading(_ reading: PressureReading) async throws {
        let db = try requireDB()
        try await db.write { db in
            try reading.insert(db)
        }
    }

    func getPressureHistory(sessionID: String) async throws -> [PressureReading] {
        let db = try requireDB()
        return try await db.read { db in
            try PressureReading
                .filter(Column("sessionID") == sessionID)
                .order(Column("timestamp").asc)
                .fetchAll(db)
        }
    }

    // MARK: - Trends

    func getTrendData(metric: String, limit: Int = 20) async throws -> [(date: Date, value: Double)] {
        let sessions = try await getAllSessions(limit: limit)
        let decoder = JSONDecoder()
        return sessions.compactMap { session in
            guard let metrics = try? decoder.decode(MetricsResult.self, from: session.metricsJSON) else {
                return nil
            }
            let value: Double? = {
                switch metric {
                case "trunkLeanAngle": return metrics.trunkLeanAngle
                case "shoulderAsymmetry": return metrics.shoulderAsymmetry
                case "hipAsymmetry": return metrics.hipAsymmetry
                case "ribHumpProxy": return metrics.ribHumpProxy
                case "trunkRotationAngle": return metrics.trunkRotationAngle
                case "spineDeviation": return metrics.spineDeviation
                case "backAsymmetryRisk": return metrics.backAsymmetryRisk
                case "rotationRiskScore": return metrics.rotationRiskScore
                default: return nil
                }
            }()
            guard let v = value else { return nil }
            return (session.createdAt, v)
        }
    }
}
