# B7 Locator REST API with FastAPI, MySQL 

This is a REST API built using FastAPI and SQLAlchemy with MySQL as the database backend.

## Project Structure

- `models`: This directory contains the SQLAlchemy model definitions for the database tables.
- `schemas`: This directory contains Pydantic models (schemas) used for data validation and serialization.
- `routes`: This directory contains FastAPI router modules, each responsible for handling API endpoints related to specific resources.
- `app.py`: The main application file where the FastAPI application, CORS, middleware is created and configured.
- `config/db.py`: Contains the database connection setup using SQLAlchemy.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/daptheHuman/b7-locator
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Environment Variables

To run the B7 Locator REST API, you need to set up a `.env` file in the project root directory. Start by making a copy of the `.env.sample` file and renaming it to `.env`. Then, update the values of the environment variables as needed.

### `.env` Configuration

- `ALLOWED_ORIGINS`: A comma-separated list of origins that are allowed to access the API.
- `DATABASE_URL`: The connection URL for your MySQL database. Make sure to replace `username`, `password`, `hostname`, and `database_name` with your database credentials and details.


### Creating the `.env` File

1. Start by making a copy of the provided `.env.sample` file:

   ```bash
   cp .env.sample .env
   ```

2. Open the `.env` file in a text editor and update the values as described above.

3. Save the changes to the `.env` file.

## Running the Application

Once you have configured the `.env` file with the appropriate database connection details, you can run the FastAPI application using the following command:

```bash
python app.py
```

The API will now be accessible at the specified endpoints, and you can use the provided API documentation (`/docs`) to explore and interact with the endpoints.

