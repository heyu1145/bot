# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.1.0] - 2025-11-23

### Added
- Auto-Cog Loading System: Implemented an abstract layer for automatic discovery and loading of cogs
- CogLoader Class: Created a utility class in `utils/cog_loader.py` with functions to load, reload, and unload cogs
- Automatic Discovery: The system now automatically discovers and loads all cog files in the `cogs/` directory
- Cog Management: Added functions to get loaded/failed cogs status and manage cogs dynamically
- Documentation: Updated README.md with instructions for the new auto-cog loading system

### Changed
- Modified `bot.py` to use the new auto-cog loading system instead of manual loading
- Updated comments and documentation to be in English
- Improved logging messages during cog loading process

### Fixed
- Standardized error handling during cog loading operations
- Improved error messages for better debugging

## [1.0.0] - 2025-11-22

### Added
- Initial release of Discord Bot with comprehensive server management features
- Web dashboard for real-time monitoring
- Ticket system with multi-option panels
- Administrative tools for server management
- Data management system with JSON storage
- Event handling and permission controls
- Flask-based web interface with system monitoring