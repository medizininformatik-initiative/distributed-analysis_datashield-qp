#!/bin/bash

#
## Make sure conf folder is available
#if [ ! -d $OPAL_HOME/conf ]
#    then
#    mkdir -p $OPAL_HOME/conf
#    cp -r /usr/share/opal/conf/* $OPAL_HOME/conf
#fi
#
#
#if [ -z "$AGATE_PORT_8444_TCP_ADDR" -a -e /opt/opal/bin/first_run.sh ]
#    then
#    echo "Disabling Agate as Agate env var not set..."
#    sed s@#org.obiba.realm.url=https://localhost:8444@org.obiba.realm.url=@g $OPAL_HOME/conf/opal-config.properties > /tmp/opal-config.properties
#	  mv -f /tmp/opal-config.properties $OPAL_HOME/conf/opal-config.properties
#fi
#
## check if 1st run. Then configure properties.
#if [ -n "$AGATE_PORT_8444_TCP_ADDR" -a -e /opt/opal/bin/first_run.sh ]
#    then
#    echo "Configuring AGATE..."
#    sed s/localhost:8444/$AGATE_PORT_8444_TCP_ADDR:$AGATE_PORT_8444_TCP_PORT/g $OPAL_HOME/conf/opal-config.properties | \
#    sed s/#org.obiba.realm.url/org.obiba.realm.url/g > /tmp/opal-config.properties
#	mv -f /tmp/opal-config.properties $OPAL_HOME/conf/opal-config.properties
#fi
#
#if [ -n "$RSERVER_PORT_6312_TCP_ADDR" -a -e /opt/opal/bin/first_run.sh ]
#    then
#    echo "Setting R server host to $RSERVER_PORT_6312_TCP_ADDR..."
#    sed s/#org.obiba.opal.Rserve.host=/org.obiba.opal.Rserve.host=$RSERVER_PORT_6312_TCP_ADDR/g $OPAL_HOME/conf/opal-config.properties > /tmp/opal-config.properties
#	mv -f /tmp/opal-config.properties $OPAL_HOME/conf/opal-config.properties
#fi
#
#if [ -e /opt/opal/bin/set_password.sh ]
#    then
#    /opt/opal/bin/set_password.sh
#    mv /opt/opal/bin/set_password.sh /opt/opal/bin/set_password.sh.done
#fi
#
## Start opal
#if [ -e /opt/opal/bin/first_run.sh ]
#    then
#    # check if 1st run. Then configure database and datashield.
#	/usr/share/opal/bin/opal &
#
#	# Wait for the opal server to be up and running
#	echo "Startup opal and install spss import pluging..."
#	until opal rest -o https://localhost:8443 -u administrator -p $OPAL_ADMINISTRATOR_PASSWORD -m GET /system/databases &> /dev/null
#	do
#	    sleep 5
#	done
#
#    # install spss plugin
#    echo "Installing spss plugin..."
#    echo '' | opal rest --opal https://localhost:8443 -u administrator -p $OPAL_ADMINISTRATOR_PASSWORD --content-type 'application/json' -m POST "/plugins?name=opal-datasource-spss"
#
#
#    echo "Restarting Opal and waiting for it to be ready..."
#    kill `pgrep -f bin/opal`
#    kill `pgrep -f opal/lib`
#    /usr/share/opal/bin/opal &
#
#	until opal rest -o https://localhost:8443 -u administrator -p $OPAL_ADMINISTRATOR_PASSWORD -m GET /system/databases &> /dev/null
#	do
#	    sleep 5
#	done
#
#    /opt/opal/bin/first_run.sh
#    mv /opt/opal/bin/first_run.sh /opt/opal/bin/first_run.sh.done
#
#    tail -f $OPAL_HOME/logs/opal.log
#
#else
#	/usr/share/opal/bin/opal
#fi


#!/bin/bash

# utils
set_property () {
  field=$1
  value=$2
  file=$3
  tmpfile=/tmp/`basename ${file}`
  if grep -q ${field} ${file}
  then
    sed -r "s#${field}\s*=.*#${field}=${value}#g" ${file} | \
      sed -r "s/^#${field}=/${field}=/g" > ${tmpfile}
  else
    cat ${file} > ${tmpfile}
    echo "${field} = ${value}" >> ${tmpfile}
  fi
  mv ${tmpfile} ${file}
}

# Legacy parameters
if [ -n "$AGATE_PORT_8444_TCP_ADDR" ] ; then AGATE_HOST=$AGATE_PORT_8444_TCP_ADDR ; fi
if [ -n "$AGATE_PORT_8444_TCP_PORT" ] ; then AGATE_PORT=$AGATE_PORT_8444_TCP_PORT ; fi
if [ -n "$RSERVER_PORT_6312_TCP_ADDR" ] ; then RSERVER_HOST=$RSERVER_PORT_6312_TCP_ADDR ; fi

# Make sure conf folder is available
if [ ! -d $OPAL_HOME/conf ]
then
  echo "Preparing default conf in $OPAL_HOME ..."
  mkdir -p $OPAL_HOME/conf
  cp -r /usr/share/opal/conf/* $OPAL_HOME/conf
  if [ -f /opt/opal/bin/first_run.sh.done ]
  then
    mv /opt/opal/bin/first_run.sh.done /opt/opal/bin/first_run.sh
  fi
fi

# Install default plugins
if [ ! -d $OPAL_HOME/plugins ]
then
  echo "Preparing default plugins in $OPAL_HOME ..."
  mkdir -p $OPAL_HOME/plugins
  cp -r /usr/share/opal/plugins/* $OPAL_HOME/plugins
fi

# check if 1st run. Then configure properties.
if [ ! -f /opt/opal/bin/first_run.sh.done ]
then

  #
  # Agate
  #

  if [ -n "$AGATE_HOST" ]
  then
    echo "Setting Agate connection..."
    AGATE_URL=$AGATE_HOST
    if [ -n "$AGATE_PORT" ]
    then
      AGATE_URL="$AGATE_HOST:$AGATE_PORT"
    fi
    if [[ ! "$AGATE_URL" =~ ^http ]]
    then
      AGATE_URL="https://$AGATE_URL"
    fi
    set_property "org.obiba.realm.url" "$AGATE_URL" "$OPAL_HOME/conf/opal-config.properties"
  else
    echo "Disabling default Agate setting as AGATE_HOST is not defined..."
    set_property "org.obiba.realm.url" "" "$OPAL_HOME/conf/opal-config.properties"
  fi

  #
  # Rock R server
  #

  if [ -n "$ROCK_HOSTS" ]
  then
    echo "Setting Rock R server connection..."
    set_property "apps.discovery.rock.hosts" "$ROCK_HOSTS" "$OPAL_HOME/conf/opal-config.properties"
  fi

  if [ -n "$ROCK_ADMINISTRATOR_USER" ] && [ -n "$ROCK_ADMINISTRATOR_PASSWORD" ]
  then
    echo "Setting Rock R server administrator credentials..."
    set_property "rock.default.administrator.username" "$ROCK_ADMINISTRATOR_USER" "$OPAL_HOME/conf/opal-config.properties"
    set_property "rock.default.administrator.password" "$ROCK_ADMINISTRATOR_PASSWORD" "$OPAL_HOME/conf/opal-config.properties"
  fi

  if [ -n "$ROCK_MANAGER_USER" ] && [ -n "$ROCK_MANAGER_PASSWORD" ]
  then
    echo "Setting Rock R server manager credentials..."
    set_property "rock.default.manager.username" "$ROCK_MANAGER_USER" "$OPAL_HOME/conf/opal-config.properties"
    set_property "rock.default.manager.password" "$ROCK_MANAGER_PASSWORD" "$OPAL_HOME/conf/opal-config.properties"
  fi

  if [ -n "$ROCK_USER_USER" ] && [ -n "$ROCK_USER_PASSWORD" ]
  then
    echo "Setting Rock R server user credentials..."
    set_property "rock.default.user.username" "$ROCK_USER_USER" "$OPAL_HOME/conf/opal-config.properties"
    set_property "rock.default.user.password" "$ROCK_USER_PASSWORD" "$OPAL_HOME/conf/opal-config.properties"
  fi

  #
  # R repositories
  #

  if [ -n "$R_REPOS" ]
  then
    set_property "org.obiba.opal.r.repos" "$R_REPOS" "$OPAL_HOME/conf/opal-config.properties"
  fi

  #
  # R server (legacy)
  #
  
  if [ -n "$RSERVER_HOST" ]
  then
    echo "Setting R server connection..."
    set_property "org.obiba.opal.Rserve.host" "$RSERVER_HOST" "$OPAL_HOME/conf/opal-config.properties"
  fi

fi

#
# Administrator password
#

if [ ! -f /opt/opal/bin/set_password.sh.done ]
then
  echo "Setting password..."
  /opt/opal/bin/set_password.sh
  mv /opt/opal/bin/set_password.sh /opt/opal/bin/set_password.sh.done
fi

# Start opal
if [ -f /opt/opal/bin/first_run.sh.done ]
then
  echo "Starting Opal..."
  /usr/share/opal/bin/opal
else
  echo "Starting Opal before first run script..."
  # check if 1st run. Then configure database and datashield.
  /usr/share/opal/bin/opal &
  # Wait for the opal server to be up and running
  echo "Waiting for Opal to be ready..."
  until opal rest -o https://localhost:8443 -u administrator -p $OPAL_ADMINISTRATOR_PASSWORD -m GET /system/databases &> /dev/null
  do
    sleep 5
  done
  echo "First run setup..."
  /opt/opal/bin/first_run.sh
  mv /opt/opal/bin/first_run.sh /opt/opal/bin/first_run.sh.done
  ls /srv/plugins
  tail -f $OPAL_HOME/logs/opal.log
fi