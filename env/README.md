# SUPREME V4 environment profiles

These files separate local, demo, homologation and production intent.

- `.env.local.example`: developer workstation only.
- `.env.demo.example`: non-sensitive demo with synthetic data only.
- `.env.homologation.example`: client/staging validation.
- `.env.production.example`: production values and real infrastructure.

Never rename these examples in git. Copy the chosen profile to `.env` and replace
all `CHANGE_ME` values outside version control.
