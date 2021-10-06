docker exec --user=root poll_server bash -c "cd /usr/local/share/ca-certificates && update-ca-certificates"

docker exec --user=root ds_simple_client bash -c "cd /usr/local/share/ca-certificates && update-ca-certificates"