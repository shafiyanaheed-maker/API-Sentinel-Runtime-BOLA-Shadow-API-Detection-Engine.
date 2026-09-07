use anyhow::Result;
use aya::{
    programs::{Xdp, XdpMode},
    Ebpf,
};

fn main() -> Result<()> {
    let ebpf_path = "../kernel/target/bpfel-unknown-none/debug/kernel";

    println!("Loading eBPF object: {}", ebpf_path);

    let mut ebpf = Ebpf::load_file(ebpf_path)?;

    println!("eBPF object loaded successfully.");

    let program = ebpf
        .program_mut("api_sentinel")
        .ok_or_else(|| anyhow::anyhow!("api_sentinel program not found"))?;

    let program: &mut Xdp = program.try_into()?;

    println!("Loading XDP program into kernel...");

    program.load()?;

    println!("XDP program loaded.");

    println!("Attaching api_sentinel to eth0...");

    program.attach("eth0", XdpMode::default())?;

    println!("=================================");
    println!("XDP program attached successfully!");
    println!("Interface: eth0");
    println!("Program:   api_sentinel");
    println!("Action:    XDP_PASS");
    println!("=================================");

    println!("Press Ctrl+C to detach and exit.");

    loop {
        std::thread::park();
    }
}