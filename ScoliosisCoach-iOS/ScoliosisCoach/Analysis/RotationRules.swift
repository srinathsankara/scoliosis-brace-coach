import Foundation

struct RotationThresholds {
    let ribHumpPx: CGFloat
    let axillaryDiffPx: CGFloat
    let rotationAngleDeg: CGFloat

    static let `default` = RotationThresholds(ribHumpPx: 7, axillaryDiffPx: 5, rotationAngleDeg: 4)
}

let rotationAgeThresholds: [String: RotationThresholds] = [
    "under12": RotationThresholds(ribHumpPx: 5, axillaryDiffPx: 4, rotationAngleDeg: 3),
    "under15": RotationThresholds(ribHumpPx: 7, axillaryDiffPx: 5, rotationAngleDeg: 4),
    "under18": RotationThresholds(ribHumpPx: 9, axillaryDiffPx: 6, rotationAngleDeg: 5),
    "adult": RotationThresholds(ribHumpPx: 10, axillaryDiffPx: 7, rotationAngleDeg: 5),
]

struct RotationResult {
    let ribHumpProxy: CGFloat
    let ribHumpStatus: String
    let axillaryFoldDiff: CGFloat
    let axillaryStatus: String
    let trunkRotationAngle: CGFloat
    let rotationStatus: String
    let trunkOffset: CGFloat
    let scapularWingingDiff: CGFloat
    let pelvicObliquity: CGFloat
    let rotationRiskScore: CGFloat
}

func analyzeRotation(
    landmarks: [[String: CGFloat]],
    imageSize: CGSize,
    ageGroup: String = "under15"
) -> RotationResult? {
    guard landmarks.count >= 27 else { return nil }

    let detector = PoseDetector.shared

    let lSh = detector.landmark(landmarks, at: 11) ?? .zero
    let rSh = detector.landmark(landmarks, at: 12) ?? .zero
    let lHip = detector.landmark(landmarks, at: 23) ?? .zero
    let rHip = detector.landmark(landmarks, at: 24) ?? .zero
    let lElbow = detector.landmark(landmarks, at: 13) ?? .zero
    let rElbow = detector.landmark(landmarks, at: 14) ?? .zero

    let midHipX = (lHip.x + rHip.x) / 2

    // Rib hump: lateral protrusion from hip midline
    let lLateral = abs(lSh.x - midHipX)
    let rLateral = abs(rSh.x - midHipX)
    let ribHumpProxy = abs(lLateral - rLateral)

    // Axillary fold difference
    let axillaryDiff = abs(lElbow.y - rElbow.y)

    // Trunk rotation angle: shoulder line vs hip line
    let shAngle = atan2(rSh.y - lSh.y, rSh.x - lSh.x) * 180 / .pi
    let hipAngle = atan2(rHip.y - lHip.y, rHip.x - lHip.x) * 180 / .pi
    var rotationAngle = abs(shAngle - hipAngle)
    if rotationAngle > 180 { rotationAngle = 360 - rotationAngle }

    // Trunk offset
    let midShX = (lSh.x + rSh.x) / 2
    let trunkOffset = midShX - midHipX

    // Scapular winging proxy
    let lScap = abs(lElbow.x - lSh.x)
    let rScap = abs(rElbow.x - rSh.x)
    let scapDiff = abs(lScap - rScap)

    // Pelvic obliquity
    let pelvicObliquity = abs(lHip.y - rHip.y)

    let thresholds = rotationAgeThresholds[ageGroup] ?? .default

    let ribHumpStatus = ribHumpProxy < thresholds.ribHumpPx ? "good" : "needs_improvement"
    let rotationStatus = rotationAngle < thresholds.rotationAngleDeg ? "good" : "needs_improvement"
    let axillaryStatus = axillaryDiff < thresholds.axillaryDiffPx ? "good" : "needs_improvement"

    // Risk score
    var riskScore: CGFloat = 0
    if ribHumpProxy > thresholds.ribHumpPx {
        riskScore += min(40, (ribHumpProxy / thresholds.ribHumpPx) * 20)
    }
    if rotationAngle > thresholds.rotationAngleDeg {
        riskScore += min(30, (rotationAngle / thresholds.rotationAngleDeg) * 15)
    }
    if axillaryDiff > thresholds.axillaryDiffPx {
        riskScore += min(20, (axillaryDiff / thresholds.axillaryDiffPx) * 10)
    }
    if scapDiff > thresholds.ribHumpPx {
        riskScore += min(10, (scapDiff / thresholds.ribHumpPx) * 5)
    }

    return RotationResult(
        ribHumpProxy: ribHumpProxy.roundedTo(2),
        ribHumpStatus: ribHumpStatus,
        axillaryFoldDiff: axillaryDiff.roundedTo(2),
        axillaryStatus: axillaryStatus,
        trunkRotationAngle: rotationAngle.roundedTo(2),
        rotationStatus: rotationStatus,
        trunkOffset: trunkOffset.roundedTo(2),
        scapularWingingDiff: scapDiff.roundedTo(2),
        pelvicObliquity: pelvicObliquity.roundedTo(2),
        rotationRiskScore: riskScore.roundedTo(1)
    )
}
