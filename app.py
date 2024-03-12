#!/usr/bin/env python3

import os

import aws_cdk as cdk
from dotenv import load_dotenv

from weirdsheeplabs_cdn.infrastructure import CdnStack

load_dotenv()

app = cdk.App()
stack = CdnStack(
    app,
    "WeirdSheepLabsCdnStack",
    env=cdk.Environment(
        account=os.environ.get("CDK_DEPLOY_ACCOUNT", os.environ["CDK_DEFAULT_ACCOUNT"]),
        region=os.environ.get("CDK_DEPLOY_REGION", os.environ["CDK_DEFAULT_REGION"]),
    ),
)

# Add tags to entire stack
cdk.Tags.of(stack).add("Project", "Weird Sheep Labs CDN")

app.synth()
