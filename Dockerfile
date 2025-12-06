FROM python:3.11

# Create and set working directory
RUN mkdir -p /usr/app
WORKDIR /usr/app

# Copy dependency file first, install deps
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the rest of the code (including src/)
COPY . .

EXPOSE 5000

# Run the app *file* directly, NOT as a module
CMD ["python", "src/app.py"]
