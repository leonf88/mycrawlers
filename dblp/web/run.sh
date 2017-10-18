#!/usr/bin/env bash

cur_dir=$(dirname $0)

nohup bash -c "mongod --dbpath ${cur_dir}/../data --port 27017" &
cnpm start
