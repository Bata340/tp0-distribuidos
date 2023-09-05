FROM subfuzion/netcat
COPY ./netcat.sh /netcat.sh
ENV NETCAT_MESSAGE="TEST_MESSAGE"
ENV SVR_CONTAINER_NAME="server"
ENV PORT=12345
ENTRYPOINT ["/bin/sh"]