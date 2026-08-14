# SymptomTracker

SymptomTracker is a self-hosted web application for recording and
analysing food intake, medications and symptoms.

The application is designed to help users maintain a structured
personal diary and explore possible relationships between recorded
events.

## Features

- food and drink diary
- symptom tracking
- medication tracking
- symptom severity recording
- body-part association
- image attachments for foods and symptoms
- ingredient database
- risk-component database
- ingredient/risk-component relationships
- statistical analysis of recorded events
- Hungarian and English user interface
- multilingual reference data
- Excel export
- mobile-friendly web interface
- self-hosted PostgreSQL database

## Included reference data

A fresh installation contains the application's reference data,
including:

- ingredients
- ingredient translations
- risk components
- risk-component translations
- ingredient/risk-component relationships
- symptom types
- symptom-type translations
- body parts
- body-part translations
- default medications

Personal diary data is not included in the distribution.

In particular, the distribution does not contain the developer's:

- events
- food records and recipes
- food images
- symptom events
- symptom images
- medication events

## Requirements

The supported installation target is currently:

- Ubuntu 24.04 LTS
- x86-64
- internet connection during installation

The installer is being designed to install or configure the required
runtime components automatically.

## Installation

SymptomTracker is currently in alpha development.

Detailed installation instructions:

[Installation guide](docs/INSTALL.md)

## Languages

The application currently supports:

- Hungarian
- English

The installer also supports Hungarian and English.

## Data storage

SymptomTracker is self-hosted.

Application data is stored in a PostgreSQL database controlled by the
operator of the installation. Uploaded images are stored on the host
running SymptomTracker.

Users and system administrators are responsible for protecting,
backing up and securely handling their own data.

## Medical disclaimer

SymptomTracker is a diary and analysis tool. It is not a medical
device and does not provide medical diagnosis, medical advice or
treatment recommendations.

Statistical associations or risk indicators shown by the application
do not prove causation, allergy, intolerance or any medical condition.

Do not use SymptomTracker as a substitute for professional medical
advice, diagnosis or treatment.

See [DISCLAIMER.md](DISCLAIMER.md) for additional information.

## Development status

SymptomTracker is currently alpha software.

Features, database structures, installation procedures and interfaces
may change before the first stable release.

Do not rely on an alpha release as the sole storage location for
important health-related records.

## License

SymptomTracker is free and open-source software licensed under the
GNU General Public License version 3.

See [LICENSE](LICENSE).

## Hungarian documentation

A Hungarian introduction is available in
[README.hu.md](README.hu.md).

## Support development

SymptomTracker is free and open-source software.

If you find the project useful and would like to support its continued
development, you can do so on Patreon:

https://www.patreon.com/c/ZoltanRigo
