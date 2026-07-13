import UIKit
import MediaPipeTasksVision

actor PoseDetector {
    static let shared = PoseDetector()

    private var landmarker: PoseLandmarker?
    private var isLoaded = false

    private static let modelURL = URL(string: "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/latest/pose_landmarker_lite.task")!
    private static let modelFilename = "pose_landmarker.task"

    private func modelPath() throws -> String {
        if let bundled = Bundle.main.path(forResource: "pose_landmarker", ofType: "task") {
            return bundled
        }
        let documents = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask).first!
        let cached = documents.appendingPathComponent(Self.modelFilename)
        if FileManager.default.fileExists(atPath: cached.path) {
            return cached.path
        }
        throw PoseError.modelNotFound
    }

    func ensureLoaded() async throws {
        guard !isLoaded else { return }

        var modelPath: String
        do {
            modelPath = try self.modelPath()
        } catch {
            modelPath = try await downloadModel()
        }

        let baseOptions = BaseOptions()
        baseOptions.modelAssetPath = modelPath
        let options = PoseLandmarkerOptions()
        options.baseOptions = baseOptions
        options.runningMode = .image
        options.minPoseDetectionConfidence = 0.5
        options.minTrackingConfidence = 0.5
        options.numPoses = 1

        do {
            landmarker = try PoseLandmarker(options: options)
            isLoaded = true
        } catch {
            throw PoseError.loadFailed("init: \(error.localizedDescription) (domain: \((error as NSError).domain), code: \((error as NSError).code))")
        }
    }

    private func downloadModel() async throws -> String {
        let documents = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask).first!
        let destination = documents.appendingPathComponent(Self.modelFilename)

        let session = URLSession(configuration: .default)
        let (tempURL, response) = try await session.download(from: Self.modelURL)
        guard let http = response as? HTTPURLResponse, http.statusCode == 200 else {
            throw PoseError.downloadFailed
        }
        try FileManager.default.moveItem(at: tempURL, to: destination)
        return destination.path
    }

    func detect(_ image: UIImage) async throws -> [[String: CGFloat]]? {
        try await ensureLoaded()

        let mpImage: MPImage
        do {
            mpImage = try MPImage(uiImage: image)
        } catch {
            throw PoseError.detectionFailed("MPImage: \(error.localizedDescription)")
        }

        guard let landmarker = landmarker else {
            throw PoseError.detectionFailed("landmarker is nil after ensureLoaded")
        }

        let result: PoseLandmarkerResult
        do {
            result = try landmarker.detect(image: mpImage)
        } catch {
            throw PoseError.detectionFailed("detect: \(error.localizedDescription) (domain: \((error as NSError).domain), code: \((error as NSError).code))")
        }

        guard let landmarks = result.landmarks.first else {
            return nil
        }

        let width = image.size.width
        let height = image.size.height

        return landmarks.map { landmark in
            [
                "x": CGFloat(landmark.x) * width,
                "y": CGFloat(landmark.y) * height,
                "z": CGFloat(landmark.z),
                "visibility": CGFloat(landmark.visibility?.doubleValue ?? 0)
            ]
        }
    }

    nonisolated func landmark(_ landmarks: [[String: CGFloat]], at index: Int) -> CGPoint? {
        guard index < landmarks.count else { return nil }
        let lm = landmarks[index]
        return CGPoint(x: lm["x"] ?? 0, y: lm["y"] ?? 0)
    }

    nonisolated func angle(_ a: CGPoint, _ b: CGPoint, _ c: CGPoint) -> CGFloat {
        let radians = atan2(c.y - b.y, c.x - b.x) - atan2(a.y - b.y, a.x - b.x)
        var angle = abs(radians * 180 / .pi)
        if angle > 180 { angle = 360 - angle }
        return angle
    }

    enum PoseError: LocalizedError {
        case modelNotFound
        case downloadFailed
        case loadFailed(String)
        case detectionFailed(String)

        var errorDescription: String? {
            switch self {
            case .modelNotFound:
                return "Pose detection model not found."
            case .downloadFailed:
                return "Failed to download pose detection model. Check your internet connection and try again."
            case .loadFailed(let msg):
                return "Model load failed: \(msg)"
            case .detectionFailed(let msg):
                return "Detection failed: \(msg)"
            }
        }
    }
}
