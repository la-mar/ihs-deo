# ihs-deo

# Functionality

- Retry download => baked into queues

- Check for changes and deletes => TODO

- Delete files in IHS exports if full => TODO

- query the well header for a specific api => implemented via the HTTP API

- query all production for a specific api => implemented via the HTTP API

- query production in a date range for a specific api => TODO

- hash the json record and compare to existing hashs => TODO

- Persist to mongodb
  1. hash incomming json record
  2. look for existing records with the same hash
  3. if hash is found, disrgard the update
  4. if hash is NOT found, perform the update, saving the hash value with the record

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
