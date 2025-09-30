# Double Agent

![Double Agent Running](./img/successful_run.png)

## Background

Agent DVR is security monitoring software. Versions <= 6.6.1.0 are vulnerable to path traversal on the 'addrecording' API call. This can be combined with the 'streamFile.cgi' API call to fetch local files. Both of these calls are unauthenticated, and work even if a user has specified a username/password in the UI.

I've tested this against the fresh installs of the latest version (6.6.1.0) as well as version 6.2.7.0. The exploit works against both Linux and Windows, but the --os flag must be specified accordingly when running.

## Usage

To run Double Agent:
```
doubleagent.py [-h] --target TARGET [--port PORT] --file FILE [--os {windows,linux}]
```

## Links

- [Agent DVR](https://www.ispyconnect.com/)
- [Agent DVR API Docs](https://ispysoftware.github.io/Agent_API/)
- [My Website!](https://www.ericholub.com)
