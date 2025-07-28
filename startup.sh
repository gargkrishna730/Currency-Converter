#!/bin/bash

# Set OpenTelemetry environment variables
export OTEL_EXPORTER_OTLP_ENDPOINT="http://dev.kubesense.ai:33443"
export OTEL_SERVICE_NAME="MyCurrencyConverterService"
export OTEL_RESOURCE_ATTRIBUTES="kubesense.env_type=legacy,kubesense.cluster=cluster-1"
export FLASK_ENV="production"
export OTEL_EXPORTER_OTLP_PROTOCOL="http/protobuf"
export OTEL_NODE_RESOURCE_DETECTORS="env,host,os,process"

# Additional OpenTelemetry settings for better performance and reliability
export OTEL_BSP_SCHEDULE_DELAY=5000  # 5 seconds batch delay
export OTEL_BSP_MAX_EXPORT_BATCH_SIZE=512
export OTEL_BSP_EXPORT_TIMEOUT=30000  # 30 seconds timeout
export OTEL_BSP_MAX_QUEUE_SIZE=2048

# Python-specific OpenTelemetry settings
export OTEL_PYTHON_LOG_CORRELATION=true
export OTEL_PYTHON_LOG_FORMAT="%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] [trace_id=%(otelTraceID)s span_id=%(otelSpanID)s] - %(message)s"

echo "Starting Currency Converter Service with OpenTelemetry..."
echo "Service Name: $OTEL_SERVICE_NAME"
echo "OTLP Endpoint: $OTEL_EXPORTER_OTLP_ENDPOINT"
echo "Resource Attributes: $OTEL_RESOURCE_ATTRIBUTES"
echo "Protocol: $OTEL_EXPORTER_OTLP_PROTOCOL"

# Run the Flask application
python app.py
