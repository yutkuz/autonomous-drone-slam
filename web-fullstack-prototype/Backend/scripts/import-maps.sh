#!/usr/bin/env bash
set -euo pipefail

curl -X POST http://localhost:5090/api/maps/import
echo
