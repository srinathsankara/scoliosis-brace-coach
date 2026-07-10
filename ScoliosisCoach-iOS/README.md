# Scoliosis Coach — iOS

Native iOS app for AI-powered scoliosis brace monitoring. **100% on-device. Zero data leaves the phone.**

## Requirements

- Xcode 16+
- iOS 17+ (for Swift Charts)
- macOS 14+ (Sonoma)
- Apple Developer Program ($99/yr) — required for App Store distribution

## Dependencies (Swift Package Manager)

The project uses SPM. Xcode will resolve these automatically on first open:

| Package | URL | Purpose |
|---------|-----|---------|
| GRDB.swift | https://github.com/groue/GRDB.swift.git | SQLite database |
| MediaPipeTasksVision | Via CocoaPods (see below) | Pose landmark detection |

### MediaPipe Setup

MediaPipe Tasks Vision SDK requires CocoaPods (SPM not yet available):

```bash
sudo gem install cocoapods
cd ScoliosisCoach-iOS
pod init
```

Add to `Podfile`:
```ruby
target 'ScoliosisCoach' do
  pod 'MediaPipeTasksVision'
end
```

```bash
pod install
```

Then open `ScoliosisCoach.xcworkspace` instead of `.xcodeproj`.

---

## Quick Start

1. Clone or copy this project to a Mac
2. Install dependencies (CocoaPods + GRDB.swift via SPM)
3. Open `ScoliosisCoach.xcworkspace`
4. Select iOS 17+ simulator or device
5. Build and run (⌘R)

The model file `pose_landmarker.task` is bundled in Resources and loads on first launch.

---

## Architecture

```
ScoliosisCoach/
├── ScoliosisCoachApp.swift          # App entry point
├── ContentView.swift                # Main tab navigation
├── Views/                           # SwiftUI screens
│   ├── CameraView.swift             # Camera capture + photo picker
│   ├── ResultsView.swift            # Analysis results display
│   ├── HistoryView.swift            # Session history list
│   ├── DashboardView.swift          # Clinician dashboard
│   ├── TrendsView.swift             # Longitudinal trends charts
│   ├── CompareView.swift            # With/without brace comparison
│   ├── SensorsView.swift            # BLE pressure + compliance
│   └── AboutView.swift              # Educational content + disclaimer
├── Analysis/                        # Core analysis engine
│   ├── PoseDetector.swift           # MediaPipe wrapper
│   ├── PostureRules.swift           # Posture metrics + thresholds
│   ├── RotationRules.swift          # Trunk rotation + rib hump
│   ├── BackAsymmetry.swift          # Pixel-level back analysis
│   ├── BraceDetector.swift          # Color-based brace detection
│   ├── GaitRules.swift              # Walking analysis
│   └── ExerciseRules.swift          # Exercise scoring (placeholder)
├── Models/                          # Data structures
│   ├── Session.swift                # Analysis session model
│   ├── Metrics.swift                # Metric result structs
│   └── Compliance.swift             # Wear-time tracking models
├── Services/                        # Business logic
│   ├── DatabaseService.swift        # GRDB.swift database layer
│   ├── AnalysisService.swift        # Orchestrates full analysis
│   ├── ReportService.swift          # PDF report generation
│   └── BLEService.swift             # Core Bluetooth scanner
├── Extensions/                      # Swift extensions
│   ├── Color+Theme.swift            # App color scheme
│   └── View+Disclaimer.swift        # Medical disclaimer modifier
└── Resources/
    ├── pose_landmarker.task         # MediaPipe model (~5MB)
    └── Assets.xcassets              # App icons, colors
```

## Data Flow

```
Camera/Photo → UIImage → PoseDetector.landmarks
                                    ↓
                    ┌───────────────┼───────────────┐
                    ↓               ↓               ↓
            PostureRules     RotationRules    BackAsymmetry
                    ↓               ↓               ↓
                    └───────────────┼───────────────┘
                                    ↓
                            Metrics Result
                                    ↓
                        DatabaseService.save()
                                    ↓
                      Dashboard / Trends / PDF
```

## Privacy

- **All processing is on-device** — no internet connection required
- No data is ever uploaded, shared, or collected
- The MediaPipe model runs entirely on-device
- Photos are stored locally in the app sandbox
- User can delete all data via Settings or app deletion

## Medical Disclaimer

This app is **NOT a medical device**. It is an educational tool for monitoring purposes only. Metrics are estimates from computer vision analysis and should not be used for clinical decisions. Always consult a qualified healthcare provider.

## License

MIT License — Copyright 2025 Srinath Sankara
