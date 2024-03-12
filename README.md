# InterVision-Use-Case

## Summary 
This repository contains assets for services related to a demo California government services contact center.

## Lex Bot
In the 'lex-bots' directory you will find the configuration for a sample lex bot. Associated lambda is in the 'lambda' directory

### Features
- Uses Generative AI to answer general questions (Optimally would use a knowledge base vector index)
- Uses lambda to do a dynamodb data dip to verify if a vehicle registration is valid (ca_car_registrations.csv)
- For Case intent, is able to prompt and store information in slots to open a case.
- To-do: Add multi-language support


## Contact Flow
In the 'contact-flows' directory you will find JSON for a contact flow that outlines the logic for a call center.

### Features
- Connects callers with specific government service department (Drivers License, Car Registration, Unemployment, Housing Assistance, Collections)
- Supports inbound calls for any California county.
- Dynamic Menu options presented per services configured in the 'ca_county_services' DynamoDB table
- Lex bot handles voice utterance or DTMF
- Checks for closed Holiday depending on department
- Checks regular service hours and provides logic for out of regular hour's customer support
- Logic to route for voicemails when closed
- Call flow errors are sent to Customer Support
- To-do: Add multi-language support
