# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

import time
import sys
import os
import requests
import json
from azure.iot.device import IoTHubModuleClient, Message

# global counters
SENT_IMAGES = 0

# global client
CLIENT = None

# Send a message to IoT Hub
# Route output1 to $upstream in deployment.template.json
def send_to_hub(strMessage):
    message = Message(bytearray(strMessage, 'utf8'))
    CLIENT.send_message_to_output(message, "output1")
    global SENT_IMAGES
    SENT_IMAGES += 1

# Send an image to the image classifying server
# Return the JSON response from the server with the prediction result
def sendFrameForProcessing(imagePath, imageProcessingEndpoint):
    headers = {'Content-Type': 'application/octet-stream'}

    with open(imagePath, mode="rb") as test_image:
        try:
            response = requests.post(imageProcessingEndpoint, headers = headers, data = test_image)
            # printJsonResponse(imagePath, response)
            printSimplePrediction(imagePath, response)
        except Exception as e:
            print(e)
            print("No response from classification service")
            return None

    return json.dumps(response.json())

def printJsonResponse(imagePath, response):
    print("Response from classification service for image " + imagePath + ": (" + str(response.status_code) + ") " + json.dumps(response.json()) + "\n")

def printSimplePrediction(imagePath, response):
    predictions = []
    for prediction in response.json()['predictions']:
        predictions.append(prediction['probability'])
    
    streetProbability = predictions[0]
    carProbability = predictions[1]

    certainty = 0
    if streetProbability >= 0.9:
        guess = "STREET"
        certainty = streetProbability
    elif carProbability >= 0.9:
        guess = "CAR"
        certainty = carProbability
    else: 
        guess = "VERY SADLY UNKNOWN"

    isGuessRight = ""
    if ("street" in imagePath.lower() and guess == "STREET") or ("car" in imagePath.lower() and guess == "CAR"):
        isGuessRight = "THE GUESS IS FUCKING RIGHT MOTHAFOCKA"
    else:
        isGuessRight = "WARNING !!!!1 WRONG GUESS"

    print("The code is " + str(f"{certainty*100:.2f}")  + "%% sure that "  + imagePath + " is a f*cking " + guess + " ---------------->" + isGuessRight)

def get_jpg_files(folder_name):
    folder_path = os.path.join(os.path.dirname(__file__), folder_name)
    jpg_files = [file for file in os.listdir(folder_path) if file.lower().endswith(".jpg")]
    return jpg_files

def main(imagePath, imageProcessingEndpoint):
    try:
        print ( "Simulated camera module for Azure IoT Edge. Press Ctrl-C to exit." )

        try:
            global CLIENT
            CLIENT = IoTHubModuleClient.create_from_edge_environment()
        except Exception as iothub_error:
            print ( "Unexpected error {} from IoTHub".format(iothub_error) )
            return

        print ( "The sample is now sending images for processing and will indefinitely.")

        while True:
            print("\n This is the start of the iteration")
            jpg_files = get_jpg_files(imagePath)
            for image in jpg_files:
                classification = sendFrameForProcessing(image, imageProcessingEndpoint)
                if classification:
                    send_to_hub(classification)
                time.sleep(5)

    except KeyboardInterrupt:
        print ( "IoT Edge module sample stopped" )

if __name__ == '__main__':
    try:
        # Retrieve the image location and image classifying server endpoint from container environment
        # IMAGE_PATH = os.getenv('IMAGE_PATH', "")
        # IMAGE_PROCESSING_ENDPOINT = os.getenv('IMAGE_PROCESSING_ENDPOINT', "")
        IMAGE_PATH = "ImagesToClassify/"
        IMAGE_PROCESSING_ENDPOINT = "http://samplemodule/image"
    except ValueError as error:
        print ( error )
        sys.exit(1)

    if ((IMAGE_PATH and IMAGE_PROCESSING_ENDPOINT) != ""):
        main(IMAGE_PATH, IMAGE_PROCESSING_ENDPOINT)
    else: 
        print ( "PUMO Test Error: Image path or image-processing endpoint PUMO missing" )