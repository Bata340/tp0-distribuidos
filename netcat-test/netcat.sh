result=$(echo "$NETCAT_MESSAGE" | nc -w 1 $SVR_CONTAINER_NAME $PORT)
echo $result | grep "$NETCAT_MESSAGE"
# TEST WILL PASS ONLY IF GREP FINDS THE NETCAT MESSAGE. IF NOT THE CODE WON'T BE 0
if test $? -eq 0
then
    echo "Netcat message is OK - Echo Server - result is: $result, and initial message: $NETCAT_MESSAGE"
else
    echo "Netcat error: Received $result and awaited $NETCAT_MESSAGE."
fi