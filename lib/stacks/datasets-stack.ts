import * as s3 from 'aws-cdk-lib/aws-s3'
import * as cdk from 'aws-cdk-lib/core';
import { Construct } from 'constructs';

export class DatasetsStack extends cdk.Stack {
  public readonly datasetBucket: s3.Bucket;

  constructor(scope: Construct, id: string) {
    super(scope, id);

    this.datasetBucket = new s3.Bucket(this, 'DatasetBucket', {
      removalPolicy: cdk.RemovalPolicy.DESTROY
    });
  }
}