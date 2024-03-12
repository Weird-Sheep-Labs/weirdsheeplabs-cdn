import os

from aws_cdk import Stack
from aws_cdk import aws_certificatemanager as acm
from aws_cdk import aws_cloudfront as cf
from aws_cdk import aws_cloudfront_origins as cf_origins
from aws_cdk import aws_route53 as route53
from aws_cdk import aws_route53_targets as route53_targets
from aws_cdk import aws_s3 as s3
from constructs import Construct


class CdnStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        cors_rule = s3.CorsRule(
            allowed_methods=[s3.HttpMethods.GET, s3.HttpMethods.HEAD],
            allowed_headers=["*"],
            allowed_origins=["*"],
            max_age=300,
        )

        bucket = s3.Bucket(
            self,
            "WeirdSheepLabsCdnBucket",
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            access_control=s3.BucketAccessControl.PRIVATE,
            cors=[cors_rule],
        )

        certificate = acm.Certificate.from_certificate_arn(
            self,
            "WeirdSheepLabsCdnCertificate",
            certificate_arn=os.environ["CERTIFICATE_ARN"],
        )

        distribution = cf.Distribution(
            self,
            "WeirdSheepLabsCdnDistribution",
            default_behavior={"origin": cf_origins.S3Origin(bucket)},
            domain_names=[os.environ["DOMAIN"]],
            certificate=certificate,
        )

        zone = route53.HostedZone.from_hosted_zone_attributes(
            self,
            "WeirdSheepLabsHostedZone",
            hosted_zone_id=os.environ["HOSTED_ZONE_ID"],
            zone_name=os.environ["HOSTED_ZONE_NAME"],
        )

        route53.ARecord(
            self,
            "WeirdSheepLabsCdnARecord",
            zone=zone,
            target=route53.RecordTarget.from_alias(
                route53_targets.CloudFrontTarget(distribution)  # type: ignore
            ),
        )

        route53.AaaaRecord(
            self,
            "WeirdSheepLabsCdnAaaaRecord",
            zone=zone,
            target=route53.RecordTarget.from_alias(
                route53_targets.CloudFrontTarget(distribution)  # type: ignore
            ),
        )
