# iOS Mobile App — Scoliosis Brace Coach

## Roadmap & Requirements

---

## Approach 1: Native SwiftUI (Recommended)

**Full rewrite in Swift, best performance, App Store ready.**

### Architecture

```
┌─────────────────────────────────────┐
│         SwiftUI App                  │
├─────────────────────────────────────┤
│  Views:                              │
│  - CameraView (AVFoundation)         │
│  - PhotoPicker (PHPicker)            │
│  - ResultsView (metrics cards)       │
│  - DashboardView (trends charts)     │
│  - CompareView (with/without brace)  │
│  - PDFReportView (PDFKit)            │
├─────────────────────────────────────┤
│  Analysis Engine (Swift):            │
│  - MediaPipe Tasks iOS SDK           │
│    → PoseLandmarker (33 landmarks)   │
│  - Core Image / Vision framework     │
│    → Back asymmetry pixel analysis   │
│  - Custom Swift math                 │
│    → Posture, rotation, gait rules   │
├─────────────────────────────────────┤
│  Storage:                            │
│  - Core Data / SQLite (GRDB.swift)   │
│  - FileManager (uploaded images)     │
├─────────────────────────────────────┤
│  Export:                             │
│  - PDFKit (clinical reports)         │
│  - ShareSheet (export to Health app) │
└─────────────────────────────────────┘
```

### SDK Replacements

| Feature | Python (Current) | iOS (New) | Complexity |
|---------|-----------------|------------|------------|
| Pose detection | MediaPipe Tasks Python | MediaPipe Tasks iOS SDK | Medium |
| Image processing | OpenCV (cv2) | Core Image / Accelerate / vImage | Medium |
| Posture rules | Python math | Swift math (same logic) | Easy |
| Rotation rules | Python math | Swift math (same logic) | Easy |
| Back asymmetry | OpenCV + numpy | Core Image + Accelerate | Hard |
| Brace detection | OpenCV HSV + contours | Core Image color filters | Medium |
| Gait analysis | Python + landmarks | Swift + landmarks | Medium |
| SQLite DB | sqlite3 (Python) | GRDB.swift or Core Data | Easy |
| PDF reports | ReportLab | PDFKit (native) | Medium |
| Trends/charts | Matplotlib (data) + HTML charts | Swift Charts (iOS 16+) | Medium |
| BLE sensors | bleak (Python) | Core Bluetooth | Hard |
| Camera | OpenCV cv2.VideoCapture | AVFoundation | Medium |

### Timeline (assuming 1 developer)

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| **P0: MVP** | 6-8 weeks | Camera capture → pose detection → posture/rotation analysis → results screen |
| **P1: Core** | 4-6 weeks | History, dashboard, trends charts, session comparison |
| **P2: Polish** | 2-3 weeks | PDF reports, brace detection, sensor integration |
| **P3: Launch** | 2 weeks | App Store assets, testing, submission |
| **Total** | **14-19 weeks** | |

### Costs

| Item | Cost |
|------|------|
| Apple Developer Program (annual) | $99/yr |
| Mac with Xcode | Already owned or ~$1,000 |
| MediaPipe Tasks iOS SDK | Free (open source) |
| App Store hosting | Included in $99/yr |
| Push notifications server (optional) | Free (Vercel/AWS Free Tier) |
| **Total minimum** | **$99/yr** |

---

## Approach 2: WebView Wrapper (Quick, Limited)

**Wrap the existing Flask web app in an iOS WKWebView.**

### Pros
- 1-2 days to build
- Exact same functionality
- No rewrite needed
- All Python logic preserved

### Cons
- Requires a local server — cannot run fully offline without bundling Python (technically possible with `python-ios` but complex and large ~100MB+)
- Not App Store friendly (Apple rejects apps that download/run interpreted code)
- No native camera integration
- Slower, feels like a website

### How It Works
```swift
// WKWebView pointing to local Flask server
let webView = WKWebView()
let url = URL(string: "http://localhost:5000")!
webView.load(URLRequest(url: url))
```

**Will NOT be approved for App Store** — Apple prohibits apps that run downloaded scripts or require external interpreters.

---

## Approach 3: Hybrid (Flutter + MediaPipe)

**Cross-platform with Flutter, using MediaPipe Flutter plugin.**

### Pros
- Single codebase for iOS + Android
- Growing MediaPipe Flutter plugin support
- Hot reload for fast development

### Cons
- Flutter plugin ecosystem for MediaPipe is less mature than native SDKs
- Performance overhead vs SwiftUI
- Larger binary size
- Still need to rewrite all analysis logic in Dart

### Timeline: 12-16 weeks

---

## Recommended Path

### Phase 0 (Immediate — $0)
1. Buy a used Mac Mini M1 (~$400) or use existing Mac
2. Install Xcode 16 (free)
3. Create Apple Developer account ($99)
4. Learn SwiftUI basics (~40 hrs on free YouTube tutorials)
5. Try MediaPipe Tasks iOS quickstart (google's sample project)

### Phase 1 (MVP — 6-8 weeks)
Build a stripped-down app with:
- Camera / photo picker
- MediaPipe pose detection
- Posture + rotation analysis (ported from Python)
- Results screen
- SQLite history
- **No** dashboard, trends, PDF, BLE sensors yet

### Phase 2 (Feature Complete — +6-8 weeks)
Add:
- Dashboard with Swift Charts
- Trends with regression
- Session comparison
- PDF export with PDFKit
- Brace color detection

### Phase 3 (Sensors — +4 weeks)
- Core Bluetooth for BLE sensors
- Compliance tracking
- Pressure mapping

### Phase 4 (App Store — 2 weeks)
- App Store Connect setup
- Screenshots, privacy policy, marketing copy
- Review and release

---

## Key Technical Decisions

### 1. MediaPipe Tasks iOS SDK
```pod
# Podfile
pod 'MediaPipeTasksVision'
```
Docs: https://developers.google.com/mediapipe/solutions/vision/pose_landmarker/ios

### 2. Camera vs Photo Library
```swift
// AVFoundation camera (recommended)
let captureSession = AVCaptureSession()
captureSession.sessionPreset = .high

// PHPicker for gallery
let picker = PHPickerViewController(configuration: config)
```

### 3. Back Asymmetry (Core Image)
```swift
// Instead of OpenCV, use Core Image filters
let ciImage = CIImage(cgImage: cgImage)
let edges = ciImage.applyingFilter("CIEdges")
let brightness = ciImage.applyingFilter("CIAreaAverage")
```

### 4. Charts (Swift Charts — iOS 16+)
```swift
Chart {
    ForEach(sessions) { session in
        LineMark(
            x: .value("Date", session.date),
            y: .value("Angle", session.trunkLeanAngle)
        )
    }
}
```

### 5. Database (GRDB.swift)
```swift
// SQLite with Swift types
try dbQueue.write { db in
    try db.execute(sql: "CREATE TABLE sessions (...)")
}
```

---

## First Steps (This Week, $0)

1. **Install Xcode** from Mac App Store (free)
2. **Try the MediaPipe iOS quickstart**:
   ```
   git clone https://github.com/google-ai-edge/mediapipe-samples
   cd mediapipe-samples/examples/pose_landmarker/ios
   ```
3. **Build and run** on iPhone simulator — verify pose detection works
4. **Port the posture rules** from Python to Swift (pure math, no dependencies)
5. **Build a single-screen app**: take photo → run pose → show shoulder angle

---

## iOS-Specific Challenges

| Challenge | Mitigation |
|-----------|------------|
| No `numpy` | Use `Accelerate` framework (vDSP, BNNS) for vector math |
| No `OpenCV` `findContours` | Core Image contour detection or custom pixel walk |
| No `reportlab` | PDFKit `UIGraphicsPDFRenderer` |
| No `matplotlib` trends | Swift Charts (iOS 16+) or `Charts` pod (iOS 12+) |
| App Store Review Guidelines | No medical claims, clear disclaimer, privacy-first design |
| File size | MediaPipe model ~5MB, app ~50MB total |

---

## ML Model: On-Device vs Server

**On-device (recommended):**
- MediaPipe Pose Landmarker model bundled in the app (~5MB)
- No internet required
- No privacy concerns
- Instant analysis

**Server-side (not recommended for this app):**
- Send photo to cloud API
- Requires internet
- Privacy risk
- Server costs

Current architecture is already on-device → makes iOS port natural.

---

## App Store Considerations

- **Category**: Medical (or Health & Fitness) — will require additional scrutiny
- **Content**: No user-generated content moderation needed (no social features)
- **Privacy**: No data collection → minimal privacy policy
- **Medical disclaimer**: Required prominently — already exists in web version
- **Age rating**: 4+ (no objectionable content)
- **Price**: Free (monetize later via subscription if desired)
