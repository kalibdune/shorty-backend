# Shorty - URL Shortener

Shorty is a URL shortening service written in Python. It allows you to shorten long URLs into more manageable, shorter links.

## Features

- Shorten long URLs
- Redirect shortened URLs to the original URLs
- Track the number of clicks on shortened URLs

## Requirements

- Python 3.12+
- Poetry

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/shorty.git
    cd shorty
    ```

2. Install dependencies using Poetry:
    ```sh
    poetry install
    ```

## Running the Application

### Using Poetry

1. Activate the virtual environment:
    ```sh
    poetry shell
    ```

2. Run the application:
    ```sh
    python -m shorty
    ```

### Using Docker

1. Build the Docker image:
    ```sh
    docker build -t shorty:latest .
    ```

2. Run the Docker container:
    ```sh
    docker run -d -p 8000:8000 shorty:latest
    ```

## Usage

Once the application is running, you can access it at `http://localhost:8000`. Use the web interface to shorten URLs and manage your shortened links.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

Links:
- [Frontend repository](https://github.com/kalibdune/shorty-frontend)
- [Base repository](https://github.com/kalibdune/shorty)
