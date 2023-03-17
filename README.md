# MQTT2Postgres

Simple script to get MQTT sensor data and store it in a PostgreSQL database. Runs in a container.

Features:
- probably bugs
- tailored to my own needs, not yours
- hardcoded credentials (did I accidentally publish them in this repo? So be it...)
- runs locally, no security in mind
- should be reconnecting if mqtt broker or db goes down. limited testing

Setting up the database should be done manually, before running this.

I strongly advise you to use Timescale if you're going to store time series in PostgreSQL.

### DISCLAIMER

Dockerfiles and Python are not my thing. I just fiddle until it works.
