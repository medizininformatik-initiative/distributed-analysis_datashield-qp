FROM python:3.9

COPY . /home/dsqueue/ds_queue
RUN mkdir -p /home/dsqueue/ds_queue/logging
RUN pip install ds-common==0.0.3

RUN groupadd -r dsqueue && useradd -r -s /bin/false -g dsqueue dsqueue
RUN chown -R dsqueue:dsqueue /home/dsqueue

WORKDIR /home/dsqueue/ds_queue

COPY docker-entrypoint.sh /usr/local/bin/

USER dsqueue

ENTRYPOINT ["docker-entrypoint.sh"]
