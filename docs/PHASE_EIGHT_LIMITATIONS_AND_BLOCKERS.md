# Phase 8 Limitations And Blockers

## Blocking Production Items

1. Real code-signing certificate is not present.
   - Local build can create and hash a JAR.
   - Production requires signed JAR and signed Windows agent.

2. Real external SENTINELA/SUPREME domain is not present in this workspace.
   - Local and staging examples exist.
   - Production requires DNS, TLS and configured secrets.

3. Device pairing authority is not provisioned.
   - Agent code now supports scoped device credentials, local signature
     verification and revocation fingerprints.
   - Production still needs a central pairing service, rotation policy and
     server-side revocation store backed by real operational credentials.

4. Full IPED action coverage is bounded by public extension points.
   - `ResultSetViewer` can observe table selection and model changes.
   - Some actions may require an upstream IPED event bus if not exposed through
     the result table or viewer lifecycle.

5. Central ingest contract is still the SUPREME V4 behavioral event contract.
   - The agent maps supported operational events to `/v1/events/ingest`.
   - `session_start`, `session_end` and `item_close` remain field-custody
     events until the central API receives a native field-session endpoint.

## Not Acceptable As "100%"

- Calling the old `SupremeAuditLogger` source patch the final architecture.
- Treating unsigned dev JARs as production artifacts.
- Treating localhost SENTINELA as external access.
- Treating simulated replay as field certification.

## Required To Unblock

- Provide code-signing certificate/keystore through secure CI or local secret
  store.
- Provide production domain/TLS and server credentials.
- Provision central device-pairing, credential rotation and revocation.
- Run Phase 8 gate with `-RequireProductionPrereqs`.
- Validate plugin load in official IPED without source modifications.
