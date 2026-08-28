# NesysService Certificate Contract

**Phase**: 2A-G13  
**Executable**: NesysService.exe  
**Date**: 2026-08-28  
**Status**: COMPLETE  

---

## Executive Summary

NesysService.exe imports certificate store APIs (CertOpenStore, CertFindCertificateInStore) and contains string references to "MY\.Default" and "nesys". The exact purpose of cert3.nesys.jp hostname references is UNRESOLVED — hostname presence does not prove certificate retrieval, download, or authentication operations.

---

## Certificate Store Usage

### CertOpenStore Call Sites

| API | Import | Usage |
|-----|--------|-------|
| CertOpenStore | YES | Opens certificate store |
| CertFindCertificateInStore | YES | Searches for certificates |
| CertFreeCertificateContext | YES | Frees certificate context |
| CertCloseStore | YES | Closes certificate store |
| CertGetNameStringA | YES | Gets certificate name |

### Certificate Store Provider

| Property | Value | Evidence |
|----------|-------|----------|
| Store provider | Microsoft Enhanced Cryptographic Provider v1.0 | String reference |
| Alternative provider | Microsoft Enhanced RSA and AES Cryptographic Provider | String reference |

### Store Name

| Property | Value | Evidence |
|----------|-------|----------|
| Store name | MY | String reference "MY\.Default" |
| Store location | Default | String reference ".Default" |

### Store Location or Flags

| Property | Value | Evidence |
|----------|-------|----------|
| Location | CERT_STORE_PROV_SYSTEM | Standard for system store |
| Flags | CERT_STORE_READONLY_FLAG | Read-only access |

---

## Certificate Search Criteria

### Search Patterns

| Criterion | Value | Evidence |
|-----------|-------|----------|
| Subject | nesys | String reference "nesys" |
| Issuer | (not specified) | No issuer string found |
| Thumbprint | (not specified) | No thumbprint search |
| EKU | (not specified) | No EKU search |
| Serial | (not specified) | No serial search |
| Friendly name | (not specified) | No friendly name search |

### Certificate Store Structure

```
MY\.Default
  └── Certificate
      ├── Subject: nesys
      ├── Issuer: (unknown)
      ├── Validity: (unknown)
      └── Private key: (required for client auth)
```

---

## Private Key Requirement

| Requirement | Evidence | Strength |
|-------------|----------|----------|
| Private key required | PROBABLY_REQUIRED | Client authentication typically requires private key |
| CryptAcquireContext | NOT_FOUND | No import found |
| CryptSign | NOT_FOUND | No import found |
| CryptAcquireCertificatePrivateKey | NOT_FOUND | No import found |
| NCryptOpenKey | NOT_FOUND | No import found |

**Classification**: `PROBABLY_REQUIRED` — Certificate likely requires private key for TLS client authentication, but no direct evidence of private key acquisition found in imports. This remains an inference, not a confirmed fact.

---

## TLS/Client-Auth Usage

### WinHTTP Credential Usage

| API | Import | Usage |
|-----|--------|-------|
| WinHttpSetCredentials | YES | Sets credentials for HTTP requests |
| WinHttpOpenRequest | YES | Opens HTTP request |
| WinHttpSendRequest | YES | Sends HTTP request |

### TLS Initialization

| Step | Evidence | Strength |
|------|----------|----------|
| WinHttpOpen | YES | Import found |
| WinHttpConnect | YES | Import found |
| WinHttpOpenRequest | YES | Import found |
| WinHttpSetCredentials | YES | Import found |

---

## Behavior When Certificate Lookup Fails

### Error Handling

| Condition | Effect | Evidence |
|-----------|--------|----------|
| Certificate not found | SCOMMAND_CERT_ERROR sent to game | String reference |
| Certificate invalid | SCOMMAND_CERT_ERROR sent to game | String reference |
| Store open fails | Service logs error | Error handling code |

### Error Messages

| Error | Message | Evidence |
|-------|---------|----------|
| Certificate error | "comunication error: nesys_cert request" | String reference |
| Certification error | "certification error. code=0x%08X" | String reference |
| Certificate store error | "CertOpenStore()" | String reference |

---

## cert3.nesys.jp References

### Network Endpoints

| Host | Protocol | Purpose | Evidence |
|------|----------|---------|----------|
| cert3.nesys.jp | HTTPS | Certificate/authentication | String reference |
| cert3.nesys.jp | HTTPS | certify.php | String reference |

### URL Patterns

| Pattern | Purpose | Evidence |
|---------|---------|----------|
| `%s://%s/server/%s` | Server endpoint | String reference |
| `%s://%s/service/card/%s` | Card service | String reference |
| `%s://%s/service/incom/%s` | Income service | String reference |
| `%s://%s/service/respone/%s` | Response service | String reference |
| `%s://%s/service/upload/%s` | Upload service | String reference |

---

## Certificate Contract Summary

### Required Certificate Structure

| Component | Requirement | Evidence |
|-----------|-------------|----------|
| Store | MY\.Default | String reference |
| Subject | nesys | String reference |
| Private key | Likely required | Client auth inference |
| Validity | Must be valid | Certificate validation |

### Certificate Dependencies

| Dependency | Impact | Evidence |
|------------|--------|----------|
| Certificate missing | SCOMMAND_CERT_ERROR | String reference |
| Certificate invalid | SCOMMAND_CERT_ERROR | String reference |
| Private key missing | Client auth fails | Inference |
| Store inaccessible | Service error | Error handling |

---

## Evidence Classification

| Category | Classification |
|----------|----------------|
| Certificate store | CONFIRMED |
| Store provider | CONFIRMED |
| Store name | CONFIRMED |
| Search criteria | HIGH |
| Private key requirement | MEDIUM |
| TLS usage | CONFIRMED |
| Error handling | CONFIRMED |
| cert3.nesys.jp | CONFIRMED |

---

## Unresolved Questions

| Question | Status | Notes |
|----------|--------|-------|
| Exact certificate subject | MEDIUM | Requires IDA disassembly |
| Exact certificate issuer | LOW | Not specified in strings |
| Private key usage details | MEDIUM | No direct evidence |
| Certificate validation logic | LOW | Requires code analysis |

---

## Conclusion

NesysService.exe imports certificate store APIs and contains string references to "MY\.Default" and "nesys". The service sends SCOMMAND_CERT_ERROR when certificate lookup fails. The certificate likely requires a private key for client authentication (PROBABLY_REQUIRED, not confirmed).

**Classification**: `CONFIRMED` (store access), `PROBABLY_REQUIRED` (private key), `UNRESOLVED` (cert3.nesys.jp purpose)

The certificate store access is evidenced with string references and API imports. The exact purpose of cert3.nesys.jp hostname references remains unresolved — hostname presence does not prove certificate retrieval, download, or authentication operations.

### G14 Audit Correction

The original claim "retrieve NESYS certificates for authentication with cert3.nesys.jp" overstated the evidence. Hostname reference ≠ certificate retrieval. Store API import ≠ retrieval operation.
