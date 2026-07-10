import SwiftUI

struct ReportView: View {
    let sessionID: String?
    @State private var pdfData: Data?
    @State private var isLoading = false
    @State private var showShare = false

    var body: some View {
        VStack(spacing: 16) {
            if isLoading {
                ProgressView("Generating Report...")
            } else if pdfData != nil {
                Image(systemName: "doc.pdf.fill")
                    .font(.system(size: 64))
                    .foregroundColor(.accentColor)
                Text("PDF Report Ready")
                    .font(.title2).bold()
                Button("Share Report") {
                    showShare = true
                }
                .buttonStyle(.borderedProminent)
            } else {
                Image(systemName: "doc.text")
                    .font(.system(size: 48))
                    .foregroundColor(.secondary)
                Text("Generate a PDF report from your analysis results")
                    .foregroundColor(.secondary)
                Button("Generate") {
                    Task { await generateReport() }
                }
                .buttonStyle(.borderedProminent)
            }
        }
        .padding()
        .navigationTitle("Report")
        .sheet(isPresented: $showShare) {
            if let data = pdfData {
                ShareSheet(activityItems: [data])
            }
        }
    }

    private func generateReport() async {
        isLoading = true
        if let id = sessionID {
            pdfData = await ReportService.shared.generatePDF(sessionIDs: [id])
        }
        isLoading = false
    }
}

struct ShareSheet: UIViewControllerRepresentable {
    let activityItems: [Any]

    func makeUIViewController(context: Context) -> UIActivityViewController {
        UIActivityViewController(activityItems: activityItems, applicationActivities: nil)
    }

    func updateUIViewController(_ uiViewController: UIActivityViewController, context: Context) {}
}
