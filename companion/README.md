# Network settings file server

This folder serves a Riverside Town network settings file on your home
network with nginx in Docker. The screensaver downloads the file every few
minutes, so you can change birthdays, messages, and some settings without
building the town again. README.md at the top of the repository describes
every field, in "Network settings file".

## Set it up

1. Copy this folder to a computer on your home network that runs Docker and
   stays on.
2. Edit `public/riverside.json`.
3. Start the server:

   ```
   docker compose up -d
   ```

4. Find the IP address of that computer, for example `192.168.1.50`. In
   your router, reserve that address for the computer, so it does not
   change. Use the IP address and not a name such as `server.local`,
   because a Roku may not be able to look up names like that.
5. Check the file from another computer or a phone browser:
   `http://192.168.1.50:8080/riverside.json`
6. In `town.json`, add:

   ```json
   "external_config_url": "http://192.168.1.50:8080/riverside.json"
   ```

   Then build the town and install it on the Roku again. This is the only
   time you need to do that for the network settings file.

## Change the file

Edit `public/riverside.json` and save it. You do not need to restart the
container. The screensaver uses the change at its next download (every
`refresh_minutes`, 10 by default).

Check the file for mistakes before you save it over the one in use:

```
python3 tools/check_external_config.py companion/public/riverside.json
```

That needs a copy of this repository and the jsonschema package
(`pip install jsonschema`). Without them, use the generator image:

```
docker run --rm -v "$PWD/public:/data" --entrypoint python3 \
  ghcr.io/rorpage/riverside-town-roku-generator:1 \
  /app/tools/check_external_config.py /data/riverside.json
```

If the file has a mistake, the screensaver skips the values it cannot use
and keeps the values from `town.json` for them. If the file is not valid
JSON at all, it keeps using the last good copy.

## Go back to the settings in town.json

- Remove fields from the file to go back to their values in `town.json`.
- Replace the contents with `{}`, or delete the file, to go back to all of
  them. Deleting the file also deletes the copy the Roku saved.
- If the server is down, the Roku keeps using the last good copy for up to
  7 days, then uses the settings in `town.json`.
