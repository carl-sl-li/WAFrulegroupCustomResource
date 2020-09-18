# WAFrulegroupCustomResource
CloudFormation Custom Resource to insert, update and delete WAF rule group to a WAF WebACL

**Use Case**

You purchased a pre-configured WAF RuleGroup in the AWS Marketplace and like to add the purchased managed rules to AWS Web Application Firewall (WAF) Web Access Control List (ACL) via CloudFormation.

**Description**

At the moment of writing, the API call to subscribe managed WAF rule group is not yet supported in CloudFormation and is only available with AWS CLI/SDK and console.  This is a solution which uses a Lambda backed Custom Resource to insert, update and delete WAF rule group to a WAF WebACL.