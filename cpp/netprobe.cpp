// NullSec - C++ Network Probe (Fast Scanner)
// Part of the NullSec Framework
// https://github.com/bad-antics | @AnonAntics
// x.com/AnonAntics

#include <iostream>
#include <vector>
#include <thread>
#include <mutex>
#include <atomic>
#include <chrono>
#include <cstring>
#include <queue>
#include <condition_variable>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <unistd.h>
#include <fcntl.h>
#include <poll.h>
#include <netdb.h>

using namespace std;

const char* VERSION = "1.0.0";
const char* BANNER = R"(
╔═══════════════════════════════════════════════════════╗
║          NullSec - C++ Network Probe                  ║
║              @AnonAntics | NullSec                    ║
║         x.com/AnonAntics for keys                   ║
╚═══════════════════════════════════════════════════════╝
)";

// Thread-safe result storage
struct ScanResult {
    string ip;
    int port;
    bool open;
    string service;
    chrono::milliseconds latency;
};

class ThreadPool {
private:
    vector<thread> workers;
    queue<function<void()>> tasks;
    mutex queue_mutex;
    condition_variable condition;
    atomic<bool> stop{false};

public:
    ThreadPool(size_t threads) {
        for (size_t i = 0; i < threads; ++i) {
            workers.emplace_back([this] {
                while (true) {
                    function<void()> task;
                    {
                        unique_lock<mutex> lock(queue_mutex);
                        condition.wait(lock, [this] {
                            return stop || !tasks.empty();
                        });
                        if (stop && tasks.empty()) return;
                        task = move(tasks.front());
                        tasks.pop();
                    }
                    task();
                }
            });
        }
    }

    template<class F>
    void enqueue(F&& f) {
        {
            unique_lock<mutex> lock(queue_mutex);
            tasks.emplace(forward<F>(f));
        }
        condition.notify_one();
    }

    ~ThreadPool() {
        stop = true;
        condition.notify_all();
        for (thread& worker : workers) {
            worker.join();
        }
    }
};

class NetworkScanner {
private:
    vector<ScanResult> results;
    mutex results_mutex;
    atomic<int> scanned{0};
    atomic<int> open_ports{0};
    int timeout_ms;
    bool verbose;

public:
    NetworkScanner(int timeout = 1000, bool verb = false) 
        : timeout_ms(timeout), verbose(verb) {}

    bool isPortOpen(const string& ip, int port, chrono::milliseconds& latency) {
        int sock = socket(AF_INET, SOCK_STREAM, 0);
        if (sock < 0) return false;

        // Set non-blocking
        int flags = fcntl(sock, F_GETFL, 0);
        fcntl(sock, F_SETFL, flags | O_NONBLOCK);

        struct sockaddr_in addr;
        addr.sin_family = AF_INET;
        addr.sin_port = htons(port);
        inet_pton(AF_INET, ip.c_str(), &addr.sin_addr);

        auto start = chrono::steady_clock::now();
        
        connect(sock, (struct sockaddr*)&addr, sizeof(addr));

        struct pollfd pfd;
        pfd.fd = sock;
        pfd.events = POLLOUT;

        bool connected = false;
        if (poll(&pfd, 1, timeout_ms) > 0) {
            int error;
            socklen_t len = sizeof(error);
            getsockopt(sock, SOL_SOCKET, SO_ERROR, &error, &len);
            connected = (error == 0);
        }

        auto end = chrono::steady_clock::now();
        latency = chrono::duration_cast<chrono::milliseconds>(end - start);

        close(sock);
        return connected;
    }

    string identifyService(int port) {
        static const map<int, string> services = {
            {21, "FTP"}, {22, "SSH"}, {23, "Telnet"}, {25, "SMTP"},
            {53, "DNS"}, {80, "HTTP"}, {110, "POP3"}, {143, "IMAP"},
            {443, "HTTPS"}, {445, "SMB"}, {3306, "MySQL"}, {3389, "RDP"},
            {5432, "PostgreSQL"}, {6379, "Redis"}, {8080, "HTTP-Proxy"},
            {8443, "HTTPS-Alt"}, {27017, "MongoDB"}
        };
        
        auto it = services.find(port);
        return it != services.end() ? it->second : "Unknown";
    }

    void scanPort(const string& ip, int port) {
        chrono::milliseconds latency;
        bool open = isPortOpen(ip, port, latency);
        
        scanned++;
        
        if (open) {
            open_ports++;
            ScanResult result{ip, port, true, identifyService(port), latency};
            
            lock_guard<mutex> lock(results_mutex);
            results.push_back(result);
            
            if (verbose) {
                cout << "[+] " << ip << ":" << port << " OPEN (" 
                     << result.service << ") " << latency.count() << "ms" << endl;
            }
        }
    }

    void scanRange(const string& ip, int startPort, int endPort, int threads = 100) {
        ThreadPool pool(threads);
        
        for (int port = startPort; port <= endPort; port++) {
            pool.enqueue([this, ip, port] {
                scanPort(ip, port);
            });
        }
    }

    void scanNetwork(const string& subnet, int port, int threads = 100) {
        // Parse CIDR
        string baseIP = subnet.substr(0, subnet.find('/'));
        int cidr = stoi(subnet.substr(subnet.find('/') + 1));
        
        uint32_t ip;
        inet_pton(AF_INET, baseIP.c_str(), &ip);
        ip = ntohl(ip);
        
        uint32_t mask = ~((1 << (32 - cidr)) - 1);
        uint32_t network = ip & mask;
        uint32_t broadcast = network | ~mask;
        
        ThreadPool pool(threads);
        
        for (uint32_t addr = network + 1; addr < broadcast; addr++) {
            uint32_t netAddr = htonl(addr);
            char ipStr[INET_ADDRSTRLEN];
            inet_ntop(AF_INET, &netAddr, ipStr, INET_ADDRSTRLEN);
            string targetIP(ipStr);
            
            pool.enqueue([this, targetIP, port] {
                scanPort(targetIP, port);
            });
        }
    }

    vector<ScanResult> getResults() { return results; }
    int getScannedCount() { return scanned.load(); }
    int getOpenCount() { return open_ports.load(); }
};

void printUsage() {
    cout << "Usage: netprobe [options]" << endl << endl;
    cout << "Options:" << endl;
    cout << "    -t, --target IP      Target IP address" << endl;
    cout << "    -n, --network CIDR   Scan network range (e.g., 192.168.1.0/24)" << endl;
    cout << "    -p, --ports RANGE    Port range (e.g., 1-1000 or 80,443,8080)" << endl;
    cout << "    -T, --threads N      Number of threads (default: 100)" << endl;
    cout << "    --timeout MS         Connection timeout in ms (default: 1000)" << endl;
    cout << "    -v, --verbose        Verbose output" << endl;
    cout << "    -h, --help           Show this help" << endl;
    cout << endl;
    cout << "Get more tools: x.com/AnonAntics" << endl;
}

int main(int argc, char* argv[]) {
    cout << BANNER << endl;
    cout << "Version: " << VERSION << endl << endl;

    if (argc < 2) {
        printUsage();
        return 1;
    }

    string target;
    string network;
    int startPort = 1, endPort = 1000;
    int threads = 100;
    int timeout = 1000;
    bool verbose = false;

    for (int i = 1; i < argc; i++) {
        string arg = argv[i];
        
        if ((arg == "-t" || arg == "--target") && i + 1 < argc) {
            target = argv[++i];
        } else if ((arg == "-n" || arg == "--network") && i + 1 < argc) {
            network = argv[++i];
        } else if ((arg == "-p" || arg == "--ports") && i + 1 < argc) {
            string ports = argv[++i];
            if (ports.find('-') != string::npos) {
                startPort = stoi(ports.substr(0, ports.find('-')));
                endPort = stoi(ports.substr(ports.find('-') + 1));
            } else {
                startPort = endPort = stoi(ports);
            }
        } else if ((arg == "-T" || arg == "--threads") && i + 1 < argc) {
            threads = stoi(argv[++i]);
        } else if (arg == "--timeout" && i + 1 < argc) {
            timeout = stoi(argv[++i]);
        } else if (arg == "-v" || arg == "--verbose") {
            verbose = true;
        } else if (arg == "-h" || arg == "--help") {
            printUsage();
            return 0;
        }
    }

    NetworkScanner scanner(timeout, verbose);
    auto start = chrono::steady_clock::now();

    if (!network.empty()) {
        cout << "[*] Scanning network: " << network << " port " << startPort << endl;
        scanner.scanNetwork(network, startPort, threads);
    } else if (!target.empty()) {
        cout << "[*] Scanning " << target << " ports " << startPort << "-" << endPort << endl;
        scanner.scanRange(target, startPort, endPort, threads);
    } else {
        cerr << "[!] No target specified" << endl;
        return 1;
    }

    // Wait for completion
    this_thread::sleep_for(chrono::seconds(2));

    auto end = chrono::steady_clock::now();
    auto duration = chrono::duration_cast<chrono::seconds>(end - start);

    cout << endl << "[*] Scan complete!" << endl;
    cout << "[*] Scanned: " << scanner.getScannedCount() << " ports" << endl;
    cout << "[*] Open: " << scanner.getOpenCount() << " ports" << endl;
    cout << "[*] Time: " << duration.count() << " seconds" << endl;

    if (!verbose && scanner.getOpenCount() > 0) {
        cout << endl << "[+] Open ports:" << endl;
        for (const auto& r : scanner.getResults()) {
            cout << "    " << r.ip << ":" << r.port 
                 << " (" << r.service << ") " << r.latency.count() << "ms" << endl;
        }
    }

    return 0;
}
