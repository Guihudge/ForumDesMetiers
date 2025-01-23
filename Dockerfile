# syntax=docker/dockerfile:1.7-labs
FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# Install python3
RUN apt update
RUN DEBIAN_FRONTEND=noninteractive apt install -y --no-install-recommends python3 python3-pip

# Copy requierment and install 
COPY requierment.txt .
RUN pip3 install --break-system-packages -r requierment.txt

# install prod server
RUN pip3 install --break-system-packages waitress

# Copy app
COPY --chown=root:root --exclude=app/app.db --exclude=*/__pycache__ --exclude=.venv/ --exclude=migrations/ . /ForumMetier/

# Go to app dir
WORKDIR /ForumMetier

CMD [ "/usr/local/bin/waitress-serve", "app:app" ]