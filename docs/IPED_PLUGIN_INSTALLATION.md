# SUPREME IPED Plugin Installation

## Build

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\build_supreme_iped_plugin.ps1 -Root .
```

For production signing, set the keystore variables before building:

```powershell
$env:SUPREME_CODESIGN_KEYSTORE="C:\secure\supreme-codesign.p12"
$env:SUPREME_CODESIGN_ALIAS="supreme-release"
$env:SUPREME_CODESIGN_STOREPASS="<provided interactively or by secure CI secret>"
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\build_supreme_iped_plugin.ps1 -Root . -RequireRealSigning
```

Do not commit the keystore, password or signed private material.

## Verify

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\verify_supreme_iped_plugin.ps1 -Root .
```

Production:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\verify_supreme_iped_plugin.ps1 -Root . -RequireRealSigning
```

## Install Into IPED

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\install_supreme_iped_plugin.ps1 -Root . -IpedHome "C:\IPED" -Force
```

The installer:

- copies `supreme-iped-plugin.jar` to `IPED\plugins`;
- backs up `conf\ResultSetViewersConf.xml`;
- appends `com.supreme.iped.SupremeFieldTelemetryViewer`;
- writes `supreme-plugin-install-manifest.json`;
- supports `-VerifyOnly` and `-Rollback`.

## Test Installer Safely

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\test_phase8_plugin_install.ps1 -Root .
```

This uses a temporary IPED-like folder and does not alter the analyst's real
IPED installation.
