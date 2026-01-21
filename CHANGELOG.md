# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

[Unreleased]: https://github.com/sieteunoseis/netbox-graylog/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/sieteunoseis/netbox-graylog/releases/tag/v1.0.0
