NotABot
--
Discord bot for Vectozavr server

Usage (as application)
--
Install it and start bot with token as first argument

Usage (with docker)
--
Notabot needs token in `notabot-token` secret and `notabot-var` volume to store data independent from deploys and restarts. You can download prebuilt image from `nakidai/notabot:latest` or build your own (you need to edit compose.yml with your image name then). You can't use docker compose as `compose.yml` uses external secrets, so you can deploy with stack: `docker stack deploy -c compose.yml notabot`.

Contributing (writing own extension)
--
If you want write your own extension or edit exisitng one, firstly check [Example extension](https://github.com/nakidai/NotABot/blob/master/extensions/Example/__init__.py)
