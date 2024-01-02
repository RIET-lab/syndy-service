import * as cdk from 'aws-cdk-lib';
import ContainerStack from '../lib/stacks/container-stack';
import VpcStack from '../lib/stacks/vpc-stack';
import EcsServiceStack from '../lib/stacks/ecs-service-stack';
import PythonLambdaStack from '../lib/stacks/serverless-api-stack';
import { DatasetsStack } from '../lib/stacks/datasets-stack';
import * as dotenv from 'dotenv';

dotenv.config();

const app = new cdk.App();
const vpc = new VpcStack(app, 'SynDyVpcStack');

const inferenceContainer = new ContainerStack(app, 'SynDyInferenceContainerStack', {
    name: 'SynDyInferenceContainer',
    directory: 'services/modeling/'
});

const inferenceService = new EcsServiceStack(app, 'SynDyInferenceServiceStack', {
    vpc: vpc.vpc, 
    imageAsset: inferenceContainer.imageAsset,
    name: 'SynDyInference',
    healthCheckPath: '/predictions/test-sentence-transformer'
});
inferenceService.addDependency(inferenceContainer);
inferenceService.addDependency(vpc);

const annotate = new PythonLambdaStack(app, 'AnnotationLambda', {
    vpc: vpc.vpc,
    code: 'services/labeling/deployment.zip',
    handler: 'extract.handle'
});
annotate.addDependency(vpc);

const datapull = new PythonLambdaStack(app, 'DataPullLambda', {
    vpc: vpc.vpc,
    code: 'services/data_pulling/deployment.zip',
    handler: 'data.handle',
    timeout: 300
});
datapull.addDependency(vpc);

const syndyContainer = new ContainerStack(app, 'SynDyContainerStack', {
    name: 'SynDyContainer',
    directory: 'services/syndy/'
});

const datasets = new DatasetsStack(app, 'DatasetsStack');

const syndyService = new EcsServiceStack(app, 'SynDyServiceStack', {
    vpc: vpc.vpc, 
    imageAsset: syndyContainer.imageAsset,
    name: 'SynDy',
    healthCheckPath: '/test',
    env: {
        OPENAI_KEY: process.env.OPENAI_KEY || '',
        DATAPULL_ARN: datapull.lambdaFunction.functionArn,
        ANNOTATE_ARN: annotate.lambdaFunction.functionArn,
        REDDIT_CLIENT_ID: process.env.REDDIT_CLIENT_ID || '',
        REDDIT_CLIENT_SECRET: process.env.REDDIT_CLIENT_SECRET || '',
        REDDIT_USER_AGENT: process.env.REDDIT_USER_AGENT || '',
        DATASET_BUCKET: datasets.datasetBucket.bucketName,
        INFERENCE_URL: inferenceService.service.loadBalancer.loadBalancerDnsName
    },
    port: 80
});
datapull.lambdaFunction.grantInvoke(syndyService.service.taskDefinition.taskRole);
annotate.lambdaFunction.grantInvoke(syndyService.service.taskDefinition.taskRole);
datasets.datasetBucket.grantReadWrite(syndyService.service.taskDefinition.taskRole);
syndyService.addDependency(syndyContainer);
syndyService.addDependency(vpc);
syndyService.addDependency(datapull);
syndyService.addDependency(annotate);
syndyService.addDependency(datasets);

app.synth();
