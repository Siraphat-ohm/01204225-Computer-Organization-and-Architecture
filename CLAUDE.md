# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Manim-based visualization project for a Computer Architecture course report. It renders animated diagrams of a RISC-V single-cycle datapath, modelled after the Patterson & Hennessy schematic.

## Commands

**Environment**: Uses `uv` with a `.venv`. Python 3.12 required.

**Render a scene** (low quality, preview):
```
manim -pql <file.py> <SceneName>
```

**Render high quality**:
```
manim -pqh <file.py> <SceneName>
```

**Examples**:
```bash
# Render individual component tests
manim -pql scenes/component_tests.py TestALUScene
manim -pql scenes/component_tests.py TestMuxScene
manim -pql scenes/component_tests.py TestRegFileScene
manim -pql scenes/component_tests.py TestIMScene

# Render integration scenes
manim -pql scenes/integration_scenes.py IfALUMuxScene
manim -pql wiring_test.py DatapathTest
```

## Architecture

### Component modules (root directory)

Each file defines a single Manim `VGroup` subclass representing a RISC-V datapath component:

- **`ALU.py`** — `ALUComponent`: The characteristic P&H ALU trapezoid shape. Exposes ports via `get_input_a()`, `get_input_b()`, `get_output()`, `get_zero_port()`, `get_ctrl_port()`. Supports animated operations via `animate_operation(scene, op)` using `RV32I_ALU_OPS`.
- **`MUX.py`** — `MuxComponent`: 2-to-1 MUX as a rounded rectangle with labelled 0/1 inputs. Ports: `get_input_0()`, `get_input_1()`, `get_output()`, `get_ctrl_port()`.
- **`RegFile.py`** — `RegFileComponent`: Register file rectangle with read/write ports. Ports: `get_read_reg1/2()`, `get_write_reg()`, `get_write_data()`, `get_read_data1/2()`, `get_reg_write()`.
- **`InstructionMemory.py`** — `InstructionMemoryComponent`: Instruction memory with a multi-output instruction bus. Has individual field ports (`get_inst_31_26()` through `get_inst_15_0()`) plus `inst_bus_origin()` (intentionally not prefixed with `get_` to avoid Manim attribute interception).

### Wire/animation utilities (`utils.py`)

Central module imported by all scenes. Key abstractions:

- **`make_ortho_wire(start, end, bend_x=, bend_ratio=)`** — Smart H→V→H orthogonal routing; use instead of raw `Line` for all datapath wires.
- **`make_bus_split(origin, trunk_x, branches)`** — Fan-out bus: draws entry wire + vertical spine + labelled branches. Returns a dict with keys `entry`, `spine`, `branches`, `dots`, `labels`, `all`. Use `animate_bus(scene, bus)` to animate it.
- **`make_wire_labelled(start, end, label, ...)`** — Returns `(wire, label_text)` tuple.
- **`signal_flow(scene, steps)`** — Drives a sequence of wire pulses and component highlights; each step dict can have `wire`, `component`, `label`, `value`, `ctrl`, `pause`, `run_time`.
- **`pulse_wire/pulse_wires`**, **`flash_component`**, **`highlight_component`** — Individual animation helpers.

### Scenes

- **`scenes/component_tests.py`** — One `TestXxxScene` per component for isolated visual testing. Imports components via `sys.path` manipulation pointing to the parent directory.
- **`scenes/integration_scenes.py`** — `IfALUMuxScene`: Demonstrates a conditional branch using two ALUs and a MUX with full signal flow animation.
- **`wiring_test.py`** — `DatapathTest`: Full wiring harness connecting InstructionMemory → MUX → RegFile using `make_bus_split` and `make_ortho_wire`. Serves as the reference for correct bus layout patterns.

### Design conventions

- All port methods return absolute `np.ndarray([x, y, 0])` positions. After moving a component, its port methods automatically return the updated position — **never hardcode coordinates in scenes**.
- Control signals use `CTRL_COLOR` (`#4A90D9`); data signals use `SIGNAL_COLOR` (`YELLOW`).
- Manim intercepts `get_<name>()` calls internally; avoid naming non-port methods with the `get_` prefix on `VGroup` subclasses (see `inst_bus_origin()` in `InstructionMemory.py`).
