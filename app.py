from flask import Flask, render_template, request, jsonify
import requests

# OpenTelemetry imports
import os
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.resources import SERVICE_NAME, SERVICE_VERSION

# Initialize OpenTelemetry
def init_telemetry():
    # Get configuration from environment variables
    service_name = os.getenv('OTEL_SERVICE_NAME', 'currency-converter')
    endpoint = os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT', 'http://localhost:4318')
    
    # Parse custom resource attributes from environment
    resource_attributes = {
        SERVICE_NAME: service_name,
        SERVICE_VERSION: "1.0.0",
    }
    
    # Add custom kubesense attributes from environment
    otel_resource_attrs = os.getenv('OTEL_RESOURCE_ATTRIBUTES', '')
    if otel_resource_attrs:
        for attr in otel_resource_attrs.split(','):
            if '=' in attr:
                key, value = attr.split('=', 1)
                resource_attributes[key.strip()] = value.strip()
    
    # Create resource with all attributes
    resource = Resource.create(resource_attributes)
    
    # Set up the tracer provider
    trace.set_tracer_provider(TracerProvider(resource=resource))
    tracer = trace.get_tracer(__name__)
    
    # Configure OTLP exporter using environment variables
    # Since you're using http/protobuf protocol, we use the HTTP exporter
    otlp_exporter = OTLPSpanExporter(
        endpoint=f"{endpoint}/v1/traces",  # Add the traces path for HTTP protocol
        timeout=30,  # Add timeout for reliability
    )
    
    # Add the exporter to a BatchSpanProcessor
    span_processor = BatchSpanProcessor(otlp_exporter)
    trace.get_tracer_provider().add_span_processor(span_processor)
    
    return tracer

# Initialize telemetry
tracer = init_telemetry()

app = Flask(__name__)
API_KEY = "4fb1a521132a87a158434378"

# Instrument Flask and requests libraries
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()

def get_exchange_rate(from_currency, to_currency):
    # Create a custom span for this function
    with tracer.start_as_current_span("get_exchange_rate") as span:
        # Add attributes to the span
        span.set_attribute("currency.from", from_currency)
        span.set_attribute("currency.to", to_currency)
        span.set_attribute("api.provider", "exchangerate-api.com")
        
        url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/{from_currency}"
        
        try:
            response = requests.get(url)
            span.set_attribute("http.status_code", response.status_code)
            
            if response.status_code == 200:
                data = response.json()
                exchange_rate = data['conversion_rates'][to_currency]
                span.set_attribute("exchange.rate", exchange_rate)
                span.set_attribute("operation.success", True)
                return exchange_rate
            else:
                span.set_attribute("operation.success", False)
                span.add_event("API request failed", {
                    "status_code": response.status_code,
                    "response_text": response.text[:200]  # Limit response text
                })
                return None
                
        except Exception as e:
            span.set_attribute("operation.success", False)
            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            raise

@app.route('/')
def index():
    # The Flask instrumentation will automatically create spans for routes
    current_span = trace.get_current_span()
    current_span.set_attribute("route.name", "index")
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert_currency():
    current_span = trace.get_current_span()
    current_span.set_attribute("route.name", "convert_currency")
    
    from_currency = request.form['from_currency']
    to_currency = request.form['to_currency']
    amount = request.form['amount']
    
    # Add request parameters as span attributes
    current_span.set_attribute("request.from_currency", from_currency)
    current_span.set_attribute("request.to_currency", to_currency)
    current_span.set_attribute("request.amount", amount)
    
    if not amount:
        current_span.add_event("Validation failed: empty amount")
        current_span.set_attribute("validation.error", "empty_amount")
        return jsonify({'error': 'Amount Not Entered. Please enter a valid amount.'})
    
    try:
        amount = float(amount)
        current_span.set_attribute("parsed.amount", amount)
    except ValueError:
        current_span.add_event("Validation failed: invalid amount format")
        current_span.set_attribute("validation.error", "invalid_amount_format")
        return jsonify({'error': 'Invalid amount. Please enter a number.'})
    
    try:
        exchange_rate = get_exchange_rate(from_currency, to_currency)
        if exchange_rate:
            new_amount = exchange_rate * amount
            result = round(new_amount, 4)
            
            # Add successful conversion details
            current_span.set_attribute("conversion.success", True)
            current_span.set_attribute("conversion.result", result)
            current_span.set_attribute("conversion.rate", exchange_rate)
            
            return jsonify({'result': result})
        else:
            current_span.add_event("Exchange rate fetch failed")
            current_span.set_attribute("conversion.success", False)
            return jsonify({'error': 'Failed to fetch exchange rate. Please try again later.'})
            
    except Exception as e:
        current_span.record_exception(e)
        current_span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
        current_span.set_attribute("conversion.success", False)
        return jsonify({'error': str(e)})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
