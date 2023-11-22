import * as cdk from 'aws-cdk-lib/core';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as ecs from 'aws-cdk-lib/aws-ecs';
import * as ecr from 'aws-cdk-lib/aws-ecr';
import * as elbv2 from 'aws-cdk-lib/aws-elasticloadbalancingv2';
import * as ecrAssets from 'aws-cdk-lib/aws-ecr-assets';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import { Construct } from 'constructs';

interface ApiStackProps extends cdk.StackProps {
    nlb: elbv2.NetworkLoadBalancer;
}

class ApiStack extends cdk.Stack {
    constructor(scope: Construct, id: string, props: ApiStackProps) {
        super(scope, id, props);

        const vpcLink = new apigateway.VpcLink(this, 'TestServiceVpcLink', {
            targets: [props.nlb],
        });
    
        // Create an HTTP API Gateway
        const integration = new apigateway.Integration({
            type: apigateway.IntegrationType.HTTP_PROXY,
            options: {
              connectionType: apigateway.ConnectionType.VPC_LINK,
              vpcLink: vpcLink,
            },
            integrationHttpMethod: 'POST'
          });

        const api = new apigateway.RestApi(this, 'TestServiceApi', {
            restApiName: 'TestServiceApi',
            defaultIntegration: integration
        });
        const predict = api.root.addResource('predict');
        predict.addMethod('POST', integration);
    }
};
    
export default ApiStack;
