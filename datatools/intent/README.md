# intent

Intents HTTP server. Decouples intents triggered in datatools apps from their effects.

An HTTP `POST` carries an entity in its body; the server reacts based on `Content-Type`
(dispatch table in `dispatcher.py`) — copy to clipboard, open in browser/IDEA, save a
file, store an entity, etc.

Run: `python -m datatools.intent.server` (listens on `0.0.0.0:7777`).
A user systemd unit is provided in `intent-server.service`.

## Kiosk routing

A "kiosk" is just another instance of this same server on the LAN. A `POST` can be
forwarded to it by adding the header `X-Destination: kiosk`.

- **Discovery** (`kiosk_scanner.py`): a daemon thread scans on start and every 5 min.
  It probes the local IP's last octet ±10 (excluding self) for a host accepting TCP
  connections on port 7777, in parallel, and remembers the lowest responder.
- **Routing** (`post_request_router.py`): `post_request_destination()` returns the
  kiosk IP when `X-Destination: kiosk` is set and a kiosk is known; `route_post_request()`
  proxies the request there via `http.client`, stripping the `X-Destination` header, and
  mirrors the kiosk's response back to the caller.
- **Fallback**: if no kiosk is known, or the proxy call fails, the request is handled
  locally (`dispatch()`) as usual.

## Layout

| File | Role |
|------|------|
| `server.py` | HTTP server; `do_GET`/`do_PUT`/`do_POST`/`do_DELETE` |
| `post_request_router.py` | Decide destination + proxy to kiosk |
| `kiosk_scanner.py` | Background LAN discovery of the kiosk |
| `dispatcher.py` | Local handling by `Content-Type` |
| `handler_*.py` | Per-content-type handlers |
