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

### Real Analysis: Person with Scoliosis

**Image:** scoliosis_back2.jpg (Openverse CC-licensed photo)
**Mode:** Standing (Without Brace)
**Age Group:** Under 15

| Metric | Value | Status | What It Means |
|--------|-------|--------|---------------|
| Shoulder Asymmetry | 19 px | NEEDS_IMPROVEMENT | Shoulders are uneven |
| Hip Asymmetry | 9 px | - | Hips show some tilt |
| Trunk Lean Angle | 14.04 degrees | NEEDS_IMPROVEMENT | Lateral lean present |
| Head Tilt | 13.0 px | - | Head is tilted to one side |
| Spine Deviation | 35.0 px | - | Spine shifted from center |
| Trunk Rotation | 7.27 degrees | NEEDS_IMPROVEMENT | Vertebral rotation present |
| Rotation Risk Score | 57.3/100 | NEEDS_IMPROVEMENT | Moderate-high risk |

**Interpretation:** This analysis shows moderate asymmetry. The combination of shoulder imbalance (19px), trunk lean (14.04 degrees), and rotation (7.27 degrees) with a risk score of 57.3 suggests a spinal deformity that warrants clinical evaluation.

### Real Analysis: Severe Scoliosis

**Image:** scoliosis_back3.jpg (Openverse CC-licensed photo)
**Mode:** Standing (Without Brace)
**Age Group:** Under 15

| Metric | Value | Status | What It Means |
|--------|-------|--------|---------------|
| Shoulder Asymmetry | 27 px | NEEDS_IMPROVEMENT | Shoulders significantly uneven |
| Hip Asymmetry | 27 px | - | Hips show significant tilt |
| Trunk Lean Angle | 6.98 degrees | - | Mild lateral lean |
| Head Tilt | 59.5 px | - | Head significantly tilted |
| Spine Deviation | 75.5 px | - | Significant spine shift |
| Trunk Rotation | 2.04 degrees | - | Mild vertebral rotation |
| Rotation Risk Score | 30/100 | GOOD | Low-moderate risk |

**Interpretation:** This analysis shows significant shoulder and hip asymmetry with notable head tilt and spine deviation. Despite the lower rotation score, the combined asymmetry patterns suggest scoliosis that requires clinical assessment.

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
