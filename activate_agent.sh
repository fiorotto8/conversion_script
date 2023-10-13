#for the oidc agent on the cloud
#!/bin/bash

#export IAM_CLIENT_ID="18b94299-49fd-4230-8ddc-474b209b2693"
#export IAM_CLIENT_SECRET="AKlCP9WI6O4R1F9pXVD1enGdZQPYPuAYGsbvggCosVpRABqHis50qQEiScDYazYsdQkKkc7Dc-d060DmmKe9kTQ"
#export REFRESH_TOKEN="eyJhbGciOiJub25lIn0.eyJqdGkiOiI0NzY2YjhlYS1jZjg2LTRjNTEtYmZkYy1hMDRmMDE2YmUyMzQifQ."

export REFRESH_TOKEN="eyJhbGciOiJub25lIn0.eyJqdGkiOiIxMDU2NDFhZS0zODlhLTQ3NWYtYTgyYi1jN2FmNjk0NjE1YTcifQ."
    export IAM_CLIENT_SECRET="APABvAtqWkRUH3GQfLiTJzBGiqFpOV7KMmdZtLOtxZgTo6QrvWYI-8ZAYAfHiavFst5jmuKQe-ffofr4Au0eJAg"
    export IAM_CLIENT_ID="4b53b391-e7a0-42bb-be5d-a6109c1ae4c5"
export IAM_SERVER=https://iam.cloud.infn.it/
unset OIDC_SOCK; unset OIDCD_PID; eval `oidc-keychain`
oidc-gen --client-id $IAM_CLIENT_ID --client-secret $IAM_CLIENT_SECRET --rt $REFRESH_TOKEN --manual --issuer $IAM_SERVER --pw-cmd="echo pwd" --redirect-uri="edu.kit.data.oidc-agent:/redirect http://localhost:29135 http://localhost:8080 http://localhost:4242" --scope "openid email wlcg wlcg.groups profile offline_access" infncloud-wlcg


#oidc-gen --client-id $IAM_CLIENT_ID --client-secret $IAM_CLIENT_SECRET --rt $REFRESH_TOKEN --manual --issuer $IAM_SERVER --pw-cmd="echo pwd"  --scope "openid email wlcg wlcg.groups profile offline_access" infncloud-wlcg
#export IAM_CLIENT_ID="341bd918-43b5-4d52-b521-06ce793eb4ab"
#export IAM_CLIENT_SECRET="XDKH3ESOWvtJ8SynNTHbv_EoRaq0jd3o7xWUPg5oHk7YBLpFsKtgRg9CTeWLLYicxOUBydaKXN1NNAK_PEOnCQ"
#export REFRESH_TOKEN="eyJhbGciOiJub25lIn0.eyJqdGkiOiI5M2E2NGRjYS02ZTQ1LTRiZTQtOTQ2OS00YzhkMTIyOWVkY2MifQ."
