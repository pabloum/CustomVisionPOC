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

# GLOBAL RETRUES
retries = 10

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
            for retry in range(1,retries):
                response = requests.post(imageProcessingEndpoint, headers = headers, data = test_image)
                if response.status_code == 200:
                    # printJsonResponse(imagePath, response)
                    printSimplePrediction(imagePath, response)
                    return json.dumps(response.json())
        except Exception as e:
            print(e)
            print("No response from classification service")
            return None

    return None

def printJsonResponse(imagePath, response):
    print("Response from classification service for image " + imagePath + ": (" + str(response.status_code) + ") " + json.dumps(response.json()) + "\n")

def printSimplePrediction(imagePath, response):
    predictions = []
    for prediction in response.json()['predictions']:
        predictions.append(prediction['probability'])
    
    streetProbability = predictions[0]
    carProbability = predictions[1]

    mostLikelyTag = getMostLikelyTag(streetProbability, carProbability)
    certainty = max([streetProbability, carProbability])
    guessCorrectness = getGuessCorrectness(imagePath, mostLikelyTag)

    print("The code is " + str(f"{certainty*100:.2f}")  + "%% sure that "  + imagePath + " is a f*cking " + mostLikelyTag +  guessCorrectness)

def getMostLikelyTag(streetProbability, carProbability):
    if streetProbability >= 0.9:
        return "STREET"
    elif carProbability >= 0.9:
        return "CAR"
    else: 
        return "VERY SADLY UNKNOWN"

def getGuessCorrectness(imagePath, guess):
    if ("street" in imagePath.lower() and guess == "STREET") or ("car" in imagePath.lower() and guess == "CAR"):
        return ""
    else:
        return "----------------> WARNING !!!!1 WRONG GUESS"

def get_jpg_files(folder_name):
    folder_path = os.path.join(os.path.dirname(__file__), folder_name)
    jpg_files = [file for file in os.listdir(folder_path) if file.lower().endswith(".jpg")]
    jpg_files.sort()
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
                time.sleep(1)

    except KeyboardInterrupt:
        print ( "IoT Edge module sample stopped" )

if __name__ == '__main__':
    try:
        # Retrieve the image location and image classifying server endpoint from container environment
        IMAGE_PATH = os.getenv('IMAGE_PATH', "")
        IMAGE_PROCESSING_ENDPOINT = os.getenv('IMAGE_PROCESSING_ENDPOINT', "")
    except ValueError as error:
        print ( error )
        sys.exit(1)

    if ((IMAGE_PATH and IMAGE_PROCESSING_ENDPOINT) != ""):
        main(IMAGE_PATH, IMAGE_PROCESSING_ENDPOINT)
    else: 
        print ( "Test Error: Image path or image-processing endpoint missing" )