import Foundation

struct PostureThresholds {
    let shoulderDiffPx: CGFloat
    let trunkAngleDeg: CGFloat

    static let `default` = PostureThresholds(shoulderDiffPx: 15, trunkAngleDeg: 3.0)
}

let ageThresholds: [String: PostureThresholds] = [
    "under12": PostureThresholds(shoulderDiffPx: 12, trunkAngleDeg: 2.5),
    "under15": PostureThresholds(shoulderDiffPx: 15, trunkAngleDeg: 3.0),
    "under18": PostureThresholds(shoulderDiffPx: 18, trunkAngleDeg: 3.5),
    "adult": PostureThresholds(shoulderDiffPx: 20, trunkAngleDeg: 4.0),
]

struct PostureResult {
    let shoulderAsymmetry: CGFloat
    let hipAsymmetry: CGFloat
    let trunkLeanAngle: CGFloat
    let headTilt: CGFloat
    let spineDeviation: CGFloat
    let armHangDiff: CGFloat
    let shoulderStatus: String
    let trunkStatus: String
}

func analyzePosture(
    landmarks: [[String: CGFloat]],
    imageSize: CGSize,
    ageGroup: String = "under15"
) -> PostureResult? {
    guard landmarks.count >= 29 else { return nil }

    let detector = PoseDetector.shared

    let lSh = detector.landmark(landmarks, at: 11) ?? .zero
    let rSh = detector.landmark(landmarks, at: 12) ?? .zero
    let lHip = detector.landmark(landmarks, at: 23) ?? .zero
    let rHip = detector.landmark(landmarks, at: 24) ?? .zero
    let nose = detector.landmark(landmarks, at: 0) ?? .zero
    let lWrist = detector.landmark(landmarks, at: 15) ?? .zero
    let rWrist = detector.landmark(landmarks, at: 16) ?? .zero

    let midShX = (lSh.x + rSh.x) / 2
    let midShY = (lSh.y + rSh.y) / 2
    let midHipX = (lHip.x + rHip.x) / 2
    let midHipY = (lHip.y + rHip.y) / 2

    let shoulderDiff = abs(lSh.y - rSh.y)
    let hipDiff = abs(lHip.y - rHip.y)

    // Trunk lean angle
    let dx = midShX - midHipX
    let dy = midHipY - midShY
    let trunkAngle = abs(atan2(dx, dy) * 180 / .pi)

    let headTilt = abs(nose.x - midShX)

    let spineDeviation = abs(midShX - midHipX)

    let leftArmLength = lSh.y - lWrist.y
    let rightArmLength = rSh.y - rWrist.y
    let armDiff = abs(leftArmLength - rightArmLength)

    // FIX #8: safe fallback instead of force-unwrap
    let thresholds = ageThresholds[ageGroup] ?? .default

    let shoulderStatus = shoulderDiff < thresholds.shoulderDiffPx ? "good" : "needs_improvement"
    let trunkStatus = trunkAngle < thresholds.trunkAngleDeg ? "good" : "needs_improvement"

    return PostureResult(
        shoulderAsymmetry: shoulderDiff.rounded(to: 2),
        hipAsymmetry: hipDiff.rounded(to: 2),
        trunkLeanAngle: trunkAngle.rounded(to: 2),
        headTilt: headTilt.rounded(to: 2),
        spineDeviation: spineDeviation.rounded(to: 2),
        armHangDiff: armDiff.rounded(to: 2),
        shoulderStatus: shoulderStatus,
        trunkStatus: trunkStatus
    )
}

extension CGFloat {
    func rounded(to places: Int) -> CGFloat {
        let divisor = pow(10.0, CGFloat(places))
        return (self * divisor).rounded() / divisor
    }
}
