# WAFrulegroupCustomResource
CloudFormation Custom Resource to insert, update and delete WAF rule group to a WAF WebACL

## Use Case

When you purchased a pre-configured WAF RuleGroup in the AWS Marketplace and like to add the purchased managed rules to AWS Web Application Firewall (WAF) Web Access Control List (ACL) via CloudFormation.

## Description

At the moment of writing, the API call to subscribe managed WAF rule group is not yet supported in CloudFormation and is only available with AWS CLI/SDK and console.  This is a solution which uses a Lambda backed Custom Resource to insert, update and delete WAF rule group to a WAF WebACL in a CloudFormation stack.

**There are 3 main resources types to be constructed in subscribe_rulegroup.yaml template:**

a) Custom::Resource (AssociateWAFRulesGroup) : Custom resource which passes WebACLid, RulesProperty to ServiceToken which reference to the Lambda fucntion.

b) AWS::Lambda::Function (WAFRuleGroupLambda): Lambda code which will receive the "ResourceProperties" via Custom Resource and process it using AWS "WebACLUpdate" API call and INSERT, UPDATE or DELETE rule group to WAF web acl as a custom resource.

c) AWS::IAM::Role (LambdaExecutionRole): Required Lambda basic permissions to create and write cloud watch logs along with appropriate "WAF" IAM permissions (required by the Lambda function).

The code zipped file has to be uploaded to an S3 bucket in the same region as where you CloudFormation stack is created.

      Code:
        S3Bucket: <bucket_name>
        S3Key: updatewafrulegroup.py.zip

**Walk-through on what the code updatewafrulegroup.py does:**

CREATE logic:

1. Get ChangeToken and stored as variable.  A change token is mandatory to perform any change in AWS WAF objects
2. "RuleProperty" - a list of objects as defined by "AssociateWAFRulesGroup" resource in the above CFN template snippet is passed to Lambda function.  Below an example of the RuleProperty(list):
        [{'ActivatedRule': {'Type': 'GROUP', 'Priority': '3', 'RuleId': 'f65b84fc-e4da-494f-9c1b-xxxxxxxxxxxx', 'OverrideAction': {'Type': 'COUNT'}}}]
3. 'Action' : 'INSERT' key value pair is appended to rulesProperty list/array.
        [{'Action': 'INSERT', 'ActivatedRule': {'Type': 'GROUP', 'Priority': '3', 'RuleId': 'f65b84fc-e4da-494f-9c1b-946859cc2abd', 'OverrideAction': {'Type': 'COUNT'}}}]
4. rulesProperty[0]['ActivatedRule']['Priority'] needs to be type INT
        [{'Action': 'INSERT', 'ActivatedRule': {'Type': 'GROUP', 'Priority': 3, 'RuleId': 'f65b84fc-e4da-494f-9c1b-946859cc2abd', 'OverrideAction': {'Type': 'COUNT'}}}]
5. The "rulesProperty" list is then consumed by update_web_acl api call method and apply the WAF web rule insertion to the WAF web ACL

UPDATE logic:

1. Get ChangeToken and stored as variable.  A change token is mandatory to perform any change in AWS WAF objects
2. ['OldResourceProperties']['RuleProperty'] - The existing Rule Group Property that was created/updated by CloudFormation as previously declared in "AssociateWAFRulesGroup" resource in the above CFN template snippet.  Below an example of an existing RuleProperty:
        [{'ActivatedRule': {'Type': 'GROUP', 'Priority': '3', 'RuleId': 'f65b84fc-e4da-494f-9c1b-xxxxxxxxxxxx', 'OverrideAction': {'Type': 'COUNT'}}}]
3. ['ResourceProperties']['RuleProperty'] - The new Rule Group Property to be updated by CloudFormation for this stack update action as declared in "AssociateWAFRulesGroup" resource in the above CFN template snippet.  Below an example of a new RuleProperty:
        [{'ActivatedRule': {'Type': 'GROUP', 'Priority': '3', 'RuleId': 'f65b84fc-e4da-494f-9c1b-xxxxxxxxxxxx', 'OverrideAction': {'Type': 'NONE'}}}]
4. Construct rulesProperty by appending newrulesProperty so it becomes a list of 2 json objects.  The first object is the existing oldProperty and the second object is the newProperty to be applied
5. 'Action' : 'DELETE' key value pair is appended to first object in rulesProperty list.
6. 'Action' : 'INSERT' key value pair is appended to second object in rulesProperty list.
7. rulesProperty[0]['ActivatedRule']['Priority'] and rulesProperty[1]['ActivatedRule']['Priority'] need to be type INT
8. The "rulesProperty" list is then consumed by update_web_acl api call method and apply the WAF web rule deletion to the first object in rulesProperty and insert the second object in rulesProperty to the WAF web ACL

The DELETE logic follows the same flow as CREATE logic mentioned above except the Key Value 'Action' : 'DELETE' is added to rulesProperty instead of 'INSERT'