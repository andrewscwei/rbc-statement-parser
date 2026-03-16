# syntax=docker/dockerfile:1

## Dockerfile for [rbc-statement-parser](https://github.com/andrewscwei/rbc-statement-parser)

ARG pythonVersion="3.12"

# -- Base Stage

FROM python:${pythonVersion}-slim AS base-stage

ENV workDir="/app"
ENV nonRootUser="notroot"
ARG nonRootUID="1000"

# Create input and output directories
RUN mkdir -p ${workDir}/input ${workDir}/output

# Set default locale to UTF-8
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
# Prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
# Enable Python tracebacks on segfaults
ENV PYTHONFAULTHANDLER=1
# Create the virtualenv inside project directory
ENV PIPENV_VENV_IN_PROJECT=1

# Create a non-root user
RUN <<EOT
  set -e
  groupadd -g $nonRootUID $nonRootUser
  useradd -m -u $nonRootUID -g $nonRootUID $nonRootUser
EOT

# -- Build Stage 

FROM base-stage AS build-stage
WORKDIR ${workDir}

# Install and run `pipenv` to build Python dependencies
RUN pip install --no-cache-dir pipenv
COPY Pipfile Pipfile.lock ./
RUN pipenv install --python $(which python3) -d

# -- Run Stage

FROM base-stage AS run-stage
WORKDIR ${workDir}
USER ${nonRootUser}

# Set the Python path to use the virtualenv
ENV PATH="${workDir}/.venv/bin:$PATH"

# Copy built virtualenv and source code
COPY --from=build-stage ${workDir}/.venv ${workDir}/.venv
COPY --chown=${nonRootUser}:${nonRootUser} . .

# Copy over .rc file if it exists. App will use default config if one is not found.
COPY .rc* .

# Set the entrypoint to run the Python script
ENTRYPOINT ["python3", "main.py"]
# Default to showing help/usage if no arguments provided
CMD ["--help"]