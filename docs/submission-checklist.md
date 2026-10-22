# Submission compliance checklist

Checked against official About page and detailed Rules tab on October 22, 2026.
[Official event and rules](https://builder.aws.com/build/hackathons/4f50957c-1d08-37ab-b11c-97516b9adeb4/agent-experience-hackathon?tab=rules)
· [AWS Builder Terms](https://builder.aws.com/terms).

**Deadline:** October 23, 2026 11:59 PM PDT, equivalent to **October 24, 2026
12:29 PM IST**. Submit before the cutoff; do not rely on other listings' dates.

| Requirement | Evidence / action |
| --- | --- |
| Working agent on AWS, Decider meaningful decision + Bedrock generation | Implementation in `src/agent.py`; actual execution status in `docs/verification.md`. Do not mark compliant without a real combined run. |
| Exactly one declared pattern and pattern tag | Tool selection; #tool-selection. |
| Required Decider tag | #strands-decider-2b. |
| Public source repository | Local Git repository prepared; GitHub authentication verified; publication pending review. |
| OSI-approved open-source license | Apache-2.0 in `LICENSE`; upstream attribution in `NOTICE`. |
| Clearly labeled reusable pattern | `src/decider.py` + `docs/decision-pattern.md`: typed question/options, enforced wiring, instructions. |
| Written article published on AWS Builder Center | Review `docs/builder-center-article.md`, add final repo/video links and verified observations, publish. |
| Public video showing agent and real Decider decision | Record using `docs/demo-script.md`. Must show actual Decider + Bedrock run, not preview. |
| Video shorter than three minutes | Target 2:45; verify exported duration. Judges need not watch beyond three minutes. |
| Accepted public video host | YouTube, Vimeo, Facebook Video or Youku, per detailed Rules. |
| Video rights | Own narration/screens; no unlicensed music, third-party trademarks or copyrighted material. |
| Original, not previously published agent | Entrant to confirm; this implementation was created for this workspace. |
| Participant eligibility | Entrant must be 18+, have a Builder Center profile, meet residence/employment exclusions and one-entry limit. Read full Rules. |
| Registration and final entry | Entrant joins event, accepts applicable terms, supplies article/repository/video links and both tags. |

## Before publishing

- Run tests, inspect evidence artifacts, and verify at least two combined scenarios.
- Review article/video for truthful claims and synthetic-data labels.
- Check `.env`, runtime caches, logs and AWS files are excluded from Git.
- Scan source and artifacts for credentials/confidential telemetry.
- Replace final-link placeholders in the draft; no placeholder URLs in the submission.
- Confirm public repository visibility, article availability and playable video.
- Confirm the participant meets the detailed Rules; this app cannot verify eligibility.

## Judging rubric

Creativity 30%; effective Decider + Bedrock use/reusable pattern 30%; communication
25%; originality 15%. Measured latency/cost improvements are optional bonuses.
A benchmark is not required and must not be invented. Qualification requires all
three published parts plus genuine Decider usage; missing one is a pass/fail failure.
