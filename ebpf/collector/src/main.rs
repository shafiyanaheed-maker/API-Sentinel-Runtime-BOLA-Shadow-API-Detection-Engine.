use anyhow::{anyhow, Result};
use aya::{
    maps::RingBuf,
    programs::TracePoint,
    Ebpf,
};
use std::{
    thread,
    time::Duration,
};

fn main() -> Result<()> {
    let ebpf_path = "../kernel/target/bpfel-unknown-none/debug/kernel";

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

    println!("Ring buffer initialized.");
    println!();
    println!("Waiting for network connection events...");
    println!("Press Ctrl+C to stop.");
    println!();

    loop {
        while let Some(event) = ring_buf.next() {
            let data: &[u8] = &event;

            /*
             * ApiEvent contains:
             *
             * pid        = 4 bytes
             * tgid       = 4 bytes
             * uid        = 4 bytes
             * gid        = 4 bytes
             * event_type = 4 bytes
             *
             * Total = 20 bytes
             */

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
        }

        thread::sleep(Duration::from_millis(10));
    }
}