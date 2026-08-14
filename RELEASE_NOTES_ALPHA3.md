# SymptomTracker 0.1.0-alpha.3

This is the third public alpha release of SymptomTracker.

## Fixed

This release contains additional installation fixes discovered during
real clean-install testing.

The installer now:

- creates the Python virtual environment with permissions that allow
  the SymptomTracker systemd service user to execute Gunicorn and use
  the installed Python packages;
- restores the normal file-creation mask after securely creating the
  private `.env` file;
- explicitly sets the installation directory ownership to `root:root`
  with executable directory permissions.

## Validation

The installer has been checked with Bash syntax validation and
ShellCheck.

This release should be tested with a complete clean installation on
Ubuntu 24.04 LTS amd64 before being considered successfully validated.

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
