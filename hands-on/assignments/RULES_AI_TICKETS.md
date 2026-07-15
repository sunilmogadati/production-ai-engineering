# Rules-based AI assignment tickets (Session 3 homework)

Reusable student assignment tickets — homework for Session 3
("When rules break — enter ML"). Extending the rules by hand is the point:
students feel the elif pain the session demonstrated.
Follows the ticket template in `COHORT_COLLABORATION_MODEL.md` (section 4).

Focus: build "intelligent" behavior using rules, and find where it strains.
Reference file: `main_ai.py` (call center domain: classification, lead scoring, upsell, streaming).

Instructor note: rules should be explainable. Every decision should carry a human-readable
reason. Keep additions backward-compatible with the existing `main_ai.py` endpoints.

---

## Ticket 4.1: Add an objection-handling rule

- **Objective:** Detect a common sales objection in a call transcript and suggest a response.
- **File(s) to edit:** `main_ai.py`
- **Acceptance criteria:**
  - Classification recognizes at least one objection category (e.g. "too expensive").
  - The response includes a suggested rebuttal and a reason.
  - Existing `/nlp/classify-call` intents still work.
- **API request example:**
  ```bash
  curl -X POST http://127.0.0.1:8000/nlp/classify-call \
    -H "Content-Type: application/json" \
    -d '{"customer_id":"CUST-1024","call_text":"This is too expensive for me right now."}'
  ```
- **Expected output:** An intent plus an objection label and suggested handling text.
- **Reviewer checklist:**
  - [ ] New rule does not shadow existing intents.
  - [ ] Reason string is present and clear.
  - [ ] One edge case documented in the PR.

---

## Ticket 4.2: Extend lead scoring with a new signal

- **Objective:** Add one more scoring factor with an explainable weight.
- **File(s) to edit:** `main_ai.py`
- **Acceptance criteria:**
  - `/ml/score-lead` incorporates one new input factor (e.g. prior purchases or channel).
  - Score stays within `0-100`.
  - The `reason` explains the new factor's contribution.
- **API request example:**
  ```bash
  curl -X POST http://127.0.0.1:8000/ml/score-lead \
    -H "Content-Type: application/json" \
    -d '{"customer_id":"CUST-1024","product":"vacuum","ad_source":"tv","budget":120,"intent_signal":80}'
  ```
- **Expected output:** A `hot`/`warm`/`cold` decision with a reason that mentions the new factor.
- **Reviewer checklist:**
  - [ ] Score bounds preserved.
  - [ ] Decision thresholds still make sense.
  - [ ] Reason reflects the new factor.

---

## Ticket 4.3: Add an upsell rule for a new segment or product

- **Objective:** Broaden `/ml/upsell` coverage with one explainable branch.
- **File(s) to edit:** `main_ai.py`
- **Acceptance criteria:**
  - A new recommendation branch (new segment behavior, or product-specific bundle).
  - A confidence value that reflects rule strength.
- **API request example:**
  ```bash
  curl -X POST http://127.0.0.1:8000/ml/upsell \
    -H "Content-Type: application/json" \
    -d '{"customer_id":"CUST-1024","base_product":"vacuum","customer_segment":"vip"}'
  ```
- **Expected output:** A recommendation string and a confidence value for the branch.
- **Reviewer checklist:**
  - [ ] New branch does not break existing segments.
  - [ ] Confidence is justified in the PR.

---

## Ticket 4.4: Add a streaming status stage

- **Objective:** Add one meaningful stage to the streaming score demo.
- **File(s) to edit:** `main_ai.py`
- **Acceptance criteria:**
  - `/ml/stream-score` emits one additional labeled stage (e.g. "validation").
  - Stream still ends with a `done` event.
- **API request example:**
  ```bash
  curl -N "http://127.0.0.1:8000/ml/stream-score?customer_id=CUST-1024"
  ```
- **Expected output:** Server-sent events including the new stage, ending in `done`.
- **Reviewer checklist:**
  - [ ] Event format unchanged (`data: {json}`).
  - [ ] Stream terminates cleanly.

---

## Ticket 4.5: Document the "where rules fail" note

- **Objective:** Capture the teaching point that motivates moving to ML.
- **File(s) to edit:** `README.md` or `COHORT_TEACHING_PLAYBOOK.md`
- **Acceptance criteria:**
  - A short note listing 3-5 cases where keyword/threshold rules break down.
  - Links to the Module D (classical ML) roadmap.
- **Expected output:** A concise, teachable "limits of rules" section.
- **Reviewer checklist:**
  - [ ] Examples are concrete.
  - [ ] No broken doc links (`python3 scripts/validate_repo.py`).
