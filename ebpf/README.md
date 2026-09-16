# API-Sentinel eBPF Traffic Collector

This directory contains the kernel-level traffic collection component for API-Sentinel.

## Architecture

Linux kernel
    |
    v
eBPF network/socket tracing
    |
    v
Rust collector
    |
    v
API-Sentinel traffic ingestion

## Components

- kernel/ - eBPF programs for kernel-level traffic observation.
- collector/ - Rust userspace collector for receiving and processing eBPF events.

## Goal

Capture relevant runtime network traffic and provide structured events to the existing API-Sentinel traffic ingestion pipeline.

The collector should integrate with the existing /traffic/ingest endpoint rather than duplicate backend traffic-processing logic.
