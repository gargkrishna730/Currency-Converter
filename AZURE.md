# Azure App Service Deployment using Container


## To build and push a Docker Image
```bash
docker buildx build --platform linux/amd64,linux/arm64 -t <REGISTRY_URL>/<REPOSITORY_NAME>:<TAG> --push .
```

## Create a WebApp in Azure

### 1. Login into Azure from Azure CLI
```bash
az login
```

### 2. Create App Service Plan
```bash
az appservice plan create --name <app-service-plan-name> --resource-group <resource-group-name> --sku S1 --is-linux
```

### Example
```bash
az appservice plan create --name app-service-container --resource-group gpu-poc --sku F1 --is-linux
```

### 3. Create App Service
```bash
az webapp create --name <app-name> --resource-group <resource-group-name> --plan <app-service-plan-name> --deployment-container-image-name <image-name-and-tag>
```

### Example
```bash
az webapp create --name app-service-container --resource-group gpu-poc --plan app-service-container --deployment-container-image-name gargkrishna730/currencyconverter:jaspreetappservice
```
