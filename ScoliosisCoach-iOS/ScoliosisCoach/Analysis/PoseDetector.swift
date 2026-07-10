import UIKit
import MediaPipeTasksVision
import CoreImage

actor PoseDetector {
    static let shared = PoseDetector()

    private var landmarker: PoseLandmarker?
    private var isLoaded = false

    func ensureLoaded() async throws {
        guard !isLoaded else { return }

        guard let modelPath = Bundle.main.path(forResource: "pose_landmarker", ofType: "task") else {
            throw PoseError.modelNotFound
        }

        let options = PoseLandmarkerOptions()
        options.baseOptions.modelAssetPath = modelPath
        options.runningMode = .image
        options.minPoseDetectionConfidence = 0.5
        options.minTrackingConfidence = 0.5

        landmarker = try PoseLandmarker(options: options)
        isLoaded = true
    }

    func detect(_ image: UIImage) async throws -> [[String: CGFloat]]? {
        try await ensureLoaded()

        guard let landmarker = landmarker,
              let mpImage = try? MPImage(uiImage: image) else {
            return nil
        }

        let result = try landmarker.detect(image: mpImage)

        guard let landmarks = result.landmarks.first else {
            return nil
        }

        // Convert normalized landmarks to pixel coordinates
        let width = image.size.width
        let height = image.size.height

        return landmarks.map { landmark in
            [
                "x": CGFloat(landmark.x) * width,
                "y": CGFloat(landmark.y) * height,
                "z": CGFloat(landmark.z),
                "visibility": CGFloat(landmark.visibility)
            ]
        }
    }

    /// Get landmark coordinates as CGPoint
    func landmark(_ landmarks: [[String: CGFloat]], at index: Int) -> CGPoint? {
        guard index < landmarks.count else { return nil }
        let lm = landmarks[index]
        return CGPoint(x: lm["x"] ?? 0, y: lm["y"] ?? 0)
    }

    /// Calculate angle between three points (in degrees)
    func angle(_ a: CGPoint, _ b: CGPoint, _ c: CGPoint) -> CGFloat {
        let radians = atan2(c.y - b.y, c.x - b.x) - atan2(a.y - b.y, a.x - b.x)
        var angle = abs(radians * 180 / .pi)
        if angle > 180 { angle = 360 - angle }
        return angle
    }

    enum PoseError: LocalizedError {
        case modelNotFound
        case detectionFailed(String)

        var errorDescription: String? {
            switch self {
            case .modelNotFound:
                return "Pose detection model not found. Ensure pose_landmarker.task is in app resources."
            case .detectionFailed(let msg):
                return "Pose detection failed: \(msg)"
            }
        }
    }
}
