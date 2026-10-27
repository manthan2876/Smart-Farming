# Flutter Mobile Client (Farmer Edition)

The Flutter mobile application provides the native Android farmer-facing client for the Smart Farming platform. It features an offline-first diagnostic scan queue, camera-assisted leaf capture, center-crosshair GIS farm boundary drawing, dynamic Supabase Remote Config, and native secure token storage.

## Key Features

- **5-Tab Farmer Shell (`FarmerShell`)**: Today (dashboard & weather), History (longitudinal scans), Center Camera FAB (instant diagnosis), Farm (plot & boundary management), and Settings.
- **Center-Crosshair GIS Boundary Drawing (`field_boundary_screen.dart`)**: Native map boundary creator with crosshair targeting, magnetic point snapping, geodesic acreage calculation, and offline tile caching.
- **Dynamic Remote Config (`RemoteConfigService`)**: Backend URL is resolved dynamically at startup from Supabase `public.app_config` via PostgREST and cached locally in `SharedPreferences`. No manual server URL input is exposed to users, preventing MITM redirection.
- **Offline Scan Queue (`SyncService` + `OfflineQueueDb`)**: Scans captured in remote fields with intermittent connectivity are persisted in local SQLite and automatically synced with exponential backoff on reconnection.
- **Trilingual Localization (EN / GU / HI)**: Complete vernacular UI and domain translations with Flutter tests enforcing 100% catalog parity.
- **Dual Text-to-Speech Engine (`TtsService`)**: High-fidelity cloud neural audio with automatic on-device `flutter_tts` fallback for spoken regional advisories.
- **Secure Token Storage (`TokenStorage`)**: Encrypted access and refresh token persistence via `flutter_secure_storage` with automated 401 token refresh rotation.

## Development and Validation

```bash
cd mobile
flutter pub get
flutter analyze
flutter test
```

## Running on Device / Emulator

Configure `mobile/.env` (passed via `--dart-define-from-file=.env`):
```bash
flutter run -d <DEVICE_ID> --dart-define-from-file=.env
```

## Android Release Signing & Obfuscation

Release builds must not use the debug signing key. For local signing:
1. Copy `android/key.properties.example` to `android/key.properties` and set your private keystore credentials.
2. Build obfuscated release artifacts:
   ```bash
   ./scripts/build_release.sh
   # Or directly:
   flutter build appbundle --release --obfuscate --split-debug-info=build/app/outputs/symbols --dart-define-from-file=.env
   ```
CI/CD automation in `.github/workflows/mobile-release.yml` uses repository secrets (`ANDROID_KEYSTORE_BASE64`, `ANDROID_KEY_ALIAS`, etc.) for automated signed release generation.
