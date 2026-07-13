import UIKit
import CoreImage
import OSLog

struct XrayResult {
    var cobbAngle: CGFloat
    var curveDirection: String
    var apexLevel: String
    var risserSign: String
    var curveType: String
    var confidence: CGFloat
    var message: String
}

actor XrayAnalyzer {
    static let shared = XrayAnalyzer()
    private let log = Logger(subsystem: "com.srinathsankara.scoliotrack", category: "XrayAnalyzer")

    func analyze(_ image: UIImage) -> XrayResult {
        let cgImage: CGImage
        if let cg = image.cgImage {
            cgImage = cg
        } else if let ci = image.ciImage, let cg = ci.toCGImage() {
            cgImage = cg
        } else {
            log.error("No CGImage available from input UIImage")
            return errorResult("No CGImage available")
        }

        let resized = resizeToMaxDimension(cgImage, maxDim: 400)
        let (w, h, pixels) = grayscalePixels(resized)
        guard w > 40, h > 40 else {
            log.error("Image too small: \(w)x\(h)")
            return errorResult("Image too small (\(w)x\(h))")
        }

        log.debug("Image size: \(w)x\(h), pixel count: \(pixels.count)")

        let enhanced = adaptiveEnhance(pixels, w, h)
        let spinePoints = detectSpine(enhanced, w: w, h: h)
        log.debug("Spine points detected: \(spinePoints.count)")

        guard spinePoints.count >= 12 else {
            log.warning("Insufficient spine points: \(spinePoints.count)")
            return errorResult("Spine not clearly detected (\(spinePoints.count) points)")
        }

        let smoothed = smoothPoints(spinePoints, window: 7)
        let angle = estimateCobbAngle(points: smoothed)
        let direction = classifyCurveDirection(points: smoothed)
        let apex = classifyApex(points: smoothed, imageHeight: CGFloat(h))

        log.debug("Cobb angle: \(angle)°, direction: \(direction), apex: \(apex)")

        let curveType: String
        var msg = ""
        if angle > 25 {
            curveType = "Moderate-Severe"
            msg = "Significant curvature detected"
        } else if angle > 10 {
            curveType = "Mild"
            msg = "Mild curvature detected"
        } else {
            curveType = "Normal"
            msg = "No significant curvature detected"
        }

        let confidence: CGFloat = min(1.0, CGFloat(spinePoints.count) / 80.0)

        return XrayResult(
            cobbAngle: angle,
            curveDirection: direction,
            apexLevel: apex,
            risserSign: "Not assessed",
            curveType: curveType,
            confidence: confidence,
            message: msg
        )
    }

    private func errorResult(_ msg: String) -> XrayResult {
        XrayResult(cobbAngle: 0, curveDirection: "None", apexLevel: "Unknown",
                   risserSign: "Not assessed", curveType: "Normal", confidence: 0, message: msg)
    }

    // MARK: - Preprocessing

    private func resizeToMaxDimension(_ cgImage: CGImage, maxDim: Int) -> CGImage {
        let w = cgImage.width
        let h = cgImage.height
        let scale = min(CGFloat(maxDim) / CGFloat(w), CGFloat(maxDim) / CGFloat(h))
        guard scale < 1.0 else { return cgImage }
        let newW = Int(CGFloat(w) * scale)
        let newH = Int(CGFloat(h) * scale)
        let cs = CGColorSpaceCreateDeviceGray()
        let context = CGContext(data: nil, width: newW, height: newH,
                                bitsPerComponent: 8, bytesPerRow: newW,
                                space: cs, bitmapInfo: CGImageAlphaInfo.none.rawValue)
        context?.interpolationQuality = .high
        context?.draw(cgImage, in: CGRect(x: 0, y: 0, width: newW, height: newH))
        return context?.makeImage() ?? cgImage
    }

    private func grayscalePixels(_ cgImage: CGImage) -> (Int, Int, [UInt8]) {
        let w = cgImage.width
        let h = cgImage.height
        var pixels = [UInt8](repeating: 0, count: w * h)
        let cs = CGColorSpaceCreateDeviceGray()
        let context = CGContext(data: &pixels, width: w, height: h,
                                bitsPerComponent: 8, bytesPerRow: w,
                                space: cs, bitmapInfo: CGImageAlphaInfo.none.rawValue)
        context?.draw(cgImage, in: CGRect(x: 0, y: 0, width: w, height: h))
        return (w, h, pixels)
    }

    /// Adaptive contrast enhancement using local histogram equalization
    private func adaptiveEnhance(_ pixels: [UInt8], _ w: Int, _ h: Int) -> [UInt8] {
        var result = [UInt8](repeating: 0, count: pixels.count)

        let tileSize = 32
        let tilesX = (w + tileSize - 1) / tileSize
        let tilesY = (h + tileSize - 1) / tileSize

        var tiles: [[UInt8]] = Array(repeating: Array(repeating: 0, count: w * h), count: tilesX * tilesY)
        for ty in 0..<tilesY {
            for tx in 0..<tilesX {
                let tileIdx = ty * tilesX + tx
                let xStart = tx * tileSize
                let yStart = ty * tileSize
                let xEnd = min(xStart + tileSize, w)
                let yEnd = min(yStart + tileSize, h)

                var hist = [Int](repeating: 0, count: 256)
                for y in yStart..<yEnd {
                    for x in xStart..<xEnd {
                        hist[Int(pixels[y * w + x])] += 1
                    }
                }

                var cdf = [Int](repeating: 0, count: 256)
                var sum = 0
                for i in 0..<256 { sum += hist[i]; cdf[i] = sum }
                let total = (xEnd - xStart) * (yEnd - yStart)
                let cdfMin = cdf.first(where: { $0 > 0 }) ?? 0
                let denom = max(total - cdfMin, 1)

                for y in yStart..<yEnd {
                    for x in xStart..<xEnd {
                        let idx = y * w + x
                        let v = Int(pixels[idx])
                        let mapped = (CGFloat(cdf[v] - cdfMin) / CGFloat(denom)) * 255
                        tiles[tileIdx][idx] = UInt8(max(0, min(255, mapped)))
                    }
                }
            }
        }

        for y in 0..<h {
            for x in 0..<w {
                let tx = min(x / tileSize, tilesX - 1)
                let ty = min(y / tileSize, tilesY - 1)
                result[y * w + x] = tiles[ty * tilesX + tx][y * w + x]
            }
        }

        return result
    }

    // MARK: - Spine Detection

    private func detectSpine(_ pixels: [UInt8], w: Int, h: Int) -> [CGPoint] {
        let bandHeight = max(1, h / 120)
        let stepY = max(1, bandHeight / 2)

        var rawPoints: [(x: Double, y: Double, score: Double)] = []

        for yStart in stride(from: 0, to: h - bandHeight, by: stepY) {
            let yEnd = min(yStart + bandHeight, h)
            let midY = (yStart + yEnd) / 2

            let brightThreshold = computeBrightThreshold(pixels, w, h, yStart, yEnd)

            var bestX = w / 2
            var bestScore: Double = 0

            let stripHalf = 4

            for x in stripHalf..<(w - stripHalf) {
                var score: Double = 0
                var count = 0
                for y in yStart..<yEnd {
                    for dx in -stripHalf...stripHalf {
                        let px = x + dx
                        if px >= 0, px < w {
                            let val = Int(pixels[y * w + px])
                            if val >= brightThreshold {
                                score += Double(val - brightThreshold)
                            }
                            count += 1
                        }
                    }
                }
                let avg = score / Double(max(1, count))
                if avg > bestScore {
                    bestScore = avg
                    bestX = x
                }
            }

            if bestScore > 0.5 {
                rawPoints.append((x: Double(bestX), y: Double(midY), score: bestScore))
            }
        }

        guard rawPoints.count >= 6 else {
            log.warning("Only \(rawPoints.count) points after threshold filtering")
            return rawPoints.map { CGPoint(x: $0.x, y: $0.y) }
        }

        let medianX = rawPoints.sorted(by: { $0.x < $1.x })[rawPoints.count / 2].x
        let filtered = rawPoints.filter { abs($0.x - medianX) < Double(w) * 0.45 }
        log.debug("Median X: \(medianX), filtered from \(rawPoints.count) to \(filtered.count) points")

        guard filtered.count >= 6 else {
            return rawPoints.map { CGPoint(x: $0.x, y: $0.y) }
        }

        let weighted = filtered.map { CGPoint(x: $0.x, y: $0.y) }
        return weighted
    }

    private func computeBrightThreshold(_ pixels: [UInt8], _ w: Int, _ h: Int,
                                         _ yStart: Int, _ yEnd: Int) -> Int {
        var values: [Int] = []
        for y in yStart..<yEnd {
            for x in 0..<w {
                values.append(Int(pixels[y * w + x]))
            }
        }
        values.sort()
        let topIdx = Int(Double(values.count) * 0.75)
        return values[min(topIdx, values.count - 1)]
    }

    private func smoothPoints(_ points: [CGPoint], window: Int) -> [CGPoint] {
        guard points.count > window * 2 else { return points }
        var result: [CGPoint] = []
        let half = window / 2
        for i in 0..<points.count {
            let start = max(0, i - half)
            let end = min(points.count, i + half + 1)
            let slice = points[start..<end]
            let avgX = slice.reduce(0) { $0 + $1.x } / CGFloat(slice.count)
            result.append(CGPoint(x: avgX, y: points[i].y))
        }
        return result
    }

    // MARK: - Cobb Angle Estimation

    private func estimateCobbAngle(points: [CGPoint]) -> CGFloat {
        guard points.count > 12 else { return 0 }

        let n = points.count
        let first = points.first!
        let last = points.last!
        let dx = last.x - first.x
        let dy = last.y - first.y
        let lineLen = sqrt(dx * dx + dy * dy)
        guard lineLen > 0 else { return 0 }

        var deviations: [CGFloat] = []
        for p in points {
            let dist = ((p.x - first.x) * dy - (p.y - first.y) * dx) / lineLen
            deviations.append(dist)
        }

        guard let maxAbsDev = deviations.map({ abs($0) }).max(), maxAbsDev > 2 else {
            return 0
        }

        let apexIdx = deviations.firstIndex { abs($0) == maxAbsDev } ?? n / 2
        let apex = points[apexIdx]

        var maxAngleAbove: CGFloat = 0
        for i in 0..<apexIdx {
            let p = points[i]
            let ddx = apex.x - p.x
            let ddy = apex.y - p.y
            if abs(ddy) > 2 {
                let angle = atan2(abs(ddx), abs(ddy)) * 180 / .pi
                if angle > maxAngleAbove { maxAngleAbove = angle }
            }
        }

        var maxAngleBelow: CGFloat = 0
        for i in (apexIdx + 1)..<n {
            let p = points[i]
            let ddx = p.x - apex.x
            let ddy = p.y - apex.y
            if abs(ddy) > 2 {
                let angle = atan2(abs(ddx), abs(ddy)) * 180 / .pi
                if angle > maxAngleBelow { maxAngleBelow = angle }
            }
        }

        let cobb = maxAngleAbove + maxAngleBelow
        log.debug("Cobb estimator: above=\(maxAngleAbove)°, below=\(maxAngleBelow)°, total=\(cobb)°")

        if cobb < 5 && maxAbsDev > 4 {
            let imgHeight = last.y - first.y
            let devRatio = maxAbsDev / max(imgHeight, 1)
            let fallback = devRatio * 160.0
            log.debug("Fallback estimator: devRatio=\(devRatio), angle=\(fallback)°")
            return fallback
        }

        return cobb
    }

    private func classifyCurveDirection(points: [CGPoint]) -> String {
        guard points.count > 5 else { return "None" }
        let midX = (points.first!.x + points.last!.x) / 2
        let deviations = points.map { $0.x - midX }
        let netDeviation = deviations.reduce(0, +)
        guard let maxAbs = deviations.map({ abs($0) }).max(), maxAbs > 2 else { return "None" }
        return netDeviation > 0 ? "Right" : "Left"
    }

    private func classifyApex(points: [CGPoint], imageHeight: CGFloat) -> String {
        guard points.count > 5 else { return "Unknown" }
        let first = points.first!
        let last = points.last!
        let dx = last.x - first.x
        let dy = last.y - first.y
        let lineLen = sqrt(dx * dx + dy * dy)
        guard lineLen > 0 else { return "Unknown" }

        var maxDist: CGFloat = 0
        var apexY: CGFloat = 0
        for p in points {
            let dist = abs((p.x - first.x) * dy - (p.y - first.y) * dx) / lineLen
            if dist > maxDist { maxDist = dist; apexY = p.y }
        }

        let ratio = (apexY - first.y) / max(last.y - first.y, 1)
        if ratio < 0.3 { return "Thoracic (upper)" }
        if ratio < 0.5 { return "Thoracic" }
        if ratio < 0.7 { return "Thoracolumbar" }
        return "Lumbar"
    }
}

private extension CIImage {
    func toCGImage() -> CGImage? {
        let context = CIContext()
        return context.createCGImage(self, from: self.extent)
    }
}
