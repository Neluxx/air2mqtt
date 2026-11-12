# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

### Changed

### Deprecated

### Removed

### Fixed

### Security

### Dependencies

## [v0.1.0](https://github.com/Neluxx/air2mqtt/releases/tag/v0.1.0) - 2026-11-12

### Added
- Read CO₂ from an MH-Z19 via UART without root privileges
- Read temperature, humidity and pressure from a BME680 via I²C
- Publish all values to Home Assistant via device-based MQTT discovery
- Mark the device as unavailable via MQTT last will and expire stale values
- Reconnect to the MQTT broker automatically and drop measurements while it is unreachable
- Add `TEMPERATURE_OFFSET` to correct BME680 readings affected by heat from the Pi
- Configure everything via environment variables or a `.env` file
- Run as a systemd service
