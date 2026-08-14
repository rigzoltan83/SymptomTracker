# Changelog

All notable changes to SymptomTracker will be documented in this file.

## [0.1.0-alpha.5] - 2026-08-14

Fifth public alpha release.

### Fixed

- Changed the installed Gunicorn service binding from localhost
  (`127.0.0.1`) to all network interfaces (`0.0.0.0`).
- Fresh installations can now be accessed from other devices on the
  local network using the server IP address and application port.

### Security

- SymptomTracker does not configure router port forwarding or expose
  the application to the public Internet automatically.
- Network access is still subject to the server firewall and network
  configuration.

### Status

This is an alpha release intended for clean-install testing.

## [0.1.0-alpha.4] - 2026-08-14

Fourth public alpha release.

### Fixed

- Applied `/opt/symptomtracker` ownership and permissions after the
  release files are copied into place.
- Prevented archive metadata from restoring the source directory
  ownership on the installed application root.

### Validation

- Installer and helper scripts pass Bash syntax validation.
- Main installer scripts pass ShellCheck validation.
- Clean-install permission handling was reviewed after the alpha.3
  installation test.

### Status

This is an alpha release intended for clean-install testing.

## [0.1.0-alpha.3] - 2026-08-14

Third public alpha release.

### Fixed

- Fixed virtualenv permissions so the SymptomTracker systemd service
  user can execute Gunicorn and access the Python environment.
- Restored the normal file-creation mask after generating the private
  `.env` file.
- Hardened `/opt/symptomtracker` ownership and permissions during
  installation.

### Validation

- Installer and helper scripts pass Bash syntax validation.
- Main installer scripts pass ShellCheck validation.
- Installation directory and runtime permission handling were audited.

### Status

This is an alpha release intended for clean-install testing.

## [0.1.0-alpha.2] - 2026-08-14

Second public alpha release.

### Fixed

- Fixed runtime failures in the installer caused by invalid multiline
  shell test expressions.
- Fixed fresh installation file-copy execution.
- Prevented the installer from continuing with missing application
  directories after the failed condition checks.

### Status

This is an alpha release intended for installation testing.

## [0.1.0-alpha.1] - 2026-08-14

First public alpha release.

### Added

- Food and drink diary
- Symptom diary
- Medication tracking
- Symptom severity and affected body-part tracking
- Multiple image attachments for foods and symptoms
- Ingredient database
- Risk-component database
- Ingredient/risk-component relationships
- Food risk-component handling
- Analysis of recorded events and possible associations
- Excel export
- Hungarian and English user interface
- Hungarian and English reference-data translations
- Administration interfaces for reference data
- PostgreSQL database support
- Database migrations
- Reference-data seed export and import
- Clean installation without personal events or recipes
- Automatic application and database port selection
- Ubuntu 24.04 installation support
- Automatic installation of required system dependencies
- Docker and Docker Compose dependency handling
- systemd service installation
- Installation health checks
- Hungarian and English installer
- GPL-3.0 licensing
- Medical disclaimer

### Included reference data

The installation contains the application's reusable reference data,
including:

- ingredients and translations
- risk components and translations
- ingredient/risk-component relationships
- symptom types and translations
- body parts and translations
- medications

Personal diary events, food/recipe records and uploaded personal images
are not included in the release seed data.

### Status

This is an alpha release intended for testing.

Back up important data before upgrading or testing future releases.
