import json
import boto3

def elicit_intent(intent, slots, message):
        
    response = {
        "sessionState": {
            "dialogAction": {
                "slotToElicit": slots,
                "type": "ElicitSlot"
            },
            "intent": {
                "name": intent,
                "slots": slots
            }
        }
    }
    
    return response
    

def is_valid_california_plate(plate):
    """
    This function checks if a string is a valid California license plate.
    
    Args:
      plate: The string to validate.
    
    Returns:
      True if the plate is valid, False otherwise.
    """
    # Check for basic format (7 characters)
    if len(plate) != 7:
        return False
    
    # Check first character is a letter
    if not plate[0].isalpha():
        return False
    
    # Check remaining 6 characters alphanumeric
    for char in plate[1:]:
        if not char.isalnum():
          return False
    
    # Additional California specific checks
    # California plates start with 1-8 or A-Z (excluding I, O, Q)
    #if not (plate[0].isdigit(1, 8) or plate[0].isalpha() and plate[0] not in "IOQ"):
    #    return False
    
    # No restrictions on the following 3 characters
    # Last 3 characters can be alphanumeric
    for char in plate[4:]:
        if not char.isalnum():
          return False

    return True


def call_bedrock(question):
    
    client_bedrock = boto3.client('bedrock-runtime')

    prompt_data= str(question)
        
    #formatting body for Jurassic models
    body = json.dumps({"prompt": prompt_data, "maxTokens":500})
    
    #formatting body for claude
    #body = json.dumps({"prompt": "Human:"+prompt_data+"\nAssistant:", "max_tokens_to_sample":700})
    
    #set model
    modelId='ai21.j2-mid-v1'
    #modelId='amazon.titan-text-lite-v1'
    accept = 'application/json'
    contentType = 'application/json'
    
    #invoke model
    response = client_bedrock.invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)
    response_body = json.loads(response.get('body').read())
    #print(json.dumps(response_body))
    answer = response_body['completions'][0]['data']['text']
    
    return(response_body['completions'][0]['data']['text'])
    

def get_plate_status(plate_id):
    
    client_dynamodb = boto3.client('dynamodb')
    
    print(plate_id)
    response = client_dynamodb.get_item(
        TableName = 'ca_car_registrations',
        Key={"plate_id": {"S": plate_id}}
    )
    
    print(response)
    
    #{'Item': {'plate_id': {'S': 'ABC1234'}, 'expired': {'BOOL': False}}
    if "Item" in response:
        if response['Item']['expired']['BOOL'] == False: 
            print('valid')
            return False
        else:
            return True
    else:
        return True
            

def validate_slot(intent, slots, customer_text):
    
    if intent == 'RegistrationStatus':
        if not slots['PlateNumber']:
        
            return{
                'isValid': False,
                'invalidSlot': 'PlateNumber',
                'message': 'Please enter a valid license plate number.'
            }
        else:
            
            plate_number = slots['PlateNumber']['value']['originalValue']
            plate_format = is_valid_california_plate(plate_number)
            
            if plate_format:
                expired = get_plate_status(plate_number)
                
                if not expired:
                    message = 'Registration is valid'
                else:
                    message = 'Registration is expired'
            else:
                message = 'Not a valid California license plate!'
            
            return{
                'isValid': True,
                'invalidSlot': 'PlateNumber',
                'message': message
            }
            
    if intent == 'Help':
        
        answer = call_bedrock(customer_text)
        print(answer)
        
        
        
        return{
            'isValid': False,
            'invalidSlot': 'Question',
            'message': answer
        }
    
    
def lambda_handler(event, context):
    print(json.dumps(event)) 
    
    bot = event['bot']['name']
    slots = event['sessionState']['intent']['slots']
    intent = event['sessionState']['intent']['name']
    customer_text = event['inputTranscript']
    
    print(bot)
    print(slots)
    print(intent)
    print(customer_text)
    
    
    order_validation_result = validate_slot(intent, slots, customer_text)


    if event['invocationSource'] == 'DialogCodeHook':
        if order_validation_result['isValid'] == False:
            if 'message' in order_validation_result:
                response = {
                    "sessionState": {
                        "dialogAction": {
                            "slotToElicit": order_validation_result['invalidSlot'],
                            "type": "ElicitSlot"
                        },
                        "intent": {
                            "name": intent,
                            "slots": slots
                        }
                    },
                    "messages": [
                        {
                            "contentType": "PlainText",
                            "content": order_validation_result['message']
                        }
                    ]
                }
            else:
                response = {
                    "sessionState": {
                        "dialogAction": {
                            "slotToElicit": order_validation_result['invalidSlot'],
                            "type": "ElicitSlot"
                        },
                        "intent": {
                            "name": intent,
                            "slots": slots
                        }
                    }
                }
        else:
            response = {
                "sessionState": {
                    "dialogAction": {
                        "type": "Delegate"
                    },
                    "intent": {
                        'name': intent,
                        'slots': slots
                    }
                }
            }

    if event['invocationSource'] == 'FulfillmentCodeHook':
        response = {
            "sessionState": {
                "dialogAction": {
                    "type": "Close"
                },
                "intent": {
                    "name": intent,
                    "slots": slots,
                    "state": "Fulfilled"
                }

            },
            "messages": [
                {
                    "contentType": "PlainText",
                    "content": order_validation_result['message']
                }
            ]
        }

    print(response)
    return response

