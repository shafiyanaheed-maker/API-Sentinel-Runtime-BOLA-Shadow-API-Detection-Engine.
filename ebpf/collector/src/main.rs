use anyhow::{anyhow, Result};
use aya::{
    maps::RingBuf,
    programs::TracePoint,
    Ebpf,
};
use reqwest::blocking::Client;
use serde_json::json;
use std::{
    thread,
    time::Duration,
};

fn main() -> Result<()> {
    let ebpf_path = "../kernel/target/bpfel-unknown-none/debug/kernel";
    let api_url = "http://127.0.0.1:8000/api/v1/traffic/ingest";

    println!("=================================");
    println!("API-Sentinel eBPF Traffic Collector");
    println!("=================================");
    println!("Loading eBPF object: {}", ebpf_path);

    let mut ebpf = Ebpf::load_file(ebpf_path)?;

    println!("eBPF object loaded successfully.");

    {
        let program = ebpf
            .program_mut("api_sentinel")
            .ok_or_else(|| anyhow!("api_sentinel program not found"))?;

        let program: &mut TracePoint = program.try_into()?;

        println!("Loading tracepoint program...");
        program.load()?;

        println!("Attaching to:");
        println!("  category: syscalls");
        println!("  event:    sys_enter_connect");

        program.attach("syscalls", "sys_enter_connect")?;

        println!("Tracepoint attached successfully.");
    }

    let mut ring_buf = RingBuf::try_from(
        ebpf.map_mut("EVENTS")
            .ok_or_else(|| anyhow!("EVENTS map not found"))?,
    )?;

    let client = Client::new();

    println!("Ring buffer initialized.");
    println!("API endpoint: {}", api_url);
    println!();
    println!("Waiting for network connection events...");
    println!("Press Ctrl+C to stop.");
    println!();

    loop {
        while let Some(event) = ring_buf.next() {
            let data: &[u8] = &event;

            if data.len() != 20 {
                println!(
                    "Received unexpected event size: {} bytes",
                    data.len()
                );
                continue;
            }

            let pid = u32::from_ne_bytes(
                data[0..4]
                    .try_into()
                    .map_err(|_| anyhow!("invalid pid data"))?,
            );

            let tgid = u32::from_ne_bytes(
                data[4..8]
                    .try_into()
                    .map_err(|_| anyhow!("invalid tgid data"))?,
            );

            let uid = u32::from_ne_bytes(
                data[8..12]
                    .try_into()
                    .map_err(|_| anyhow!("invalid uid data"))?,
            );

            let gid = u32::from_ne_bytes(
                data[12..16]
                    .try_into()
                    .map_err(|_| anyhow!("invalid gid data"))?,
            );

            let event_type = u32::from_ne_bytes(
                data[16..20]
                    .try_into()
                    .map_err(|_| anyhow!("invalid event_type data"))?,
            );

            println!(
                "[API-SENTINEL] event_type={} pid={} tgid={} uid={} gid={}",
                event_type,
                pid,
                tgid,
                uid,
                gid
            );

            let payload = json!({
                "method": "CONNECT",
                "path": "/ebpf/connect",
                "host": "kernel",
                "status_code": 200,
                "source_ip": "127.0.0.1",
                "destination_ip": null,
                "authenticated_user_id": uid,
                "user_role": "system",
                "request_headers": {
                    "x-ebpf-event": "connect",
                    "x-ebpf-pid": pid.to_string(),
                    "x-ebpf-tgid": tgid.to_string(),
                    "x-ebpf-gid": gid.to_string(),
                    "x-ebpf-event-type": event_type.to_string()
                },
                "request_body": null,
                "response_headers": {},
                "response_body": null,
                "latency_ms": 0
            });

            match client.post(api_url).json(&payload).send() {
                Ok(response) => {
                    if response.status().is_success() {
                        println!(
                            "[API-SENTINEL] forwarded successfully: HTTP {}",
                            response.status()
                        );
                    } else {
                        println!(
                            "[API-SENTINEL] API rejected event: HTTP {}",
                            response.status()
                        );
                    }
                }

                Err(error) => {
                    println!(
                        "[API-SENTINEL] failed to forward event: {}",
                        error
                    );
                }
            }
        }

        thread::sleep(Duration::from_millis(10));
    }
}