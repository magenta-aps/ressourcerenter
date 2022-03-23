# Ressourcerenter


### Test-overførsel til Prisme
For at teste overførsel til Prisme fra et lokalt udviklingsmiljø, kan følgende 
miljøvariable sættes i docker-compose.override.yml:

    PRISME_PUSH_HOST=172.17.0.1
    PRISME_PUSH_PORT=2222
    PRISME_PUSH_USER=<brugernavn fra bitwarden (Grønland/Skattestyrelsen/KAS Prisme 10Q password)>
    PRISME_PUSH_PASSWORD=<password fra bitwarden>
    PRISME_PUSH_DEST_PROD_AVAILABLE=false

Med VPN åben skal der også åbnes en tunnel med:

    ssh -L 172.17.0.1:2222:sftp.erp.gl:22 larsp@10.240.76.76

Således routes trafik fra containeren over til hosten på port 2222, og videre 
gennem tunnellen til ressourcerenter-testserveren og til `sftp.erp.gl`
