#!/bin/bash
set -e

alembic upgrade head
python backfill.py