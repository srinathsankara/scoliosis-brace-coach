# How the Tool Measures Posture

## Pose Detection Process

1. **Upload Photo** - MediaPipe detects 33 body landmarks
2. **Calculate Metrics** - Compute asymmetry and angles
3. **Compare Thresholds** - Age-specific normal ranges
4. **Generate Report** - Status badges and risk scores

## Key Measurements

### Shoulder Asymmetry
Measures height difference between left and right shoulders.

```
Shoulder Line:
    Left Shoulder *=================* Right Shoulder
                  | delta_h (pixels) |

If delta_h > threshold -> needs_improvement
```

### Trunk Lean Angle
Measures how much the torso tilts to one side.

```
         * Mid-Shoulder
        /|
       / |
      /  | delta_x (pixels)
     / theta |
    *----* Mid-Hip

theta = arctan(delta_x / delta_y)
```

### Trunk Rotation
Measures vertebral rotation from shoulder vs hip angles.

```
Shoulder Line Angle: theta_s
Hip Line Angle: theta_h
Rotation = |theta_s - theta_h|
```

## Example Results

### Good Posture
- Shoulder Asymmetry: 2px [GOOD]
- Trunk Lean: 1 degree [GOOD]
- Rotation: 1 degree [GOOD]
- Risk Score: 0/100

### Real Analysis: Person with Posture Issues

**Image:** person_posture.jpg (Pexels free stock photo)
**Mode:** Standing (Without Brace)
**Age Group:** Adult

| Metric | Value | Status | What It Means |
|--------|-------|--------|---------------|
| Shoulder Asymmetry | 107 px | NEEDS_IMPROVEMENT | Shoulders are significantly uneven |
| Hip Asymmetry | 34 px | - | Hips show some tilt |
| Trunk Lean Angle | 47.95 degrees | NEEDS_IMPROVEMENT | Significant lateral lean |
| Head Tilt | 56.5 px | - | Head is tilted to one side |
| Spine Deviation | 148.0 px | - | Spine shifted from center |
| Trunk Rotation | 47.61 degrees | NEEDS_IMPROVEMENT | Vertebral rotation present |
| Rotation Risk Score | 60/100 | NEEDS_IMPROVEMENT | Moderate-high risk |

**Interpretation:** This analysis shows significant asymmetry across multiple metrics. The combination of shoulder imbalance (107px), trunk lean (47.95 degrees), and rotation (47.61 degrees) suggests a 3D spinal deformity that warrants clinical evaluation.

### How to Read the Results

1. **Status Badges:**
   - GOOD = Within normal range for age group
   - NEEDS_IMPROVEMENT = Outside normal range - monitor closely

2. **Risk Score (0-100):**
   - 0-29: Low risk
   - 30-59: Moderate risk
   - 60-100: High risk - seek clinical evaluation

3. **Key Patterns to Watch:**
   - Shoulder asymmetry > Trunk lean > Rotation (combined indicates scoliosis)
   - High rotation risk score with multiple "needs_improvement" metrics
   - Consistent asymmetry across multiple sessions
