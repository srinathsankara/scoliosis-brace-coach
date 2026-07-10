import SwiftUI

struct AnalysisView: View {
    @State private var showingImagePicker = false
    @State private var sourceType: UIImagePickerController.SourceType = .camera
    @State private var selectedImage: UIImage?
    @State private var isAnalyzing = false
    @State private var result: AnalysisResult?
    @State private var showResult = false
    @State private var showCameraAlert = false
    @State private var selectedMode = "standing_no_brace"
    @State private var selectedAgeGroup = "under15"

    let modes = [
        "standing_no_brace", "standing_with_brace",
        "walking_no_brace", "walking_with_brace",
        "exercises_no_brace", "exercises_with_brace"
    ]

    let ageGroups = ["under15", "over15"]

    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 16) {
                    // Mode picker
                    VStack(alignment: .leading) {
                        Text("Analysis Mode")
                            .font(.headline)
                        Picker("Mode", selection: $selectedMode) {
                            ForEach(modes, id: \.self) { mode in
                                Text(mode.replacingOccurrences(of: "_", with: " ").capitalized)
                                    .tag(mode)
                            }
                        }
                        .pickerStyle(MenuPickerStyle())
                    }
                    .padding(.horizontal)

                    // Age group
                    VStack(alignment: .leading) {
                        Text("Age Group")
                            .font(.headline)
                        Picker("Age", selection: $selectedAgeGroup) {
                            ForEach(ageGroups, id: \.self) { age in
                                Text(age == "under15" ? "Under 15" : "15 and Over").tag(age)
                            }
                        }
                        .pickerStyle(SegmentedPickerStyle())
                    }
                    .padding(.horizontal)

                    // Photo area
                    ZStack {
                        RoundedRectangle(cornerRadius: 12)
                            .stroke(Color.secondary, lineWidth: 2)
                            .frame(height: 350)

                        if let image = selectedImage {
                            Image(uiImage: image)
                                .resizable()
                                .scaledToFit()
                                .frame(height: 340)
                                .cornerRadius(10)
                        } else {
                            VStack(spacing: 8) {
                                Image(systemName: "photo.badge.plus")
                                    .font(.system(size: 48))
                                    .foregroundColor(.secondary)
                                Text("Tap to take or select a photo")
                                    .foregroundColor(.secondary)
                            }
                        }
                    }
                    .padding(.horizontal)
                    .onTapGesture {
                        showCameraAlert = true
                    }
                    .confirmationDialog("Select Source", isPresented: $showCameraAlert) {
                        Button("Camera") {
                            sourceType = .camera
                            showingImagePicker = true
                        }
                        Button("Photo Library") {
                            sourceType = .photoLibrary
                            showingImagePicker = true
                        }
                        Button("Cancel", role: .cancel) {}
                    }

                    // Analyze button
                    Button(action: runAnalysis) {
                        if isAnalyzing {
                            ProgressView()
                                .progressViewStyle(CircularProgressViewStyle(tint: .white))
                        } else {
                            Text("Analyze")
                        }
                    }
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(Color.accentColor)
                    .foregroundColor(.white)
                    .cornerRadius(10)
                    .padding(.horizontal)
                    .disabled(selectedImage == nil || isAnalyzing)
                }
                .padding(.vertical)
            }
            .navigationTitle("Analyze")
            .sheet(isPresented: $showingImagePicker) {
                ImagePicker(image: $selectedImage, sourceType: sourceType)
            }
            .sheet(isPresented: $showResult) {
                if let result = result {
                    ResultsView(result: result)
                }
            }
        }
    }

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

struct ImagePicker: UIViewControllerRepresentable {
    @Binding var image: UIImage?
    var sourceType: UIImagePickerController.SourceType

    func makeUIViewController(context: Context) -> UIImagePickerController {
        let picker = UIImagePickerController()
        picker.delegate = context.coordinator
        picker.sourceType = sourceType
        return picker
    }

    func updateUIViewController(_ uiViewController: UIImagePickerController, context: Context) {}

    func makeCoordinator() -> Coordinator {
        Coordinator(self)
    }

    class Coordinator: NSObject, UINavigationControllerDelegate, UIImagePickerControllerDelegate {
        let parent: ImagePicker
        init(_ parent: ImagePicker) { self.parent = parent }
        func imagePickerController(_ picker: UIImagePickerController,
                                    didFinishPickingMediaWithInfo info: [UIImagePickerController.InfoKey: Any]) {
            parent.image = info[.originalImage] as? UIImage
            picker.dismiss(animated: true)
        }
    }
}
