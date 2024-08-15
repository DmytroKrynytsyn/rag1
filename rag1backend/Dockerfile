# First stage: build the wheel file and requirements.txt
FROM python:3.12-slim as builder

# Install Poetry
RUN pip install poetry

# Set the working directory
WORKDIR /app

# Copy the entire application folder
COPY . .

# Install dependencies and build the wheel
RUN poetry install --only main --no-root
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes
RUN poetry build -f wheel

# Second stage: create the final image
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Copy the wheel file and requirements.txt from the builder stage
COPY --from=builder /app/dist/*.whl /app/
COPY --from=builder /app/requirements.txt /app/

# Install dependencies using pip
RUN pip install -r requirements.txt
RUN pip install /app/*.whl

# Command to run the application
CMD ["python", "-m", "rag1backend.entrypoint.main"]