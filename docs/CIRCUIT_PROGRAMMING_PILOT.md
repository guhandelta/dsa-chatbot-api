# Circuit programming pilot: C, C++, Python, Rust

Status: design proposal, 7 November 2026. No circuit execution or hardware grading is implemented.

## One board, four language routes

Use a Raspberry Pi Pico with the RP2040 as the first target. Keep the exact board revision, pin map, SDK/runtime versions, and wiring diagram in each project template. Raspberry Pi documents a C/C++ SDK and MicroPython for the Pico family; the rp-rs project provides an RP2040 HAL and examples for Rust. This shared target allows one physical circuit to teach the same concepts while preserving each language's real toolchain.

| Route | Toolchain and runtime | First validation |
| --- | --- | --- |
| C | Pico C/C++ SDK, C source | compile firmware; test pure decision logic on host |
| C++ | Pico C/C++ SDK, C++ source | compile firmware; test pure decision logic on host |
| Python | Pico MicroPython firmware | syntax and pure logic checks; run on the target board |
| Rust | `rp2040-hal` and `thumbv6m-none-eabi` target | build firmware; test pure decision logic on host |

Pin library versions in the templates after a clean build on the supported development environment. Rust embedded support is community maintained, so verify the chosen crate and examples before locking the course. CircuitPython is a later, separate Python runtime choice; do not mix its APIs into MicroPython lessons.

## Narrow first pathway

1. Board orientation: voltage, ground, safe GPIO use, pin numbering, and reading a wiring diagram.
2. Onboard LED: output state, timing, a first firmware build/upload, and a serial or visible result.
3. External LED and button: resistor and wiring, input/output, pull-up/down, and a button-controlled output.
4. Debounce: distinguish physical bounce from software state, implement a pure transition function, then test it on the board.
5. One sensor over I2C: pin choice, bus address, missing-device behavior, and interpreting readings. Choose the sensor only after checking device support in all four routes.

Each lesson needs a diagram, expected observation, troubleshooting cases, and an explanation of what a host-side test can and cannot prove. Start with instructor-run hardware checks; a simulator can be added only after its board, peripheral, and language support are verified. A successful generic C, C++, Python, or Rust code-runner result is never a circuit pass.

## Workspace boundary and acceptance gate

Keep circuit projects in a separate workspace from DSA exercises. The workspace needs a board/pin view, wiring view, source editor, build/upload result, serial output, and evidence capture. Accept a lesson only when its source builds in the pinned toolchain, the wiring has been reviewed, a real-board observation matches the expected behavior, and at least one intentional fault produces useful feedback. Do not award circuit mastery from a text answer or host-only unit test.

Sources: Raspberry Pi [Pico SDK](https://www.raspberrypi.com/documentation/pico-sdk/index_doxygen.html) and [microcontroller guidance](https://www.raspberrypi.com/documentation/microcontrollers/microcontroller-chips.html); rp-rs [RP2040 HAL](https://github.com/rp-rs/rp-hal).
