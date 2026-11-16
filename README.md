# The ROM Depot — importer plugin for ROMarr / ROM Hub

Upstream `theromdepot` plugin searches the operator's saved catalogue and hands a
download URL to the browser (`stream`). This fork adds the missing half: an
`importer`, so a grab inside ROMarr fetches the file itself.

## Install

ROMarr -> Hub -> *Add your own* -> `https://github.com/powkakashi/rom-hub-romdepot-import`

or

    rom-hub plugin install https://github.com/powkakashi/rom-hub-romdepot-import

## Configure

    # export the whole tree once, while signed in: https://theromdepot.com/api/getContents
    rom-hub plugin config romdepot-import --set catalog_path=/config/romdepot.json

    # the session, never written to the manifest:
    rom-hub plugin secret set romdepot-import session_cookie --stdin

The cookie is the `Cookie:` header a signed-in browser sends (`connect.sid=…`).
It is stored in ROM Hub's secret store and only ever sent to theromdepot.com,
which `[permissions] network` already allowlists.

## What it needs from the host

1. `Cookie` must be a permitted plan header. Stock ROM Hub refuses it
   (`rom_hub/types.py`, `_FORBIDDEN_HEADERS`) because the broker model does not
   hand plugins a cookie jar. Without this the importer refuses with
   *"no session cookie"* only after the host rejects the header.
2. The scan that registers the upload needs `tasks.run`. Stock
   `REQUIRED_SCOPES` omits it, so RomM 5.4.1 answers *"You are not authorized to
   run scans"* on the socket event.

Both are host-side policy decisions, not plugin bugs — patch them locally or wait
for upstream. Without them this plugin still *searches*; it cannot import.

## Verified

Live: `rom-hub import romdepot-import "Nintendo DS/US/Uno 52 (U).zip" --platform nds`
-> RomM row 15028; and a grab from ROMarr's search the same way (row 15027).
