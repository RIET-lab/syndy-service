import * as cdk from 'aws-cdk-lib/core';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as ecs from 'aws-cdk-lib/aws-ecs';
import * as ecrAssets from 'aws-cdk-lib/aws-ecr-assets';
import * as ecs_patterns from 'aws-cdk-lib/aws-ecs-patterns';
import { Construct } from 'constructs';

interface EcsServiceStackProps extends cdk.StackProps {
    vpc: ec2.Vpc;
    imageAsset: ecrAssets.DockerImageAsset;
    name: string;
    healthCheckPath?: string;
    port?: number;
    env?: { [key: string]: string };
    cluster?: ecs.Cluster;
}

class EcsServiceStack extends cdk.Stack {
    cluster: ecs.Cluster;
    service: ecs_patterns.ApplicationLoadBalancedFargateService;
    
    constructor(scope: Construct, id: string, props: EcsServiceStackProps) {
        super(scope, id, props);
    
        const vpc = props.vpc;
        this.cluster = props.cluster ? props.cluster : new ecs.Cluster(this, `${props.name}Cluster`, {
            vpc, 
            clusterName: `${props.name}Cluster`,
        });  
        
        this.service = new ecs_patterns.ApplicationLoadBalancedFargateService(this, props.name, {
            cluster: this.cluster,
            cpu: 2048,
            desiredCount: 1,
            taskImageOptions: { 
                image: ecs.ContainerImage.fromDockerImageAsset(props.imageAsset),
                containerPort: props.port || 8080,
                environment: props.env ? props.env : {}
            },
            memoryLimitMiB: 8192,
            publicLoadBalancer: true,
            listenerPort: props.port || 8080,
            minHealthyPercent: 0
        });
        
        if (props.healthCheckPath) {
            this.service.targetGroup.configureHealthCheck({
                path: props.healthCheckPath,
            });
        }
    }
};
    
export default EcsServiceStack;
