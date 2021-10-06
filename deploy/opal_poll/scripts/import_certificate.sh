#!/bin/bash


docker exec datashield_opal bash -c "cd /auth && chmod +x import_certificate.sh && ./import_certificate.sh"
