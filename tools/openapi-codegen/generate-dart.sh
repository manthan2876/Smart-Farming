#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
generator_version="7.26.0"
generator_url="https://repo1.maven.org/maven2/org/openapitools/openapi-generator-cli/${generator_version}/openapi-generator-cli-${generator_version}.jar"
generator_sha256="1760050094997b9cc790cc1350be095f15da8c08a996b184d3eadc4ccda5e35e"
cache_dir="${XDG_CACHE_HOME:-$HOME/.cache}/smart-farming"
generator_jar="${cache_dir}/openapi-generator-cli-${generator_version}.jar"
mobile_spec="${cache_dir}/mobile-openapi.json"

mkdir -p "$cache_dir"
if [[ ! -f "$generator_jar" ]]; then
  curl --fail --location --silent --show-error "$generator_url" --output "$generator_jar"
fi
echo "${generator_sha256}  ${generator_jar}" | sha256sum --check --status

python "$repo_root/tools/openapi-codegen/mobile-openapi.py" \
  "$repo_root/Docs/openapi.json" "$mobile_spec"
java -jar "$generator_jar" generate \
  --input-spec "$mobile_spec" \
  --generator-name dart-dio \
  --output "$repo_root/mobile/api_client" \
  --additional-properties=pubName=smart_farming_api,pubLibrary=smart_farming_api,pubVersion=0.1.0,serializationLibrary=json_serializable,disallowAdditionalPropertiesIfNotPresent=false \
  --global-property apis,models,supportingFiles,apiDocs=false,modelDocs=false,apiTests=false,modelTests=false

python - "$repo_root/mobile/api_client/pubspec.yaml" <<'PY'
from pathlib import Path
import sys

pubspec = Path(sys.argv[1])
text = pubspec.read_text(encoding="utf-8")
text = text.replace("sdk: '>=3.5.0 <4.0.0'", "sdk: '>=3.8.0 <4.0.0'")
pubspec.write_text(text, encoding="utf-8")

ignore_file = pubspec.parent / ".gitignore"
ignore_text = ignore_file.read_text(encoding="utf-8")
ignore_text = ignore_text.replace("pubspec.lock\n", "")
ignore_file.write_text(ignore_text, encoding="utf-8")
PY

(cd "$repo_root/mobile/api_client" && dart pub get && dart run build_runner build --delete-conflicting-outputs)
