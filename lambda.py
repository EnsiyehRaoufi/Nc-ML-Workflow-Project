#first lambda function for getting images

import json
import boto3
import base64

s3 = boto3.client('s3')

def lambda_handler(event, context):
    """A function to serialize target data from S3"""

    # Get the s3 address from the Step Function event input
    key = event["s3_key"]
    bucket = event["s3_bucket"]

    # Download the data from s3 to /tmp/image.png
    #download_path = "/tmp/image.png"
    data = s3.get_object(Bucket=bucket, Key=key)
    newFile = open('/tmp/image.png','wb')
    newFile.write(data['Body'].read())
    newFile.close()
    #s3.download_file( key, download_path)
    

    # We read the data from a file
    with open("/tmp/image.png", "rb") as f:
        image_data = base64.b64encode(f.read())
 
    # Pass the data back to the Step Function
    print("Event:", event.keys())
    return {
        'statusCode': 200,
        'body': {
            "image_data": image_data,
            "s3_bucket": bucket,
            "s3_key": key,
            "inferences": []
        }
    }
    
#second lambda function for getting inferences
   
import json
import base64
import boto3

# Fill this in with the name of your deployed model
ENDPOINT = "image-classification-2022-01-10-13-34-52-408"
runtime = boto3.client('runtime.sagemaker')

def lambda_handler(event, context):

    # Decode the image data
    image = base64.b64decode(event["image_data"])

    # Instantiate a Predictor
    predict = runtime.invoke_endpoint(EndpointName=ENDPOINT, 
                                       ContentType='image/png',
                                       Body=image)
    
    # Make a prediction:
    inferences = json.loads(predict['Body'].read())
    
    # We return the data back to the Step Function    
    event["inferences"] = inferences.copy()
    return {
        'statusCode': 200,
        'body': json.dumps(event)
    }
    
    
#last lambda function for checking a confidence threshold

THRESHOLD = .93
import json

def lambda_handler(event, context):
    
    # Grab the inferences from the event
    inferences = event["inferences"]
    
    # Check if any values in our inferences are above THRESHOLD
    meets_threshold = max(inferences) > THRESHOLD
    
    # If our threshold is met, pass our data back out of the
    # Step Function, else, end the Step Function with an error
    if meets_threshold:
        pass
    else:
        raise("THRESHOLD_CONFIDENCE_NOT_MET")

    return {
        'statusCode': 200,
        'body': json.dumps(event)
    }
