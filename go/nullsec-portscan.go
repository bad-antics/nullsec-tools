// NullSec Port Scanner
// High-performance concurrent port scanner written in Go
// Author: bad-antics | GitHub: bad-antics | Discord: x.com/AnonAntics

package main

import (
"flag"
"fmt"
"net"
"os"
"sort"
"strconv"
"strings"
"sync"
"time"
)

const banner = `
╔═══════════════════════════════════════════════════════════╗
║     ███╗   ██╗██╗   ██╗██╗     ██╗     ███████╗███████╗   ║
║     ████╗  ██║██║   ██║██║     ██║     ██╔════╝██╔════╝   ║
║     ██╔██╗ ██║██║   ██║██║     ██║     ███████╗█████╗     ║
║     ██║╚██╗██║██║   ██║██║     ██║     ╚════██║██╔══╝     ║
║     ██║ ╚████║╚██████╔╝███████╗███████╗███████║███████╗   ║
║     ╚═╝  ╚═══╝ ╚═════╝ ╚══════╝╚══════╝╚══════╝╚══════╝   ║
║                    PORT SCANNER (Go)                       ║
║            bad-antics | bad-antics | x.com/AnonAntics  ║
╚═══════════════════════════════════════════════════════════╝
`

var commonPorts = []int{
21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 445, 993, 995,
1723, 3306, 3389, 5432, 5900, 8080, 8443, 8888, 9090, 27017,
}

var serviceMap = map[int]string{
21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
80: "HTTP", 110: "POP3", 111: "RPC", 135: "MSRPC", 139: "NetBIOS",
143: "IMAP", 443: "HTTPS", 445: "SMB", 993: "IMAPS", 995: "POP3S",
1723: "PPTP", 3306: "MySQL", 3389: "RDP", 5432: "PostgreSQL",
5900: "VNC", 8080: "HTTP-Proxy", 8443: "HTTPS-Alt", 27017: "MongoDB",
}

type ScanResult struct {
Port    int
Open    bool
Service string
Banner  string
}

func scanPort(host string, port int, timeout time.Duration, results chan<- ScanResult, wg *sync.WaitGroup) {
defer wg.Done()

address := fmt.Sprintf("%s:%d", host, port)
conn, err := net.DialTimeout("tcp", address, timeout)

result := ScanResult{
Port:    port,
Open:    err == nil,
Service: serviceMap[port],
}

if err == nil {
// Try to grab banner
conn.SetReadDeadline(time.Now().Add(2 * time.Second))
banner := make([]byte, 1024)
n, _ := conn.Read(banner)
if n > 0 {
result.Banner = strings.TrimSpace(string(banner[:n]))
if len(result.Banner) > 50 {
result.Banner = result.Banner[:50] + "..."
}
}
conn.Close()
}

results <- result
}

func parsePorts(portStr string) []int {
var ports []int

if portStr == "" || portStr == "common" {
return commonPorts
}

if portStr == "all" {
for i := 1; i <= 65535; i++ {
ports = append(ports, i)
}
return ports
}

parts := strings.Split(portStr, ",")
for _, part := range parts {
part = strings.TrimSpace(part)
if strings.Contains(part, "-") {
rangeParts := strings.Split(part, "-")
start, _ := strconv.Atoi(rangeParts[0])
end, _ := strconv.Atoi(rangeParts[1])
for i := start; i <= end; i++ {
ports = append(ports, i)
}
} else {
port, _ := strconv.Atoi(part)
ports = append(ports, port)
}
}
return ports
}

func main() {
fmt.Println(banner)

host := flag.String("host", "", "Target host")
portStr := flag.String("ports", "common", "Ports to scan (common, all, or range like 1-1000)")
threads := flag.Int("threads", 100, "Number of concurrent threads")
timeout := flag.Int("timeout", 1000, "Timeout in milliseconds")
flag.Parse()

if *host == "" {
fmt.Println("Usage: nullsec-portscan -host <target> [-ports <ports>] [-threads <n>] [-timeout <ms>]")
os.Exit(1)
}

ports := parsePorts(*portStr)
timeoutDuration := time.Duration(*timeout) * time.Millisecond

fmt.Printf("[*] Scanning %s (%d ports)\n", *host, len(ports))
fmt.Printf("[*] Threads: %d | Timeout: %dms\n\n", *threads, *timeout)

results := make(chan ScanResult, len(ports))
var wg sync.WaitGroup

// Semaphore for limiting concurrent goroutines
sem := make(chan struct{}, *threads)

startTime := time.Now()

for _, port := range ports {
wg.Add(1)
sem <- struct{}{}
go func(p int) {
scanPort(*host, p, timeoutDuration, results, &wg)
<-sem
}(port)
}

// Close results channel when all scans complete
go func() {
wg.Wait()
close(results)
}()

// Collect results
var openPorts []ScanResult
for result := range results {
if result.Open {
openPorts = append(openPorts, result)
}
}

elapsed := time.Since(startTime)

// Sort by port number
sort.Slice(openPorts, func(i, j int) bool {
return openPorts[i].Port < openPorts[j].Port
})

// Print results
fmt.Println("PORT      STATE    SERVICE         BANNER")
fmt.Println("----      -----    -------         ------")
for _, r := range openPorts {
service := r.Service
if service == "" {
service = "unknown"
}
fmt.Printf("%-9d %-8s %-15s %s\n", r.Port, "open", service, r.Banner)
}

fmt.Printf("\n[*] Scan completed in %v\n", elapsed.Round(time.Millisecond))
fmt.Printf("[*] %d open ports found\n", len(openPorts))
}
