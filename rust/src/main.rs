// NullSec Hash Cracker
// Multi-threaded hash cracking tool written in Rust
// Author: bad-antics | Twitter: bad-antics | Discord: discord.gg/killers

use std::env;
use std::fs::File;
use std::io::{BufRead, BufReader};
use std::sync::atomic::{AtomicBool, AtomicU64, Ordering};
use std::sync::Arc;
use std::thread;
use std::time::Instant;
use md5;
use sha1::Sha1;
use sha2::{Sha256, Sha512, Digest};

const BANNER: &str = r#"
╔═══════════════════════════════════════════════════════════╗
║     ███╗   ██╗██╗   ██╗██╗     ██╗     ███████╗███████╗   ║
║     ████╗  ██║██║   ██║██║     ██║     ██╔════╝██╔════╝   ║
║     ██╔██╗ ██║██║   ██║██║     ██║     ███████╗█████╗     ║
║     ██║╚██╗██║██║   ██║██║     ██║     ╚════██║██╔══╝     ║
║     ██║ ╚████║╚██████╔╝███████╗███████╗███████║███████╗   ║
║     ╚═╝  ╚═══╝ ╚═════╝ ╚══════╝╚══════╝╚══════╝╚══════╝   ║
║                   HASH CRACKER (Rust)                      ║
║            bad-antics | bad-antics | discord.gg/killers  ║
╚═══════════════════════════════════════════════════════════╝
"#;

#[derive(Clone, Copy, PartialEq)]
enum HashType {
    MD5,
    SHA1,
    SHA256,
    SHA512,
}

fn detect_hash_type(hash: &str) -> Option<HashType> {
    match hash.len() {
        32 => Some(HashType::MD5),
        40 => Some(HashType::SHA1),
        64 => Some(HashType::SHA256),
        128 => Some(HashType::SHA512),
        _ => None,
    }
}

fn hash_password(password: &str, hash_type: HashType) -> String {
    match hash_type {
        HashType::MD5 => format!("{:x}", md5::compute(password)),
        HashType::SHA1 => {
            let mut hasher = Sha1::new();
            hasher.update(password.as_bytes());
            format!("{:x}", hasher.finalize())
        }
        HashType::SHA256 => {
            let mut hasher = Sha256::new();
            hasher.update(password.as_bytes());
            format!("{:x}", hasher.finalize())
        }
        HashType::SHA512 => {
            let mut hasher = Sha512::new();
            hasher.update(password.as_bytes());
            format!("{:x}", hasher.finalize())
        }
    }
}

fn crack_hash(
    target_hash: &str,
    hash_type: HashType,
    wordlist: Vec<String>,
    found: Arc<AtomicBool>,
    attempts: Arc<AtomicU64>,
) -> Option<String> {
    for word in wordlist {
        if found.load(Ordering::Relaxed) {
            return None;
        }
        
        attempts.fetch_add(1, Ordering::Relaxed);
        let computed = hash_password(&word, hash_type);
        
        if computed == target_hash.to_lowercase() {
            found.store(true, Ordering::Relaxed);
            return Some(word);
        }
    }
    None
}

fn main() {
    println!("{}", BANNER);
    
    let args: Vec<String> = env::args().collect();
    
    if args.len() < 3 {
        eprintln!("Usage: {} <hash> <wordlist> [threads]", args[0]);
        eprintln!("\nSupported hash types:");
        eprintln!("  MD5     (32 chars)");
        eprintln!("  SHA1    (40 chars)");
        eprintln!("  SHA256  (64 chars)");
        eprintln!("  SHA512  (128 chars)");
        std::process::exit(1);
    }
    
    let target_hash = &args[1];
    let wordlist_path = &args[2];
    let num_threads: usize = args.get(3).and_then(|s| s.parse().ok()).unwrap_or(4);
    
    let hash_type = match detect_hash_type(target_hash) {
        Some(t) => t,
        None => {
            eprintln!("[-] Unknown hash type (length: {})", target_hash.len());
            std::process::exit(1);
        }
    };
    
    let hash_name = match hash_type {
        HashType::MD5 => "MD5",
        HashType::SHA1 => "SHA1",
        HashType::SHA256 => "SHA256",
        HashType::SHA512 => "SHA512",
    };
    
    println!("[*] Target hash: {}", target_hash);
    println!("[*] Hash type: {}", hash_name);
    println!("[*] Wordlist: {}", wordlist_path);
    println!("[*] Threads: {}", num_threads);
    println!();
    
    // Load wordlist
    let file = match File::open(wordlist_path) {
        Ok(f) => f,
        Err(e) => {
            eprintln!("[-] Failed to open wordlist: {}", e);
            std::process::exit(1);
        }
    };
    
    let reader = BufReader::new(file);
    let words: Vec<String> = reader.lines().filter_map(|l| l.ok()).collect();
    let total_words = words.len();
    
    println!("[*] Loaded {} words", total_words);
    println!("[*] Starting crack...\n");
    
    let chunk_size = (total_words + num_threads - 1) / num_threads;
    let found = Arc::new(AtomicBool::new(false));
    let attempts = Arc::new(AtomicU64::new(0));
    let start_time = Instant::now();
    
    let mut handles = vec![];
    
    for chunk in words.chunks(chunk_size) {
        let chunk_vec = chunk.to_vec();
        let target = target_hash.to_string();
        let found_clone = Arc::clone(&found);
        let attempts_clone = Arc::clone(&attempts);
        
        let handle = thread::spawn(move || {
            crack_hash(&target, hash_type, chunk_vec, found_clone, attempts_clone)
        });
        handles.push(handle);
    }
    
    let mut result: Option<String> = None;
    for handle in handles {
        if let Some(password) = handle.join().unwrap() {
            result = Some(password);
        }
    }
    
    let elapsed = start_time.elapsed();
    let total_attempts = attempts.load(Ordering::Relaxed);
    let speed = total_attempts as f64 / elapsed.as_secs_f64();
    
    println!();
    match result {
        Some(password) => {
            println!("╔════════════════════════════════════════╗");
            println!("║            PASSWORD FOUND!             ║");
            println!("╠════════════════════════════════════════╣");
            println!("║ Hash:     {:<28} ║", &target_hash[..28.min(target_hash.len())]);
            println!("║ Password: {:<28} ║", password);
            println!("╚════════════════════════════════════════╝");
        }
        None => {
            println!("[-] Password not found in wordlist");
        }
    }
    
    println!("\n[*] Statistics:");
    println!("    Attempts: {}", total_attempts);
    println!("    Time: {:.2?}", elapsed);
    println!("    Speed: {:.0} H/s", speed);
}
