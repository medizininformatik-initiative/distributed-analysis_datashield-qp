FROM python:3.9

RUN pip install ds-common==0.0.3
RUN pip install requests==2.22.0
COPY . /home/dspoll/ds_poll
RUN groupadd -r dspoll && useradd -r -s /bin/false -g dspoll dspoll
VOLUME /home/dspoll/ds_poll/logging
RUN chown -R dspoll:dspoll /home/dspoll

WORKDIR /home/dspoll/ds_poll

COPY docker-entrypoint.sh /usr/local/bin/

USER dspoll

ENTRYPOINT ["docker-entrypoint.sh"]