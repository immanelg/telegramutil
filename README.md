# Telegram utilities
Warning: **Using this program can result in a ban.** Telegram often considers third-party clients as suspicious and can ban you / logout of all devices / whatever. Reviewing the code, trusting Telegram and making data backups is your responsibility.
## How to prepare secrets
- Get API keys from [Telegram](https://my.telegram.org/apps)
- Get phone and password 
- `cp example.env test-account.env`
- Configure `test-account.env`
- `. test-account.env`
## Commands
### Export channel list
```sh
uv run main.py -L >channels.list
```
### Import channel list
```sh
cat channels.list | uv run main.py -S
```
