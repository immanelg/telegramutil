# Telegram utilities
A collection of random telethon commands.
Warning: **USING THIS PROGRAM CAN RESULT IN A BAN.** Telegram often considers third-party clients as suspicious and can ban you / logout of all devices / whatever. Reviewing the code, trusting Telegram and making data backups is your responsibility.
## How to run
- Prepare .env file(s):
```sh
cp example.env .env
```

- Get API keys from [Telegram](https://my.telegram.org/apps) and configure `.env`.

- Configure `.env` with your phone and your password (optional)

- Export variables:
```sh
. .env
```

Note: The script will create a persistent `$PHONE_NUM.session` file in the current dir.

### Edit the script for your needs
To activate the virtual environment, run
```
uv sync
source .venv/bin/activate
```
### Run the script
```
uv run main.py
```

