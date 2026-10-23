# Bedrock diagnosis — October 23, 2026

The actual Strands Agents SDK report call was inspected, rather than inferred from
a generic UI message. Evidence is in `artifacts/bedrock-diagnosis.json`. Full STS
identity is kept only under ignored `artifacts/private/bedrock-diagnosis/`.
No access keys, secrets, signed headers or session tokens are recorded.

| Setting | Verified value |
| --- | --- |
| Profile / region | bhoomil / us-west-2 |
| Authenticated account | ending 4677; full identity checked privately using STS |
| Model | amazon.nova-lite-v1:0; catalog status ACTIVE |
| Endpoint service | bedrock-runtime, not bedrock-mantle |
| Endpoint | https://bedrock-runtime.us-west-2.amazonaws.com |
| Actual SDK operation | ConverseStream |
| Output reservation | max_tokens=2400 |
| HTTP status / error code | 429 / ThrottlingException |
| Complete service message | Too many tokens per day, please wait before trying again. |
| Request ID | 3b19031d-c812-426f-b7d4-940ea528cbc6 |

## Matching applied allowances

| Code | Quota | Applied value | Adjustable |
| --- | --- | --- | --- |
| L-45E0AD92 | Model invocation max tokens per day for Amazon Nova Lite (doubled for cross-region calls) | 0 | No |
| L-7C42E72A | Cross-region model inference tokens per minute for Amazon Nova Lite | 0 | Yes |
| L-89F8391A | Cross-region model inference requests per minute for Amazon Nova Lite | 0 | No |
| L-E3F10727 | Cross-Model Max Tokens Per Day | 150,000,000 | No |

This establishes a zero model-specific daily allowance; it does **not** establish
that 150 million account-wide tokens were consumed. The service error does not
supply a quota code. The matching zero daily allowance is the relevant observed
restriction; AWS Support must confirm the account's effective enforcement and
restore access. An adjustable cross-region TPM entry is a request route, not proof
that changing only cross-region capacity would fix this direct on-demand call.

## CloudWatch check

The two-day UTC window, exact dimensions and hourly Sum datapoints are preserved
in the diagnosis JSON under namespace AWS/Bedrock. The Nova Lite ModelId series
contains one accepted invocation, 8 input tokens, 16 output tokens, and six
throttles. The separate series without dimensions records 11 throttles, two
client errors, and an estimated token-usage observation of 24. Do not add
model-specific and aggregate series together. Empty cache series are unavailable
observations, not proof of zero usage. Regional metrics and accepted token counts
do not establish exact remaining daily allowance; admission also reserves input
plus maximum output tokens.

AWS documents these distinctions in [token quota accounting](https://docs.aws.amazon.com/bedrock/latest/userguide/quotas-token-burndown.html)
and [runtime monitoring](https://docs.aws.amazon.com/bedrock/latest/userguide/monitoring-runtime-metrics.html).

## Prepared request — not submitted

1. Sign into the **bhoomil** account and select **US West (Oregon), us-west-2**.
2. Open **Service Quotas → AWS services → Amazon Bedrock**.
3. Find **Cross-region model inference tokens per minute for Amazon Nova Lite**,
   code **L-7C42E72A**. Confirm that its current applied value is 0 and it is adjustable.
4. Request **10,000 tokens/minute** as a proposed small demo allowance. This is a
   suggested request, not a guaranteed minimum, approval or automatic daily reset.
5. In the support follow-up, provide the exact model, endpoint, operation, error,
   request ID and zero **daily** quota **L-45E0AD92** above. Ask AWS to review and
   restore the daily/on-demand allowance as part of the request. State that the app
   makes only a few small synthetic demo reports. Do not request an unrelated
   increase to the 150-million cross-model limit.
6. After AWS confirms the effective allowance, rerun the real report verification
   command in README. An approved request alone is not a passed application test.

AWS's [runtime quota instructions](https://docs.aws.amazon.com/bedrock/latest/userguide/quotas-runtime.html)
specify the adjustable cross-region token quota as the support entry point for
combined cross-region, on-demand and daily-token review. The proposed request
fields are saved in `artifacts/bedrock-quota-request-draft.json`; no request API
has been executed. Account-owner approval is required before submission.

Repeat diagnosis (read-only inspection plus one real reporting attempt):

```bash
OPSPILOT_AWS_PROFILE=bhoomil AWS_REGION=us-west-2 .venv/bin/python -m scripts.diagnose_bedrock
```
