# Security and operational scope

- AWS SDK profiles/environment credential chain only. No credentials in `.env`,
  source, exports, tests, screenshots or Git. `.env.example` contains no secrets.
- Both local servers bind to loopback. Decider upstream has no authentication;
  do not expose its port to the internet.
- Three fixed analysis functions; no generated commands, write APIs or remediation.
- Supplied telemetry is bounded and validated; logs remain literal data.
- Bedrock receives the incident description and selected tools' observed evidence.
  Use synthetic demo data or data you are authorized to share with AWS.
- JSON exports include original input. Review/redact before publishing.
- Root causes remain hypotheses. Evidence-reference validation cannot prove semantic
  grounding; model output requires human review.
- Changes such as restarts, rollbacks or configuration updates always require
  separate human approval and are outside this application's capabilities.

## Minimum AWS permissions

The reporting flow requires `bedrock:InvokeModel` and, depending on provider/SDK,
`bedrock:InvokeModelWithResponseStream`, scoped to the chosen model or inference
profile. Cross-region inference may require underlying regional model resources.
`ListFoundationModels` is needed only for model discovery. STS identity is a
read-only preflight. Do not grant `AdministratorAccess` for this app.

The example policy in `docs/iam-policy.example.json` is a template, not deployable
until its model ARN placeholder is replaced. Choose resources for the exact model,
region and inference-profile setup; follow the AWS documentation for that model.

No IAM roles, policies, billing settings or infrastructure are created by this
repository. Live mode explicitly reads EC2 inventory and CloudWatch CPU averages; no application logs or memory are collected. See aws-usage-and-cleanup.md.
