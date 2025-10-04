az containerapp env create -n actovatorBackendEnv -g actovator --location eastus

az containerapp create --name actovator-backend --resource-group actovator --environment actovatorBackendEnv --image mcr.microsoft.com/azuredocs/containerapps-helloworld:latest --ingress external --cpu 0.5 --memory 1.0Gi --system-assigned

$acrId = az acr show -n actovatorregistry -g actovator --query id -o tsv

$principalId = az containerapp show -n actovator-backend -g actovator --query identity.principalId -o tsv

az containerapp registry set --name actovator-backend --resource-group actovator --server actovatorregistry.azurecr.io --identity system

az ad sp create-for-rbac --name "github-action-sp" --role contributor --scopes /subscriptions/d52146ae-f113-4eaa-807f-037c91531fe6/resourceGroups/actovator --sdk-auth
