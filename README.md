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

# Usage

- Launch application services:

  ```bash
  docker-compose up
  ```
