import * as cdk from 'aws-cdk-lib';
import ContainerStack from '../lib/stacks/container-stack';
import VpcStack from '../lib/stacks/vpc-stack';
import EcsServiceStack from '../lib/stacks/ecs-service-stack';
import { PythonLambdaStack } from '../lib/stacks/serverless-api-stack';
import { DatasetsStack } from '../lib/stacks/datasets-stack';


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
const datapull = new PythonLambdaStack(app, 'DataPullLambda', {
    vpc: vpc.vpc,
    code: 'services/data_pulling/deployment.zip',
    handler: 'data.handle',
    timeout: 300
});
annotate.addDependency(vpc);
datapull.addDependency(vpc);
const datasets = new DatasetsStack(app, 'DatasetsStack');
app.synth();
