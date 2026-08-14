# SymptomTracker 0.1.0-alpha.6

This release contains a comprehensive hardening pass of the public
installer.

## Main changes

- Browser-friendly application ports are now selected from 8000-8199.
- The installed Gunicorn service listens on all IPv4 interfaces.
- The installer prints a usable LAN URL after installation.
- Port availability checks now match the actual service bind.
- The application waits for PostgreSQL readiness before starting.
- Docker is explicitly enabled and started.
- Leftover installation directories, users, groups, containers and
  database volumes are detected before a fresh installation starts.
- The service user and group are created deterministically.
- Required system packages now explicitly include `tar` and
  `iproute2`.
- Active UFW installations receive a clear firewall warning and the
  exact port-opening command.

## Installation target

The automated installer currently targets:

- Ubuntu 24.04 LTS
- amd64 / x86_64
- systemd
- Internet access during installation
- root / sudo privileges

## Validation target

This release should be validated with:

1. download from the public GitHub release;
2. SHA256 verification;
3. dry run;
4. complete clean installation;
5. browser access from another LAN device;
6. application smoke testing;
7. server reboot;
8. post-reboot database, service and HTTP verification.

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
