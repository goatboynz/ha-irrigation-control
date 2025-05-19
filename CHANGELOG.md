# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-05-20
### Added
- Initial release
- Web-based interface for irrigation control
- Support for unlimited irrigation zones
- P1/P2 event scheduling system
  - Up to 50 time slots per event type
  - Priority-based execution
  - Conditional triggering
- Zone grouping functionality
  - Sequential or parallel operation
  - Configurable zone ordering
  - Unlimited zones per group
- Advanced scheduling features
  - Multiple time slots per schedule
  - Day-of-week selection
  - Duration controls
  - Manual override options
- Integration features
  - Home Assistant API integration
  - Entity state monitoring
  - Conditional scheduling based on sensor data
- System features
  - SQLite database for configuration storage
  - APScheduler for managing irrigation schedules
  - Real-time status updates
  - Operation history tracking
  - System health monitoring
- User Interface
  - Material Design
  - Responsive layout
  - Real-time updates
  - Mobile-friendly design
- Documentation
  - Installation guide
  - Configuration instructions
  - API documentation
  - Troubleshooting guide

### Security
- Implemented AppArmor profile
- Secure Home Assistant API communication
- Input validation and sanitization
- Rate limiting on API endpoints
- Token-based authentication

### Technical
- FastAPI backend implementation
- Jinja2 templating for frontend
- S6-Overlay service management
- SQLite database initialization
- Supervisor token handling
- Multi-arch support (aarch64, amd64, armv7)
- Resource usage optimization

[0.1.0]: https://github.com/YOUR_USERNAME/ha-irrigation-control/releases/tag/v0.1.0
