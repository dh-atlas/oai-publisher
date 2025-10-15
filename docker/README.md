# OAI Publisher Flask App

This repository contains a Flask application based on the project [dh-atlas/oai-publisher](https://github.com/dh-atlas/oai-publisher).

## Building the Docker Image

To build the Docker image of the Flask app, run the following command:

```bash
docker build --no-cache   --build-arg REPO_URL="https://github.com/dh-atlas/oai-publisher.git"   --build-arg REPO_REF="main"   -t atlas-oai-publisher:latest .
```

### Build Arguments
- `REPO_URL`: Git repository URL to clone the source code.
- `REPO_REF`: Branch or tag of the repository to use.

## Running the Container

Once the image is built, you can start the Flask app with:

```bash
docker run --rm -p 5000:5000 atlas-oai-publisher:latest
```

The app will be accessible at [http://localhost:5000](http://localhost:5000).
