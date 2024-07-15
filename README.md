# Currency Converter Web App

A simple currency converter web application built with Flask. This app allows users to convert amounts from one currency to another using real-time exchange rates.

## Features

- Convert between multiple currencies
- Real-time exchange rates
- User-friendly interface

## Installation

### Prerequisites

- Python 3.7 or higher
- Docker (optional, for containerized deployment)

### Local Setup

1. Clone the repository:
    ```sh
    git clone https://github.com/gargkrishna730/Currency-Converter.git
    cd currency-converter
    ```

2. Set up a virtual environment and activate it:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

4. Run the application:
    ```sh
    python currency_converter_web.py
    ```

5. Open your browser and go to `http://127.0.0.1:5001`.

### Docker Setup

1. Pull the Docker image from Docker Hub:
    ```sh
    docker pull gargkrishna730/currency-converter:latest
    ```

2. Run the Docker container:
    ```sh
    docker run -p 5001:5000 gargkrishna730/currency-converter:latest
    ```

3. Open your browser and go to `http://127.0.0.1:5001`.

## Usage

1. Enter the amount you want to convert.
2. Select the currency you are converting from.
3. Select the currency you are converting to.
4. Click the "Convert" button to see the converted amount.

## Deployment

You can access the deployed application at [convertcurrency.online](https://convertcurrency.online).
