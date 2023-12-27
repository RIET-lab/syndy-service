import * as cdk from 'aws-cdk-lib/core';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as ec2 from 'aws-cdk-lib/aws-ec2'
import { Function, Code } from 'aws-cdk-lib/aws-lambda';
import { Construct } from 'constructs';
import { Ec2Action } from 'aws-cdk-lib/aws-cloudwatch-actions';

export interface PythonLambdaProps {
  vpc: ec2.Vpc;
  code: string;
  handler: string;
  timeout?: number;
}

export class PythonLambdaStack extends cdk.Stack {
  public readonly lambdaFunction: lambda.Function;

  constructor(scope: Construct, id: string, props: PythonLambdaProps) {
    super(scope, id);

    this.lambdaFunction = new Function(this, 'MyPythonFunction', {
      code: Code.fromAsset(props.code),
      handler: props.handler,
      runtime: lambda.Runtime.PYTHON_3_8,
      vpc: props.vpc,
      timeout: cdk.Duration.seconds(props.timeout || 60),
    });
  }
}
export default PythonLambdaStack;
