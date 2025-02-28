import json

# Load dynamic paths from a JSON file
with open('iac/params/dynamic_paths.json', 'r') as f:
    data = json.load(f)

resources = {}

for res in data.get("resources", []):
    # Create a logical ID for the resource (capitalize first letter of pathPart)
    logical_id = ''.join(word.capitalize() for word in res["pathPart"].split('-')) + "Resource"
    method_id = ''.join(word.capitalize() for word in res["pathPart"].split('-')) + "Method"

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
            "Uri": { "Fn::Sub": f"arn:aws:apigateway:${{AWS::Region}}:lambda:path/2015-03-31/functions/{res['lambdaFunctionArn']}/invocations" }
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

print(json.dumps({"Resources": resources}, indent=2))
