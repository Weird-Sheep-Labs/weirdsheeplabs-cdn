import aws_cdk as core
import aws_cdk.assertions as assertions

from weirdsheeplabs_cdn.weirdsheeplabs_cdn_stack import WeirdsheeplabsCdnStack

# example tests. To run these tests, uncomment this file along with the example
# resource in weirdsheeplabs_cdn/weirdsheeplabs_cdn_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = WeirdsheeplabsCdnStack(app, "weirdsheeplabs-cdn")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
