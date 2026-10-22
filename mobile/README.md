# Flutter mobile client

The Flutter application provides the farmer-facing mobile experience, offline scan queue, localized UI, and native secure token storage.

## Development and validation

```bash
flutter pub get
flutter analyze
flutter test
```

Configure the backend URL through the mobile remote-configuration flow or the documented build-time configuration. Do not embed API credentials or signing material in the app bundle.

## Android release signing

Release builds must not use the debug signing key. For local signing, copy `android/key.properties.example` to `android/key.properties` and set values for a private keystore; the actual properties file and keystore are ignored by Git. CI/release automation may instead provide the `ANDROID_KEYSTORE_*` and `ANDROID_KEY_*` environment variables.

Build release artifacts with Flutter's release mode. Store obfuscation symbol files securely when using `--obfuscate --split-debug-info`.
