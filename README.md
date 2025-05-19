# Home Assistant Irrigation Control Addon

[![Home Assistant Add-on](https://img.shields.io/badge/Home%20Assistant-Add--on-blue.svg)](https://www.home-assistant.io)
[![License](https://img.shields.io/github/license/YOUR_USERNAME/ha-irrigation-control.svg)](LICENSE)
[![Maintenance](https://img.shields.io/maintenance/yes/2025.svg)](https://github.com/YOUR_USERNAME/ha-irrigation-control/graphs/commit-activity)

Advanced irrigation control for Home Assistant with support for unlimited zones, P1/P2 event scheduling, and comprehensive watering management.

## Features

- ✨ Support for unlimited irrigation zones
- 🎯 P1/P2 event scheduling with up to 50 time slots each
- 🔄 Map existing Home Assistant switch entities
- 📅 Create advanced watering schedules
- 👥 Group zones for coordinated watering
- 🕒 Sequential or parallel zone operation
- 📱 User-friendly web interface
- 🔧 Manual control options
- 🌡️ Conditional scheduling based on sensors
- 📊 Detailed operation history

## Screenshots

![Dashboard](docs/images/dashboard.png)
![Schedules](docs/images/schedules.png)
*(Screenshots coming soon)*

## Event Types

### P1 Events (Priority 1)
- Primary watering schedules
- Takes precedence over P2 events
- Up to 50 time slots per event
- Ideal for essential watering needs

### P2 Events (Priority 2)
- Secondary watering schedules
- Runs when no P1 events are active
- Up to 50 time slots per event
- Perfect for supplementary watering

## Quick Start

1. Add the repository to your Home Assistant instance:
   ```yaml
   https://github.com/YOUR_USERNAME/ha-irrigation-control
   ```

2. Install the addon through the Home Assistant Add-on Store

3. Start the addon and enable "Show in sidebar"

4. Open the web interface and follow the setup wizard

## Documentation

For detailed setup and configuration instructions, please see the [full documentation](DOCS.md).

## Requirements

- Home Assistant OS or Supervised installation
- One or more configured switch entities for irrigation control
- Access to the Supervisor panel
- Sufficient system resources for your zone count

## System Requirements

Memory usage scales with the number of zones and active schedules:
- Base: ~100MB RAM
- Additional per active zone: ~10MB
- Additional per active schedule: ~5MB

Storage:
- Base installation: ~50MB
- Database growth depends on number of zones and schedules

## Support

- [Open an issue](https://github.com/YOUR_USERNAME/ha-irrigation-control/issues)
- [Documentation](DOCS.md)
- [Discussion Forum](https://github.com/YOUR_USERNAME/ha-irrigation-control/discussions)

## Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Scheduling powered by [APScheduler](https://apscheduler.readthedocs.io/)
- UI components from [Material Design Icons](https://materialdesignicons.com/)

## Authors

- **YOUR_NAME** - *Initial work* - [YOUR_USERNAME](https://github.com/YOUR_USERNAME)

## Project Status

This addon is actively maintained and in regular use. Feature requests and bug reports are welcome through the issue tracker.

## Support the Project

If you find this addon helpful, please consider:

- ⭐ Starring the repository
- 🐛 Reporting bugs
- 💡 Suggesting new features
- 🤝 Contributing to the code

## Related Projects

- [Home Assistant](https://www.home-assistant.io/)
- [ESPHome](https://esphome.io/) - For creating custom irrigation controllers
