# G22 Evidence Discipline Corrections

## Correction 1: Port 1042 Ownership

**G22 Statement:** "Port 1042 = NesysService (cabinet service controller)"

**Corrected Statement:** "The game attempts a local connection to localhost:1042. The failure is correlated with repeated NESYS CertError messages. The expected local listener, complete protocol and exact certificate responsibility remain to be confirmed."

**Evidence:** G23 capture shows 35 TCP SYN attempts to localhost:1042, all RST. NesysService.exe contains the full command protocol strings.

## Correction 2: Connection Count

**G22 Statement:** "4,575 connection attempts"

**Corrected Statement:** "4,575 log lines do not equal 4,575 connection attempts. G23 capture shows 35 SYN attempts over 17s. Log lines represent repeated polling/retry of the same failed state."

**Evidence:** G23 capture: 35 SYN, all RST. Game log: 4575 CertError lines over 77s.

## Correction 3: Certificate Validation

**G22 Statement:** "NesysService required for certificate validation"

**Corrected Statement:** "NesysService performs certificate operations via CertFindCertificateInStore() with MY\\.Default store. The exact certificate validation chain remains to be fully confirmed."

**Evidence:** NesysService.exe strings: CertFindCertificateInStore(), CertOpenStore(), MY\\.Default, nesys, SCOMMAND_CERT_ERROR