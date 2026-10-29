#!/bin/bash
# Builds riverside-town.zip and installs it on a Roku in developer mode.
# Based on build.sh in rorpage/pages-watch-mcu-screensaver.
#
#     ROKU_DEV_TARGET=<roku-ip-address> ./build.sh   Build the zip and install it
#     ./build.sh --zip-only                          Only build the zip, for a manual install
#
# The zip is written to the repository root. It holds only the files the Roku
# needs (manifest, source, components, images), with the manifest at the top
# level of the zip.

cd "$(dirname "${BASH_SOURCE[0]}")" || exit 1

APP_ZIP_FILE=riverside-town.zip
DEV_SERVER_TMP_FILE=/tmp/dev_server_out

delete_temp_file() {
  rm -f ${DEV_SERVER_TMP_FILE}
}

display_padded_message() {
  echo ""
  echo $1
  echo ""
}

create_zip() {
  echo ""
  echo -n "Creating zip file..."

  rm -f ${APP_ZIP_FILE}
  zip -q -r ${APP_ZIP_FILE} manifest source components images -x "*.DS_Store" || exit 1

  echo "Done! Wrote ${APP_ZIP_FILE}"
}

if [[ "$1" == "--zip-only" ]]; then
  create_zip
  exit 0
fi

if [ -z ${ROKU_DEV_TARGET} ]; then
  echo "ERROR: ROKU_DEV_TARGET is not set. Set it to the Roku's IP address, or run ./build.sh --zip-only to only build the zip.";
  exit 1;
fi

HOST_OS=linux
QUICK_PING_ARGS='-c 1 -w 1'

if [[ "$OSTYPE" == "darwin"* ]]; then
  HOST_OS=macos
  QUICK_PING_ARGS='-c 1 -t 1'
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
  HOST_OS=cygwin
  QUICK_PING_ARGS='-n 1 -w 1000'
fi

echo "Checking dev server at ${ROKU_DEV_TARGET}..."

# Ping device
if ! ping ${QUICK_PING_ARGS} ${ROKU_DEV_TARGET} &> ${DEV_SERVER_TMP_FILE}; then
  echo "ERROR: Device is not responding to ping."
  delete_temp_file
  exit 1
fi

delete_temp_file

# Check for ECP
if ! curl --connect-timeout 2 --silent --output ${DEV_SERVER_TMP_FILE} \
    http://${ROKU_DEV_TARGET}:8060; then
  echo "ERROR: Device is not responding to ECP...is it a Roku?"
  delete_temp_file
  exit 1
fi

ROKU_DEV_NAME=`cat ${DEV_SERVER_TMP_FILE} | \
    grep -o "<friendlyName>.*</friendlyName>" | \
    sed "s|<friendlyName>||" | \
    sed "s|</friendlyName>||"`

echo "Device reports name as \"${ROKU_DEV_NAME}\""

delete_temp_file

if ! curl --connect-timeout 2 --silent --output ${DEV_SERVER_TMP_FILE} \
    http://${ROKU_DEV_TARGET}; then
  echo "ERROR: Device server is not responding...is the developer installer enabled?"
  delete_temp_file
  exit 1
fi

delete_temp_file

echo "The Roku is ready."

create_zip

# Get developer account password
echo ""
echo -n "Developer account password: "
read -s USERPASS
echo ""

display_padded_message "Uploading zip file to device..."

HTTP_STATUS=`curl --user "rokudev:${USERPASS}" --digest --silent --show-error \
    -F "mysubmit=Install" -F "archive=@${APP_ZIP_FILE}" \
    --output ${DEV_SERVER_TMP_FILE} \
    --write-out "%{http_code}" \
    http://${ROKU_DEV_TARGET}/plugin_install`

delete_temp_file

if [[ "$HTTP_STATUS" == 200 ]]; then
  echo "File uploaded successfully!"
elif [[ "$HTTP_STATUS" == 401 ]]; then
  echo "Oops! Looks like that was the wrong password perhaps?"
  exit 1
else
  echo "Error: Device returned HTTP ${HTTP_STATUS}"
  exit 1
fi
