# Home Assistant Irrigation Control Addon

## Overview

This addon provides advanced irrigation control features for Home Assistant, with support for unlimited irrigation zones, P1/P2 event scheduling, and detailed control over watering patterns.

## Features

- Map unlimited Home Assistant switch entities to irrigation zones
- Create zone groups for coordinated watering
- P1/P2 event scheduling with up to 50 time slots each
- Priority-based scheduling system
- Sequential or parallel zone operation
- Conditional scheduling based on Home Assistant sensors
- Manual control of individual zones and groups
- User-friendly web interface

## Installation

1. Navigate to the Home Assistant Supervisor panel
2. Click on "Add-on Store"
3. Click the menu icon (⋮) and select "Repositories"
4. Add this repository URL: `https://github.com/YOUR_USERNAME/ha-irrigation-control`
5. Find the "Irrigation Control" addon in the list and click it
6. Click "Install"

## Configuration

### Addon Configuration

```yaml
log_level: info  # One of: trace, debug, info, warning, error, fatal
p1_enabled: true # Enable P1 event scheduling
p2_enabled: true # Enable P2 event scheduling
p1_max_slots: 50 # Maximum number of time slots for P1 events (1-100)
p2_max_slots: 50 # Maximum number of time slots for P2 events (1-100)
timezone: UTC    # Your local timezone
max_concurrent_zones: 3 # Maximum number of zones that can run simultaneously
```

### Initial Setup

1. After installing and starting the addon, open the web interface
2. Navigate to the "Solenoids" page
3. Map your existing Home Assistant switch entities to irrigation zones
4. (Optional) Create zone groups on the "Groups" page
5. Create watering schedules on the "Schedules" page

## Usage

### Understanding P1/P2 Events

The addon supports two types of scheduled events:

- **P1 Events (Priority 1)**: Primary watering schedules that take precedence
- **P2 Events (Priority 2)**: Secondary schedules that run when no P1 events are active

Each event type can have up to 50 different time slots, allowing for complex watering patterns.

### Mapping Solenoids

1. Go to the "Solenoids" page
2. You'll see a list of available Home Assistant switch entities
3. Click "Map as Solenoid" next to each switch you want to use
4. The mapped solenoids will appear in the "Mapped Solenoids" section
5. Optionally set a sequence order for sequential watering
6. Use the manual control buttons to test each solenoid

### Creating Zone Groups

1. Navigate to the "Groups" page
2. Click "Create New Group"
3. Enter a name for the group
4. Select the solenoids to include
5. Choose sequential or parallel operation
6. Set sequence orders if using sequential mode
7. Click "Save Group"

### Setting Up Schedules

1. Go to the "Schedules" page
2. Click "Create New Schedule"
3. Fill in the schedule details:
   - Name: A descriptive name for the schedule
   - Event Type: P1, P2, or Manual
   - Target Type: Choose between single solenoid or group
   - Target: Select the specific solenoid or group
   - Enable/Disable: Toggle the schedule's active status
4. Add time slots:
   - Click "Add Time Slot"
   - Set the start time
   - Set the duration (1-360 minutes)
   - Select the days of the week
5. Add conditions (optional):
   - Select Home Assistant entities to monitor
   - Set conditions that must be met for the schedule to run
6. Add additional time slots if needed (up to 50 per P1/P2 event)
7. Click "Save Schedule"

### Schedule Priority System

1. P1 events have the highest priority and will prevent P2 events from starting
2. Within each priority level:
   - Earlier start times take precedence
   - Sequential groups wait for all zones to complete
   - Parallel groups run simultaneously up to max_concurrent_zones

### Manual Control

- Individual solenoids can be controlled from the Dashboard or Solenoids page
- Groups can be controlled from the Groups page
- Schedules can be run immediately using the "Run Now" button
- Manual operations respect the max_concurrent_zones setting

## Troubleshooting

### Common Issues

1. **Too many concurrent zones:**
   - Check the max_concurrent_zones setting
   - Review overlapping schedules
   - Consider using sequential groups

2. **Schedules not running:**
   - Check if the schedule is enabled
   - Verify P1/P2 settings if using those event types
   - Check for conflicting schedules
   - Review any conditions that might prevent execution

3. **Database errors:**
   - Check available storage space
   - Review logs for specific errors
   - Consider reducing the number of time slots if near limits

### Getting Help

- Check the [addon repository](https://github.com/YOUR_USERNAME/ha-irrigation-control) for known issues
- Review the Home Assistant logs for more detailed error information
- Open an issue on GitHub if you need assistance

## Technical Details

### Storage

The addon uses two SQLite databases stored in the `/data` directory:

- `/data/db/irrigation_addon.db`: Main database for solenoids, groups, and schedules
- `/data/db/apscheduler_jobs.sqlite`: APScheduler job store

### Resource Considerations

- Each active schedule requires memory for tracking its state
- More concurrent zones require more system resources
- Large numbers of time slots increase database size
- Consider reducing time slots or concurrent zones if experiencing performance issues

### Backup and Restore

The addon's data is automatically included in Home Assistant backups. To manually back up the data:

1. Stop the addon
2. Copy the contents of the `/data` directory
3. Store the backup in a safe location

To restore:

1. Stop the addon
2. Replace the contents of the `/data` directory with your backup
3. Start the addon

## Support

For support, please:

1. Check the documentation first
2. Search existing GitHub issues
3. Open a new issue if needed, providing:
   - Addon version
   - Home Assistant version
   - Clear description of the problem
   - Relevant logs
   - Steps to reproduce the issue
