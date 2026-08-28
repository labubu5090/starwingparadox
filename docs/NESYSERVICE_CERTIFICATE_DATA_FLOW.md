# NesysService Certificate Data Flow

**Phase**: 2A-G14  
**Executable**: NesysService.exe  
**Date**: 2026-08-28  
**Status**: COMPLETE  

---

## Executive Summary

NesysService.exe imports certificate store APIs and contains string references to "MY\.Default" and "nesys". The exact certificate data flow is partially recovered: store access is confirmed, but private key acquisition and TLS client-certificate attachment are NOT_SHOWN.

---

## Certificate Store APIs

### Imported APIs

| API | Import | Usage | Evidence |
|-----|--------|-------|----------|
| CertOpenStore | YES | Opens certificate store | Import table |
| CertFindCertificateInStore | YES | Searches for certificates | Import table |
| CertFreeCertificateContext | YES | Frees certificate context | Import table |
| CertCloseStore | YES | Closes certificate store | Import table |
| CertGetNameStringA | YES | Gets certificate name | Import table |

### Missing APIs

| API | Required For | Present |
|-----|--------------|---------|
| CertGetCertificateContextProperty | Private key detection | NOT_FOUND |
| CryptAcquireCertificatePrivateKey | Private key acquisition | NOT_FOUND |
| NCryptOpenKey | Key access | NOT_FOUND |
| CryptAcquireContext | Crypto context | NOT_FOUND |
| CryptSign | Signing | NOT_FOUND |

---

## Store Provider

| Property | Value | Confidence | Evidence |
|----------|-------|------------|----------|
| Provider | Microsoft Enhanced Cryptographic Provider v1.0 | HIGH | String reference |
| Alternative | Microsoft Enhanced RSA and AES Cryptographic Provider | HIGH | String reference |
| Store type | CERT_STORE_PROV_SYSTEM | INFERRED | Standard for system store |
| Flags | CERT_STORE_READONLY_FLAG | INFERRED | Standard for read-only access |

---

## Store Name

| Property | Value | Confidence | Evidence |
|----------|-------|------------|----------|
| Store name | MY | CONFIRMED | String reference "MY\.Default" |
| Store location | .Default | CONFIRMED | String reference ".Default" |
| Full path | MY\.Default | CONFIRMED | String reference |

---

## Certificate Search Criteria

### Search Parameters

| Criterion | Value | Confidence | Evidence |
|-----------|-------|------------|----------|
| Subject | nesys | CONFIRMED | String reference "nesys" |
| Issuer | NOT_FOUND | NOT_FOUND | No issuer string found |
| Thumbprint | NOT_FOUND | NOT_FOUND | No thumbprint search |
| EKU | NOT_FOUND | NOT_FOUND | No EKU search |
| Serial | NOT_FOUND | NOT_FOUND | No serial search |
| Friendly name | NOT_FOUND | NOT_FOUND | No friendly name search |

### Search Pattern

```
CertOpenStore("MY\.Default")
  → CertFindCertificateInStore(subject="nesys")
    → Certificate context
```

---

## Certificate Selection Loop

### Status

| Property | Status | Notes |
|----------|--------|-------|
| Multiple certificates | NOT_SHOWN | No loop logic found |
| Selection criteria | NOT_SHOWN | No sorting or filtering |
| Fallback behavior | NOT_SHOWN | No fallback logic |

**Certificate Selection Loop**: `NOT_SHOWN`

---

## Certificate Validity Checks

### Status

| Property | Status | Notes |
|----------|--------|-------|
| Validity period check | NOT_SHOWN | No time comparison |
| Revocation check | NOT_SHOWN | No CRL or OCSP |
| Chain validation | NOT_SHOWN | No chain building |

**Certificate Validity Checks**: `NOT_SHOWN`

---

## EKU Checks

### Status

| Property | Status | Notes |
|----------|--------|-------|
| Client authentication EKU | NOT_SHOWN | No EKU comparison |
| Server authentication EKU | NOT_SHOWN | No EKU comparison |
| Any EKU check | NOT_SHOWN | No EKU logic |

**EKU Checks**: `NOT_SHOWN`

---

## Issuer Checks

### Status

| Property | Status | Notes |
|----------|--------|-------|
| Issuer comparison | NOT_SHOWN | No issuer string |
| Issuer chain | NOT_SHOWN | No chain building |

**Issuer Checks**: `NOT_SHOWN`

---

## Thumbprint or Serial Matching

### Status

| Property | Status | Notes |
|----------|--------|-------|
| Thumbprint search | NOT_SHOWN | No thumbprint string |
| Serial search | NOT_SHOWN | No serial string |
| Hash comparison | NOT_SHOWN | No hash logic |

**Thumbprint/Serial Matching**: `NOT_SHOWN`

---

## Private Key Acquisition

### Status

| Property | Status | Notes |
|----------|--------|-------|
| CryptAcquireCertificatePrivateKey | NOT_FOUND | No import |
| NCryptOpenKey | NOT_FOUND | No import |
| CryptAcquireContext | NOT_FOUND | No import |
| Key container access | NOT_SHOWN | No key logic |

**Private Key Acquisition**: `NOT_SHOWN`

### Classification

**Private Key Requirement**: `PROBABLY_REQUIRED`

Certificate likely requires private key for TLS client authentication, but no direct evidence of private key acquisition found in imports. This remains an inference from client-auth pattern, not a confirmed fact.

---

## Client-Certificate Attachment to TLS

### Status

| Property | Status | Notes |
|----------|--------|-------|
| WinHttpSetClientCertificate | NOT_FOUND | No import |
| SChannel credential | NOT_SHOWN | No SChannel setup |
| CertContext attachment | NOT_SHOWN | No attachment logic |

**Client-Certificate Attachment**: `NOT_SHOWN`

---

## Server-Certificate Validation

### Status

| Property | Status | Notes |
|----------|--------|-------|
| CertGetCertificateChain | NOT_FOUND | No import |
| CertVerifyCertificateChainPolicy | NOT_FOUND | No import |
| WinHttpSetOption with certificate | NOT_FOUND | No option setting |
| Server cert validation | NOT_SHOWN | No validation logic |

**Server-Certificate Validation**: `NOT_SHOWN`

---

## Failure Codes

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

## Retry Paths

### Status

| Property | Status | Notes |
|----------|--------|-------|
| Retry on failure | NOT_SHOWN | No retry logic found |
| Maximum retries | NOT_FOUND | No retry count |
| Retry delay | NOT_FOUND | No delay logic |

**Retry Paths**: `NOT_SHOWN`

---

## Logging Paths

### Status

| Property | Status | Notes |
|----------|--------|-------|
| Certificate errors | SCOMMAND_CERT_ERROR | String reference |
| Store errors | Error handling | Error code logging |
| Detailed logging | NOT_SHOWN | No verbose logging |

**Logging Paths**: `PARTIAL`

---

## Certificate Data Flow Summary

### Recovered Flow

```
1. CertOpenStore("MY\.Default")
2. CertFindCertificateInStore(subject="nesys")
3. [Certificate context obtained]
4. [Private key acquisition NOT_SHOWN]
5. [TLS client-certificate attachment NOT_SHOWN]
6. [Server-certificate validation NOT_SHOWN]
7. [Network request to cert3.nesys.jp UNRESOLVED]
```

### Unrecovered Flow

| Step | Status | Impact |
|------|--------|--------|
| Private key acquisition | NOT_SHOWN | Cannot use certificate for client auth |
| TLS client-certificate attachment | NOT_SHOWN | Cannot attach certificate to TLS |
| Server-certificate validation | NOT_SHOWN | Cannot validate server |
| cert3.nesys.jp purpose | UNRESOLVED | Cannot determine relationship |

---

## Evidence Classification

| Category | Classification |
|----------|----------------|
| Certificate store | CONFIRMED |
| Store provider | HIGH |
| Store name | CONFIRMED |
| Search criteria | CONFIRMED |
| Private key acquisition | NOT_SHOWN |
| TLS attachment | NOT_SHOWN |
| Server validation | NOT_SHOWN |
| Failure handling | CONFIRMED |
| cert3.nesys.jp | UNRESOLVED |

---

## Unresolved Questions

| Question | Status | Notes |
|----------|--------|-------|
| Private key acquisition method | NOT_SHOWN | No import found |
| TLS client-certificate attachment | NOT_SHOWN | No API found |
| Server-certificate validation | NOT_SHOWN | No validation logic |
| cert3.nesys.jp purpose | UNRESOLVED | Hostname reference only |
| Certificate validity checks | NOT_SHOWN | No time or chain checks |
| Certificate selection logic | NOT_SHOWN | No loop or filtering |

---

## Conclusion

NesysService.exe imports certificate store APIs and contains string references to "MY\.Default" and "nesys". The certificate store access is confirmed, but private key acquisition, TLS client-certificate attachment, and server-certificate validation are NOT_SHOWN. The exact purpose of cert3.nesys.jp hostname references remains UNRESOLVED.

**Classification**: 
- Certificate store: `CONFIRMED`
- Private key: `PROBABLY_REQUIRED` (inference)
- TLS attachment: `NOT_SHOWN`
- cert3.nesys.jp: `UNRESOLVED`

---

## Certificate Dependency JSON

**Output**: `artifacts/phase_2a_g14/certificate_dependency.json`

```json
{
  "phase": "2A-G14",
  "executable": "NesysService.exe",
  "certificate_store": {
    "provider": "Microsoft Enhanced Cryptographic Provider v1.0",
    "store_name": "MY",
    "store_location": ".Default",
    "confidence": "CONFIRMED"
  },
  "search_criteria": {
    "subject": "nesys",
    "issuer": "NOT_FOUND",
    "thumbprint": "NOT_FOUND",
    "eku": "NOT_FOUND",
    "serial": "NOT_FOUND"
  },
  "private_key": {
    "acquisition": "NOT_SHOWN",
    "requirement": "PROBABLY_REQUIRED",
    "confidence": "LOW"
  },
  "tls_attachment": {
    "client_certificate": "NOT_SHOWN",
    "server_validation": "NOT_SHOWN"
  },
  "cert3_nesys_jp": {
    "purpose": "UNRESOLVED",
    "hostname_reference": "CONFIRMED",
    "operation": "UNRESOLVED"
  },
  "failure_handling": {
    "cert_error": "SCOMMAND_CERT_ERROR",
    "store_error": "Error logging"
  }
}
```

---

## G14 Audit Notes

This document was created in Phase 2A-G14 to trace certificate data flow through IDA static analysis. The certificate store access is confirmed, but private key acquisition and TLS attachment are NOT_SHOWN. The exact purpose of cert3.nesys.jp hostname references remains UNRESOLVED — hostname presence does not prove certificate retrieval, download, or authentication operations.
