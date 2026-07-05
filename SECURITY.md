# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability, please report it responsibly:

1. **Do NOT open a public issue** for security vulnerabilities
2. Email the maintainer at: **srinathsankara@users.noreply.github.com**
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

You should receive a response within 48 hours.

## Security Considerations

### Data Privacy

- This application runs locally — no data is sent to external servers
- Uploaded images are stored locally in the `uploads/` directory
- Analysis results are stored in local SQLite databases
- No patient data leaves your machine

### Known Limitations

- The application is not a medical device
- No authentication system is currently implemented
- BLE sensor communication relies on the `bleak` library
- Model files are downloaded from Google's CDN on first run

### Best Practices

- Run the application in a secure, local environment
- Do not expose the Flask development server to the internet
- Use a production WSGI server (Gunicorn, uWSGI) for deployment
- Keep dependencies updated
- Do not commit database files or uploaded images to version control

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | Yes                |
| < 1.0   | No                 |

## Security Updates

Security updates will be released as patch versions and announced in the [Releases](https://github.com/srinathsankara/scoliosis-brace-coach/releases) page.
