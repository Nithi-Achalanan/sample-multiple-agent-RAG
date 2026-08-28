# RAG Run Log

- Generated at: 2026-08-28T14:26:12
- Status: completed

## Input

```text
What is the maternity leave policy?
```

## Output

I couldn’t locate a maternity‑leave policy in the available documents.  
Could you let me know:

1. **Scope** – Are you asking about your company’s policy, a specific state or country’s law, or a general comparison?  
2. **Details** – Do you need information on paid vs. unpaid leave, eligibility, duration, or benefits?

Once I have that, I can search for the precise policy.

## Relevance Response

### Retrieval response 1

I performed a broad keyword search for information related to maternity leave, parental leave, family leave, and related policies across various jurisdictions. The search results returned only sections of the company’s annual leave policy and international travel policy, none of which contain details about maternity leave.

**Summary of findings**

| Source | Relevance | Key points |
|--------|-----------|------------|
| `knowledge_base.txt#section-5` | Low | Annual leave policy – 12 paid days, no mention of maternity leave |
| `knowledge_base.txt#section-25` | Low | Half‑day annual leave – no maternity leave |
| `knowledge_base.txt#section-23` | Low | Annual leave carry‑over – no maternity leave |
| `knowledge_base.txt#section-24` | Low | Peak period leave – no maternity leave |
| `knowledge_base.txt#section-26` | Low | Annual leave cancellation – no maternity leave |
| `knowledge_base.txt#section-1,3,7,8,9` | Low | International travel policies – no maternity leave |

**Conclusion**

No reliable information about a maternity leave policy was found in the current knowledge base. The query is ambiguous because:

1. **Scope** – It is unclear whether you are asking for a company‑specific policy, a state or federal policy, or an international comparison.
2. **Jurisdiction** – The search included multiple countries (USA, UK, Canada, etc.), but no policy was located for any of them.
3. **Policy type** – The request could refer to paid maternity leave, unpaid leave, eligibility criteria, duration, or benefits, none of which were identified.

**Recommendation**

Please clarify:
- Which organization or jurisdiction’s maternity leave policy you need (e.g., your company, a specific state, or a country’s national law).
- Whether you are interested in paid or unpaid leave, eligibility requirements, duration, or benefits.

Once the scope is narrowed, I can perform a focused search to locate the relevant policy details.

## Relevance Context Log

### Context 1

- Source: `knowledge_base.txt#section-25`
- Matched keywords: parental leave, family leave, leave policy

```text
[SECTION: Annual Leave Policy]
Title: Half-Day Annual Leave

Employees may request annual leave in half-day increments.

Half-day leave requests must be submitted through
the normal leave management system.

Manager approval is required before taking the leave.
```

### Context 2

- Source: `knowledge_base.txt#section-5`
- Matched keywords: parental leave, leave policy

```text
[SECTION: Annual Leave Policy]
Title: Annual Leave Policy

Full-time employees receive 12 days of paid annual leave per year.

Leave requests of more than three consecutive working days
should be submitted at least seven days in advance.

All leave requests require manager approval.
```

### Context 3

- Source: `knowledge_base.txt#section-23`
- Matched keywords: parental leave, leave policy

```text
[SECTION: Annual Leave Policy]
Title: Annual Leave Carryover

Employees are encouraged to use their annual leave within
the year in which it is granted.

Up to five unused annual leave days may be carried forward
to the following year.

Additional carryover requires HR approval.
```

### Context 4

- Source: `knowledge_base.txt#section-24`
- Matched keywords: parental leave, leave policy

```text
[SECTION: Annual Leave Policy]
Title: Peak Period Leave Requests

Managers may limit annual leave during critical business periods
when sufficient staffing is required.

Employees should submit leave requests as early as possible
during these periods.

Approval will depend on operational requirements.
```

### Context 5

- Source: `knowledge_base.txt#section-26`
- Matched keywords: parental leave, leave policy

```text
[SECTION: Annual Leave Policy]
Title: Annual Leave Cancellation

Employees who need to cancel approved annual leave
should inform their manager as soon as possible.

Cancelled leave days will be returned to the employee's
available leave balance.

Changes remain subject to manager approval.
```

### Context 6

- Source: `knowledge_base.txt#section-1`
- Matched keywords: leave policy

```text
[SECTION: International Travel Policy]
Title: International Travel Policy

Employees who travel internationally for business must obtain approval
from their direct manager before booking any flights.

Economy class is required for flights shorter than six hours.
Business class may be approved for flights longer than six hours.

Employees must purchase company-approved travel insurance before departure.
```

### Context 7

- Source: `knowledge_base.txt#section-3`
- Matched keywords: leave policy

```text
[SECTION: Domestic Travel Policy]
Title: Domestic Travel Policy

Domestic business travel must be approved by the employee's manager.

Employees should use company-approved transportation when available.

Hotel accommodation may be reimbursed when an overnight stay is required.
```

### Context 8

- Source: `knowledge_base.txt#section-7`
- Matched keywords: leave policy

```text
[SECTION: International Travel Policy]
Title: Passport and Visa Requirements

Employees are responsible for ensuring that their passports remain valid
for the entire duration of an international business trip.

Required business visas should be arranged before departure.

Reasonable visa application fees may be reimbursed by the company
when the travel has been approved.
```

### Context 9

- Source: `knowledge_base.txt#section-8`
- Matched keywords: leave policy

```text
[SECTION: International Travel Policy]
Title: International Flight Booking

International flights should be booked through the company's approved
travel agency or booking platform.

Employees should make reservations at least 14 days before departure
whenever practical.

Changes to approved bookings should be reported to the employee's manager.
```

### Context 10

- Source: `knowledge_base.txt#section-9`
- Matched keywords: leave policy

```text
[SECTION: International Travel Policy]
Title: International Ground Transportation

Employees may use taxis, public transportation, or company-approved
ride-hailing services while traveling internationally.

Premium transportation services should only be used when necessary
for safety or business requirements.

Receipts should be retained for reimbursement.
```
