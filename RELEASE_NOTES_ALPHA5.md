# SymptomTracker 0.1.0-alpha.5

This is the fifth public alpha release of SymptomTracker.

## Fixed

The installed application previously listened only on the loopback
interface (`127.0.0.1`).

As a result, the application could pass its local HTTP health check
but could not be accessed from another device on the local network.

This release changes the Gunicorn service binding to `0.0.0.0`.

After installation, SymptomTracker can therefore be accessed using:

`http://SERVER_IP:APP_PORT/`

The actual application port is selected automatically during
installation.

## Security note

Binding to `0.0.0.0` makes the application available through the
server's network interfaces, subject to the host firewall and network
configuration.

The installer does not configure router port forwarding and does not
automatically expose SymptomTracker to the public Internet.

For Internet-facing deployments, a properly configured reverse proxy,
HTTPS and appropriate access controls are strongly recommended.

## Validation

This release should be tested with a complete clean installation on
Ubuntu 24.04 LTS amd64.

The test should verify both local HTTP access and access from another
device on the local network.

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
