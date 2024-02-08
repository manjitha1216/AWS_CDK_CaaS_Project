#!/usr/bin/env python3

import aws_cdk as cdk

from aws_caa_s_project.aws_caa_s_project_stack import AwsCaaSProjectStack


app = cdk.App()
AwsCaaSProjectStack(app, "AwsCaaSProjectStack")

app.synth()
