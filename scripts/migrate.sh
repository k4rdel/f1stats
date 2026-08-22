#!/bin/bash
set -e

alembic upgrade head
python -m scripts.backfill