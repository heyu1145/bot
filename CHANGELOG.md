# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.0.0-rc.1] - 2026.??.??

### Added
- Documentation: Created the `docs/` in both frontend and backend and necessary documents will go there for better finding
- All log file after `7 days` and `__pycache__` will be marked as unused cache and removed after runing `cleanup_unused_cache.py`
- The bot now will have an activity randomly, you can freely edit it at `bot_tasks.py`
- Created a new file `utils/parse_changelog.py` for parsing versions in changelogs
- Created new Commands `/send` and `/event` supports you do some activity as bot
- You can now check bots changelog by `/changelog` command
- You can config cogs status (`attach` or `deattach`) by `/config_cog` command
- Add some common checks in `checks.py`

### Changed
- Both Frontend and Backend Splited for debugging and building
- Frontend Change: Modifyed whole the Front Frame for better viewing.
- Backend Change: Added some Special Routes
- The logger from `utils/logger.py` will automatic log all levels to a file at `logs/`
- The `utils/cog_loader.py` moved to `cogs/cog_loader.py` and upgrade for better handling
- Added auto reload cogs and load new cogs in dir `cogs`, content in `bot_tasks.py`

### Fixed
- Cogs Error will be handled when cog raised a error while action

## [1.1.0] - 2025-10-08

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

## [1.0.0] - 2025-9-17

### Added
- Initial release of Discord Bot with comprehensive server management features
- Web dashboard for real-time monitoring
- Ticket system with multi-option panels
- Administrative tools for server management
- Data management system with JSON storage
- Event handling and permission controls
- Flask-based web interface with system monitoring
