import UIKit

actor ReportService {
    static let shared = ReportService()

    func generatePDF(sessionIDs: [String]) async -> Data? {
        let db = DatabaseService.shared
        var sessions: [Session] = []
        for id in sessionIDs {
            if let session = try? await db.getSession(id: id) {
                sessions.append(session)
            }
        }
        return generatePDF(sessions: sessions)
    }

    func generatePDF(sessions: [Session]) -> Data? {
        let pdfMetaData = [
            kCGPDFContextCreator: "Scoliosis Brace Coach",
            kCGPDFContextAuthor: "Srinath Sankara",
            kCGPDFContextTitle: "Scoliosis Monitoring Report"
        ]
        let format = UIGraphicsPDFRendererFormat()
        format.documentInfo = pdfMetaData as [String: Any]

        let pageWidth: CGFloat = 595.2
        let pageHeight: CGFloat = 841.8
        let renderer = UIGraphicsPDFRenderer(
            bounds: CGRect(x: 0, y: 0, width: pageWidth, height: pageHeight),
            format: format
        )

        let data = renderer.pdfData { context in
            context.beginPage()

            let titleFont = UIFont.boldSystemFont(ofSize: 18)
            let headingFont = UIFont.boldSystemFont(ofSize: 14)
            let bodyFont = UIFont.systemFont(ofSize: 10)
            let smallFont = UIFont.systemFont(ofSize: 8)

            // Title
            "Scoliosis Brace Monitoring Report".draw(at: CGPoint(x: 40, y: 40),
                                                     withAttributes: [.font: titleFont])
            let dateStr = DateFormatter.localizedString(from: Date(), dateStyle: .medium, timeStyle: .short)
            "Generated: \(dateStr)".draw(at: CGPoint(x: 40, y: 68),
                                         withAttributes: [.font: smallFont, .foregroundColor: UIColor.gray])
            "Created by Srinath Sankara".draw(at: CGPoint(x: 40, y: 82),
                                              withAttributes: [.font: smallFont, .foregroundColor: UIColor.gray])

            // Disclaimer
            let disclaimerRect = CGRect(x: 40, y: 100, width: pageWidth - 80, height: 50)
            let disclaimerText = """
            MEDICAL DISCLAIMER: This report is for educational and monitoring purposes only. \
            It is not a medical device and does not provide diagnosis. Always consult a qualified healthcare provider.
            """
            disclaimerText.draw(in: disclaimerRect, withAttributes: [
                .font: UIFont.systemFont(ofSize: 7),
                .foregroundColor: UIColor.red
            ])

            var yPos: CGFloat = 160

            // Session Summary
            "Session Summary".draw(at: CGPoint(x: 40, y: yPos),
                                   withAttributes: [.font: headingFont])
            yPos += 24

            let decoder = JSONDecoder()
            for session in sessions {
                guard let metrics = try? decoder.decode(MetricsResult.self, from: session.metricsJSON) else {
                    continue
                }

                let modeStr = session.mode.replacingOccurrences(of: "_", with: " ").capitalized
                "\(modeStr) — \(DateFormatter.localizedString(from: session.createdAt, dateStyle: .short, timeStyle: .short))"
                    .draw(at: CGPoint(x: 40, y: yPos), withAttributes: [.font: bodyFont])
                yPos += 16

                // FIX #16: right-align values for readability
                let labelX: CGFloat = 50
                let valueX: CGFloat = 280

                let rowData: [(label: String, value: String)] = [
                    ("Trunk Lean Angle", "\(metrics.trunkLeanAngle)° (\(metrics.trunkStatus))"),
                    ("Shoulder Asymmetry", "\(metrics.shoulderAsymmetry) px (\(metrics.shoulderStatus))"),
                    ("Rotation Risk", "\(metrics.rotationRiskScore)/100 (\(metrics.rotationStatus))"),
                    ("Back Asymmetry Risk", "\(metrics.backAsymmetryRisk)% (\(metrics.backAsymmetryStatus))"),
                ]

                for row in rowData {
                    row.label.draw(at: CGPoint(x: labelX, y: yPos),
                                   withAttributes: [.font: smallFont])
                    row.value.draw(at: CGPoint(x: valueX, y: yPos),
                                   withAttributes: [.font: smallFont, .foregroundColor: UIColor.darkGray])
                    yPos += 14
                }
                yPos += 8

                if yPos > pageHeight - 60 {
                    context.beginPage()
                    yPos = 40
                }
            }

            // Footer
            let footer = "Scoliosis Brace Coach — Created by Srinath Sankara — Educational purposes only"
            footer.draw(at: CGPoint(x: 40, y: pageHeight - 30),
                        withAttributes: [.font: smallFont, .foregroundColor: UIColor.gray])
        }

        return data
    }
}
