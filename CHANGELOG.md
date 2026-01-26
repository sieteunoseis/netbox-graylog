# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.1.0] - 2026-01-26

### Added

- **Virtual Chassis Support**
  - For Virtual Chassis members, log queries now use the chassis name (original hostname) instead of member-specific name
  - Example: Member "switch.2" queries logs using "switch" to find logs from the stack
- **Combined OR Query for Hostname and IP**
  - Queries now search hostname AND IP address simultaneously using OR
  - Shows full query in UI: `(source:hostname* OR gl2_remote_ip:ip OR source:ip)`
  - Improves search reliability without requiring separate fallback searches

### Changed

- Query display now shows "combined" search type when using OR query
- Device name preserved in results for better debugging

## [1.0.2] - 2025-01-24

### Fixed

- Version alignment for PyPI release

## [1.0.1] - 2025-01-21

### Fixed
- Fixed version alignment between pyproject.toml and git tags
- Updated changelog with proper version history

## [1.0.0] - 2025-01-21

### Added

- **Logs Tab**
  - Adds "Logs" tab to Device and VirtualMachine detail pages
  - Displays recent logs from Graylog in real-time
  - Configurable log limit (default: 50 entries)

- **Time Range Selection**
  - Quick buttons for common time ranges: 5m, 15m, 1h, 4h, 24h, 7d
  - Configurable default time range

- **Smart Search**
  - Primary search by hostname (source field)
  - Automatic fallback to primary IP if hostname returns no results
  - Configurable search field (source or gl2_remote_ip)
  - FQDN support with configurable toggle

- **Performance**
  - API response caching to reduce load on Graylog
  - Configurable timeout and cache duration
  - Graceful error handling when Graylog is unavailable

- **Settings Page**
  - View current configuration
  - Test connection button
  - Configuration help with example

### Technical

- Built for NetBox 4.0+ (not compatible with NetBox 3.x)
- Requires Graylog 4.0+ with API access
- Python 3.10+ required
- Apache 2.0 license

[Unreleased]: https://github.com/sieteunoseis/netbox-graylog/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/sieteunoseis/netbox-graylog/compare/v1.0.2...v1.1.0
[1.0.2]: https://github.com/sieteunoseis/netbox-graylog/compare/v1.0.1...v1.0.2
[1.0.1]: https://github.com/sieteunoseis/netbox-graylog/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/sieteunoseis/netbox-graylog/releases/tag/v1.0.0
