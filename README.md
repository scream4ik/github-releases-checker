# Releases checker

### Motivation
These days we have a lot of external dependencies. And in good form, we should monitor new releases of external dependencies and update them


### About
Simple application check new releases from provided urls and notify about a new release in slack 

### Howto use
You can find docker-compose example. This should answer most questions

Pay attention to Github rate limits https://docs.github.com/en/developers/apps/building-github-apps/rate-limits-for-github-apps

Also, need to be set next environment variables:
```
GITHUB_REPOS=https://github.com/leachim6/hello-world,https://github.com/octocat/Hello-World
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX
CHECK_FREQUENCY=7200
```

env var `CHECK_FREQUENCY` expect value in seconds

Howto create Slack webhook url https://api.slack.com/messaging/webhooks

Dockerhub image can be found here https://hub.docker.com/r/scream4ik/releases-checker
