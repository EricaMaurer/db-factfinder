#!/bin/bash

# Setting environmental variables
function set_env {
  for envfile in $@
  do
    if [ -f $envfile ]
      then
        export $(cat $envfile | sed 's/#.*//g' | xargs)
      fi
  done
}

# Setting Environmental Variables
set_env .env version.env
DATE=$(date "+%Y-%m-%d")

function count {
  psql -d $BUILD_ENGINE -At -c "SELECT count(*) FROM $1;" | 
  while read -a count; do
  echo -e "
  \e[33m$1: $count records\e[0m
  "
  done

  ddl=$(psql -At $BUILD_ENGINE -c "SELECT get_DDL('$1') as DDL;")
  echo -e "
  \e[33m$ddl\e[0m
  "
}

# Parsing database url
function urlparse {
    proto="$(echo $1 | grep :// | sed -e's,^\(.*://\).*,\1,g')"
    url=$(echo $1 | sed -e s,$proto,,g)
    userpass="$(echo $url | grep @ | cut -d@ -f1)"
    BUILD_PWD=`echo $userpass | grep : | cut -d: -f2`
    BUILD_USER=`echo $userpass | grep : | cut -d: -f1`
    hostport=$(echo $url | sed -e s,$userpass@,,g | cut -d/ -f1)
    BUILD_HOST="$(echo $hostport | sed -e 's,:.*,,g')"
    BUILD_PORT="$(echo $hostport | sed -e 's,^.*:,:,g' -e 's,.*:\([0-9]*\).*,\1,g' -e 's,[^0-9],,g')"
    BUILD_DB="$(echo $url | grep / | cut -d/ -f2-)"
}

# Pretty print messages
function display {
  echo -e "
  \e[92m\e[1m$@\e[21m\e[0m
  "
}
