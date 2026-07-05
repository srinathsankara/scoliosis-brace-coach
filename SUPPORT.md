# Support

## Getting Help

### Documentation

- **[README.md](README.md)** — Full setup and usage guide
- **[About Page](http://localhost:5000/about)** — In-app AIS education and treatment information

### Common Issues

#### "No person detected" error
- Ensure the photo shows a full-body view of the person
- Good lighting is essential
- The person should be standing against a plain background
- Avoid blurry or low-resolution images

#### MediaPipe model download fails
- Check your internet connection (first run only)
- The model (~5MB) downloads from Google's CDN
- If blocked, manually download `pose_landmarker.task` to the project root

#### BLE sensor not found
- Ensure Bluetooth is enabled on your device
- Install `bleak`: `pip install bleak`
- Some sensors may require specific pairing procedures

#### Server won't start
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version (3.8+ required)
- Ensure port 5000 is not in use

### Reporting Issues

1. Check [existing issues](https://github.com/srinathsankara/scoliosis-brace-coach/issues)
2. If not found, open a new issue using the appropriate template
3. Include your Python version, OS, and steps to reproduce

### Feature Requests

Open an issue with the **Feature Request** template. Describe:
- The problem you're trying to solve
- How you envision the solution
- Any research papers or clinical guidelines that support the feature

### Discussions

For general questions, ideas, or community chat, use [Discussions](https://github.com/srinathsankara/scoliosis-brace-coach/discussions).

## Medical Disclaimer

**This application is not a medical device.** It cannot diagnose conditions, prescribe treatment, or replace professional medical advice. For medical concerns, always consult a qualified healthcare provider.
