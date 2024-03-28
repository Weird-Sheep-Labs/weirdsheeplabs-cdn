import os

from aws_cdk import Stack
from aws_cdk import aws_certificatemanager as acm
from aws_cdk import aws_cloudfront as cf
from aws_cdk import aws_cloudfront_origins as cf_origins
from aws_cdk import aws_iam as iam
from aws_cdk import aws_route53 as route53
from aws_cdk import aws_route53_targets as route53_targets
from aws_cdk import aws_s3 as s3
from constructs import Construct


class CdnStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self._fqdn = None

        # Set up S3 bucket and access controls
        cors_rule = s3.CorsRule(
            allowed_methods=[s3.HttpMethods.GET, s3.HttpMethods.HEAD],
            allowed_headers=["*"],
            allowed_origins=["*"],
            max_age=300,
        )

        bucket = s3.Bucket(
            self,
            "WeirdSheepLabsCdnBucket",
            bucket_name=os.environ["BUCKET_NAME"],
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            access_control=s3.BucketAccessControl.PRIVATE,
            cors=[cors_rule],
        )

        bucket.add_to_resource_policy(
            iam.PolicyStatement(
                actions=["s3:*"],
                resources=[bucket.bucket_arn, bucket.arn_for_objects("*")],
                principals=[iam.AnyPrincipal()],  # type: ignore
                conditions={
                    "StringLike": {
                        "aws:PrincipalArn": [
                            f"arn:aws:iam::{self.account}:*",
                            # Needed for stack deployment when authenticated with AWS SSO
                            f"arn:aws:sts::{self.account}:*",
                        ]
                    }
                },
            )
        )

        # Get SSL certificate
        certificate = acm.Certificate.from_certificate_arn(
            self,
            "WeirdSheepLabsCdnCertificate",
            certificate_arn=os.environ["CERTIFICATE_ARN"],
        )

        # Create Cloudfront distribution
        distribution = cf.Distribution(
            self,
            "WeirdSheepLabsCdnDistribution",
            default_behavior=cf.BehaviorOptions(origin=cf_origins.S3Origin(bucket)),
            domain_names=[self.fqdn],
            certificate=certificate,
        )

        # Get existing hosted zone and create records for CDN subdomain
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
            record_name=os.environ["SUBDOMAIN"],
        )

        route53.AaaaRecord(
            self,
            "WeirdSheepLabsCdnAaaaRecord",
            zone=zone,
            target=route53.RecordTarget.from_alias(
                route53_targets.CloudFrontTarget(distribution)  # type: ignore
            ),
            record_name=os.environ["SUBDOMAIN"],
        )

    @property
    def fqdn(self):
        """
        Forms the FQDN for the CDN subdomain.
        """
        if not self._fqdn:
            self._fqdn = f"{os.environ["SUBDOMAIN"]}.{os.environ["HOSTED_ZONE_NAME"]}"
        return self._fqdn
