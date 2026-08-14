# SymptomTracker 0.1.0-alpha.2

This is the second public alpha release of SymptomTracker.

## Fixed

The first public alpha exposed a runtime bug in the installation
script during a real clean installation.

This release fixes the invalid multiline shell test expressions that
prevented:

- the root privilege check from running correctly;
- the application files from being copied into `/opt/symptomtracker`.

The installer condition syntax has been audited after the fix.

## Installation testing

This release is intended to continue clean-install testing on
Ubuntu 24.04 LTS amd64 systems.

Please install it from the published GitHub release package rather
than copying files from an existing SymptomTracker installation.

## Alpha status

This is still alpha software.

Do not rely on an alpha installation as the only copy of important
data.

## Medical disclaimer

SymptomTracker is a personal diary and informational analysis tool.
It is not a medical device and does not provide medical diagnosis or
treatment recommendations.

See `DISCLAIMER.md` for the complete disclaimer.

## License

SymptomTracker is licensed under the GNU General Public License
version 3 (GPL-3.0).

## Support development

https://www.patreon.com/c/ZoltanRigo
