# REST API Microservice Template

A boilerplate project for building a REST API microservice. This template provides a simple, scalable foundation for developing RESTful APIs, with built-in features like dependency management, structured logging, and environment-based configuration.

## Features

- **FastAPI** framework for handling RESTful endpoints
- **Poetry** for dependency management
- **Docker** support for containerized deployment
- Environment-based configuration management
- Structured logging
- Automated testing with **Pytest**

## Prerequisites

- **Python 3.x**: Ensure Python is installed on your system.
- **Poetry**: Used for dependency management.
  ```bash
  pip install poetry
  
### Dependencies
Once Python and poetry are installed, you can install the project dependencies by doing the following in a terminal

```bash 
poetry config virtualenvs.create false
poetry install
```

## Usage
### Running the Application
To start the application locally:

```bash 
python application.py
```
The API will be available at http://127.0.0.1:7100/ui.

### Running with Docker
If you prefer to use Docker, build and run the container:

```bash
docker build -t rest-api-template .
docker run -d -p 7100:7100 rest-api-template
```

### API Endpoints
You will create your own endpoints, but some common endpoint types that are REST are listed below.

* GET: Retrieve a resource.
* POST: Insertion of a datapoint or other API action.
* PUT: Initial creation of a resource or item.
* DELETE: Delete an item.

Here is in depth [documentation](https://docs.github.com/en/rest?apiVersion=2022-11-28) around REST if you would like to read further.

### Testing
To run the test suite:

```bash 
pytest
```

### General Application Structure
bash
```
├── src
│   ├── application.py           # Application entry point
|   ├── prometheus_middleware.py # Application middleware
│   ├── routes                   # API route definitions
│   ├── models                   # API data models
|   |   ├── requests             # Data models going into the system
|   |   └── responses            # Data models going out of the system
│   └── tests                    # Test cases
|       ├── integration          # Test cases involving external dependencies
|       └── unit                 # Test cases involving internal dependencies
├── Dockerfile                   # Project Dockerfile
├── docker-compose.yml           # Project docker compose, can combine multiple services
├── pyproject.toml               # Poetry dependency configuration
└── README.md                    # Project documentation
```