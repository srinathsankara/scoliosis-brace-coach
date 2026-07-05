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

### Needs Improvement
- Shoulder Asymmetry: 18px [NEEDS_IMPROVEMENT]
- Trunk Lean: 75 degrees [NEEDS_IMPROVEMENT]
- Rotation: 50 degrees [NEEDS_IMPROVEMENT]
- Risk Score: 30/100
