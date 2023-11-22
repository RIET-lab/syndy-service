import * as cdk from 'aws-cdk-lib/core';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as ecs from 'aws-cdk-lib/aws-ecs';
import * as ecr from 'aws-cdk-lib/aws-ecr';
import * as elbv2 from 'aws-cdk-lib/aws-elasticloadbalancingv2';
import * as ecrAssets from 'aws-cdk-lib/aws-ecr-assets';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import * as ecs_patterns from 'aws-cdk-lib/aws-ecs-patterns';
import { Construct } from 'constructs';

interface EcsServiceStackProps extends cdk.StackProps {
    vpc: ec2.Vpc;
    imageAsset: ecrAssets.DockerImageAsset;
}

class EcsServiceStack extends cdk.Stack {
    public readonly nlb: elbv2.NetworkLoadBalancer;

    constructor(scope: Construct, id: string, props: EcsServiceStackProps) {
        super(scope, id, props);
    
        const vpc = props.vpc;
        const cluster = new ecs.Cluster(this, 'TestServiceCluster', {
            vpc, 
            clusterName: 'TestServiceCluster',
            // capacity: {
            //     instanceType: new ec2.InstanceType('c6g.xlarge'),
            //     maxCapacity: 1,
            // }
        });  
        
        const service = new ecs_patterns.ApplicationLoadBalancedFargateService(this, "TestService", {
            cluster: cluster, // Required
            cpu: 2048, // Default is 256
            desiredCount: 1, // Default is 1
            taskImageOptions: { 
                image: ecs.ContainerImage.fromDockerImageAsset(props.imageAsset),
                containerPort: 8080
            },
            memoryLimitMiB: 8192, // Default is 512
            publicLoadBalancer: true, // Default is true
            listenerPort: 8080,
            minHealthyPercent: 0
        });
        service.targetGroup.configureHealthCheck({
            path: "/predictions/test-sentence-transformer",
        });
        // service.targetGroup.setAttribute('port', '8080');

        // const nlb = new elbv2.NetworkLoadBalancer(this, 'TestServiceNLB', {
        //     vpc,
        //     internetFacing: true
        // });
    
        // const targetGroup = new elbv2.NetworkTargetGroup(this, 'TestServiceTargetGroup', {
        //     vpc,
        //     port: 8080
        // });
    
        // nlb.addListener('TestServiceListener', {
        //     port: 8080,
        //     defaultTargetGroups: [targetGroup]
        // });
    
        // const taskDefinition = new ecs.FargateTaskDefinition(this, 'TestServiceTaskDef', {
        //     memoryLimitMiB: 8192,
        //     cpu: 2048
        // });
        
        // taskDefinition.addContainer('TestServiceContainer', {
        //     // image: ecs.ContainerImage.fromDockerImageAsset(props.imageAsset),
        //     image: ecs.ContainerImage.fromEcrRepository(props.imageAsset.repository, props.imageAsset.imageTag),
        //     memoryLimitMiB: 4096,
        //     portMappings: [{ containerPort: 8080 }]
        // });

        // const targetGroup = new elbv2.ApplicationTargetGroup(this, 'TestServiceTargetGroup', {
        //     port: 8080,
        //     vpc: vpc,
        //     targetType: elbv2.TargetType.IP,
        //     targets: [taskDefinition]
        // });
    
        // const service = new ecs.FargateService(this, 'MyService', {
        //     cluster,
        //     taskDefinition
        // });
    
        // targetGroup.addTarget(service);
        // this.nlb = nlb;
    }
};
    
export default EcsServiceStack;
