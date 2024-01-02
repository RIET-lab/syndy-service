// This is a simplified example and may need additional configurations
import * as cdk from 'aws-cdk-lib';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as ecr from 'aws-cdk-lib/aws-ecr';
import * as ecrAssets from 'aws-cdk-lib/aws-ecr-assets';
import { Construct } from 'constructs';

interface ContainerStackProps extends cdk.StackProps {
  name: string;
  directory: string;
};

class ContainerStack extends cdk.Stack {
  public readonly repositoryUri: string;
  public readonly imageAsset: ecrAssets.DockerImageAsset;
  
  constructor(scope: Construct, id: string, props: ContainerStackProps) {
    super(scope, id, props);

    this.imageAsset = new ecrAssets.DockerImageAsset(this, props.name, {
      directory: props.directory,
    });
  }
}

export default ContainerStack
