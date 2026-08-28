# cert3.nesys.jp Relationship

**Phase**: 2A-G14  
**Executable**: NesysService.exe  
**Date**: 2026-08-28  
**Status**: COMPLETE  

---

## Executive Summary

NesysService.exe contains string references to "cert3.nesys.jp" and associated endpoint paths. The exact purpose of the hostname is UNRESOLVED — hostname presence does not prove network connection, operation type, or data flow direction. No evidence of certificate retrieval, download, or authentication operations was found.

---

## String References

### Hostname Strings

| String | Location | Evidence |
|--------|----------|----------|
| "cert3.nesys.jp" | Data section | String reference |
| "certify.php" | Data section | String reference |
| "cardn.cgi" | Data section | String reference |
| "data.php" | Data section | String reference |

### URL Patterns

| Pattern | Evidence | Purpose (Inferred) |
|---------|----------|-------------------|
| `%s://%s/server/%s` | String reference | Server endpoint (UNRESOLVED) |
| `%s://%s/service/card/%s` | String reference | Card service (UNRESOLVED) |
| `%s://%s/service/incom/%s` | String reference | Income service (UNRESOLVED) |
| `%s://%s/service/respone/%s` | String reference | Response service (UNRESOLVED) |
| `%s://%s/service/upload/%s` | String reference | Upload service (UNRESOLVED) |

---

## Function RVA Analysis

### Status

| Property | Status | Notes |
|----------|--------|-------|
| Function RVA | NOT_FOUND | Requires IDA disassembly |
| Call chain | NOT_FOUND | Requires code analysis |
| Cross-references | NOT_FOUND | Requires xref analysis |

**Function RVA Analysis**: `NOT_SHOWN`

---

## Call Chain Analysis

### Status

| Property | Status | Notes |
|----------|--------|-------|
| Direct callers | NOT_SHOWN | No xref found |
| Indirect callers | NOT_SHOWN | No xref found |
| Call depth | NOT_SHOWN | No call chain |

**Call Chain Analysis**: `NOT_SHOWN`

---

## Imported Network APIs

### APIs Present

| API | Import | Usage |
|-----|--------|-------|
| WinHttpOpen | YES | Initializes WinHTTP |
| WinHttpConnect | YES | Connects to server |
| WinHttpOpenRequest | YES | Opens HTTP request |
| WinHttpSendRequest | YES | Sends HTTP request |
| WinHttpReceiveResponse | YES | Receives response |
| WinHttpReadData | YES | Reads response data |
| WinHttpSetCredentials | YES | Sets authentication |
| WinHttpCloseHandle | YES | Closes handle |

### APIs Not Present

| API | Required For | Present |
|-----|--------------|---------|
| WinHttpSetClientCertificate | Client cert attachment | NOT_FOUND |
| WinHttpSetOption | Certificate option | NOT_FOUND |
| CertGetCertificateChain | Chain validation | NOT_FOUND |

---

## Surrounding Strings

### Certificate-Related Strings

| String | Evidence | Context |
|--------|----------|---------|
| "MY\.Default" | CONFIRMED | Certificate store |
| "nesys" | CONFIRMED | Certificate subject |
| "comunication error: nesys_cert request" | CONFIRMED | Error message |
| "certification error. code=0x%08X" | CONFIRMED | Error message |
| "CertOpenStore()" | CONFIRMED | Error message |

### Network-Related Strings

| String | Evidence | Context |
|--------|----------|---------|
| "cert3.nesys.jp" | CONFIRMED | Hostname reference |
| "data.nesys.jp" | CONFIRMED | Hostname reference |
| "nesys.taito.co.jp" | CONFIRMED | Hostname reference |
| "fjm170920zero.nesica.net" | CONFIRMED | Hostname reference |

---

## Request Construction

### Status

| Property | Status | Notes |
|----------|--------|-------|
| HTTP method | NOT_SHOWN | No GET/POST string |
| Request headers | NOT_SHOWN | No header construction |
| Request body | NOT_SHOWN | No body construction |
| Query parameters | NOT_SHOWN | No parameter building |

**Request Construction**: `NOT_SHOWN`

---

## Protocol Evidence

### Status

| Property | Status | Notes |
|----------|--------|-------|
| HTTP/HTTPS | INFERRED | Port 443 implies HTTPS |
| Protocol version | NOT_SHOWN | No HTTP version string |
| TLS version | NOT_SHOWN | No TLS configuration |

**Protocol Evidence**: `INFERRED`

---

## Port Encoding

### Status

| Property | Status | Notes |
|----------|--------|-------|
| Explicit port | NOT_FOUND | No port string "443" |
| Implicit port | INFERRED | HTTPS implies 443 |
| Port parameter | NOT_SHOWN | No port in URL pattern |

**Port Encoding**: `IMPLICIT`

---

## Data Consumed After Response

### Status

| Property | Status | Notes |
|----------|--------|-------|
| Response parsing | NOT_SHOWN | No parsing logic |
| Data extraction | NOT_SHOWN | No extraction code |
| Certificate extraction | NOT_SHOWN | No cert parsing |
| Configuration extraction | NOT_SHOWN | No config parsing |

**Data Consumed**: `NOT_SHOWN`

---

## Relationship to Local Certificate Selection

### Status

| Property | Status | Notes |
|----------|--------|-------|
| Certificate retrieval | NOT_SHOWN | No download logic |
| Certificate provisioning | NOT_SHOWN | No provisioning code |
| Certificate validation | NOT_SHOWN | No validation logic |
| Certificate usage | NOT_SHOWN | No usage code |

**Relationship**: `UNRESOLVED`

---

## Purpose Classification

### Possible Purposes

| Purpose | Evidence | Confidence |
|---------|----------|------------|
| DNS resolution | Hostname string | CONFIRMED (hostname exists) |
| TLS connection | HTTPS implied | INFERRED |
| HTTP request | URL patterns | INFERRED |
| Certificate enrollment | "certify.php" | UNRESOLVED |
| Certificate download | "cert3" prefix | UNRESOLVED |
| Revocation checking | NONE | NOT_FOUND |
| Authentication | NONE | NOT_FOUND |
| Application data | URL patterns | UNRESOLVED |
| Configuration update | NONE | NOT_FOUND |

### Confirmed Evidence

| Evidence | Classification |
|----------|----------------|
| Hostname string reference | CONFIRMED |
| Endpoint path strings | CONFIRMED |
| WinHTTP imports | CONFIRMED |
| Certificate store APIs | CONFIRMED |

### Unresolved Evidence

| Evidence | Classification |
|----------|----------------|
| Network connection to host | NOT_SHOWN |
| Certificate retrieval | NOT_SHOWN |
| Certificate download | NOT_SHOWN |
| Authentication operation | NOT_SHOWN |
| Data flow direction | UNRESOLVED |

---

## Do NOT

| Action | Status |
|--------|--------|
| Resolve hostname | CONFIRMED NOT DONE |
| Connect to host | CONFIRMED NOT DONE |
| Search for credentials | CONFIRMED NOT DONE |
| Obtain certificates | CONFIRMED NOT DONE |

---

## Evidence Classification

| Category | Classification |
|----------|----------------|
| Hostname reference | CONFIRMED |
| Endpoint strings | CONFIRMED |
| WinHTTP imports | CONFIRMED |
| Network connection | NOT_SHOWN |
| Certificate retrieval | NOT_SHOWN |
| Certificate download | NOT_SHOWN |
| Authentication | NOT_SHOWN |
| Data flow | UNRESOLVED |

---

## Unresolved Questions

| Question | Status | Notes |
|----------|--------|-------|
| Exact purpose of cert3.nesys.jp | UNRESOLVED | Hostname reference only |
| Certificate retrieval or download | NOT_SHOWN | No download logic |
| Authentication operation | NOT_SHOWN | No auth code |
| Data flow direction | UNRESOLVED | No request/response analysis |
| Relationship to local certificate | UNRESOLVED | No connection found |

---

## Conclusion

NesysService.exe contains string references to "cert3.nesys.jp" and associated endpoint paths. The exact purpose of the hostname is UNRESOLVED — hostname presence does not prove network connection, operation type, or data flow direction. No evidence of certificate retrieval, download, or authentication operations was found.

**Classification**: `UNRESOLVED`

The cert3.nesys.jp hostname reference is confirmed, but the exact purpose remains unresolved.

---

## G14 Audit Notes

This document was created in Phase 2A-G14 to build an evidence-based call graph for all cert3.nesys.jp references. The hostname reference is confirmed, but the exact purpose remains unresolved. No certificate retrieval, download, or authentication operations were found in static analysis.
