for Windows:

- for excluding game from task: add '__' in name of file (exbpl: '__1winroken.py')
- to run browsers in the background mode: '__const.py': 'HEADLESS = True'
- edit 'cron_configs' of games to change frequency and time of starting (https://arq-docs.helpmanual.io/).

1. install redis (https://github.com/redis-windows/redis-windows)
2. 'redis-server' (start redis server)
3. 'python3 -m venv .venv'
4. '.venv/bin/activate'
5. 'pip install -r requirements.txt'
6. 'playwright install' (https://playwright.dev/python/docs/intro)
7. 'python fu.py' (saving storage state of browser)
8. 'python main.py'

The script was created for fun, and hardly follows the rules of good coding!)
