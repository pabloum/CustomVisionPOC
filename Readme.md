
# Custom Vision PoC

## About

This is a Proof of Concept (PoC) for an image recognition software. The model was trained to identify cars.

I followed these 2 tutorials from Microsoft:
- [Create Custom View Tutorial ](https://learn.microsoft.com/en-us/azure/iot-edge/tutorial-deploy-custom-vision?view=iotedge-1.4)
- [Azure IotEdge Service](https://learn.microsoft.com/en-us/training/modules/create-image-recognition-solution-iot-edge-cognitive-services/6-exercise-build-deploy-solution)

Other useful tutorials followed

- [Provision Linux device with symetric keys](https://learn.microsoft.com/en-us/azure/iot-edge/how-to-provision-single-device-linux-symmetric?view=iotedge-1.4&viewFallbackFrom=iotedge-2020-11&tabs=azure-portal%2Cubuntu)
- [Tutorial develop for linux](https://learn.microsoft.com/en-us/azure/iot-edge/tutorial-develop-for-linux?view=iotedge-1.4&tabs=csharp&pivots=iotedge-dev-cli)

## Technologies used:

- Custom Vision AI
- Azure IoT Hub
- Python 
- Docker

## How to run it 

1. Create an Azure IotEdge Device on a Linux device. 
1. Build and push the images to your Azure Container registry (this step does not require Linux). 
1. Then deploy the images on the IotEdge device. 