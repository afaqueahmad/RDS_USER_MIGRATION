# RDS_USER_MIGRATION

# What Problem it will solve?
Lets Say you created a new RDS instance and you dont want to create all the user account from scratch.
This python based script will help you to create all those users,password and its access level from any existing RDS instance.
So basically this will migrate all your user from one RDS instance to another RDS instance.
When you create a user in any RDS instance and store password somwhere in AWS secrets, fetching all those password is not fasible, Also granting same level of access is chalenging.

A Python based lambda function to migrate list of all users from one RDS Instance to other RDS Instance.

# Authentication 
It uses RDS IAM authentication mechanism for admin access and migration.


# Lambda function Invocation
aws lambda invoke --function-name <function-name> --payload file://test-event.json output.json


**test-event.json**
{
  "Source_DB": "SOURCE-DB-ENDPOINT",
  "Target_DB": "TARGET-DB-ENDPOINT"
}
