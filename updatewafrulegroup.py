from __future__ import print_function
import json
import boto3
from botocore.vendored import requests

SUCCESS = "SUCCESS"
FAILED = "FAILED"

def send(event, context, responseStatus, responseData, physicalResourceId=None, noEcho=False):
    responseUrl = event['ResponseURL']

    print(responseUrl)

    responseBody = {}
    responseBody['Status'] = responseStatus
    responseBody['Reason'] = 'See the details in CloudWatch Log Stream: ' + context.log_stream_name
    responseBody['PhysicalResourceId'] = physicalResourceId or context.log_stream_name
    responseBody['StackId'] = event['StackId']
    responseBody['RequestId'] = event['RequestId']
    responseBody['LogicalResourceId'] = event['LogicalResourceId']
    responseBody['NoEcho'] = noEcho
    responseBody['Data'] = responseData

    json_responseBody = json.dumps(responseBody)

    print("Response body:\n" + json_responseBody)

    headers = {
        'content-type' : '',
        'content-length' : str(len(json_responseBody))
    }

    try:
        response = requests.put(responseUrl,
                                data=json_responseBody,
                                headers=headers)
        print("Status code: " + response.reason)
    except Exception as e:
        print("send(..) failed executing requests.put(..): " + str(e))


print('Loading function')
print('Imported Boto3 Version %s' % boto3.__version__)
api = boto3.client('waf')

def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))
    responseData={}
    if(event['RequestType'] == 'Create'):
        try:
            print("Request Type:",event['RequestType'])
            print("Processing Request based on Custom resource data")
            print("Getting Change Token")
            tokenResponse = api.get_change_token()
            webAclid = event['ResourceProperties']['WebACLId']
            rulesProperty = event['ResourceProperties']['RulesProperty']
            # Add Key Value 'Action' : 'INSERT' to rulesProperty
            rulesProperty[0]['Action'] = 'INSERT'
            # Covert Priority from string to integer
            rulesProperty[0]['ActivatedRule']['Priority'] = int(rulesProperty[0]['ActivatedRule']['Priority'])
            print(rulesProperty)
            updatedRule = api.update_web_acl(WebACLId=webAclid, ChangeToken=tokenResponse['ChangeToken'], Updates=rulesProperty)
            print("Inserting Rule Group....")
            print(updatedRule)
            responseData = {'ChangeToken': updatedRule['ChangeToken']}
            print(responseData)
            print("Sending response to custom resource")
            send(event, context, SUCCESS, responseData)
        except Exception as e:
            print('Failed to process:', e)
            send(event, context, FAILED, responseData)
    elif(event['RequestType'] == 'Delete'):
        try:
            print("Request Type:",event['RequestType'])
            print("Processing Request based on Custom resource data")
            print("Getting Change Token")
            tokenResponse = api.get_change_token()
            webAclid = event['ResourceProperties']['WebACLId']
            rulesProperty = event['ResourceProperties']['RulesProperty']
            # Add Key Value 'Action' : 'DELETE' to rulesProperty
            rulesProperty[0]['Action'] = 'DELETE'
            rulesProperty[0]['ActivatedRule']['Priority'] = int(rulesProperty[0]['ActivatedRule']['Priority'])
            print(rulesProperty)
            updatedRule = api.update_web_acl(WebACLId=webAclid, ChangeToken=tokenResponse['ChangeToken'], Updates=rulesProperty)
            print("Deleting Rule Group....")
            print(updatedRule)
            responseData = {'ChangeToken': updatedRule['ChangeToken']}
            print(responseData)
            print("Sending response to custom resource")
            send(event, context, SUCCESS, responseData)
        except Exception as e:
            print('Failed to process:', e)
            send(event, context, FAILED, responseData)
    elif (event['RequestType'] == 'Update'):
        try:
            print("Request Type:",event['RequestType'])
            print("Processing Request based on Custom resource data")
            print("Getting Change Token")
            tokenResponse = api.get_change_token()
            webAclid = event['ResourceProperties']['WebACLId']
            rulesProperty = event['OldResourceProperties']['RulesProperty']
            newrulesProperty = event['ResourceProperties']['RulesProperty']
            rulesProperty.append(newrulesProperty[0])
            # Add Key Value 'Action' : 'DELETE' to first object and 'Action' : 'INSERT' to rulesProperty to second object
            rulesProperty[0]['Action'] = 'DELETE'
            rulesProperty[1]['Action'] = 'INSERT'
            rulesProperty[0]['ActivatedRule']['Priority'] = int(rulesProperty[0]['ActivatedRule']['Priority'])
            rulesProperty[1]['ActivatedRule']['Priority'] = int(rulesProperty[0]['ActivatedRule']['Priority'])
            print(rulesProperty)
            updatedRule = api.update_web_acl(WebACLId=webAclid, ChangeToken=tokenResponse['ChangeToken'], Updates=rulesProperty)
            print("Updating Rule Group....")
            print(updatedRule)
            responseData = {'ChangeToken': updatedRule['ChangeToken']}
            print(responseData)
            print("Sending response to custom resource")
            send(event, context, SUCCESS, responseData)
        except Exception as e:
            print('Failed to process:', e)
            send(event, context, FAILED, responseData)
