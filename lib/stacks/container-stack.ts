// This is a simplified example and may need additional configurations
import * as cdk from 'aws-cdk-lib';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as ecr from 'aws-cdk-lib/aws-ecr';
import * as ecrAssets from 'aws-cdk-lib/aws-ecr-assets';
import { Construct } from 'constructs';

class ContainerStack extends cdk.Stack {
  public readonly repositoryUri: string;
  public readonly imageAsset: ecrAssets.DockerImageAsset;
  
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // const repository = new ecr.Repository(this, 'TestModelRepository');
    this.imageAsset = new ecrAssets.DockerImageAsset(this, 'TestModelDockerImage', {
      directory: 'services/modeling/', // Directory where your Dockerfile is located
    });
    
    // this.repositoryUri = repository.repositoryUri;
  }
}

export default ContainerStack
