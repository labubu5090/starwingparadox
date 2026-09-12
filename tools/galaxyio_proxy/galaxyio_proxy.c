/*
 * GALAXYIO Proxy DLL - Replaces the wrapper GALAXYIO.dll
 * Exports: GALAXYIO_Init, GALAXYIO_Delete, GALAXYIO_Update, GALAXYIO_GetStatus
 *
 * Reads keyboard (WASD) and mouse state, writes fake USBIO data to the
 * context struct that the game's UGALAXYIOWrapper reads after calling Update.
 *
 * Context layout (from real DLL analysis):
 *   +0x34 .. +0x52 : 31 bytes of USBIO axis/button data copied to globals
 *   +0x5B .. +0x6A : 16 bytes (button flags?)
 *   +0x6B .. +0x6E : 4 bytes
 *   +0xE1 .. +0xF0 : 16 bytes
 *   +0x19F .. +0x1B2 : 16 bytes
 *
 * We populate the context with keyboard/mouse-driven values and return.
 * The game reads from the context after Update returns (no wrapper zeroing).
 */

#include <windows.h>

#define CONTEXT_SIZE 0x200

/* Context offsets identified from real DLL Update disassembly */
#define CTX_LEFT_STICK_X    0x34
#define CTX_LEFT_STICK_Y    0x35
#define CTX_RIGHT_STICK_X   0x36
#define CTX_RIGHT_STICK_Y   0x37
#define CTX_LEFT_LEVER_X    0x38
#define CTX_LEFT_LEVER_Y    0x39
#define CTX_RIGHT_LEVER_X   0x3A
#define CTX_RIGHT_LEVER_Y   0x3B
/* Buttons start around 0x3C */
#define CTX_BUTTON_BASE     0x3C

/* Center value for axes (byte: 0-255, center=128) */
#define AXIS_CENTER 0x80
#define AXIS_MAX    0xFF
#define AXIS_MIN    0x00

/* DLL state */
static int g_initialized = 0;
static LARGE_INTEGER g_perf_freq = {0};
static LARGE_INTEGER g_last_time = {0};
/* Game's per-frame Update loop accepts GetStatus returns {0, 0x100, 0x200}
 * as valid (drives input processing + stores slot state at obj+0x160).
 * The real DLL returns 0 for hardware slot 0; ANY other value (e.g. our old
 * constant 1) makes the game log "UIO_STAT_ERROR[1]" every frame and treat
 * the device as errored, so input never reaches the mech. Return 0 = valid. */
static int g_status = 0; /* 0 = valid device state (game-approved) */

/*
 * Map keyboard to axis byte.
 * WASD: W=forward(0x00), S=back(0xFF), A=left(0x00), D=right(0xFF)
 * Center = 0x80
 */
static BYTE keyboard_axis(void) {
    return (BYTE)AXIS_CENTER;
}

/*
 * Get keyboard-driven left stick value.
 * W/S map to Y axis, A/D map to X axis.
 */
static void get_keyboard_sticks(BYTE *lx, BYTE *ly, BYTE *rx, BYTE *ry) {
    BYTE left_x = AXIS_CENTER;
    BYTE left_y = AXIS_CENTER;
    BYTE right_x = AXIS_CENTER;
    BYTE right_y = AXIS_CENTER;

    /* WASD -> left stick */
    if (GetAsyncKeyState('W') & 0x8000) left_y = AXIS_MIN;   /* forward */
    if (GetAsyncKeyState('S') & 0x8000) left_y = AXIS_MAX;   /* backward */
    if (GetAsyncKeyState('A') & 0x8000) left_x = AXIS_MIN;   /* left */
    if (GetAsyncKeyState('D') & 0x8000) left_x = AXIS_MAX;   /* right */

    /* Mouse -> right stick (aiming) - use raw mouse position delta */
    /* For now, use IJKL or arrow keys as fallback */
    if (GetAsyncKeyState('I') & 0x8000) right_y = AXIS_MIN;
    if (GetAsyncKeyState('K') & 0x8000) right_y = AXIS_MAX;
    if (GetAsyncKeyState('J') & 0x8000) right_x = AXIS_MIN;
    if (GetAsyncKeyState('L') & 0x8000) right_x = AXIS_MAX;

    *lx = left_x;
    *ly = left_y;
    *rx = right_x;
    *ry = right_y;
}

/*
 * Read mouse movement and map to right stick axes.
 * Uses GetCursorPos relative to screen center.
 */
static void get_mouse_sticks(BYTE *rx, BYTE *ry) {
    POINT pt;
    int dx, dy;
    /* Get current mouse position */
    if (GetCursorPos(&pt)) {
        /* Map screen position to axis range */
        /* Screen center = axis center */
        int screen_w = GetSystemMetrics(SM_CXSCREEN);
        int screen_h = GetSystemMetrics(SM_CYSCREEN);
        /* Normalize to -128..+127 */
        dx = (pt.x * 256 / screen_w) - 128;
        dy = (pt.y * 256 / screen_h) - 128;
        /* Clamp */
        if (dx < -128) dx = -128;
        if (dx > 127) dx = 127;
        if (dy < -128) dy = -128;
        if (dy > 127) dy = 127;
        *rx = (BYTE)(dx + 128);
        *ry = (BYTE)(dy + 128);
    }
}

__declspec(dllexport) int __cdecl GALAXYIO_Init(void *context) {
    (void)context;
    QueryPerformanceFrequency(&g_perf_freq);
    QueryPerformanceCounter(&g_last_time);
    g_initialized = 1;
    g_status = 0; /* valid device state that the game's Update loop accepts */
    /* Log to OutputDebugString */
    OutputDebugStringA("GALAXYIO_PROXY: Init called - faking USBIO hardware\n");
    return 0; /* success */
}

__declspec(dllexport) int __cdecl GALAXYIO_Delete(void *context) {
    (void)context;
    g_initialized = 0;
    g_status = 0;
    OutputDebugStringA("GALAXYIO_PROXY: Delete called\n");
    return 0;
}

__declspec(dllexport) int __cdecl GALAXYIO_Update(void *context) {
    BYTE *ctx;
    BYTE lx, ly, rx, ry;
    BYTE buttons[16] = {0};

    if (!context) return 0;
    if (!g_initialized) return 0;

    ctx = (BYTE *)context;

    /* Get keyboard-driven left stick (WASD) */
    get_keyboard_sticks(&lx, &ly, &rx, &ry);

    /* Write axes to context at the offsets the game reads */
    /* Left Stick X/Y - movement */
    ctx[CTX_LEFT_STICK_X] = lx;
    ctx[CTX_LEFT_STICK_Y] = ly;

    /* Right Stick X/Y - aiming (mouse mapped) */
    {
        BYTE mouse_rx, mouse_ry;
        get_mouse_sticks(&mouse_rx, &mouse_ry);
        /* Blend keyboard and mouse for right stick */
        if (rx != AXIS_CENTER || ry != AXIS_CENTER) {
            ctx[CTX_RIGHT_STICK_X] = rx;
            ctx[CTX_RIGHT_STICK_Y] = ry;
        } else {
            ctx[CTX_RIGHT_STICK_X] = mouse_rx;
            ctx[CTX_RIGHT_STICK_Y] = mouse_ry;
        }
    }

    /* Left/Right Lever - center (not used for basic movement) */
    ctx[CTX_LEFT_LEVER_X] = AXIS_CENTER;
    ctx[CTX_LEFT_LEVER_Y] = AXIS_CENTER;
    ctx[CTX_RIGHT_LEVER_X] = AXIS_CENTER;
    ctx[CTX_RIGHT_LEVER_Y] = AXIS_CENTER;

    /* Buttons */
    /* 0x3C = button region start */
    /* Map common buttons:
     * Space = shoot (LeftButton / RightButton)
     * Enter = Start
     * 1/2 = Coin1/Coin2
     * Shift = Boost (LthumPush)
     * R = Respawn
     */
    {
        BYTE *btn = &ctx[CTX_BUTTON_BASE];

        /* LeftButton (shoot) - Space key */
        if (GetAsyncKeyState(VK_SPACE) & 0x8000)
            btn[0] = 0x01;

        /* RightButton (alt shoot?) - LMB via GetAsyncKeyState(VK_LBUTTON) */
        if (GetAsyncKeyState(VK_LBUTTON) & 0x8000)
            btn[1] = 0x01;

        /* USBIO_Start - Enter key */
        if (GetAsyncKeyState(VK_RETURN) & 0x8000) {
            ctx[0xE1] = 0x01;
        }

        /* USBIO_Coin1 - key '1' */
        if (GetAsyncKeyState('1') & 0x8000) {
            ctx[0xE1 + 1] = 0x01;
        }

        /* USBIO_LthumPush (boost) - Left Shift */
        if (GetAsyncKeyState(VK_LSHIFT) & 0x8000) {
            ctx[0x5B] = 0x01;
        }

        /* USBIO_RightButton - RMB */
        if (GetAsyncKeyState(VK_RBUTTON) & 0x8000) {
            btn[2] = 0x01;
        }
    }

    /* Zero out regions the game expects to be clean (rest of context) */
    /* Leave the axis/button regions intact */
    /* Don't zero 0x34-0x52 range - that's our data */

    return 0; /* success */
}

__declspec(dllexport) int __cdecl GALAXYIO_GetStatus(int param) {
    (void)param;
    /* Must return a state in {0, 0x100, 0x200} or the game's per-frame
     * UGALAXYIOWrapper::Update logs UIO_STAT_ERROR[<ret>] and marks the
     * slot errored (state stored at obj+0x160), blocking input delivery.
     * 0 = the value the real DLL returns for slot 0 = "normal, no error". */
    return g_status;
}
