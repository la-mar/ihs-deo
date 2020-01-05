# ihs-deo

<div style="text-align:center;">
  <table >
    <tr>
      <a href="https://codeclimate.com/github/la-mar/ihs-deo/maintainability"><img src="https://api.codeclimate.com/v1/badges/4e312abd1b377f0a38b0/maintainability" /></a>
      <a href="https://codeclimate.com/github/la-mar/ihs-deo/test_coverage"><img src="https://api.codeclimate.com/v1/badges/4e312abd1b377f0a38b0/test_coverage" /></a>
      <a href="https://codecov.io/gh/la-mar/ihs-deo">
        <img src="https://codecov.io/gh/la-mar/ihs-deo/branch/master/graph/badge.svg" />
      </a>
      <a href="(https://circleci.com/gh/la-mar/ihs-deo">
        <img src="https://circleci.com/gh/la-mar/ihs-deo.svg?style=svg" />
      </a>
    </tr>
  </table>
</div>

# Todo

- Unit Testing
- Documentation
- Process changes and deletes (nightly)
- query production in a date range for a specific api => TODO
- hash the json record and compare to existing hashs => NEEDS VALIDATION
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
  docker run ihs ihs run worker
  ```

- Bypass Chamber when launching container:
  ```bash
  docker run --entrypoint=ihs ihs
  ```
