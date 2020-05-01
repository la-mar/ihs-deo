# ihs-deo

Project to automate data sourcing and validation from IHS Energy's Energy Web Services.

<div style="text-align:center;">
  <table >
    <tr>
      <a href="https://codecov.io/gh/la-mar/ihs-deo">
        <img src="https://codecov.io/gh/la-mar/ihs-deo/branch/master/graph/badge.svg" />
      </a>
      <a href="(https://circleci.com/gh/la-mar/ihs-deo">
        <img src="https://circleci.com/gh/la-mar/ihs-deo.svg?style=svg" />
      </a>
            <a href="https://hub.docker.com/r/driftwood/ihs">
        <img src="https://img.shields.io/docker/pulls/driftwood/ihs.svg" />
      </a>
    </tr>
  </table>
</div>

Features include:

- Keep your local dataset in sync with IHS
- Scheduled well & production downloads from IHS data services
- Highly configurable scheduled tasks:

  - download by county, API list, or by producing entity ID
  - download using your existing queries stored on the IHS website

- Parses and normalizes IHS data
- Backed by MongoDB
- Built in REST API

Available on <a href="https://hub.docker.com/r/driftwood/ihs">DockerHub</a>!

# Issues

- Pagination mixin is broken. It doesnt seem to respect the passed query string
- Indexes are currently managed external to the app. These need to be ported into
  the model definitions now that they are somewhat stable.

# Todo

- Documentation
- Improve API error logging
- Add API endpoints for CLI
- Unit Testing
- Documentation
- Process changes and deletes (nightly)
- query production in a date range for a specific api?
- add endpoint: add/remove county definition (name, state_code, county_code)
- scheduled task: cleanup stale wells
- mechanism to stop submitting exports if remote capacity is full

# Usage

- Launch application services:

  ```bash
  docker-compose up
  ```

# Example environment variables

```env

IHS_URL=http://www.ihsenergy.com
IHS_USERNAME=<your_ihs_password>
IHS_PASSWORD=<your_ihs_username>
IHS_APP_KEY=<provided_by_ihs>

DATABASE_URI=mongodb://docker.for.mac.host.internal:27017
CELERY_BROKER_URL=redis://redis:6390/1
IHS_CRON_URL=redis://redis:6390/0
GUNICORN_CMD_ARGS="--bind=0.0.0.0:80 --log-level=info --name=gunicorn-ihs --timeout=120 --graceful-timeout=120 --worker-class=gevent --workers=3"
```
