import SwiftUI
import PhotosUI

struct AnalysisView: View {
    @State private var selectedImage: UIImage?
    @State private var selectedItem: PhotosPickerItem?
    @State private var isAnalyzing = false
    @State private var result: AnalysisResult?
    @State private var showResult = false
    @State private var selectedMode = "standing_no_brace"
    @State private var selectedAgeGroup = "under15"
    @State private var showCamera = false

    let modes: [(key: String, icon: String, label: String)] = [
        ("standing_no_brace", "figure.stand", "Standing"),
        ("standing_with_brace", "shield", "Braced"),
        ("walking_no_brace", "figure.walk", "Walking"),
        ("exercises_no_brace", "figure.core.training", "Exercise"),
        ("xray", "spine", "X-Ray"),
    ]

    let ageGroups: [(key: String, label: String)] = [
        ("under12", "Under 12"),
        ("under15", "13–15"),
        ("under18", "16–18"),
        ("adult", "Adult"),
    ]

    var body: some View {
        ScrollView {
            VStack(spacing: 0) {
                heroSection
                contentStack
            }
        }
        .scrollDismissesKeyboard(.immediately)
        .background(Color.backgroundPrimary.ignoresSafeArea())
        .sheet(isPresented: $showResult) {
            if let result {
                ResultsView(result: result)
            }
        }
        .sheet(isPresented: $showCamera) {
            CameraPicker(image: $selectedImage)
        }
    }

    // MARK: - Hero

    private var heroSection: some View {
        ZStack {
            Color.accentTeal
                .ignoresSafeArea(edges: .top)

            Circle()
                .fill(.white.opacity(0.08))
                .frame(width: 200)
                .offset(x: 100, y: -60)
                .blur(radius: 50)

            Circle()
                .fill(.white.opacity(0.06))
                .frame(width: 150)
                .offset(x: -60, y: 30)
                .blur(radius: 40)

            VStack(spacing: 6) {
                HStack(spacing: 8) {
                    Image(systemName: "spine")
                        .font(.title2)
                        .foregroundColor(.white.opacity(0.7))
                    Text("ScolioTrack")
                        .font(.system(size: 30, weight: .bold, design: .rounded))
                        .foregroundColor(.white)
                }

                Text("AI-Powered Posture Screening")
                    .font(.system(size: 15, weight: .medium, design: .rounded))
                    .foregroundColor(.white.opacity(0.8))
            }
            .padding(.vertical, 44)
        }
        .frame(maxWidth: .infinity)
    }

    // MARK: - Content

    private var contentStack: some View {
        VStack(spacing: 20) {
            photoSection
            modeSection
            ageSection
            analyzeButton
        }
        .padding(.horizontal, 20)
        .padding(.top, 20)
        .padding(.bottom, 32)
    }

    // MARK: - Photo

    private var photoSection: some View {
        VStack(spacing: 8) {
            if let image = selectedImage {
                ZStack(alignment: .topTrailing) {
                    Image(uiImage: image)
                        .resizable()
                        .scaledToFill()
                        .frame(height: 200)
                        .clipShape(RoundedRectangle(cornerRadius: 20))
                        .overlay(
                            RoundedRectangle(cornerRadius: 20)
                                .stroke(Color.accentTeal.opacity(0.3), lineWidth: 2)
                        )
                        .shadow(color: .cardShadowDark, radius: 16, x: 0, y: 8)

                    HStack(spacing: 8) {
                        Button {
                            showCamera = true
                        } label: {
                            ZStack {
                                Circle()
                                    .fill(.ultraThinMaterial)
                                    .frame(width: 36, height: 36)
                                Image(systemName: "camera.fill")
                                    .font(.caption.weight(.bold))
                                    .foregroundColor(.white)
                            }
                        }

                        Button {
                            withAnimation(.spring(response: 0.4)) {
                                selectedImage = nil
                                selectedItem = nil
                            }
                        } label: {
                            ZStack {
                                Circle()
                                    .fill(.ultraThinMaterial)
                                    .frame(width: 36, height: 36)
                                Image(systemName: "xmark")
                                    .font(.caption.weight(.bold))
                                    .foregroundColor(.white)
                            }
                        }
                    }
                    .padding(12)
                }
            } else {
                PhotosPicker(selection: $selectedItem, matching: .images) {
                    ZStack {
                        RoundedRectangle(cornerRadius: 20)
                            .fill(Color.accentTealLight)
                            .frame(height: 200)

                        RoundedRectangle(cornerRadius: 20)
                            .strokeBorder(
                                style: StrokeStyle(lineWidth: 2, dash: [10, 8])
                            )
                            .foregroundColor(.accentTeal.opacity(0.3))
                            .frame(height: 200)

                        VStack(spacing: 16) {
                            ZStack {
                                Circle()
                                    .fill(Color.accentTeal.opacity(0.12))
                                    .frame(width: 72, height: 72)
                                Image(systemName: "camera.viewfinder")
                                    .font(.system(size: 30))
                                    .foregroundColor(.accentTeal)
                            }

                            Text("Select Back View Photo")
                                .font(.headline.weight(.semibold))
                                .foregroundColor(.accentTeal)

                            Text("Full body from behind • or tap retake")
                                .font(.subheadline)
                                .foregroundColor(.accentTeal.opacity(0.7))
                        }
                    }
                }
                .buttonStyle(.plain)
                .onChange(of: selectedItem) { _, newItem in
                    Task {
                        guard let data = try? await newItem?.loadTransferable(type: Data.self),
                              let image = UIImage(data: data) else { return }
                        await MainActor.run { selectedImage = image }
                    }
                }
            }
        }
    }

    // MARK: - Mode Chips

    private var modeSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Label("Assessment Type", systemImage: "list.bullet")
                .font(.subheadline.weight(.semibold))
                .foregroundColor(.textSecondary)

            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 10) {
                    ForEach(modes, id: \.key) { mode in
                        Button {
                            withAnimation(.spring(response: 0.3, dampingFraction: 0.7)) {
                                selectedMode = mode.key
                            }
                        } label: {
                            HStack(spacing: 8) {
                                Image(systemName: mode.icon)
                                    .font(.subheadline)
                                Text(mode.label)
                                    .font(.subheadline.weight(.medium))
                            }
                            .padding(.horizontal, 18)
                            .padding(.vertical, 12)
                            .background(
                                selectedMode == mode.key
                                    ? AnyShapeStyle(Color.accentTeal)
                                    : AnyShapeStyle(Color.cardBackground)
                            )
                            .foregroundColor(selectedMode == mode.key ? .white : .textPrimary)
                            .clipShape(Capsule())
                            .shadow(color: selectedMode == mode.key ? .accentTeal.opacity(0.25) : .cardShadow,
                                    radius: 6, x: 0, y: 3)
                            .overlay(
                                Capsule()
                                    .stroke(selectedMode == mode.key ? Color.clear : .dividerColor, lineWidth: 1)
                            )
                        }
                    }
                }
            }
        }
    }

    // MARK: - Age

    private var ageSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Label("Age Group", systemImage: "person.fill")
                .font(.subheadline.weight(.semibold))
                .foregroundColor(.textSecondary)

            Picker("Age", selection: $selectedAgeGroup) {
                ForEach(ageGroups, id: \.key) { group in
                    Text(group.label).tag(group.key)
                }
            }
            .pickerStyle(.segmented)
        }
    }

    // MARK: - CTA Button

    private var analyzeButton: some View {
        Button(action: runAnalysis) {
            HStack(spacing: 10) {
                if isAnalyzing {
                    ProgressView()
                        .progressViewStyle(CircularProgressViewStyle(tint: .white))
                        .scaleEffect(1.1)
                } else {
                    Image(systemName: "arrow.right.circle.fill")
                        .font(.headline)
                        .symbolEffect(.bounce.up, value: selectedImage != nil)
                    Text("Start Analysis")
                        .font(.headline.weight(.semibold))
                }
            }
            .frame(maxWidth: .infinity)
            .padding(.vertical, 18)
            .background(
                selectedImage != nil && !isAnalyzing
                    ? AnyShapeStyle(Color.gradientPremium)
                    : AnyShapeStyle(Color.dividerColor)
            )
            .foregroundColor(selectedImage != nil && !isAnalyzing ? .white : .textTertiary)
            .clipShape(RoundedRectangle(cornerRadius: 16))
            .shadow(
                color: selectedImage != nil && !isAnalyzing ? .accentTeal.opacity(0.35) : .clear,
                radius: 14, x: 0, y: 7
            )
            .scaleEffect(isAnalyzing ? 0.97 : 1)
            .animation(.spring(response: 0.3), value: isAnalyzing)
        }
        .disabled(selectedImage == nil || isAnalyzing)
        .padding(.top, 4)
    }

    // MARK: - Actions

    private func runAnalysis() {
        guard let image = selectedImage else { return }
        isAnalyzing = true
        Task {
            result = await AnalysisService.shared.analyze(
                image: image,
                mode: selectedMode,
                ageGroup: selectedAgeGroup
            )
            isAnalyzing = false
            showResult = true
        }
    }
}

// MARK: - Camera Picker

struct CameraPicker: UIViewControllerRepresentable {
    @Binding var image: UIImage?
    @Environment(\.dismiss) private var dismiss

    func makeUIViewController(context: Context) -> UIImagePickerController {
        let picker = UIImagePickerController()
        picker.sourceType = .camera
        picker.delegate = context.coordinator
        return picker
    }

    func updateUIViewController(_ uiViewController: UIImagePickerController, context: Context) {}

    func makeCoordinator() -> Coordinator {
        Coordinator(self)
    }

    class Coordinator: NSObject, UIImagePickerControllerDelegate, UINavigationControllerDelegate {
        let parent: CameraPicker
        init(_ parent: CameraPicker) { self.parent = parent }
        func imagePickerController(_ picker: UIImagePickerController,
                                    didFinishPickingMediaWithInfo info: [UIImagePickerController.InfoKey: Any]) {
            if let img = info[.originalImage] as? UIImage {
                parent.image = img
            }
            parent.dismiss()
        }
        func imagePickerControllerDidCancel(_ picker: UIImagePickerController) {
            parent.dismiss()
        }
    }
}
