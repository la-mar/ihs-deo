# ihs-deo

# Todo

- Unit Testing
- Convert environment variables to SSM Parameters

- <s>Retry download => baked into queues</s>
- Process changes and deletes (nightly)
- <s>Delete files in IHS exports if full => TODO </s>
- <s>query the well header for a specific api => implemented via the HTTP API</s>
- <s>query all production for a specific api => implemented via the HTTP API</s>
- query production in a date range for a specific api => TODO
- hash the json record and compare to existing hashs => NEEDS VALIDATION
- <s>Persist to mongodb
  1. hash incomming json record
  2. look for existing records with the same hash
  3. if hash is found, disrgard the update
  4. if hash is NOT found, perform the update, saving the hash value with the record</s>

### MongoDB Collections

- well_master_horizontal
- well_master_vertical
- well_horizontal
- well_vertical
- production_master_horizontal
- production_master_vertical
- production_horizontal
- production_vertical

![refarch](/doc/refarch.png)
