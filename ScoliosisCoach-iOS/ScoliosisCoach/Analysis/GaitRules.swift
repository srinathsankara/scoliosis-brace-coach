import Foundation

/// Gait analysis requires a temporal sequence of frames from video.
/// When called with a single frame (photo mode), returns a static posture
/// estimate rather than true gait metrics.
struct GaitResult {
    let pelvicTilt: CGFloat
    let stepAsymmetry: CGFloat
    let strideLengthDiff: CGFloat
    let gaitSymmetryScore: CGFloat
    let isVideoBased: Bool
}

func analyzeGait(landmarksFrames: [[[String: CGFloat]]], imageSize: CGSize) -> GaitResult? {
    guard let lastFrame = landmarksFrames.last,
          lastFrame.count >= 25 else { return nil }

    let isVideo = landmarksFrames.count > 1

    let lHip = CGPoint(x: lastFrame[23]["x"] ?? 0, y: lastFrame[23]["y"] ?? 0)
    let rHip = CGPoint(x: lastFrame[24]["x"] ?? 0, y: lastFrame[24]["y"] ?? 0)
    let lAnkle = CGPoint(x: lastFrame[27]["x"] ?? 0, y: lastFrame[27]["y"] ?? 0)
    let rAnkle = CGPoint(x: lastFrame[28]["x"] ?? 0, y: lastFrame[28]["y"] ?? 0)
    let lKnee = CGPoint(x: lastFrame[25]["x"] ?? 0, y: lastFrame[25]["y"] ?? 0)
    let rKnee = CGPoint(x: lastFrame[26]["x"] ?? 0, y: lastFrame[26]["y"] ?? 0)

    let pelvicTilt = abs(lHip.x - rHip.x)
    let stepAsymmetry = abs(lAnkle.x - rAnkle.x)

    let leftStride = abs(lAnkle.x - lKnee.x)
    let rightStride = abs(rAnkle.x - rKnee.x)
    let strideDiff = abs(leftStride - rightStride)

    return GaitResult(
        pelvicTilt: pelvicTilt.rounded(to: 2),
        stepAsymmetry: stepAsymmetry.rounded(to: 2),
        strideLengthDiff: strideDiff.rounded(to: 2),
        gaitSymmetryScore: max(0, 100 - (pelvicTilt + stepAsymmetry + strideDiff * 2).rounded(to: 1)),
        isVideoBased: isVideo
    )
}
