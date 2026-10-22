# AWS usage, live measurements and cleanup

OpsPilot runs as a local Streamlit application and local Decider model. It is not
an agent deployed in the Amazon Bedrock Agents console. Its normal dashboard
operations do not provision infrastructure.

## Choose what to analyze

- **Examples or pasted data:** synthetic fixtures or records pasted by you. The
  "sample" badge describes these inputs, even when real Bedrock inference is used.
- **Live AWS EC2 metrics:** select a local AWS profile, region, EC2 instance and UTC
  start/end dates and times. Connect explicitly, then select **Fetch real CPU data**.
  The dashboard reads actual CloudWatch CPU averages for that selection. Changing
  the selection invalidates the previous fetch; empty results never become sample data.
- **Full AI investigation:** Decider selects diagnostics, then Bedrock writes the
  report. Telemetry and reporting can use different profiles; both are shown.

A window can span up to 24 hours. CPU samples use five-minute averages and may
arrive with a delay. This is a fetched snapshot, not a continuous monitor. One
sample cannot establish a trend. The start of the collection window is used as
the initial incident start time. The output keeps collection window, fetch time,
instance ID, region and AWS request ID.

EC2 inventory does not reveal installed/running applications. This version does
not collect process lists, memory, application log files, CloudWatch Logs or
release history. Those need explicit additional instrumentation and configuration.

## AWS calls made by the dashboard

| Purpose | Service calls | Effect |
| --- | --- | --- |
| Account identity | STS GetCallerIdentity | Read identity |
| EC2 selector | EC2 DescribeInstances | Read inventory, up to 200 instances |
| CPU measurements | CloudWatch GetMetricStatistics | Read AWS/EC2 CPUUtilization averages |
| AI report | Bedrock runtime ConverseStream | Paid inference on selected evidence |

Reports are kept in browser/session memory and explicit local downloads. The code
does not upload them to S3 or create a knowledge base, database, persistent agent,
log group or EC2 instance from the dashboard.

Bedrock usage can be inspected in the AWS CloudWatch metrics console in the
reporting region: search for model `amazon.nova-lite-v1:0` under `AWS/Bedrock`,
including Invocations, InputTokenCount and OutputTokenCount. This is usage metadata,
not a stored copy of each report. AWS billing details can arrive later.

The read-only check in `artifacts/aws-logging-check.json` found no Bedrock invocation
logging configuration for hardik/us-east-1 at check time. OpsPilot did not enable
logging. If an account enables invocation logging separately, prompts/responses
may be stored in its configured CloudWatch/S3 destinations. Do not delete unrelated
account logs, audit history or infrastructure as part of this project.

## Separately authorized disposable EC2 demonstration

The user explicitly authorized creation of a temporary EC2 in the **bhoomil**
profile because the user reported having no existing test instance. The
one-time script is separate from the dashboard's read-only collector:

- `t3.micro`, Amazon Linux 2023, `us-east-1`.
- 8 GiB encrypted gp3 root disk configured to delete on termination.
- Dedicated security group with no inbound rules; no public IP, key pair or IAM role.
- Standard CPU credits and basic monitoring; no reserved/provisioned commitment.
- A bounded shell CPU test, with scheduled OS shutdown after 15 minutes and
  instance-initiated shutdown configured to terminate.
- Existing default VPC/subnet reused without modification.

The exact resources and cleanup status are in `artifacts/ec2-demo-resource.json`.
Live input, collection receipt, actual Decider trace and Bedrock report are in
`artifacts/live-aws-investigation.json`. This is real cloud telemetry from a
controlled test, not evidence of a production outage.

Only the scoped demo resources are removed. The cleanup script verifies the
account suffix and demo RunId/Project tags before terminating the recorded
instance, waiting for termination and deleting its security group. It checks for
remaining tagged volumes. The existing VPC, subnet and default security group
are retained. Do not rerun creation merely to inspect the saved demonstration.

```sh
# Only for this separately authorized, disposable demo resource record:
.venv/bin/python -m scripts.ec2_demo cleanup
```

Termination deletes the disposable root disk permanently. Saved evidence remains
local for review. Terminated EC2 records can remain visible temporarily in the
console; billing/audit history is not removed. Shutdown scheduling is a safeguard,
not proof of cleanup: the resource record must show verified cleanup completion.

The published Linux t3.micro compute rate for US East (N. Virginia) is $0.0104/hour,
plus prorated disk and any API/model usage. This is a reference rate, not a verified
account invoice or a claim of free-tier eligibility.

## Official references

- https://aws.amazon.com/ec2/instance-types/t3/
- https://docs.aws.amazon.com/bedrock/latest/userguide/monitoring-runtime-metrics.html
- https://docs.aws.amazon.com/bedrock/latest/userguide/model-invocation-logging.html
- https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/US_SingleMetricPerInstance.html
- https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-lifecycle.html

Verified cleanup: the recorded instance is terminated, its root volume returns
InvalidVolume.NotFound, and its dedicated security group returns InvalidGroup.NotFound.
The exact check time and IDs are saved in the demo resource record.
