# eBPF Development Environment

API-Sentinel uses Rust and eBPF for kernel-level API traffic
interception and runtime visibility.

## Development Environment

- OS: Ubuntu on WSL2
- Architecture: x86_64
- Rust: 1.93.1
- Cargo: 1.93.1
- Git: 2.53.0

## Purpose

This environment will be used to develop the kernel-level
traffic interception component of API-Sentinel.

The eBPF component will eventually capture relevant network
traffic and provide runtime data to the API analysis pipeline.

## Current Status

The Linux development environment is configured and ready
for the eBPF implementation phase.
