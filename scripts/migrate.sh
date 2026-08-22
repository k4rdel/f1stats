#!/bin/bash
set -e

alembic upgrade head
python scripts/backfill.py