#!/bin/bash

./search/start_server.sh 0.0.0.0 8080 &
npx serve -s dist -l 5173 &
tail -f /dev/null