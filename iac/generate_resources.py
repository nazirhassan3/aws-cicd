import json
import sys
import yaml

# Use the first command-line argument as the input file; default if not provided.
input_file = sys.argv[1] if len(sys.argv) > 1 else 'iac/params/current_resource_paths.json'

with open(input_file, 'r') as f:
    data = json.load(f)

resources = {}
for res in data:
    logical_id = f"{res['pathPart'].capitalize()}Resource"
    method_id = f"{res['pathPart'].capitalize()}Method"
    
    resources[logical_id] = {
        "Type": "AWS::ApiGateway::Resource",
        "Properties": {
            "ParentId": { "Fn::GetAtt": [ "RestApi", "RootResourceId" ] },
            "PathPart": res["pathPart"],
            "RestApiId": { "Ref": "RestApi" }
        }
    }
    
    if res["integrationType"] == "AWS_PROXY":
        integration = {
            "IntegrationHttpMethod": "POST",
            "Type": "AWS_PROXY",
            "Uri": {
                "Fn::Join": [
                    "",
                    [
                        "arn:aws:apigateway:",
                        "${AWS::Region}",  # This will be processed by CloudFormation
                        ":lambda:path/2015-03-31/functions/",
                        res["lambdaFunctionArn"],
                        ":\\${stageVariables.lambdaAlias}/invocations"
                    ]
                ]
            }
        }
    elif res["integrationType"] == "HTTP":
        integration = {
            "IntegrationHttpMethod": res.get("httpMethod", "GET"),
            "Type": "HTTP",
            "Uri": res["endpoint"]
        }
    else:
        integration = {}

    resources[method_id] = {
        "Type": "AWS::ApiGateway::Method",
        "Properties": {
            "RestApiId": { "Ref": "RestApi" },
            "ResourceId": { "Ref": logical_id },
            "HttpMethod": res["httpMethod"],
            "AuthorizationType": "NONE",
            "Integration": integration,
            "MethodResponses": [ { "StatusCode": "200" } ]
        }
    }

print(yaml.dump({"Resources": resources}, default_flow_style=False))
