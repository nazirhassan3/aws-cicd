import json
import yaml

with open('iac/params/dynamic_paths.json', 'r') as f:
    data = json.load(f)

resources = {}
for res in data.get("resources", []):
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

# Output the generated YAML with a top-level "Resources" key.
print(yaml.dump({"Resources": resources}, default_flow_style=False))
