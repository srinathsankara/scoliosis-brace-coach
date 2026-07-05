# Example Analysis Results

Real examples showing how the Scoliosis Brace Coach AI analyzes posture from photos.

---

## Example 1: Moderate Posture Asymmetry

**Image:** Person standing posterior view
**Mode:** Standing (Without Brace)
**Age Group:** Under 15

![Example 1](docs/images/standing_posterior_view.jpg)

### Results

| Metric | Value | Status |
|--------|-------|--------|
| Shoulder Asymmetry | 18 px | ⚠️ Needs Improvement |
| Hip Asymmetry | 22 px | - |
| Trunk Lean Angle | 75.27° | ⚠️ Needs Improvement |
| Head Tilt | 13.0 px | - |
| Spine Deviation | 194.0 px | - |
| Trunk Rotation Angle | 50.11° | ⚠️ Needs Improvement |
| Rib Hump Proxy | 0.0 px | ✅ Good |
| Axillary Fold Diff | 3 px | ✅ Good |
| Rotation Risk Score | 30/100 | ⚠️ Moderate Risk |

### Interpretation

This analysis shows moderate asymmetry in multiple metrics:
- **Shoulder asymmetry** of 18px suggests uneven shoulder height
- **Trunk lean angle** of 75.27° indicates significant lateral deviation
- **Trunk rotation** of 50.11° suggests vertebral rotation
- **Rotation risk score** of 30 indicates moderate risk

**Recommendation:** This pattern would benefit from clinical evaluation. The combination of lateral deviation and rotation suggests a 3D spinal deformity that should be assessed by an orthopedic specialist.

---

## Example 2: Mild Posture Asymmetry

**Image:** Person running (back view)
**Mode:** Standing (Without Brace)
**Age Group:** Adult

![Example 2](docs/images/runner_back.jpg)

### Results

| Metric | Value | Status |
|--------|-------|--------|
| Shoulder Asymmetry | 4 px | ✅ Good |
| Hip Asymmetry | 12 px | - |
| Trunk Lean Angle | 15.31° | ⚠️ Needs Improvement |
| Head Tilt | 4.5 px | - |
| Spine Deviation | 26.0 px | - |
| Trunk Rotation Angle | 16.22° | ⚠️ Needs Improvement |
| Rib Hump Proxy | 0.0 px | ✅ Good |
| Axillary Fold Diff | 7 px | ⚠️ Needs Improvement |
| Rotation Risk Score | 30/100 | ⚠️ Moderate Risk |

### Interpretation

This analysis shows mild asymmetry:
- **Shoulder asymmetry** of 4px is within normal range
- **Trunk lean angle** of 15.31° shows slight lateral deviation
- **Trunk rotation** of 16.22° indicates mild vertebral rotation
- **Axillary fold difference** of 7px suggests some rib cage asymmetry

**Recommendation:** Mild asymmetry that could benefit from monitoring. Regular check-ups and posture exercises would be beneficial.

---

## Example 3: Good Posture Alignment

**Image:** Person in fitness pose
**Mode:** Standing (Without Brace)
**Age Group:** Under 18

![Example 3](docs/images/fitness_standing.jpg)

### Results

| Metric | Value | Status |
|--------|-------|--------|
| Shoulder Asymmetry | 2 px | ✅ Good |
| Hip Asymmetry | 0 px | ✅ Good |
| Trunk Lean Angle | 0.95° | ✅ Good |
| Head Tilt | 4.5 px | - |
| Spine Deviation | 3.5 px | - |
| Trunk Rotation Angle | 0.86° | ✅ Good |
| Rib Hump Proxy | 0.0 px | ✅ Good |
| Axillary Fold Diff | 1 px | ✅ Good |
| Rotation Risk Score | 0/100 | ✅ Low Risk |

### Interpretation

This analysis shows excellent posture alignment:
- **Shoulder asymmetry** of 2px is nearly perfectly level
- **Hip asymmetry** of 0px shows balanced pelvis
- **Trunk lean angle** of 0.95° indicates minimal lateral deviation
- **Trunk rotation** of 0.86° shows negligible vertebral rotation
- **Rotation risk score** of 0 indicates no concerning patterns

**Recommendation:** Excellent posture. Continue maintaining good habits.

---

## How to Read the Results

### Status Badges

| Badge | Meaning |
|-------|---------|
| ✅ **Good** | Metric is within normal range for the age group |
| ⚠️ **Needs Improvement** | Metric is outside normal range - monitor closely |
| 🔴 **Poor** | Metric is significantly outside normal range - seek clinical evaluation |

### Key Metrics Explained

| Metric | What It Measures | Why It Matters |
|--------|------------------|----------------|
| **Shoulder Asymmetry** | Height difference between left/right shoulders | Primary indicator of spinal curvature |
| **Hip Asymmetry** | Height difference between left/right hips | Pelvic tilt can indicate spinal imbalance |
| **Trunk Lean Angle** | How much the torso tilts to one side | Direct measure of lateral spinal deviation |
| **Trunk Rotation Angle** | Rotation of the vertebral column | Scoliosis is 3D - rotation matters as much as lateral curve |
| **Rib Hump Proxy** | Asymmetry of the rib cage | Rib prominence is a classic scoliosis sign |
| **Rotation Risk Score** | Composite score (0-100) | Overall risk assessment combining multiple factors |

### Age-Group Thresholds

Metrics are compared against age-specific thresholds:

| Metric | Under 12 | Under 15 | Under 18 | Adult |
|--------|----------|----------|----------|-------|
| Shoulder Asymmetry | 12 px | 15 px | 18 px | 20 px |
| Trunk Lean Angle | 2.5° | 3.0° | 3.5° | 4.0° |
| Rib Hump | 5 px | 7 px | 9 px | 10 px |
| Axillary Fold | 4 px | 5 px | 6 px | 7 px |
| Rotation Angle | 3° | 4° | 5° | 5° |

---

## Tips for Best Results

### Photo Quality

1. **Lighting:** Ensure good, even lighting on the person's back
2. **Background:** Plain, contrasting background works best
3. **Position:** Person should be centered in frame, facing away from camera
4. **Clothing:** Fitted clothing shows body contours better than loose clothing
5. **Full body:** Head to ankles should be visible

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| "No person detected" | Image quality too low | Improve lighting, ensure full body visible |
| High spine deviation | Camera angle | Ensure camera is level and centered |
| Inconsistent results | Different distances | Maintain consistent distance from camera |

---

## Clinical Context

These metrics are **estimates** based on computer vision analysis of 2D images. They are designed to:

1. **Track trends** over time (is posture improving or worsening?)
2. **Compare** with-brace vs without-brace effectiveness
3. **Alert** when progression is detected

**Important:** These metrics are not medical measurements. Always consult a qualified healthcare provider for clinical decisions. The tool is designed to supplement, not replace, professional medical assessment.
