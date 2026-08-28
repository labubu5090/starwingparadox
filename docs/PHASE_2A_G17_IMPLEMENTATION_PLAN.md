# PHASE 2A-G17 IMPLEMENTATION PLAN

**Date:** August 28, 2026  
**Phase:** 2A-G17 - Cleanroom Transport Architecture Implementation  
**Status:** PLANNED → IN PROGRESS  
**Reference:** G16 Evidence Base

---

## Executive Summary

Phase 2A-G17 builds directly on the G16 evidence base to implement a cleanroom transport architecture for the Starwing system. This phase focuses on establishing a foundation-free, specification-driven transport layer that eliminates legacy coupling and introduces formal command dispatch mechanisms.

---

## Objectives

1. **Cleanroom Transport Architecture** - Design and implement transport layer from specification, not legacy code
2. **Command Catalog** - Establish formal command definitions with type safety and validation
3. **Session State Machine** - Implement deterministic session lifecycle management
4. **Frame Validation** - Build robust frame parsing and validation pipeline
5. **Dispatch Foundation** - Create command routing and execution framework
6. **Synthetic Testing** - Develop test harness with synthetic command generation

---

## G16 Evidence References

| G16 Artifact | G17 Usage |
|---|---|
| Transport Protocol Specification | Foundation for cleanroom architecture |
| Command Definition Tables | Source for command catalog entries |
| Session Lifecycle Diagrams | Basis for state machine implementation |
| Frame Format Documentation | Validation rule derivation |
| Error Handling Patterns | Safety verification criteria |

---

## Implementation Phases

### Phase 1: Architecture Design (Days 1-2)
- Review G16 transport specifications
- Define cleanroom architecture boundaries
- Establish dependency isolation principles

### Phase 2: Core Implementation (Days 3-5)
- Implement transport primitives
- Build command catalog data structures
- Create session state machine

### Phase 3: Validation & Testing (Days 6-7)
- Frame validation pipeline
- Dispatch foundation testing
- Synthetic test execution

### Phase 4: Verification & Reporting (Day 8)
- Safety verification against G16
- Final documentation and reporting

---

## Success Criteria

- [ ] Transport layer operates without legacy dependencies
- [ ] All G16-defined commands present in catalog
- [ ] Session state machine covers all documented transitions
- [ ] Frame validation catches all documented malformed inputs
- [ ] Dispatch foundation routes commands correctly
- [ ] Synthetic tests achieve 100% command coverage

---

## Risk Assessment

| Risk | Impact | Mitigation |
|---|---|---|
| Legacy coupling discovered | High | Strict interface boundaries |
| Undocumented commands | Medium | G16 evidence reconciliation |
| State explosion | Medium | Formal state minimization |

---

*Document generated for Phase 2A-G17 implementation tracking.*
