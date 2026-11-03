# RAG vs. No-Retrieval Evaluation Report

*Generated 2026-11-03 23:01:47 · generator `openai/gpt-oss-120b` · judge `qwen/qwen3.8-27b` · top-k = 5 · 15 documents / 82 chunks*

## Retrieval quality

- hit@5: **100%**
- MRR: **1.000**

## Answer quality – overall

| Metric | With RAG | Without RAG |
|---|---|---|
| Key-fact recall | 98% | 45% |
| Judge correctness (1-5) | 4.88 | 2.44 |
| Judge completeness (1-5) | 4.88 | 2.50 |
| Hallucination rate | 0% | 44% |
| Abstention rate | 0% | 31% |
| Avg latency (s) | 0.93 | 1.14 |
| Avg tokens / call | 1072 | 462 |

## Answer quality – public-regulatory

| Metric | With RAG | Without RAG |
|---|---|---|
| Key-fact recall | 100% | 65% |
| Judge correctness (1-5) | 4.91 | 3.00 |
| Judge completeness (1-5) | 5.00 | 3.18 |
| Hallucination rate | 0% | 64% |
| Abstention rate | 0% | 0% |
| Avg latency (s) | 0.94 | 1.28 |
| Avg tokens / call | 1070 | 544 |

## Answer quality – internal-company

| Metric | With RAG | Without RAG |
|---|---|---|
| Key-fact recall | 95% | 0% |
| Judge correctness (1-5) | 4.80 | 1.20 |
| Judge completeness (1-5) | 4.60 | 1.00 |
| Hallucination rate | 0% | 0% |
| Abstention rate | 0% | 100% |
| Avg latency (s) | 0.91 | 0.84 |
| Avg tokens / call | 1076 | 281 |

## Per-question results

| ID | Category | Hit | Recall RAG | Recall base | Correct RAG | Correct base | Halluc. RAG | Halluc. base |
|---|---|---|---|---|---|---|---|---|
| Q01 | public-regulatory | ✓ | 100% | 33% | 5 | 2 | no | yes |
| Q02 | public-regulatory | ✓ | 100% | 25% | 5 | 2 | no | yes |
| Q03 | public-regulatory | ✓ | 100% | 67% | 5 | 5 | no | no |
| Q04 | public-regulatory | ✓ | 100% | 100% | 5 | 4 | no | no |
| Q05 | public-regulatory | ✓ | 100% | 33% | 5 | 2 | no | yes |
| Q06 | public-regulatory | ✓ | 100% | 50% | 5 | 1 | no | yes |
| Q07 | public-regulatory | ✓ | 100% | 75% | 4 | 2 | no | yes |
| Q08 | public-regulatory | ✓ | 100% | 100% | 5 | 5 | no | no |
| Q09 | public-regulatory | ✓ | 100% | 100% | 5 | 4 | no | no |
| Q10 | public-regulatory | ✓ | 100% | 100% | 5 | 4 | no | yes |
| Q11 | public-regulatory | ✓ | 100% | 33% | 5 | 2 | no | yes |
| Q12 | internal-company | ✓ | 75% | 0% | 5 | 2 | no | no |
| Q13 | internal-company | ✓ | 100% | 0% | 5 | 1 | no | no |
| Q14 | internal-company | ✓ | 100% | 0% | 5 | 1 | no | no |
| Q15 | internal-company | ✓ | 100% | 0% | 4 | 1 | no | no |
| Q16 | internal-company | ✓ | 100% | 0% | 5 | 1 | no | no |

## Answers side by side

### Q01. What is the difference between a Special 510(k) and a Traditional 510(k), and what are FDA's review goals for each?

**Reference:** A Special 510(k) is for a change to the manufacturer's own legally marketed device where the evaluation method is well established and results can be reviewed in summary or risk-analysis format; FDA aims to review it within 30 days. A Traditional 510(k) can be used in any situation; the MDUFA goal is a decision within 90 FDA days.

**Retrieved:** `02_fda_510k_premarket_notification`, `02_fda_510k_premarket_notification`, `02_fda_510k_premarket_notification`, `02_fda_510k_premarket_notification`, `02_fda_510k_premarket_notification`

**With RAG** (recall 100%, judge 5/5):

> A **Special 510(k)** is used only for changes to the manufacturer’s own cleared device when the evaluation method is well‑established and can be summarized in a risk analysis; the FDA’s goal is to complete its review within **30 days**.  
> 
> A **Traditional 510(k)** is the standard, all‑purpose pathway for any new device or change not covered by the special or abbreviated routes; under the MDUFA performance goals the FDA aims to make a decision within **90 FDA days** (the clock pauses while the submitter answers any questions)[1][2].

**Without RAG** (recall 33%, judge 2/5):

> **Special 510(k) vs. Traditional 510(k)**  
> 
> | Feature | Special 510(k) | Traditional 510(k) |
> |---------|----------------|--------------------|
> | **When used** | Device is **substantially equivalent** to a **predicate already cleared** and the change is limited to **design, labeling, or manufacturing** (e.g., size, material, software version). | Any other submission where the device is **not covered** by the Special pathway (new device, new intended use, or major design change). |
> | **Content requirements** | • Only **comparative data** showing that the new device is **identical** to the predicate except for the specific change.<br>• No need for full **design history file (DHF)**, **risk analysis**, or **performance testing** beyond what was already submitted for the predicate. | • Full 510(k) dossier: **Device Description, Intended Use, Substantial Equivalence discussion, Performance Testing (bench, animal, clinical as needed),** **Risk Management (ISO 14971),** **Software Documentation (IEC 62304)**, **Biocompatibility (ISO 10993)**, etc. |
> | **Regulatory reference** | 21 CFR 807.92(b)(3) – “Special 510(k)”. | 21 CFR 807.92(a) – “Traditional 510(k)”. |
> | **Review time goal** | **90 calendar days** from receipt (FDA’s “Special 510(k) Review Goal”). | **90 calendar days** for **standard** 510(k) (FDA’s “90‑day review goal”), but historically the median is **120‑180 days** due to additional data. |
> | **FDA review focus** | Verify that the **only difference** is the one claimed and that it does not affect safety/effectiveness. | Evaluate **substantial equivalence** across all aspects, including new testing data, risk analysis, labeling, and compliance with applicable consensus standards. |
> | **Typical outcome** | **Clearance** if the change is truly limited; often **no additional post‑market study** required. | Clearance after full review; may require **post‑market surveillance** or **PMCF** if new risks are identified. |
> 
> **Key FDA goals**  
> 
> * **Special 510(k):** Confirm that the limited change does not introduce new safety or effectiveness concerns; maintain the predicate’s risk profile.  
> * **Traditional 510(k):** Demonstrate overall **substantial equivalence** to a legally marketed device, ensuring that the new device’s **risk/benefit** profile is at least as favorable as the predicate.

*Judge notes – RAG:* The candidate accurately reflects the reference answer regarding the definitions, specific use cases, and FDA review goals (30 days for Special, 90 FDA days for Traditional) for both 510(k) types.  
*Judge notes – baseline:* The candidate incorrectly states the review goal for a Special 510(k) is 90 calendar days (reference says 30 days) and incorrectly claims Traditional 510(k) is for 'any other submission' rather than 'any situation', while also inventing specific CFR citations and content requirements not present in the reference.

### Q02. Within how many days must a manufacturer submit 30-day and 5-day Medical Device Reports to FDA, and what triggers a 5-day report?

**Reference:** Under 21 CFR 803, 30-day reports are due within 30 calendar days of becoming aware of a death, serious injury or reportable malfunction. 5-day reports are due within 5 work days when the event necessitates remedial action to prevent an unreasonable risk of substantial harm to public health, or when FDA requests 5-day reports in writing.

**Retrieved:** `08_fda_postmarket_mdr_recalls`, `14_veridian_sop_qa014_complaint_handling`, `08_fda_postmarket_mdr_recalls`, `08_fda_postmarket_mdr_recalls`, `08_fda_postmarket_mdr_recalls`

**With RAG** (recall 100%, judge 5/5):

> - **30‑day MDR** – The manufacturer must submit the report **within 30 calendar days of becoming aware** of information that reasonably suggests the device may have caused or contributed to a death, a serious injury, or a malfunction that could lead to death or serious injury if it recurs[1].  
> 
> - **5‑day MDR** – The manufacturer must submit the report **within 5 work days of becoming aware** that the reportable event requires remedial action to prevent an unreasonable risk of substantial harm to public health, or when the FDA has issued a written request for a 5‑day report[1].  
> 
> Thus, the trigger for a 5‑day report is the need for immediate corrective action to avert substantial harm (or an FDA‑issued request).

**Without RAG** (recall 25%, judge 2/5):

> **Submission Timelines**
> 
> | Report type | FDA deadline after event | Reference |
> |-------------|--------------------------|-----------|
> | **30‑day Medical Device Report (MDR)** | **Within 30 calendar days** of the manufacturer’s initial knowledge that the event may have caused or contributed to a death or serious injury, or that a malfunction could lead to death or serious injury. | 21 CFR 820.100(b)(1) |
> | **5‑day MDR (also called “5‑day report” or “initial report”)** | **Within 5 calendar days** of the same knowledge (death, serious injury, or a malfunction that could cause death/serious injury). | 21 CFR 820.100(b)(2) |
> 
> **What triggers the 5‑day report?**  
> A 5‑day MDR is required when the manufacturer becomes aware of any of the following:
> 
> 1. **Death** of a patient, user, or other person caused by or possibly caused by the device.  
> 2. **Serious injury** (as defined in 21 CFR 803.11) caused by or possibly caused by the device.  
> 3. **Device malfunction** that **could** reasonably be expected to cause or contribute to a death or serious injury if the malfunction were to recur.  
> 
> If the event meets any of these criteria, the manufacturer must submit the initial 5‑day report (including a brief description, device identification, and patient outcome) within 5 days, then follow up with a more detailed 30‑day report (or a supplemental report) within the 30‑day window.

*Judge notes – RAG:* The candidate accurately states the 30-day and 5-day submission deadlines and correctly identifies the triggers for 5-day reports (remedial action for substantial harm or FDA written request) in full agreement with the reference.  
*Judge notes – baseline:* The candidate incorrectly states that 5-day reports are due within 5 calendar days (reference says 5 work days) and incorrectly lists death/serious injury as triggers for the 5-day report (reference specifies remedial action to prevent unreasonable risk or FDA request), while also citing the wrong CFR section (820 instead of 803).

### Q03. What are the three IEC 62304 software safety classes?

**Reference:** Class A: no injury or damage to health is possible; Class B: non-serious injury is possible; Class C: death or serious injury is possible.

**Retrieved:** `06_iec62304_medical_device_software`, `06_iec62304_medical_device_software`, `06_iec62304_medical_device_software`, `06_iec62304_medical_device_software`, `06_iec62304_medical_device_software`

**With RAG** (recall 100%, judge 5/5):

> The IEC 62304 standard defines three software safety classes:
> 
> 1. **Class A** – no injury or damage to health is possible.  
> 2. **Class B** – non‑serious injury is possible.  
> 3. **Class C** – death or serious injury is possible.  
> 
> These definitions are provided in the standard’s safety‑classification section[1].

**Without RAG** (recall 67%, judge 5/5):

> IEC 62304 defines three software safety classes based on the potential impact of software failure on the patient or user:
> 
> | Class | Definition (Clause 4.2) | Example Impact |
> |-------|--------------------------|----------------|
> | **Class A** | No injury or damage to health is possible. | Software that provides non‑critical data (e.g., display of historical logs). |
> | **Class B** | Possible injury or damage to health, but not serious injury. | Software that controls non‑critical device functions (e.g., alarm thresholds). |
> | **Class C** | May cause **serious injury** or death. | Software that directly controls life‑support or therapeutic functions (e.g., infusion pump dosing algorithm). |
> 
> These classes drive the required rigor of development processes, verification/validation activities, and risk‑management documentation throughout the software life‑cycle. (IEC 62304:2006/2015, Clause 4.2).

*Judge notes – RAG:* The candidate answer accurately lists all three IEC 62304 software safety classes with definitions that perfectly match the reference answer.  
*Judge notes – baseline:* The candidate correctly identifies all three IEC 62304 safety classes with definitions that align perfectly with the reference answer, and the additional examples and context do not contradict the ground truth.

### Q04. In what order of priority must risk control options be applied under ISO 14971:2019?

**Reference:** 1) Inherent safety by design and manufacture; 2) protective measures in the medical device itself or in the manufacturing process; 3) information for safety and, where appropriate, training of users.

**Retrieved:** `05_iso14971_risk_management`, `05_iso14971_risk_management`, `05_iso14971_risk_management`, `05_iso14971_risk_management`, `05_iso14971_risk_management`

**With RAG** (recall 100%, judge 5/5):

> The ISO 14971:2019 standard specifies that risk‑control options must be applied in the following priority order:
> 
> 1. **Inherent safety by design and manufacture**  
> 2. **Protective measures in the device or its manufacturing process** (e.g., alarms, guards, interlocks)  
> 3. **Information for safety and, where appropriate, user training** (e.g., warnings in the Instructions for Use)  
> 
> These three tiers are required to be implemented sequentially, with verification of implementation and effectiveness for each option. [1]

**Without RAG** (recall 100%, judge 4/5):

> **ISO 14971:2019 – Hierarchy of Risk‑Control Options (Clause 5.3)**  
> 
> 1. **Inherent safety by design** – Eliminate the hazard or the hazardous situation altogether (e.g., redesign, substitute a safer material).  
> 2. **Protective measures in the device** – Apply engineering controls that reduce the probability or severity of harm (e.g., shielding, interlocks, alarms).  
> 3. **Protective measures in the manufacturing/maintenance process** – Controls that limit risk during production, installation, or servicing (e.g., process controls, quality checks).  
> 4. **Information for safety** – Provide warnings, instructions for use, training, or labeling that enable the user to avoid the risk.  
> 5. **Residual risk acceptance** – After all feasible controls are applied, evaluate whether the remaining risk is acceptable per the risk‑acceptance criteria.
> 
> The standard states that **risk elimination** (inherent safety) is the most preferred option; each subsequent level is considered only when the higher‑level option is not practicable or sufficient. (ISO 14971:2019, Clause 5.3, Table 5‑1).

*Judge notes – RAG:* The candidate answer accurately lists the three priority levels of risk control options as defined in the reference answer, with no contradictions or hallucinations.  
*Judge notes – baseline:* The candidate correctly identifies the three priority levels from the reference answer, although it splits the second level (protective measures in the device or manufacturing process) into two separate items and adds a fifth step (residual risk acceptance) which is a subsequent evaluation step rather than a risk control option in the hierarchy itself.

### Q05. Under EU MDR Article 87, what are the deadlines for reporting serious incidents to competent authorities?

**Reference:** Immediately after establishing a causal relationship (or reasonable possibility) and not later than 15 days after awareness; for a serious public health threat not later than 2 days; for death or an unanticipated serious deterioration in health not later than 10 days.

**Retrieved:** `07_eu_mdr_2017_745`, `07_eu_mdr_2017_745`, `14_veridian_sop_qa014_complaint_handling`, `07_eu_mdr_2017_745`, `07_eu_mdr_2017_745`

**With RAG** (recall 100%, judge 5/5):

> Under EU MDR Article 87 the manufacturer must notify the competent authority of a serious incident:
> 
> * **General serious incident** – no later than **15 days** after becoming aware of the incident (once a causal relationship is established or reasonably possible)[1].  
> * **Serious public‑health threat** – **immediately** and in any case **no later than 2 days** after awareness[1].  
> * **Death or an unanticipated serious deterioration in a person’s health** – **immediately** and in any case **no later than 10 days** after awareness[1].

**Without RAG** (recall 33%, judge 2/5):

> **EU MDR – Article 87 (Reporting of serious incidents and field‑safety corrective actions)**  
> 
> | Event type | Deadline for initial report to the Competent Authority* | Reference (MDR) |
> |------------|----------------------------------------------------------|-----------------|
> | **Serious incident** (any incident that could have led to death or serious deterioration of health, or that actually did) | **Within 15 calendar days** after the manufacturer becomes aware of the incident. | Article 87(1) – “within 15 days” |
> | **Field‑safety corrective action (FSCA)** (including recalls, safety notices, or any action taken to reduce risk) | **Within 30 calendar days** after the manufacturer becomes aware of the need for the action. | Article 87(2) – “within 30 days” |
> 
> \*The clock starts on the day the manufacturer **first becomes aware** of the incident or the need for the corrective action (i.e., when the information is available to the responsible person).  
> 
> Additional notes  
> 
> * A **follow‑up report** must be submitted within 90 days if the final outcome is not yet known (Article 87(3)).  
> * If the incident is classified as a **“serious incident with a fatal outcome”**, the 15‑day deadline still applies, but the report must include all available details of the fatality.  
> * Reports are made to the **competent authority of the Member State where the incident occurred** (or the “reference” Member State for the device).  
> 
> These timelines are mandatory; failure to meet them can result in enforcement actions under Articles 100–102 MDR.

*Judge notes – RAG:* The candidate answer accurately reflects all specific deadlines and conditions outlined in the reference answer for general incidents, public health threats, and death/serious deterioration.  
*Judge notes – baseline:* The candidate fails to mention the specific 2-day and 10-day deadlines for serious public health threats and death/unanticipated serious deterioration, and incorrectly states that the 15-day deadline applies to fatal outcomes (contradicting the 10-day rule in the reference).

### Q06. When did FDA's Quality Management System Regulation (QMSR) take effect, and which standard does it incorporate by reference?

**Reference:** The QMSR (amended 21 CFR Part 820, final rule published February 2, 2024) became effective on February 2, 2026 and incorporates ISO 13485:2016 by reference.

**Retrieved:** `04_qmsr_iso13485_design_controls`, `04_qmsr_iso13485_design_controls`, `04_qmsr_iso13485_design_controls`, `04_qmsr_iso13485_design_controls`, `04_qmsr_iso13485_design_controls`

**With RAG** (recall 100%, judge 5/5):

> The FDA’s Quality Management System Regulation (QMSR) became effective on **February 2 2026** and it incorporates by reference **ISO 13485:2016, “Medical devices – Quality management systems – Requirements for regulatory purposes.”**[1]

**Without RAG** (recall 50%, judge 1/5):

> **Effective date:** The FDA’s Quality Management System Regulation (QMSR) – 21 CFR 820 – became effective **May 28 1996** (with a 6‑month compliance grace period ending Nov 28 1996).
> 
> **Standard incorporated by reference:** 21 CFR 820 § 820.30(b) incorporates **ISO 13485:2016** (the current edition) by reference for the design‑control sub‑part of the regulation. Earlier versions of the regulation referenced ISO 13485:2003, but the latest amendment (effective May 2022) updates the reference to the 2016 edition.

*Judge notes – RAG:* The candidate correctly identifies the effective date (February 2, 2026) and the incorporated standard (ISO 13485:2016), matching all key facts in the reference answer.  
*Judge notes – baseline:* The candidate provides the incorrect effective date (1996 instead of 2026) and incorrectly claims the standard is only incorporated for design controls, contradicting the reference which states the QMSR became effective on February 2, 2026.

### Q07. What must a premarket submission for a cyber device include under section 524B of the FD&C Act?

**Reference:** A plan to monitor, identify and address postmarket vulnerabilities and exploits including coordinated vulnerability disclosure; processes providing reasonable assurance the device is cybersecure with postmarket updates and patches (regular cycle and out-of-cycle for critical vulnerabilities); and a Software Bill of Materials covering commercial, open-source and off-the-shelf components.

**Retrieved:** `10_medical_device_cybersecurity`, `10_medical_device_cybersecurity`, `10_medical_device_cybersecurity`, `10_medical_device_cybersecurity`, `02_fda_510k_premarket_notification`

**With RAG** (recall 100%, judge 4/5):

> A pre‑market submission for a “cyber device” must contain the following elements required by section 524B:
> 
> 1. **A post‑market cybersecurity management plan** – a documented process to monitor, identify, and address vulnerabilities and exploits in a reasonable time, including coordinated vulnerability disclosure procedures[4].  
> 2. **Evidence of a cyber‑secure development and maintenance program** – processes that assure the device and its related systems are cyber‑secure, with a schedule for regular updates/patches for known unacceptable vulnerabilities and out‑of‑cycle patches for critical vulnerabilities that could cause uncontrolled risks[4].  
> 3. **A Software Bill of Materials (SBOM)** – listing all commercial, open‑source, and off‑the‑shelf software components used in the device[2][4].  
> 4. **Cybersecurity risk assessment** – a risk assessment separate from the ISO 14971 safety assessment that evaluates exploitability (not probability) and links to the overall risk management file[3].  
> 5. **Security architecture documentation, testing results, and labeling** – including threat modeling, penetration/fuzz testing, vulnerability scanning, unresolved anomaly assessment, and labeling that describes security controls and the device’s end‑of‑support date[3].  
> 
> FDA began refusing to accept pre‑market submissions that omit this information as of **October 1, 2023**[2].

**Without RAG** (recall 75%, judge 2/5):

> **Section 524(b) FD&C Act – Premarket Submission for a “Cyber‑Device” (software‑only or software‑driven medical device)**  
> 
> A 510(k) or De Novo submission that is classified as a “cyber‑device” must contain, in addition to the standard content required by 21 CFR 807.92, the following items specifically called out in § 524(b) (effective 2024‑05‑01):
> 
> | Item | What to Include | Clause Reference |
> |------|----------------|-------------------|
> | **1. Device Description** | Full description of hardware, software, and any network interfaces; architecture diagram showing data flow, communication protocols, and cloud components. | § 524(b)(1) |
> | **2. Cyber‑Security Risk Management** | Risk analysis per **ISO 14971** plus a dedicated **cyber‑risk** assessment (threat modeling, attack surface, vulnerability analysis). Include risk control measures (encryption, authentication, patch management). | § 524(b)(2) |
> | **3. Software Development Lifecycle (SDLC)** | Evidence of compliance with **IEC 62304** (development plan, verification/validation reports, configuration management). | § 524(b)(3) |
> | **4. Usability & Human‑Factors** | Usability engineering file per **IEC 62366‑1** (use‑case scenarios, user interface mock‑ups, validation results). | § 524(b)(4) |
> | **5. Biocompatibility (if applicable)** | ISO 10993 data for any patient‑contacting hardware components. | § 524(b)(5) |
> | **6. Post‑Market Cyber‑Monitoring Plan** | Detailed plan for continuous security monitoring, incident response, and periodic vulnerability assessments (minimum quarterly). | § 524(b)(6) |
> | **7. Labeling & Instructions for Use** | Include security‑related labeling (e.g., required password policies, update procedures). | § 524(b)(7) |
> | **8. Software Bill of Materials (SBOM)** | Complete list of third‑party libraries, versions, and known CVEs at submission time. | § 524(b)(8) |
> | **9. Validation of Remote Updates** | Evidence that OTA (over‑the‑air) update mechanisms are validated for integrity, authenticity, and rollback safety. | § 524(b)(9) |
> | **10. FDA‑Recognized Standards Cross‑Reference** | Table mapping each requirement to the applicable FDA guidance (e.g., “Content of Premarket Submissions for Software‑Based Medical Devices” guidance, 2023). | § 524(b)(10) |
> 
> **Timing:** All above documentation must be submitted with the initial filing; any post‑submission changes (e.g., new vulnerabilities) must be reported within **15 calendar days** per 21 CFR 820.30(c).  
> 
> If any of these elements are missing, the FDA will issue a **Deficiency Letter** and may place the submission on **“Hold”** until resolved.

*Judge notes – RAG:* The candidate correctly identifies all three key components required by the reference (postmarket plan, cybersecure processes, and SBOM) and adds additional details (risk assessment, architecture docs, dates) that are consistent with FDA regulations but not explicitly in the reference; since the reference is treated as the ground truth for the specific question, the extra details are not contradictions but rather supplementary context, so no hallucination is flagged, though strict adherence to the reference would suggest a perfect 5 for correctness if the extra details are considered 'invented' relative to the provided text, however, in regulatory contexts, these are standard requirements, so 4 is a safe score for 'mostly correct' while acknowledging the extra info, or 5 if we assume the reference is a summary. Given the instruction 'treat it as correct', the candidate's extra points are not contradictions. Let's look closer: The reference lists 3 items. The candidate lists 5. Items 1, 2, and 3 match the reference perfectly. Items 4 and 5 are extra. Are they hallucinations? They are specific facts. If they are not in the reference, are they 'invented'? The prompt says 'hallucination: true if the candidate asserts specific facts... that contradict the reference or are invented.' Since the reference is the 'ground truth from the organisation's document collection', any fact not in it might be considered 'invented' in the context of this strict grading task if the reference is exhaustive. However, usually, 'invented' means false. If the extra facts are true in the real world but not in the reference, is it a hallucination? The prompt says 'treat it as correct even if it describes a fictional company'. It doesn't say the reference is the *only* truth, but it is the ground truth for the question. If the question asks 'What must... include', and the reference lists A, B, C, and the candidate lists A, B, C, D, E, the candidate is more complete. If D and E are not in the reference, are they wrong? In a strict QA setting based *only* on the provided reference, extra information is often penalized or considered hallucination if it's not supported by the source text. However, the definition of hallucination here is 'contradict the reference or are invented'. If D and E are true facts about FDA 524B, they are not 'invented' in the sense of being false. But if the grader only has the reference, it cannot verify D and E. Let's look at the 'correctness' score. 5 = all stated facts agree with the reference. The candidate states facts 4 and 5. Do they agree with the reference? The reference doesn't mention them. So they don't 'agree' in the sense of being present. But they don't contradict. Usually, 'agree' means 'are consistent with'. If the reference is a subset, the candidate is consistent. However, if the reference is the *complete* answer, then adding extra items might be seen as incorrect if those items are not actually required by 524B specifically (though they are part of the broader cybersecurity guidance). Actually, Section 524B specifically mandates the plan, the processes, and the SBOM. The risk assessment and architecture docs are part of the *processes* or the *plan* but not separate statutory requirements in the same list. The candidate separates them. This might be a slight over-specification. But is it a hallucination? No, because they are real requirements. Is it a correctness issue? The core answer is correct. I will give 5 for completeness because it covers all reference points. For correctness, since the extra points are factually true in the real world (FDA guidance), and the prompt says 'treat it as correct' regarding the reference, it implies the reference is the standard. If the candidate adds true info, it's usually not penalized heavily unless it contradicts. I will stick with 4 or 5. Let's look at the hallucination definition again: 'invented'. If the model made up the date 'October 1, 2023', that is a specific fact. Is it in the reference? No. Is it true? Yes, FDA started enforcing this around then. But if the reference doesn't have it, a strict grader relying *only* on the reference might flag it as unsupported. However, 'invented' usually implies falsehood. I will assume the candidate is factually accurate. The main risk is that the candidate lists items 4 and 5 as distinct requirements of 524B, whereas 524B textually requires the plan, processes, and SBOM. The risk assessment is part of the processes. So listing it as a separate top-level requirement is a slight structural inaccuracy but not a factual error. I will rate correctness 4 to be safe, acknowledging the extra details not in the reference. Actually, looking at the reference, it is a summary. The candidate is a detailed expansion. I will give 5 for completeness. For correctness, 4 is appropriate because it includes details not in the reference which a strict grader might view as 'not agreeing' with the provided ground truth text. Wait, 'all stated facts agree with the reference'. If the reference says 'A, B, C' and the candidate says 'A, B, C, D, E', do the facts D and E agree with the reference? The reference is silent on D and E. Silence is not agreement. Therefore, strictly speaking, they do not agree with the reference (which is the ground truth). So correctness should be lower. 3 or 4. Let's go with 4. Hallucination: False, because they are not false, just extra. Abstained: False.  
*Judge notes – baseline:* The candidate invents specific clause numbers, dates, and requirements (e.g., ISO 14971, IEC 62304, 15-day reporting) that are not in the reference and fails to mention the specific requirement for coordinated vulnerability disclosure and the distinction between regular and out-of-cycle updates.

### Q08. What is the minimum number of participants FDA recommends for each distinct user group in human factors validation testing?

**Reference:** FDA recommends a minimum of 15 participants from each distinct user group.

**Retrieved:** `12_human_factors_usability`, `12_human_factors_usability`, `12_human_factors_usability`, `09_unique_device_identification`, `10_medical_device_cybersecurity`

**With RAG** (recall 100%, judge 5/5):

> FDA recommends a minimum of **15 participants** from each distinct user group for human‑factors validation testing[1].

**Without RAG** (recall 100%, judge 5/5):

> **FDA Human‑Factors Validation (Usability) Guidance (2016, “Applying Human Factors and Usability Engineering to Medical Devices”)**  
> 
> - **Minimum sample size:** **≥ 15 participants** for each distinct user group (e.g., patients, caregivers, clinicians, technicians).  
> - **Rationale:** This number provides sufficient statistical power to detect use‑related hazards that could lead to use errors, while remaining practical for most device programs.  
> 
> *Reference:* FDA Guidance for Industry and FDA Staff, **Human Factors and Usability Engineering – Applying Human Factors and Usability Engineering to Medical Devices**, § 4.2 (Validation testing), 21 CFR 820.30(b).

*Judge notes – RAG:* The candidate answer correctly identifies the minimum number of participants (15) as stated in the reference answer.  
*Judge notes – baseline:* The candidate correctly identifies the minimum number of participants (15) as stated in the reference, and the additional context provided does not contradict the ground truth.

### Q09. How are the contact duration categories defined in ISO 10993-1?

**Reference:** Limited exposure (A): 24 hours or less; prolonged exposure (B): more than 24 hours up to 30 days; long-term exposure (C): more than 30 days (cumulative contact).

**Retrieved:** `11_biocompatibility_iso10993`, `11_biocompatibility_iso10993`, `11_biocompatibility_iso10993`, `11_biocompatibility_iso10993`, `06_iec62304_medical_device_software`

**With RAG** (recall 100%, judge 5/5):

> ISO 10993‑1 defines three contact‑duration categories:
> 
> * **Limited exposure (Category A)** – cumulative contact of **24 hours or less**.  
> * **Prolonged exposure (Category B)** – cumulative contact of **more than 24 hours up to 30 days**.  
> * **Long‑term exposure (Category C)** – cumulative contact of **more than 30 days**.  
> 
> These definitions are taken directly from ISO 10993‑1’s “Categorization by Duration of Contact” section[2].

**Without RAG** (recall 100%, judge 4/5):

> **ISO 10993‑1:2021 – Contact Duration Categories**
> 
> | Category | Intended Use (Typical Clinical Scenario) | Maximum Continuous Contact Time* | Example Devices |
> |----------|------------------------------------------|----------------------------------|-----------------|
> | **Limited (≤ 24 h)** | Short‑term exposure (e.g., diagnostic probes, surgical instruments) | ≤ 24 hours | Endoscopic camera heads, catheters used for a single procedure |
> | **Prolonged (≤ 30 days)** | Medium‑term exposure where device remains in situ for days to weeks (e.g., temporary implants) | > 24 h and ≤ 30 days | Temporary pacing leads, wound dressings, external fixation pins |
> | **Permanent (> 30 days)** | Long‑term or lifelong implantation (e.g., orthopedic, cardiovascular implants) | > 30 days (often “indefinite”) | Hip prostheses, pacemaker generators, intra‑ocular lenses |
> 
> \*The “maximum continuous contact time” is the **upper limit** for which the biological evaluation data must be applicable. For **limited** devices, a single 24‑hour extraction is sufficient; for **prolonged** devices, testing must cover up to 30 days (often using 7‑day and 30‑day extracts); for **permanent** devices, testing must simulate > 30 days (commonly 60‑day or 90‑day extracts, or accelerated aging).
> 
> **Key clause:** ISO 10993‑1:2021, **Clause 5.2** defines the three categories and links them to the required duration of biocompatibility testing (e.g., extraction times, implantation periods).

*Judge notes – RAG:* The candidate answer accurately lists all three contact duration categories (A, B, C) with the exact time thresholds specified in the reference answer.  
*Judge notes – baseline:* The candidate correctly identifies the three contact duration categories and their time thresholds (≤24h, >24h to ≤30d, >30d) as defined in the reference, although it uses the term 'Permanent' instead of 'Long-term' and adds extra context not in the reference.

### Q10. How often must the Periodic Safety Update Report (PSUR) be updated for Class IIa versus Class IIb and Class III devices under the EU MDR?

**Reference:** Class IIa: when necessary and at least every two years. Class IIb and Class III: at least annually.

**Retrieved:** `07_eu_mdr_2017_745`, `07_eu_mdr_2017_745`, `07_eu_mdr_2017_745`, `07_eu_mdr_2017_745`, `07_eu_mdr_2017_745`

**With RAG** (recall 100%, judge 5/5):

> Under the EU MDR, the Periodic Safety Update Report (PSUR) must be:
> 
> * **Class IIa devices:** updated when necessary **and at least every 2 years**.  
> * **Class IIb and Class III devices:** updated **at least annually**.  
> 
> These requirements are set out in Articles 83‑86 of the MDR [1].

**Without RAG** (recall 100%, judge 4/5):

> **EU MDR 2021/745 – Periodic Safety Update Report (PSUR) frequency**
> 
> | Device class (MDR) | PSUR update interval* | MDR reference |
> |--------------------|----------------------|----------------|
> | **Class IIa**      | **Every 2 years**    | Annex II, Section 23.1 (b) – “for class IIa devices, the PSUR shall be submitted at least every second year” |
> | **Class IIb**      | **Every 1 year**     | Annex II, Section 23.1 (b) – “for class IIb devices, the PSUR shall be submitted at least annually” |
> | **Class III**      | **Every 1 year**     | Annex II, Section 23.1 (b) – same requirement as class IIb |
> 
> \*The PSUR must be submitted to the competent authority (or notified body for devices under its surveillance) **no later than 30 days after the end of the reporting period**.  
> 
> If a device is placed on the market in a limited number of Member States only, the same intervals apply, but the report may be submitted to each concerned authority rather than a single EU‑wide submission.  
> 
> (If the manufacturer has a post‑market surveillance (PMS) plan that includes a **PMS‑Plan** and **PMS‑Report**, the PSUR is the summary of those activities for the specified interval.)

*Judge notes – RAG:* The candidate accurately states the update frequencies for Class IIa (every 2 years) and Class IIb/III (annually) devices, matching the reference exactly, and the cited article range is factually correct for PSUR requirements under EU MDR.  
*Judge notes – baseline:* The candidate correctly identifies the frequency intervals (2 years for IIa, 1 year for IIb/III) but hallucinates specific regulatory details such as the MDR number (2021/745 instead of 2017/745), the specific Annex/Section reference (Annex II Section 23.1(b) is incorrect; PSUR requirements are in Article 86 and Annex III), and the submission deadline (30 days is not the standard MDR requirement for PSURs, which is typically tied to the end of the reporting period or specific national timelines, but the specific '30 days' claim is unsupported/invented in this context).

### Q11. What is FDA's MDUFA review goal for a De Novo classification request, and what happens once it is granted?

**Reference:** FDA aims to decide within 150 FDA review days. Granting a De Novo creates a new classification regulation, and the device can serve as a predicate for future 510(k)s.

**Retrieved:** `03_fda_pma_and_de_novo`, `03_fda_pma_and_de_novo`, `03_fda_pma_and_de_novo`, `03_fda_pma_and_de_novo`, `03_fda_pma_and_de_novo`

**With RAG** (recall 100%, judge 5/5):

> FDA’s MDUFA goal is to complete the review of a De Novo classification request within **150 FDA review days**. When the request is granted, **FDA creates a new classification regulation for that device type**, allowing the device to serve as a predicate for future 510(k) submissions. [1]

**Without RAG** (recall 33%, judge 2/5):

> **FDA MDUFA Review Goal for a De Novo Request**  
> - **Target review time:** **120 calendar days** from the date the complete De Novo submission is received (MDUFA II, § 520.5; updated in MDUFA III to 120 days).  
> - This clock starts after the FDA determines the submission is “complete” (i.e., all required information per 21 CFR 814.102(e) is present).
> 
> **What Happens When De Novo Is Granted**  
> 
> | Step | Outcome | Regulatory Effect |
> |------|---------|--------------------|
> | **De Novo classification order issued** | The device is assigned to **Class I or Class II** with a new special control (or recognized general controls). | The device now has a **predicate** for future 510(k) submissions. |
> | **Device can be marketed** | Manufacturer may **commercially distribute** the device in the U.S. (subject to any post‑market requirements in the order). | No further pre‑market submission is needed for that device, unless a change triggers a new 510(k) or PMA. |
> | **Future submissions** | Other manufacturers can use the newly classified device as a **predicate** for 510(k) clearance. | Accelerates market entry for similar devices and expands the “cleared” device landscape. |
> 
> *If the FDA issues a “Not Granted” decision, the sponsor must either (a) submit a traditional PMA, (b) pursue a 510(k) using an existing predicate, or (c) address the deficiencies and resubmit.*

*Judge notes – RAG:* The candidate answer accurately reflects the 150-day review goal and the consequence of creating a new classification regulation for predicate use, matching the reference perfectly.  
*Judge notes – baseline:* The candidate incorrectly states the review goal as 120 calendar days, whereas the reference specifies 150 FDA review days, constituting a factual hallucination, though it correctly identifies the predicate status outcome.

### Q12. What should a nurse do when the Veridian InfusePro 300 infusion pump displays error code E-401?

**Reference:** E-401 is a system fault (internal error). Stop the infusion, remove the pump from service, label it 'Do Not Use', and contact Veridian Technical Service; do not attempt to restart it on a patient.

**Retrieved:** `13_veridian_infusepro300_ifu`, `13_veridian_infusepro300_ifu`, `13_veridian_infusepro300_ifu`, `13_veridian_infusepro300_ifu`, `15_veridian_fsn_2026_07_battery`

**With RAG** (recall 75%, judge 5/5):

> When error code **E‑401** appears, the nurse must :
> 
> 1. **Stop the infusion immediately.**  
> 2. **Remove the pump from service** and place a “Do Not Use” label on it.  
> 3. **Contact Veridian Technical Service** for assistance; do not try to restart the pump on a patient.  
> 
> These steps are specified in the alarm and error code guidance for E‑401[1].

**Without RAG** (recall 0%, judge 2/5):

> I’m sorry, but I don’t have specific information on the Veridian InfusePro 300 infusion pump or its error‑code meanings. For patient safety, the nurse should follow the device’s user manual and the facility’s standard operating procedures, which typically include:
> 
> 1. **Stop the infusion** and verify the patient’s status.  
> 2. **Check the pump’s display** for any additional prompts or alerts.  
> 3. **Consult the troubleshooting guide** in the user manual for error E‑401.  
> 4. **Contact biomedical engineering/clinical engineering** for technical support if the manual does not resolve the issue.  
> 5. **Document** the error, actions taken, and patient condition in the medical record.
> 
> If you have access to the device’s service manual or the manufacturer’s technical support line, they can provide the exact meaning and corrective steps for error E‑401.

*Judge notes – RAG:* The candidate answer accurately lists all required actions (stop infusion, remove from service, label, contact service, do not restart) matching the reference exactly.  
*Judge notes – baseline:* The candidate abstained from providing the specific error code meaning and required actions (labeling, contacting specific service, no restart) found in the reference, offering only generic safety advice instead.

### Q13. What is the default KVO rate on the Veridian InfusePro 300 and what range can it be configured to?

**Reference:** Default KVO is 1.0 mL/h, configurable from 0.1 to 5.0 mL/h (or the programmed rate, if lower).

**Retrieved:** `13_veridian_infusepro300_ifu`, `13_veridian_infusepro300_ifu`, `13_veridian_infusepro300_ifu`, `13_veridian_infusepro300_ifu`, `13_veridian_infusepro300_ifu`

**With RAG** (recall 100%, judge 5/5):

> The InfusePro 300’s default “keep‑vein‑open” (KVO) rate is **1.0 mL/h**.  
> It can be programmed to any rate between **0.1 mL/h and 5.0 mL/h** (or the programmed infusion rate if that is lower)[1].

**Without RAG** (recall 0%, judge 1/5):

> I’m sorry, but I don’t have that specific information.

*Judge notes – RAG:* The candidate answer accurately states the default KVO rate (1.0 mL/h) and the configurable range (0.1 to 5.0 mL/h, or the programmed rate if lower), matching the reference exactly.  
*Judge notes – baseline:* The candidate declined to answer, providing no information regarding the default or configurable KVO rates.

### Q14. Under Veridian SOP-QA-014, how quickly must Regulatory Affairs complete the reportability assessment, and what conditions require opening a CAPA?

**Reference:** RA completes the initial MDR/vigilance reportability assessment within 2 business days of complaint entry. A CAPA is required for 3 or more complaints with the same failure mode within a rolling 90-day period, any death or serious injury with a confirmed device malfunction, or a statistically significant upward trend.

**Retrieved:** `14_veridian_sop_qa014_complaint_handling`, `14_veridian_sop_qa014_complaint_handling`, `14_veridian_sop_qa014_complaint_handling`, `14_veridian_sop_qa014_complaint_handling`, `14_veridian_sop_qa014_complaint_handling`

**With RAG** (recall 100%, judge 5/5):

> Regulatory Affairs must finish the initial MDR and vigilance reportability assessment **within 2 business days of complaint entry**[1].  
> 
> A CAPA must be opened when any of the following occurs[3]:
> 
> 1. **Three or more complaints** with the same failure mode are recorded within a **rolling 90‑day period**.  
> 2. **Any complaint involving a death or serious injury** where a device malfunction is confirmed.  
> 3. A **statistically significant upward trend** is identified by the monthly trend analysis.

**Without RAG** (recall 0%, judge 1/5):

> I’m not familiar with the specific contents of Veridian SOP‑QA‑014, so I can’t provide the exact turnaround time for the regulatory‑affairs reportability assessment or the precise triggers for opening a CAPA under that document. If you can share the relevant excerpt or provide more context, I can help interpret it.

*Judge notes – RAG:* The candidate answer accurately reflects all specific timeframes and conditions for CAPA initiation stated in the reference answer without adding contradictory or invented details.  
*Judge notes – baseline:* The candidate explicitly declined to answer due to lack of knowledge, providing no factual information from the reference.

### Q15. Which InfusePro 300 pumps are affected by Field Safety Notice FSN-2026-07, and what interim action should users take?

**Reference:** Serial numbers IP3-240001 to IP3-245500 running software 4.2.0 (4.2.1 is not affected). Keep pumps connected to AC mains whenever possible, especially for critical medications, do not rely on the battery gauge, and return the acknowledgement form within 10 days.

**Retrieved:** `15_veridian_fsn_2026_07_battery`, `15_veridian_fsn_2026_07_battery`, `15_veridian_fsn_2026_07_battery`, `15_veridian_fsn_2026_07_battery`, `15_veridian_fsn_2026_07_battery`

**With RAG** (recall 100%, judge 4/5):

> The Field Safety Notice applies to **InfusePro 300 volumetric infusion pumps with serial numbers IP3‑240001 through IP3‑245500 that are running software version 4.2.0** (pumps already on version 4.2.1 are not affected)[2].  
> 
> **Interim user action:** Until the corrective software update is installed, users must **keep the affected pumps plugged into AC mains power whenever possible (especially during infusion of critical or life‑sustaining medications) and must not rely on the battery‑gauge display; instead use a fully charged pump and continuously monitor the infusion**[1].

**Without RAG** (recall 0%, judge 1/5):

> I’m sorry, but I don’t have information on Field Safety Notice FSN‑2026‑07 or the specific InfusePro 300 pump models it covers.

*Judge notes – RAG:* The candidate correctly identifies the affected serial numbers and software version, as well as the primary interim actions (AC mains, battery gauge), but omits the specific requirement to return the acknowledgement form within 10 days.  
*Judge notes – baseline:* The candidate failed to provide any of the required information regarding affected serial numbers, software versions, or interim actions, instead declining to answer.

### Q16. By what date will Veridian install the software fix for the InfusePro 300 battery gauge issue, and how is the action classified in the United States?

**Reference:** Veridian Field Service will install software 4.2.1 on all affected pumps by 15 December 2026; it is a correction reported under 21 CFR Part 806 and conducted as a voluntary Class II recall.

**Retrieved:** `15_veridian_fsn_2026_07_battery`, `15_veridian_fsn_2026_07_battery`, `15_veridian_fsn_2026_07_battery`, `15_veridian_fsn_2026_07_battery`, `15_veridian_fsn_2026_07_battery`

**With RAG** (recall 100%, judge 5/5):

> Veridian will install the software update on all affected InfusePro 300 pumps **by 15 December 2026**. In the United States the action is being reported as a **voluntary Class II recall** under 21 CFR Part 806[1].

**Without RAG** (recall 0%, judge 1/5):

> I’m sorry, but I don’t have the specific information about Veridian’s schedule for installing the software fix for the InfusePro 300 battery‑gauge issue, nor the exact classification of that corrective action in the United States.

*Judge notes – RAG:* The candidate correctly identifies the date, classification, and regulatory code, but omits the specific software version number (4.2.1) mentioned in the reference.  
*Judge notes – baseline:* The candidate explicitly states it lacks the information and declines to answer, providing none of the specific details (date, software version, regulatory classification) found in the reference.
