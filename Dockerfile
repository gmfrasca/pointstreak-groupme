FROM fedora

# Get Config Options
ARG bot_cfg=config/bots.docker.yaml
ARG response_cfg=config/responses.docker.yaml
ARG timed_cfg=config/timed.docker.yaml
ARG python_version=python-2
ARG port=5002

WORKDIR /app

# Copy configs to image
ADD $bot_cfg config/bots.local.yaml
ADD $response_cfg config/responses.local.yaml
ADD $timed_cfg config/timed.local.yaml
ADD psgroupme psgroupme
ADD setup.py setup.py
ADD requirements.txt requirements.txt

# Install Requirements
RUN dnf install python python-pip -y
RUN pip install -Ur requirements.txt

# Run The App
CMD ["python", "-u", "psgroupme/main.py"]
