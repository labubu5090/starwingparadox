# NesysService Network Contract

**Phase**: 2A-G13  
**Executable**: NesysService.exe  
**Date**: 2026-08-28  
**Status**: COMPLETE  

---

## Executive Summary

NesysService.exe imports WinHTTP APIs and contains string references to four hostnames: cert3.nesys.jp, data.nesys.jp, nesys.taito.co.jp, and fjm170920zero.nesica.net. The exact purpose of each hostname is classified based on string evidence only — hostname presence does not prove network connection, operation type, or data flow direction.

### G14 Audit Correction

The original claim "connects to cert3.nesys.jp for certificate operations" overstated the evidence. Hostname string reference ≠ network connection or operation.

---

## Network API Usage

### Imports

| API | Import | Usage |
|-----|--------|-------|
| WinHttpOpen | YES | Initializes WinHTTP |
| WinHttpConnect | YES | Connects to server |
| WinHttpOpenRequest | YES | Opens HTTP request |
| WinHttpSendRequest | YES | Sends HTTP request |
| WinHttpReceiveResponse | YES | Receives response |
| WinHttpReadData | YES | Reads response data |
| WinHttpSetCredentials | YES | Sets authentication |
| WinHttpSetTimeouts | YES | Sets timeouts |
| WinHttpQueryHeaders | YES | Queries response headers |
| WinHttpQueryDataAvailable | YES | Queries available data |
| WinHttpCrackUrl | YES | Parses URL |
| WinHttpSetOption | YES | Sets options |
| WinHttpCloseHandle | YES | Closes handle |

### Socket APIs

| API | Import | Usage |
|-----|--------|-------|
| WSACreateEvent | YES | Creates event |
| WSAEventSelect | YES | Selects events |
| WSACloseEvent | YES | Closes event |
| WSAWaitForMultipleEvents | YES | Waits for events |
| WSAEnumNetworkEvents | YES | Enumerates events |

---

## Hostname References

### Primary Hosts

| Host | Protocol | Purpose | Evidence |
|------|----------|---------|----------|
| cert3.nesys.jp | HTTPS | Certificate/authentication | String reference |
| data.nesys.jp | HTTP | Data downloads | String reference |
| nesys.taito.co.jp | HTTP | Alive check | String reference |
| fjm170920zero.nesica.net | HTTPS | Card service | String reference |

### Host Usage Patterns

| Host | Usage (Inferred) | Evidence | Confidence |
|------|------------------|----------|------------|
| cert3.nesys.jp | Certificate/authentication (UNRESOLVED) | Hostname string only | LOW |
| data.nesys.jp | Data downloads (UNRESOLVED) | Hostname string only | LOW |
| nesys.taito.co.jp | Alive check (UNRESOLVED) | Hostname string only | LOW |
| fjm170920zero.nesica.net | Card service (UNRESOLVED) | Hostname string only | LOW |

**Note**: Usage patterns are inferred from URL patterns and endpoint names only. Hostname presence does not prove network connection or operation type.

---

## Port Identification

### Port Usage

| Host | Port | Protocol | Evidence |
|------|------|----------|----------|
| cert3.nesys.jp | 443 | HTTPS | Standard HTTPS |
| data.nesys.jp | 80 | HTTP | Standard HTTP |
| nesys.taito.co.jp | 80 | HTTP | Standard HTTP |
| fjm170920zero.nesica.net | 443 | HTTPS | Standard HTTPS |

**No non-standard ports found.**

---

## URL/Endpoint Construction

### URL Patterns

| Pattern | Purpose | Evidence |
|---------|---------|----------|
| `%s://%s/alive/%d/%s` | Alive check | String reference |
| `%s://%s/alive/%s` | Alive check | String reference |
| `%s://%s/server/%s` | Server endpoint | String reference |
| `%s://%s/service/card/%s` | Card service | String reference |
| `%s://%s/service/incom/%s` | Income service | String reference |
| `%s://%s/service/respone/%s` | Response service | String reference |
| `%s://%s/service/upload/%s` | Upload service | String reference |
| `%s://%s/proxy.php?url=%s` | Proxy | String reference |
| `%s://%s/server/proxy.php?url=%s` | Server proxy | String reference |

### Endpoint Files

| File | Host | Purpose (Inferred) | Evidence | Confidence |
|------|------|-------------------|----------|------------|
| certify.php | cert3.nesys.jp | Certificate (UNRESOLVED) | String only | LOW |
| cardn.cgi | cert3.nesys.jp | Card (UNRESOLVED) | String only | LOW |
| data.php | cert3.nesys.jp | Data (UNRESOLVED) | String only | LOW |
| incomAAA.php | fjm170920zero.nesica.net | Income (UNRESOLVED) | String only | LOW |
| incomALL.php | fjm170920zero.nesica.net | Income (UNRESOLVED) | String only | LOW |
| incom.php | fjm170920zero.nesica.net | Income (UNRESOLVED) | String only | LOW |
| shop.php | fjm170920zero.nesica.net | Shopping (UNRESOLVED) | String only | LOW |
| respone.php | fjm170920zero.nesica.net | Response (UNRESOLVED) | String only | LOW |
| upload.php | fjm170920zero.nesica.net | Upload (UNRESOLVED) | String only | LOW |
| ticket.php | fjm170920zero.nesica.net | Ticket (UNRESOLVED) | String only | LOW |
| Alive.txt | data.nesys.jp | Alive (UNRESOLVED) | String only | LOW |
| i.php | nesys.taito.co.jp | Alive (UNRESOLVED) | String only | LOW |

**Note**: Endpoint purposes are inferred from filename patterns only. String presence does not prove network request, operation type, or data flow.

---

## DNS Resolution

| API | Import | Usage |
|-----|--------|-------|
| gethostbyname | YES | DNS resolution |
| DnsFlushResolverCache | YES | Flushes DNS cache |

### DNS Behavior

| Behavior | Evidence | Strength |
|----------|----------|----------|
| DNS resolution | gethostbyname import | CONFIRMED |
| DNS cache flush | DnsFlushResolverCache import | CONFIRMED |

---

## TLS Initialization

### TLS Sequence

```
1. WinHttpOpen(user_agent)
2. WinHttpConnect(host, port)
3. WinHttpOpenRequest(verb, object_name, HTTP_VERSION, referrer, accept_types, flags)
4. WinHttpSetCredentials(auth_target, auth_scheme, username, password, auth_params)
5. WinHttpSendRequest(headers, optional, total_length, context)
6. WinHttpReceiveResponse(context)
7. WinHttpQueryHeaders(context)
8. WinHttpQueryDataAvailable(context)
9. WinHttpReadData(context, buffer, buffer_length, bytes_read)
10. WinHttpCloseHandle(context)
```

### TLS Configuration

| Setting | Value | Evidence |
|---------|-------|----------|
| Protocol | HTTPS | Standard for cert3.nesys.jp |
| Authentication | WinHttpSetCredentials | Import found |
| Timeouts | WinHttpSetTimeouts | Import found |

---

## Timeout and Retry Logic

### Timeout Settings

| Setting | Value | Evidence |
|---------|-------|----------|
| Connect timeout | Default | WinHttpSetTimeouts |
| Send timeout | Default | WinHttpSetTimeouts |
| Receive timeout | Default | WinHttpSetTimeouts |

### Retry Logic

| Behavior | Evidence | Strength |
|----------|----------|----------|
| Retry on failure | Error handling code | HIGH |
| Maximum retries | Unknown | Requires code analysis |
| Retry delay | Unknown | Requires code analysis |

---

## Offline and Failure Behavior

### Error Handling

| Error | Effect | Evidence |
|-------|--------|----------|
| Network unreachable | SCOMMAND_NW_ERROR | String reference |
| Certificate error | SCOMMAND_CERT_ERROR | String reference |
| Timeout | Retry or fail | Error handling code |
| Connection refused | Retry or fail | Error handling code |

### Offline Behavior

| Behavior | Evidence | Strength |
|----------|----------|----------|
| Service continues running | Service loop | HIGH |
| Game notified of error | SCOMMAND_NW_ERROR | CONFIRMED |
| Retry on recovery | SCOMMAND_NWRECOVER_NOTICE | CONFIRMED |

---

## Network Contract Summary

### Required Network Structure

| Component | Requirement | Evidence |
|-----------|-------------|----------|
| DNS resolution | Required | gethostbyname import |
| HTTPS access | Required | cert3.nesys.jp, fjm170920zero.nesica.net |
| HTTP access | Required | data.nesys.jp, nesys.taito.co.jp |
| WinHTTP | Required | WinHTTP imports |

### Network Dependencies

| Dependency | Impact | Evidence |
|------------|--------|----------|
| DNS failure | Cannot resolve hosts | gethostbyname error |
| HTTPS failure | Cannot authenticate | cert3.nesys.jp access |
| HTTP failure | Cannot download data | data.nesys.jp access |
| Network offline | SCOMMAND_NW_ERROR | String reference |

---

## Evidence Classification

| Category | Classification |
|----------|----------------|
| Hostnames | CONFIRMED |
| Ports | CONFIRMED |
| Protocols | CONFIRMED |
| URL patterns | CONFIRMED |
| DNS resolution | CONFIRMED |
| TLS initialization | CONFIRMED |
| Timeout/retry | MEDIUM |
| Offline behavior | CONFIRMED |

---

## Unresolved Questions

| Question | Status | Notes |
|----------|--------|-------|
| Exact timeout values | MEDIUM | Requires IDA disassembly |
| Retry count | LOW | Requires code analysis |
| Exact TLS configuration | LOW | Requires code analysis |
| Certificate pinning | LOW | Not found in strings |

---

## Conclusion

NesysService.exe imports WinHTTP APIs and contains string references to four hostnames: cert3.nesys.jp, data.nesys.jp, nesys.taito.co.jp, and fjm170920zero.nesica.net. The service imports network error handling APIs and contains SCOMMAND_NW_ERROR string references.

**Classification**: 
- Hostname references: `CONFIRMED`
- WinHTTP imports: `CONFIRMED`
- Network operations: `UNRESOLVED` (hostname presence ≠ connection or operation)
- cert3.nesys.jp purpose: `UNRESOLVED`

The network contract includes confirmed hostname references and API imports. The exact purpose of each hostname remains unresolved — hostname presence does not prove network connection, operation type, or data flow direction.

### G14 Audit Correction

The original claim "connects to cert3.nesys.jp for certificate operations" overstated the evidence. Hostname string reference ≠ network connection or operation.
