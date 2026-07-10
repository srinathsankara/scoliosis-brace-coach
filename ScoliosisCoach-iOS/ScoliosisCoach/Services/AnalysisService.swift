import UIKit
import Foundation

actor AnalysisService {
    static let shared = AnalysisService()

    func analyze(
        image: UIImage,
        mode: String = "standing_no_brace",
        ageGroup: String = "under15"
    ) async -> AnalysisResult {
        do {
            let landmarks = try await PoseDetector.shared.detect(image)

            // FIX #12: consistent landmark count (PostureRules needs >= 29)
            guard let landmarks = landmarks, landmarks.count >= 29 else {
                return AnalysisResult(
                    status: "error",
                    message: "No person detected. Ensure the photo shows a full body from the back."
                )
            }

            let braceDetected = detectBrace(in: image)

            let imageSize = image.size

            var metrics = MetricsResult.empty()

            if mode.contains("standing") {
                if let posture = analyzePosture(landmarks: landmarks, imageSize: imageSize, ageGroup: ageGroup) {
                    metrics.shoulderAsymmetry = posture.shoulderAsymmetry
                    metrics.hipAsymmetry = posture.hipAsymmetry
                    metrics.trunkLeanAngle = posture.trunkLeanAngle
                    metrics.headTilt = posture.headTilt
                    metrics.spineDeviation = posture.spineDeviation
                    metrics.armHangDiff = posture.armHangDiff
                    metrics.shoulderStatus = posture.shoulderStatus
                    metrics.trunkStatus = posture.trunkStatus
                }

                if let rotation = analyzeRotation(landmarks: landmarks, imageSize: imageSize, ageGroup: ageGroup) {
                    metrics.ribHumpProxy = rotation.ribHumpProxy
                    metrics.ribHumpStatus = rotation.ribHumpStatus
                    metrics.axillaryFoldDiff = rotation.axillaryFoldDiff
                    metrics.axillaryStatus = rotation.axillaryStatus
                    metrics.trunkRotationAngle = rotation.trunkRotationAngle
                    metrics.rotationStatus = rotation.rotationStatus
                    metrics.trunkOffset = rotation.trunkOffset
                    metrics.scapularWingingDiff = rotation.scapularWingingDiff
                    metrics.pelvicObliquity = rotation.pelvicObliquity
                    metrics.rotationRiskScore = rotation.rotationRiskScore
                }

                if let backAsym = analyzeBackAsymmetry(image: image, landmarks: landmarks) {
                    metrics.brightnessAsymmetry = backAsym.brightnessAsymmetry
                    metrics.midlineDeviation = backAsym.midlineDeviation
                    metrics.textureAsymmetry = backAsym.textureAsymmetry
                    metrics.edgeAsymmetry = backAsym.edgeAsymmetry
                    metrics.spineCurveScore = backAsym.spineCurveScore
                    metrics.backAsymmetryRisk = backAsym.backAsymmetryRisk
                    metrics.backAsymmetryStatus = backAsym.backAsymmetryStatus
                }
            } else if mode.contains("walking") {
                if let gait = analyzeGait(landmarksFrames: [landmarks], imageSize: imageSize) {
                    metrics.spineDeviation = Double(gait.gaitSymmetryScore)
                }
            }

            let session = Session(
                id: UUID().uuidString,
                createdAt: Date(),
                mode: mode,
                ageGroup: ageGroup,
                braceDetected: braceDetected,
                imagePath: nil,
                metricsJSON: try JSONEncoder().encode(metrics),
                status: "success",
                errorMessage: nil
            )
            try await DatabaseService.shared.saveSession(session)

            return AnalysisResult(
                status: "success",
                mode: mode,
                braceDetected: braceDetected,
                metrics: metrics,
                sessionID: session.id
            )

        } catch let error as PoseDetector.PoseError {
            return AnalysisResult(status: "error", message: error.localizedDescription)
        } catch {
            return AnalysisResult(status: "error", message: "Analysis failed: \(error.localizedDescription)")
        }
    }
}

struct AnalysisResult {
    let status: String
    var message: String?
    var mode: String?
    var braceDetected: Bool?
    var metrics: MetricsResult?
    var sessionID: String?

    init(status: String, message: String? = nil, mode: String? = nil,
         braceDetected: Bool? = nil, metrics: MetricsResult? = nil, sessionID: String? = nil) {
        self.status = status
        self.message = message
        self.mode = mode
        self.braceDetected = braceDetected
        self.metrics = metrics
        self.sessionID = sessionID
    }
}
