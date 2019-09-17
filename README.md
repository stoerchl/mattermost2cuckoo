# Mattermost 2 Cuckoo

A python daemon which listens for web requests.
Using a POST request, the python daemon submits a file with the given name from the attachment directory to the cuckoo sandbox.
This daemon was specificly written for a slash command in Mattermost. Which could look as follows:

```sh
/cuckoo-submit [sha256 hash]
```

I myself use this daemon together with the following project (https://github.com/stoerchl/mail2mattermost).
With `mail2mattermost` it is able to save received email attachments to a directory and show them in a Mattermost channel.
It is then possible to select a specific file inside the Mattermost chanel, which should be submitted to the cuckoo sandbox.
This submission can easily be made using the slash command.

### Installation and Configuration

All needed dependencies can be installed using the following command:

```sh
pip3 install -r requirements.txt
```

All needed configuration have to be made inside the file `mattermost2cuckoo.conf`.
If the daemon runs on the same host as Mattermost then `localhost` has to be entered to `AllowedUntrustedInternalConnections` inside the Mattermost `config.cfg`.

### Usage

To start the daemon the following command can be used.

```sh
python3 mattermost2cuckoo.py start mattermost2cuckoo.conf
```

To stop or restart the daemon the corresponding keywords are available. (stop, restart)

License
----
GNU GPLv3
