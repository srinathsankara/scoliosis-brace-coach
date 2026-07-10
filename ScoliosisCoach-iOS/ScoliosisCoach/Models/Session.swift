import Foundation
import GRDB

struct Session: Codable, FetchableRecord, PersistableRecord, Identifiable {
    var id: String  // UUID
    var createdAt: Date
    var mode: String  // "standing_no_brace", "standing_with_brace", "walking", "exercise"
    var ageGroup: String  // "under12", "under15", "under18", "adult"
    var braceDetected: Bool
    var imagePath: String?
    var metricsJSON: Data
    var status: String  // "success", "error"
    var errorMessage: String?

    static let databaseTableName = "sessions"

    enum Columns {
        static let id = Column("id")
        static let createdAt = Column("createdAt")
        static let mode = Column("mode")
        static let ageGroup = Column("ageGroup")
        static let braceDetected = Column("braceDetected")
        static let imagePath = Column("imagePath")
        static let metricsJSON = Column("metricsJSON")
        static let status = Column("status")
        static let errorMessage = Column("errorMessage")
    }
}

struct MetricsResult: Codable {
    var shoulderAsymmetry: Double
    var hipAsymmetry: Double
    var trunkLeanAngle: Double
    var headTilt: Double
    var spineDeviation: Double
    var armHangDiff: Double
    var shoulderStatus: String
    var trunkStatus: String
    var ribHumpProxy: Double
    var ribHumpStatus: String
    var axillaryFoldDiff: Double
    var axillaryStatus: String
    var trunkRotationAngle: Double
    var rotationStatus: String
    var trunkOffset: Double
    var scapularWingingDiff: Double
    var pelvicObliquity: Double
    var rotationRiskScore: Double
    var brightnessAsymmetry: Double
    var midlineDeviation: Double
    var textureAsymmetry: Double
    var edgeAsymmetry: Double
    var spineCurveScore: Double
    var backAsymmetryRisk: Double
    var backAsymmetryStatus: String

    static func empty() -> MetricsResult {
        MetricsResult(
            shoulderAsymmetry: 0, hipAsymmetry: 0, trunkLeanAngle: 0, headTilt: 0,
            spineDeviation: 0, armHangDiff: 0, shoulderStatus: "good", trunkStatus: "good",
            ribHumpProxy: 0, ribHumpStatus: "good", axillaryFoldDiff: 0, axillaryStatus: "good",
            trunkRotationAngle: 0, rotationStatus: "good", trunkOffset: 0,
            scapularWingingDiff: 0, pelvicObliquity: 0, rotationRiskScore: 0,
            brightnessAsymmetry: 0, midlineDeviation: 0, textureAsymmetry: 0,
            edgeAsymmetry: 0, spineCurveScore: 0, backAsymmetryRisk: 0, backAsymmetryStatus: "good"
        )
    }
}
