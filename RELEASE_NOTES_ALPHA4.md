# SymptomTracker 0.1.0-alpha.4

This is the fourth public alpha release of SymptomTracker.

## Fixed

The alpha.3 clean installation completed successfully, but a final
permission audit showed that the installation root could inherit the
source archive directory ownership.

This release fixes that by applying the final ownership and
permissions to `/opt/symptomtracker` after the application files have
been copied.

The intended final state is:

- owner: `root`
- group: `root`
- mode: `755`

## Validation

The installer has been checked with Bash syntax validation and
ShellCheck.

This release should be validated with another full clean installation
on Ubuntu 24.04 LTS amd64.

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
