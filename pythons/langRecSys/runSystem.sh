#!/bin/bash

python3 langRecManager.py &
sleep 1

python3 BNFServer.py &
sleep 1

python3 IVEServer.py &
sleep 1

python download_server.py &
sleep 1

wait

