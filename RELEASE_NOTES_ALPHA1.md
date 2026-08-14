# SymptomTracker 0.1.0-alpha.1

This is the first public alpha release of SymptomTracker.

SymptomTracker is a self-hosted web application for recording food and
drink intake, medications and symptoms, and for exploring possible
associations between recorded events.

## Alpha status

This release is intended for testing.

The application may still contain bugs and installation or upgrade
procedures may change before the first stable release.

Do not rely on an alpha installation as the only copy of important data.

## Installation target

The automated installer currently targets:

- Ubuntu 24.04 LTS
- x86_64
- PostgreSQL 16 in Docker
- Python 3
- systemd

The installer can automatically install required system components and
select free application and PostgreSQL host ports when the default ports
are already in use.

## Languages

The application and installer support:

- English
- Hungarian

## Initial database content

A new installation includes reusable reference data such as ingredients,
risk components, ingredient/risk relationships, symptom types, body
parts, medications and their available translations.

The release does not contain the developer's personal diary events,
personal food/recipe records or uploaded personal images.

## Medical disclaimer

SymptomTracker is a personal diary and informational analysis tool.

It is not a medical device and must not be used as a substitute for
professional medical advice, diagnosis or treatment.

See DISCLAIMER.md for the complete disclaimer.

## License

SymptomTracker is free and open-source software licensed under the
GNU General Public License version 3 (GPL-3.0).

## Support development

If you find SymptomTracker useful and would like to support its
development:

https://www.patreon.com/c/ZoltanRigo
