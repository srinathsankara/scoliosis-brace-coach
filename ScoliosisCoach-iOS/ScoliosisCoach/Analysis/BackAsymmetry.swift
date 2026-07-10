import UIKit
import CoreImage
import Accelerate

struct BackAsymmetryResult {
    let brightnessAsymmetry: CGFloat
    let midlineDeviation: CGFloat
    let textureAsymmetry: CGFloat
    let edgeAsymmetry: CGFloat
    let spineCurveScore: CGFloat
    let backAsymmetryRisk: CGFloat
    let backAsymmetryStatus: String
}

func analyzeBackAsymmetry(
    image: UIImage,
    landmarks: [[String: CGFloat]]
) -> BackAsymmetryResult? {
    guard landmarks.count >= 25,
          let cgImage = image.cgImage else { return nil }

    let detector = PoseDetector.shared
    let lSh = detector.landmark(landmarks, at: 11) ?? .zero
    let rSh = detector.landmark(landmarks, at: 12) ?? .zero
    let lHip = detector.landmark(landmarks, at: 23) ?? .zero
    let rHip = detector.landmark(landmarks, at: 24) ?? .zero

    let midShX = (lSh.x + rSh.x) / 2
    let midHipX = (lHip.x + rHip.x) / 2
    let width = image.size.width
    let height = image.size.height

    // Define torso region
    let xMin = max(0, min(lSh.x, lHip.x) - 10)
    let xMax = min(width, max(rSh.x, rHip.x) + 10)
    let yMin = max(0, midShX - 20)
    let yMax = min(height, midHipX + 20)

    guard xMax > xMin, yMax > yMin else { return nil }

    // Crop to torso region
    let cropRect = CGRect(x: xMin, y: yMin, width: xMax - xMin, height: yMax - yMin)
    guard let cropped = cgImage.cropping(to: cropRect) else { return nil }

    let ciImage = CIImage(cgImage: cropped)
    let context = CIContext(options: [.outputPremultiplied: true])

    // Convert to grayscale for analysis
    guard let grayFilter = CIFilter(name: "CIPhotoEffectMono") else { return nil }
    grayFilter.setValue(ciImage, forKey: kCIInputImageKey)
    guard let grayOutput = grayFilter.outputImage,
          let grayCG = context.createCGImage(grayOutput, from: grayOutput.extent) else { return nil }

    let gray = UIImage(cgImage: grayCG)
    let grayWidth = Int(gray.size.width)
    let grayHeight = Int(gray.size.height)
    let midX = Int((midShX - xMin))
    let midHipXLocal = Int((midHipX - xMin))

    guard midX > 0, midX < grayWidth, let pixelData = gray.cgImage?.pixelData() else { return nil }

    // --- Brightness Asymmetry ---
    let leftBrightness = averageBrightness(pixelData: pixelData, width: grayWidth, height: grayHeight,
                                           xStart: 0, xEnd: midX)
    let rightBrightness = averageBrightness(pixelData: pixelData, width: grayWidth, height: grayHeight,
                                            xStart: midX, xEnd: grayWidth)
    let brightnessAsymmetry = abs(leftBrightness - rightBrightness)

    // --- Edge Asymmetry ---
    guard let edgeFilter = CIFilter(name: "CIEdges") else { return nil }
    edgeFilter.setValue(ciImage, forKey: kCIInputImageKey)
    edgeFilter.setValue(5.0, forKey: kCIInputIntensityKey)
    guard let edgeOutput = edgeFilter.outputImage,
          let edgeCG = context.createCGImage(edgeOutput, from: edgeOutput.extent) else { return nil }

    let edgePixelData = UIImage(cgImage: edgeCG).cgImage?.pixelData() ?? pixelData
    let leftEdges = averageBrightness(pixelData: edgePixelData, width: grayWidth, height: grayHeight,
                                      xStart: 0, xEnd: midX)
    let rightEdges = averageBrightness(pixelData: edgePixelData, width: grayWidth, height: grayHeight,
                                       xStart: midX, xEnd: grayWidth)
    let edgeAsymmetry = abs(leftEdges - rightEdges)

    // --- Texture Asymmetry (Laplacian variance proxy) ---
    let leftTexture = textureVariance(pixelData: pixelData, width: grayWidth, height: grayHeight,
                                      xStart: 0, xEnd: midX)
    let rightTexture = textureVariance(pixelData: pixelData, width: grayWidth, height: grayHeight,
                                       xStart: midX, xEnd: grayWidth)
    let textureAsymmetry = abs(leftTexture - rightTexture)

    // --- Midline Deviation ---
    let midlineDeviation = measureMidlineDeviation(pixelData: pixelData, width: grayWidth, height: grayHeight, midX: midHipXLocal)

    // --- Spine Curve Score ---
    let spineCurveScore = measureSpineCurve(pixelData: pixelData, width: grayWidth, height: grayHeight, midX: midX)

    // --- Combined Risk Score ---
    var riskScore: CGFloat = 0
    if brightnessAsymmetry > 5 { riskScore += min(25, brightnessAsymmetry * 1.5) }
    if midlineDeviation > 1 { riskScore += min(25, midlineDeviation * 5) }
    if textureAsymmetry > 5 { riskScore += min(20, textureAsymmetry * 0.8) }
    if edgeAsymmetry > 5 { riskScore += min(15, edgeAsymmetry * 0.6) }
    if spineCurveScore > 1 { riskScore += min(15, spineCurveScore * 3) }

    let clampedRisk = min(100, max(0, riskScore))
    let status = clampedRisk > 20 ? "needs_improvement" : "good"

    return BackAsymmetryResult(
        brightnessAsymmetry: brightnessAsymmetry.rounded(to: 2),
        midlineDeviation: midlineDeviation.rounded(to: 2),
        textureAsymmetry: textureAsymmetry.rounded(to: 2),
        edgeAsymmetry: edgeAsymmetry.rounded(to: 2),
        spineCurveScore: spineCurveScore.rounded(to: 2),
        backAsymmetryRisk: clampedRisk.rounded(to: 1),
        backAsymmetryStatus: status
    )
}

// MARK: - Pixel Helpers

private func averageBrightness(pixelData: Data, width: Int, height: Int, xStart: Int, xEnd: Int) -> CGFloat {
    let bytesPerRow = width * 4
    var total: UInt64 = 0
    var count: UInt64 = 0

    for y in 0..<height {
        for x in xStart..<min(xEnd, width) {
            let offset = y * bytesPerRow + x * 4
            if offset + 3 < pixelData.count {
                let r = UInt64(pixelData[offset])
                let g = UInt64(pixelData[offset + 1])
                let b = UInt64(pixelData[offset + 2])
                total += (r + g + b) / 3
                count += 1
            }
        }
    }

    return count > 0 ? CGFloat(total) / CGFloat(count) : 0
}

private func textureVariance(pixelData: Data, width: Int, height: Int, xStart: Int, xEnd: Int) -> CGFloat {
    let mean = averageBrightness(pixelData: pixelData, width: width, height: height, xStart: xStart, xEnd: xEnd)
    let bytesPerRow = width * 4
    var variance: CGFloat = 0
    var count: CGFloat = 0

    for y in 1..<(height - 1) {
        for x in max(1, xStart)..<min(xEnd - 1, width - 1) {
            let offset = y * bytesPerRow + x * 4
            guard offset + 3 < pixelData.count else { continue }
            let val = CGFloat(pixelData[offset])
            // Simple Laplacian approximation
            let top = CGFloat(pixelData[(y - 1) * bytesPerRow + x * 4])
            let bottom = CGFloat(pixelData[(y + 1) * bytesPerRow + x * 4])
            let left = CGFloat(pixelData[y * bytesPerRow + (x - 1) * 4])
            let right = CGFloat(pixelData[y * bytesPerRow + (x + 1) * 4])
            let laplacian = abs(4 * val - top - bottom - left - right)
            variance += (laplacian - mean) * (laplacian - mean)
            count += 1
        }
    }

    return count > 0 ? sqrt(variance / count) : 0
}

private func measureMidlineDeviation(pixelData: Data, width: Int, height: Int, midX: Int) -> CGFloat {
    let bytesPerRow = width * 4
    var deviations: [CGFloat] = []

    let stepY = max(1, height / 10)
    for y in stride(from: height / 4, to: 3 * height / 4, by: stepY) {
        var totalBrightness: UInt64 = 0
        var weightedSum: UInt64 = 0
        for x in 0..<width {
            let offset = y * bytesPerRow + x * 4
            guard offset + 3 < pixelData.count else { continue }
            let b = UInt64(pixelData[offset])
            totalBrightness += b
            weightedSum += b * UInt64(x)
        }
        if totalBrightness > 0 {
            let com = CGFloat(weightedSum) / CGFloat(totalBrightness)
            deviations.append(abs(com - CGFloat(midX)))
        }
    }

    return deviations.isEmpty ? 0 : deviations.reduce(0, +) / CGFloat(deviations.count)
}

private func measureSpineCurve(pixelData: Data, width: Int, height: Int, midX: Int) -> CGFloat {
    let bytesPerRow = width * 4
    let stripWidth = max(5, width / 10)
    let leftStart = max(0, midX - stripWidth)
    let rightEnd = min(width, midX + stripWidth)

    var leftProfile: [CGFloat] = []
    var rightProfile: [CGFloat] = []

    for y in 0..<height {
        var leftSum: UInt64 = 0
        var leftCount: UInt64 = 0
        var rightSum: UInt64 = 0
        var rightCount: UInt64 = 0

        for x in leftStart..<midX {
            let offset = y * bytesPerRow + x * 4
            guard offset + 3 < pixelData.count else { continue }
            leftSum += UInt64(pixelData[offset])
            leftCount += 1
        }
        for x in midX..<rightEnd {
            let offset = y * bytesPerRow + x * 4
            guard offset + 3 < pixelData.count else { continue }
            rightSum += UInt64(pixelData[offset])
            rightCount += 1
        }

        if leftCount > 0 && rightCount > 0 {
            leftProfile.append(CGFloat(leftSum) / CGFloat(leftCount))
            rightProfile.append(CGFloat(rightSum) / CGFloat(rightCount))
        }
    }

    guard leftProfile.count > 10 else { return 0 }

    let diffs = zip(leftProfile, rightProfile).map { $0 - $1 }
    let meanDiff = diffs.reduce(0, +) / CGFloat(diffs.count)
    let variance = diffs.map { ($0 - meanDiff) * ($0 - meanDiff) }.reduce(0, +) / CGFloat(diffs.count)
    let stdDiff = sqrt(variance)
    let consistency = stdDiff > 0 ? abs(meanDiff) / stdDiff : 0

    // Curve gradient
    let indices = Array(0..<diffs.count)
    let xMean = CGFloat(indices.count - 1) / 2
    let yMean = meanDiff
    var num: CGFloat = 0
    var den: CGFloat = 0
    for (i, d) in diffs.enumerated() {
        num += (CGFloat(i) - xMean) * (d - yMean)
        den += (CGFloat(i) - xMean) * (CGFloat(i) - xMean)
    }
    let slope = den > 0 ? num / den : 0
    let curveGradient = abs(slope) * CGFloat(diffs.count) * 0.3

    return consistency * abs(meanDiff) + curveGradient
}

extension CGImage {
    func pixelData() -> Data? {
        let width = self.width
        let height = self.height
        let bytesPerRow = width * 4
        var data = Data(count: bytesPerRow * height)
        data.withUnsafeMutableBytes { ptr in
            if let context = CGContext(
                data: ptr.baseAddress,
                width: width,
                height: height,
                bitsPerComponent: 8,
                bytesPerRow: bytesPerRow,
                space: CGColorSpaceCreateDeviceRGB(),
                bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue
            ) {
                context.draw(self, in: CGRect(x: 0, y: 0, width: width, height: height))
            }
        }
        return data
    }
}
