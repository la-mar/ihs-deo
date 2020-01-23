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
- customizable download schedules
- configurable well/production sets per job
- flexible and extensible parsers for common data types
- Save data to a MongoDB backend
- Built in REST API to interact data stored in MongoDB and/or download directly from IHS 

Available on <a href="https://hub.docker.com/r/driftwood/ihs">DockerHub</a>!


# Todo

- Unit Testing
- Documentation
- Process changes and deletes (nightly)
- query production in a date range for a specific api
- hash the json record and compare to existing hashs
- Distribute counties to update across the week instead of all at once
- Add example using Redis w/docker-compose
- Add Dockerfile without chamber to builds

### MongoDB Collections

- well_master_horizontal
- well_master_vertical
- well_horizontal
- well_vertical
- production_master_horizontal
- production_master_vertical
- production_horizontal
- production_vertical

# Usage

- Launch a worker container:

  ```bash
  docker run driftwood/ihs ihs run worker
  ```

- Bypass Chamber when launching container:
  ```bash
  docker run --entrypoint=ihs ihs
  ```
