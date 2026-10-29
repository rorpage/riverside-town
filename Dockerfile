# The riverside-town-roku-generator image. It builds a Riverside Town
# screensaver from a town.json file in the current folder:
#
#   docker run --rm -v "$PWD:/work" ghcr.io/rorpage/riverside-town-roku-generator:1
#
# It writes out/riverside-town.zip and the preview images in out/previews.
FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends libcairo2 \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir cairosvg==2.9.1 pillow==12.3.0 fonttools==4.67.0 jsonschema==4.26.0

# The screensaver code and the generator. The images are not copied, because
# they are generated for each town.
COPY manifest /app/manifest
COPY source /app/source
COPY components /app/components
COPY tools /app/tools

WORKDIR /work
ENTRYPOINT ["python3", "/app/tools/build_town.py"]
