"""Explicit lifecycle for the user-authorized disposable demo, never production cleanup."""

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import boto3
from botocore.config import Config

RECORD = Path("artifacts/ec2-demo-resource.json")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("operation", choices=["create", "cleanup"])
    parser.add_argument("--region", default="us-west-2")
    args = parser.parse_args()
    region = args.region if args.operation == "create" else json.loads(RECORD.read_text())["region"]
    session = boto3.Session(profile_name="bhoomil", region_name=region)
    config = Config(connect_timeout=5, read_timeout=20, retries={"total_max_attempts": 2})
    ec2 = session.client("ec2", config=config)
    suffix = session.client("sts", config=config).get_caller_identity()["Account"][-4:]
    if args.operation == "create":
        if RECORD.exists():
            raise SystemExit(
                "Resource record already exists. Inspect it; do not create duplicates."
            )
        vpc = ec2.describe_vpcs(Filters=[{"Name": "is-default", "Values": ["true"]}])["Vpcs"][0]
        subnet = next(
            s
            for s in ec2.describe_subnets(Filters=[{"Name": "vpc-id", "Values": [vpc["VpcId"]]}])[
                "Subnets"
            ]
            if s["State"] == "available"
        )
        ami = session.client("ssm", config=config).get_parameter(
            Name="/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64"
        )["Parameter"]["Value"]
        image = ec2.describe_images(ImageIds=[ami])["Images"][0]
        token = str(uuid4())
        tags = [
            {"Key": "Name", "Value": "OpsPilot-Hackathon-Temporary-Demo"},
            {"Key": "Project", "Value": "OpsPilotDisposableDemo"},
            {"Key": "RunId", "Value": token},
        ]
        sg = ec2.create_security_group(
            GroupName=f"opspilot-demo-{token[:8]}",
            Description="Temporary OpsPilot demo; no inbound rules",
            VpcId=vpc["VpcId"],
            TagSpecifications=[{"ResourceType": "security-group", "Tags": tags}],
        )["GroupId"]
        record = {
            "profile": "bhoomil",
            "region": region,
            "account_suffix": suffix,
            "run_id": token,
            "security_group_id": sg,
            "instance_id": None,
            "created_at_utc": datetime.now(UTC).isoformat(),
            "instance_type": "t3.micro",
            "public_ip_requested": False,
            "auto_shutdown_after_minutes": 15,
            "cleanup_status": "pending",
            "purpose": "Controlled test CPU workload; not a real incident",
        }
        RECORD.parent.mkdir(exist_ok=True)
        RECORD.write_text(json.dumps(record, indent=2))
        try:
            response = ec2.run_instances(
                ImageId=ami,
                InstanceType="t3.micro",
                MinCount=1,
                MaxCount=1,
                ClientToken=token,
                InstanceInitiatedShutdownBehavior="terminate",
                CreditSpecification={"CpuCredits": "standard"},
                Monitoring={"Enabled": False},
                MetadataOptions={"HttpTokens": "required", "HttpEndpoint": "enabled"},
                NetworkInterfaces=[
                    {
                        "DeviceIndex": 0,
                        "SubnetId": subnet["SubnetId"],
                        "Groups": [sg],
                        "AssociatePublicIpAddress": False,
                        "DeleteOnTermination": True,
                    }
                ],
                BlockDeviceMappings=[
                    {
                        "DeviceName": image["RootDeviceName"],
                        "Ebs": {
                            "VolumeSize": 8,
                            "VolumeType": "gp3",
                            "Encrypted": True,
                            "DeleteOnTermination": True,
                        },
                    }
                ],
                TagSpecifications=[
                    {"ResourceType": "instance", "Tags": tags},
                    {"ResourceType": "volume", "Tags": tags},
                ],
                UserData='#!/bin/bash\nshutdown -h +15\ntimeout 360 bash -c "while :; do :; done" &\nwait\n',
            )
            record["instance_id"] = response["Instances"][0]["InstanceId"]
            record["launch_request_id"] = response["ResponseMetadata"]["RequestId"]
            RECORD.write_text(json.dumps(record, indent=2))
            print(
                "Created dedicated temporary instance:",
                record["instance_id"],
                "security group:",
                sg,
                flush=True,
            )
        except Exception:
            # Unknown launch outcomes must be reconciled by RunId before deleting the group.
            print(
                "Launch did not return successfully. Resource record preserved for reconciliation.",
                flush=True,
            )
            raise
    else:
        record = json.loads(RECORD.read_text())
        if record["account_suffix"] != suffix:
            raise SystemExit("Account mismatch; cleanup refused.")
        matches = ec2.describe_instances(
            Filters=[
                {"Name": "tag:RunId", "Values": [record["run_id"]]},
                {"Name": "tag:Project", "Values": ["OpsPilotDisposableDemo"]},
            ]
        )
        instances = [i for r in matches["Reservations"] for i in r["Instances"]]
        for instance in instances:
            if record["instance_id"] and instance["InstanceId"] != record["instance_id"]:
                raise SystemExit("Resource identity mismatch; cleanup refused.")
            if instance["State"]["Name"] != "terminated":
                ec2.terminate_instances(InstanceIds=[instance["InstanceId"]])
                print("Termination requested:", instance["InstanceId"], flush=True)
                ec2.get_waiter("instance_terminated").wait(
                    InstanceIds=[instance["InstanceId"]],
                    WaiterConfig={"Delay": 10, "MaxAttempts": 30},
                )
        ec2.delete_security_group(GroupId=record["security_group_id"])
        volumes = ec2.describe_volumes(
            Filters=[{"Name": "tag:RunId", "Values": [record["run_id"]]}]
        )["Volumes"]
        record["cleanup_status"] = "complete" if not volumes else "volume deletion pending"
        record["remaining_volume_ids"] = [v["VolumeId"] for v in volumes]
        record["cleanup_checked_at_utc"] = datetime.now(UTC).isoformat()
        RECORD.write_text(json.dumps(record, indent=2))
        print("Cleanup:", record["cleanup_status"], flush=True)


if __name__ == "__main__":
    main()
