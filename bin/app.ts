import * as cdk from 'aws-cdk-lib';
import ContainerStack from '../lib/stacks/container-stack';
// import SageMakerEndpointStack from '../lib/stacks/sagemakerendpoint-stack';
import VpcStack from '../lib/stacks/vpc-stack';
import EcsServiceStack from '../lib/stacks/ecs-service-stack';
import { PythonLambdaStack } from '../lib/stacks/serverless-api-stack';
import { CfnAnnotationStore } from 'aws-cdk-lib/aws-omics';
// import ApiStack from '../lib/stacks/api-stack';

// import * as sqs from 'aws-cdk-lib/aws-sqs';

const app = new cdk.App();
const vpc = new VpcStack(app, 'TestVpcStack');
const container = new ContainerStack(app, 'TestContainerStack');
const service = new EcsServiceStack(app, 'TestEcsServiceStack',{vpc: vpc.vpc, imageAsset: container.imageAsset});
service.addDependency(container);
service.addDependency(vpc);
const annotate = new PythonLambdaStack(app, 'AnnotationLambda', {
    vpc: vpc.vpc,
    code: 'services/labeling/deployment.zip',
    handler: 'extract.handle'
});
annotate.addDependency(vpc);
app.synth();
