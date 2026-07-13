import SwiftUI

struct ReportView: View {
    let sessionID: String?
    @State private var pdfData: Data?
    @State private var isLoading = false
    @State private var showShare = false

    var body: some View {
        ScrollView {
            VStack(spacing: 24) {
                if isLoading {
                    ProgressView()
                        .scaleEffect(1.5)
                        .tint(.accentTeal)
                    Text("Generating Report...")
                        .font(AppFont.headline())
                        .foregroundColor(.textSecondary)
                } else if pdfData != nil {
                    successState
                } else {
                    initialState
                }
            }
            .frame(maxWidth: .infinity)
            .padding(.vertical, 60)
        }
        .background(Color.backgroundPrimary.ignoresSafeArea())
        .navigationTitle("Report")
        .sheet(isPresented: $showShare) {
            if let data = pdfData {
                ShareSheet(activityItems: [data])
            }
        }
    }

    private var successState: some View {
        VStack(spacing: 24) {
            ZStack {
                Circle()
                    .fill(Color.statusGoodLight)
                    .frame(width: 88, height: 88)
                Image(systemName: "doc.pdf.fill")
                    .font(.system(size: 36))
                    .foregroundColor(.statusGood)
            }

            Text("PDF Ready")
                .font(AppFont.title(26))

            Text("Your report is ready to share with your healthcare provider")
                .font(.subheadline)
                .foregroundColor(.textSecondary)
                .multilineTextAlignment(.center)
                .padding(.horizontal, 40)

            Button {
                showShare = true
            } label: {
                Label("Share Report", systemImage: "square.and.arrow.up")
                    .font(.headline.weight(.semibold))
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 16)
                    .background(Color.accentTeal)
                    .foregroundColor(.white)
                    .clipShape(RoundedRectangle(cornerRadius: 14))
                    .shadow(color: .accentTeal.opacity(0.3), radius: 8, x: 0, y: 4)
            }
            .padding(.horizontal, 40)

            Button(role: .destructive) {
                pdfData = nil
            } label: {
                Text("Regenerate")
                    .font(.subheadline.weight(.medium))
                    .foregroundColor(.textSecondary)
            }
        }
    }

    private var initialState: some View {
        VStack(spacing: 24) {
            ZStack {
                Circle()
                    .fill(Color.accentTealLight)
                    .frame(width: 88, height: 88)
                Image(systemName: "doc.text")
                    .font(.system(size: 36))
                    .foregroundColor(.accentTeal)
            }

            Text("Analysis Report")
                .font(AppFont.title(26))

            Text("Generate a detailed PDF report from your posture analysis results to share with your clinician")
                .font(.subheadline)
                .foregroundColor(.textSecondary)
                .multilineTextAlignment(.center)
                .padding(.horizontal, 40)

            Button {
                Task { await generateReport() }
            } label: {
                Label("Generate Report", systemImage: "doc.badge.plus")
                    .font(.headline.weight(.semibold))
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 16)
                    .background(Color.accentTeal)
                    .foregroundColor(.white)
                    .clipShape(RoundedRectangle(cornerRadius: 14))
                    .shadow(color: .accentTeal.opacity(0.3), radius: 8, x: 0, y: 4)
            }
            .padding(.horizontal, 40)
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
