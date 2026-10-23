# Security Policy

## Supported Versions

The Smart Farming project actively maintains and patches security vulnerabilities for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| `main`  | :white_check_mark: |
| `< 1.0` | :x:                |

---

## Reporting a Vulnerability

The Smart Farming development team takes security vulnerabilities seriously. We appreciate the responsible disclosure of security issues.

### How to Report
Please **do NOT report security vulnerabilities through public GitHub issues**.

Instead, please report vulnerabilities using one of the following methods:
1. **GitHub Private Vulnerability Reporting**: Go to the **Security** tab of this repository, select **Advisories**, and click **"Report a vulnerability"**.
2. **Direct Security Contact**: Send an email to [23it050@charusat.edu.in](mailto:23it050@charusat.edu.in) with:
   - A descriptive title and summary of the vulnerability.
   - Steps to reproduce or proof-of-concept (PoC).
   - The potential impact and attack vector.
   - Any suggested mitigations.

### Response SLA
- **Initial Acknowledgment**: Within **48 hours**.
- **Assessment & Triage**: Within **5 business days**.
- **Fix & Public Advisory**: Coordinated release within **14 business days** or agreed disclosure timeline.

---

## Security Best Practices for Deployments

- **JWT Secrets**: Always set strong, random, 64-character hex strings for `SECRET_KEY` and `JWT_SECRET_KEY` in production environments. Never deploy using development defaults.
- **Database Access**: Restrict Supabase/PostgreSQL connections to TLS-enforced endpoints (`sslmode=require`).
- **Data Protection**: User and telemetry data are subject to the Digital Personal Data Protection (DPDP) Act 2023. Mobile credentials must remain encapsulated in OS-native secure hardware keychains (`TokenStorage`).
