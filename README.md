# Collector-IHS



# Functionality

- Retry download

- Check for changes and deletes

- Delete files in IHS exports if full

- query the well header for a specific api

- query all production for a specific api

- query production in a date range for a specific api

- hash the json record and compare to existing hashs

- Persist to mongodb
    1) hash incomming json record
    2) look for existing records with the same api14 in the database
    3) if hash is found, disrgard the update
    4) if hash is NOT found, perform the update, saving the hash value with the record




















