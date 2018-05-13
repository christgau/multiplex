# multiplex.py

Stream data from a TCP server to multiple read-only clients.

If a TCP server accepts a limited/fixed number of connections only,
multiplex.py can be used to effectively connect more clients to the server.  A
possible use-case are RS232/422/485-Ethernet devices (like Moxa Nports) which
allow only up to, say, four TCP clients.  multiplex.py connects to the server
and forwards all data coming from the server to the connected clients.  Clients
are read-only, i.e. all their data is silently dropped.

In case of an error, such as an (intentionally) aborted connection,
multiplex.py will try to reconnect to the server with a five second interval.

# Usage

`./multiplex.py  [--nodelay] remote:port local:port`

 * `remote:port`

	The address/host name and port of the real server multiplex.py connects to.

 * `local:port`

	The address and port of the server socket provided by multiplex.py. If
	`local:` address part (including ':') is not specified, the server will
	listen on all interfaces.

 * `--nodelay`

	Set the TCP_NODELAY option for multiplex.py's own server socket, such that
	all data from the real server is forwarded as fast as possible.

# Remarks

Socat and netcat/nc appear to not having support for multiple concurrent
clients that all receive the same data. In addition automatic reconnect is not
supported (except by explicit restart).
