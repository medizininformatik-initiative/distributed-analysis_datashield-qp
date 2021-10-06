FROM obiba/opal:4.2
RUN chmod +x /usr/share/opal/bin/opal

COPY opal_with_init/bin /opt/opal/bin
COPY opal_with_init/data /opt/opal/data
COPY opal_with_init/testdata /testdata

RUN chmod +x -R /opt/opal/bin
RUN adduser --system --home $OPAL_HOME --no-create-home --disabled-password opal
RUN chown -R opal /opt/opal
RUN apt update
RUN apt install -y python3-pip && pip install requests
VOLUME /srv

# https and http
EXPOSE 8443 8080

# Define default command.
COPY opal_with_init/docker-entrypoint.sh /
COPY opal_with_init/scripts /miracum
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["app"]
