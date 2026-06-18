#!/bin/bash

#script dijalankan dari root folder
cd "$(dirname "$0")/.."

LOG_FILE="logs/pipeline.log"
mkdir -p logs

log() {
    echo "$(date "+%Y-%m-%d %H:%M:%S") - $1" | tee -a "$LOG_FILE"
}

log "Starting pipeline"

# Extract
python src/extract.py "$DATA_URL"
if [ $? -ne 0 ]; then
    log "Extract failed"
    exit 1
fi
log "Extract completed"

# Transform
python src/transform.py
if [ $? -ne 0 ]; then
    log "Transform failed"
    exit 1
fi
log "Transform completed"

# Load
python src/load.py
if [ $? -ne 0 ]; then
    log "Load failed"
    exit 1
fi
log "Load completed"

# Data Quality Check
python src/data_quality.py
if [ $? -ne 0 ]; then
    log "Data quality check failed"
    exit 1
fi
log "Report completed"
log "Data quality check completed"

log "Pipeline completed successfully"