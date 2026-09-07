#![no_std]
#![no_main]

use aya_ebpf::{
    bindings::xdp_action,
    macros::xdp,
    programs::XdpContext,
};

#[panic_handler]
fn panic(_info: &core::panic::PanicInfo) -> ! {
    loop {}
}

#[xdp]
pub fn api_sentinel(ctx: XdpContext) -> u32 {
    match try_api_sentinel(ctx) {
        Ok(ret) => ret,
        Err(_) => xdp_action::XDP_ABORTED,
    }
}

fn try_api_sentinel(_ctx: XdpContext) -> Result<u32, ()> {
    Ok(xdp_action::XDP_PASS)
}
