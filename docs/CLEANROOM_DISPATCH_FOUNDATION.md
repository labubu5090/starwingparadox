# CLEANROOM DISPATCH FOUNDATION

**Date:** August 28, 2026  
**Phase:** 2A-G17  
**Classification:** Technical Specification

---

## Overview

The Dispatch Foundation defines the command routing and execution framework for the Starwing transport system, derived from G16 specification evidence.

---

## Dispatch Architecture

```
┌─────────────────────────────────────────┐
│           Incoming Command              │
└───────────────────┬─────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│         Command Registry                │
│    (ID → Handler Mapping)               │
└───────────────────┬─────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│       Parameter Validation              │
│    (Schema-based checking)              │
└───────────────────┬─────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│       Handler Execution                 │
│    (Isolated context)                   │
└───────────────────┬─────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│       Response Construction             │
│    (Result or Error)                    │
└───────────────────┬─────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│         Response Dispatch               │
│    (Return to sender)                   │
└─────────────────────────────────────────┘
```

---

## Core Components

### Command Registry

```typescript
interface CommandRegistry {
    register(commandId: number, handler: CommandHandler): Result;
    unregister(commandId: number): Result;
    lookup(commandId: number): CommandHandler | null;
    has(commandId: number): boolean;
}
```

**G16 Ref:** §5.1.1

### Command Handler

```typescript
interface CommandHandler {
    commandId: number;
    name: string;
    parameterSchema: ParameterSchema;
    execute(context: CommandContext, params: Params): Promise<CommandResult>;
}
```

**G16 Ref:** §5.1.2

### Command Context

```typescript
interface CommandContext {
    sessionId: string;
    connectionId: string;
    sequenceNumber: number;
    timestamp: number;
}
```

**G16 Ref:** §5.1.3

### Command Result

```typescript
type CommandResult = 
    | { success: true; data: any }
    | { success: false; error: CommandError };
```

**G16 Ref:** §5.1.4

---

## Dispatch Flow

### Step 1: Command Receipt
```
command = deserialize(incomingFrame)
```

### Step 2: Registry Lookup
```
handler = registry.lookup(command.commandId)
IF handler == null:
    RETURN Error(UNKNOWN_COMMAND)
```

### Step 3: Parameter Validation
```
validationResult = handler.parameterSchema.validate(command.params)
IF validationResult.invalid:
    RETURN Error(INVALID_PARAMS, validationResult.errors)
```

### Step 4: Context Creation
```
context = createContext(command, session, connection)
```

### Step 5: Handler Execution
```
result = await handler.execute(context, command.params)
```

### Step 6: Response Dispatch
```
response = buildResponse(command.sequenceNumber, result)
send(connection, response)
```

---

## Error Handling

| Error Type | Code | Description | G16 Ref |
|---|---|---|---|
| UNKNOWN_COMMAND | 0xE001 | Command ID not registered | §5.2.1 |
| INVALID_PARAMS | 0xE002 | Parameter validation failed | §5.2.2 |
| HANDLER_ERROR | 0xE003 | Handler execution failed | §5.2.3 |
| TIMEOUT | 0xE004 | Handler exceeded time limit | §5.2.4 |
| SESSION_ERROR | 0xE005 | Session-related failure | §5.2.5 |

---

## Handler Registration

### Registration Pattern
```typescript
registry.register(0x0100, {
    commandId: 0x0100,
    name: "SESSION_CREATE",
    parameterSchema: sessionCreateSchema,
    execute: async (context, params) => {
        const session = await sessionManager.create(params);
        return { success: true, data: { sessionId: session.id } };
    }
});
```

### Batch Registration
```typescript
const handlers = [
    sessionCreateHandler,
    sessionAttachHandler,
    sessionDetachHandler,
    // ...
];
handlers.forEach(h => registry.register(h.commandId, h));
```

**G16 Ref:** §5.3.1

---

## Concurrency Model

- **Isolation:** Each handler executes in isolated context
- **Timeout:** Default 5000ms, configurable per command
- **Queueing:** Commands queued per session, processed sequentially
- **Parallelism:** Different sessions process in parallel

**G16 Ref:** §5.4.1

---

*Dispatch foundation specification for Phase 2A-G17 cleanroom transport implementation.*
