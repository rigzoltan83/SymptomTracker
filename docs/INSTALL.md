# SymptomTracker Installation Guide

This guide describes how to install the public SymptomTracker alpha release on a fresh server.

> **Alpha software:** `0.1.0-alpha.1` is intended for testing. Installation and upgrade procedures may change before the first stable release. Keep independent backups of important data.

## Supported installation target

The automated installer currently targets:

- Ubuntu 24.04 LTS
- x86_64 / amd64
- systemd
- an internet connection during installation
- root (`sudo`) access

The installer prepares the required operating-system packages, Python environment, Docker components, PostgreSQL database and systemd service.

## What the installer does

During a fresh installation the installer:

1. checks the operating system and required release files;
2. refuses to overwrite a detected existing SymptomTracker installation;
3. installs required Ubuntu packages;
4. installs Docker Engine / Docker Compose when required, or uses a compatible existing installation;
5. automatically finds free ports instead of assuming that `5432` and `5060` are available;
6. creates the `symptomtracker` system user;
7. installs the application under `/opt/symptomtracker`;
8. generates a unique PostgreSQL password and Flask secret key;
9. creates the private `.env` configuration;
10. starts a dedicated PostgreSQL 16 container;
11. creates the Python virtual environment and installs the pinned Python dependencies from `requirements.txt`;
12. applies all database migrations;
13. imports the bundled reusable reference data;
14. creates and enables `symptomtracker.service`;
15. starts the application and performs health checks.

## Download a release

Download the archive attached to the desired SymptomTracker release from the project's GitHub Releases page.

For the first public alpha, use release:

`v0.1.0-alpha.1`

Do not copy `.env`, database backups, personal uploads or other private data from the developer's installation into a fresh installation.

## Extract the archive

The exact archive filename may depend on the published GitHub release asset. For example:

```bash
tar -xzf symptomtracker-0.1.0-alpha.1.tar.gz
cd symptomtracker
```

## Optional dry run

Before making system changes, the installer can be run in dry-run mode:

```bash
./installer/install.sh --dry-run
```

The installer asks for the interface language:

- Magyar
- English

Dry-run mode checks the installation package and environment and shows the proposed ports, but does not install or modify the system.

## Install

Run the installer with root privileges:

```bash
sudo ./installer/install.sh
```

Select the desired installer language and follow the output.

## Automatic port selection

SymptomTracker deliberately does not require its preferred ports to be unused.

The installer searches for a free PostgreSQL host port starting at:

`5432`

and a free application port starting at:

`5060`

For example, if another PostgreSQL instance already occupies `5432` and another application occupies `5060`, the installer can automatically choose `5433` and `5061`.

The selected ports are written to the installation configuration and used consistently by Docker, the database connection and the systemd service.

The PostgreSQL container itself still listens on its normal internal port `5432`; only the host-side port is selected dynamically.

## Installation directory

The installed application is located at:

```text
/opt/symptomtracker
```

Important locations include:

```text
/opt/symptomtracker/.env
/opt/symptomtracker/uploads
/opt/symptomtracker/uploads/foods
/opt/symptomtracker/uploads/symptoms
/opt/symptomtracker/backups
```

The `.env` file contains installation-specific secrets. **Do not publish, commit or share it.**

## Database

A fresh installation uses a dedicated PostgreSQL 16 Docker container named:

```text
symptomtracker-db
```

The database name is:

```text
symptomtracker
```

The database user is:

```text
symptomtracker_user
```

The database password is generated automatically during installation and is not included in the public release.

## Initial reference data

A new installation imports reusable reference data bundled with the release, including:

- ingredients and their translations;
- risk components and their translations;
- ingredient/risk-component relationships;
- symptom types and their translations;
- body parts and their translations;
- medications.

The public seed data does **not** contain the developer's personal diary events, personal foods/recipes, medication events, symptom events or uploaded personal images.

## Application service

The application runs as:

```text
symptomtracker.service
```

Check its status with:

```bash
sudo systemctl status symptomtracker.service
```

Recent application logs:

```bash
sudo journalctl -u symptomtracker.service -n 100 --no-pager
```

Restart the application:

```bash
sudo systemctl restart symptomtracker.service
```

## Database container diagnostics

List running containers:

```bash
sudo docker ps
```

Inspect the SymptomTracker database container:

```bash
sudo docker inspect symptomtracker-db
```

If installation fails while starting PostgreSQL, inspect its logs:

```bash
cd /opt/symptomtracker
sudo docker compose --env-file .env -f docker-compose.yml logs --tail=100 db
```

## Backups and upgrades

This is an alpha release. Do not treat an alpha installation as the only copy of important data.

Before testing future updates, back up at least:

- the PostgreSQL database;
- `/opt/symptomtracker/uploads`;
- the installation-specific configuration needed for recovery.

Do not replace an existing installation by simply running the fresh installer over it. The installer contains protection against detected existing installations. A dedicated update procedure will be provided separately.

## Troubleshooting

If the application does not start, first check:

```bash
sudo systemctl status symptomtracker.service
sudo journalctl -u symptomtracker.service -n 100 --no-pager
sudo docker ps
```

Also verify that `/opt/symptomtracker/.env` exists and that the selected application and database ports are not being used by unrelated processes.

Do not post the contents of `.env` in public bug reports.

## Medical disclaimer

SymptomTracker is a personal diary, data-recording and informational analysis tool.

It is **not a medical device** and must not be used as a substitute for professional medical advice, diagnosis or treatment. Statistical associations, scores, risk indicators or other results produced by the application do not establish a medical diagnosis or causation.

See `DISCLAIMER.md` for the complete medical disclaimer.

## License

SymptomTracker is free and open-source software licensed under the GNU General Public License version 3 (GPL-3.0).

See `LICENSE` for the complete license text.

## Support development

If you find SymptomTracker useful and would like to support its continued development, you can do so on Patreon:

https://www.patreon.com/c/ZoltanRigo
