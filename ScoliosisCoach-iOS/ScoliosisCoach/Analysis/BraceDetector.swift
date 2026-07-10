import UIKit
import CoreImage

func detectBrace(in image: UIImage) -> Bool {
    guard let cgImage = image.cgImage else { return false }

    let ciImage = CIImage(cgImage: cgImage)
    let context = CIContext()

    let width = image.size.width
    let height = image.size.height

    // Define torso region (center 70% horizontally, middle 50% vertically)
    let torsoRect = CGRect(
        x: width * 0.15, y: height * 0.25,
        width: width * 0.7, height: height * 0.5
    )

    // Crop to torso
    guard let torsoCG = cgImage.cropping(to: torsoRect) else { return false }

    // Check for edges (real person, not blank background)
    guard let edgeFilter = CIFilter(name: "CIEdges") else { return false }
    let torsoCI = CIImage(cgImage: torsoCG)
    edgeFilter.setValue(torsoCI, forKey: kCIInputImageKey)
    guard let edgeOutput = edgeFilter.outputImage,
          let edgeCG = context.createCGImage(edgeOutput, from: edgeOutput.extent) else { return false }

    let edgePixels = UIImage(cgImage: edgeCG).cgImage?.pixelData() ?? Data()
    let torsoW = Int(torsoRect.width)
    let torsoH = Int(torsoRect.height)
    let edgeDensity = averageBrightness(pixelData: edgePixels, width: torsoW, height: torsoH,
                                        xStart: 0, xEnd: torsoW)

    // No contours — likely a blank image
    guard edgeDensity > 3 else { return false }

    // Center torso region for brace detection
    let centerRect = CGRect(
        x: width * 0.35, y: height * 0.25,
        width: width * 0.3, height: height * 0.5
    )
    guard let centerCG = cgImage.cropping(to: centerRect) else { return false }
    let centerCI = CIImage(cgImage: centerCG)

    // Detect white/light colors (brace material)
    guard let colorFilter = CIFilter(name: "CIWhitePointAdjust") else { return false }
    colorFilter.setValue(centerCI, forKey: kCIInputImageKey)
    colorFilter.setValue(CIColor.white, forKey: kCIInputColorKey)
    guard let colorOutput = colorFilter.outputImage,
          let colorCG = context.createCGImage(colorOutput, from: colorOutput.extent) else { return false }

    let cw = Int(centerRect.width)
    let ch = Int(centerRect.height)
    let pixelData = UIImage(cgImage: colorCG).cgImage?.pixelData() ?? Data()
    let meanBrightness = averageBrightness(pixelData: pixelData, width: cw, height: ch,
                                           xStart: 0, xEnd: cw)

    // If center torso is significantly bright, brace is likely present
    let brightnessThreshold: CGFloat = 200
    return meanBrightness > brightnessThreshold
}
