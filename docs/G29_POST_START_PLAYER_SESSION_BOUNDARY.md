# G29 Post-Start Player Session Boundary

## First Private Server Request

After successful Start acceptance, the game immediately sends:

`
POST http://dev.starwing.jp/mock/matching/server
`

## Timeline

1. Title screen loaded (WBP_InsertStart visible)
2. Operator pressed Z, Z, Enter
3. Credits: 0→1→2→3→4→5→6→7→8→9→10
4. Start accepted
5. HTTP POST sent to matching/server
6. Timeout error (no server running)

## G30 Implementation Required

The Python private server must handle:

- **Route:** POST /mock/matching/server
- **Port:** 80
- **Response:** Unknown (must be captured)

## Card/QR/Player Identity

No card presentation, QR scan, or player identity screens were shown. The game went directly to the matching server request.
