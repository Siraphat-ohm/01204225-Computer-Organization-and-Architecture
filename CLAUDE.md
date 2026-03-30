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
# Single-cycle component tests
manim -pql single_cycle/scenes/component_tests.py TestALUScene
manim -pql single_cycle/scenes/component_tests.py TestMuxScene
manim -pql single_cycle/scenes/component_tests.py TestRegFileScene
manim -pql single_cycle/scenes/component_tests.py TestIMScene

# Single-cycle integration / trace scenes
manim -pql single_cycle/scenes/integration_scenes.py IfALUMuxScene
manim -pql single_cycle/scenes/instruction_traces.py TraceRType
manim -pql single_cycle/performance.py PerformanceScene

# Pipeline scenes
manim -pql pipeline/pipeline_datapath.py PipelinedDatapathScene
manim -pql pipeline/pipeline_performance.py PipelinePerformanceScene

# Cache addressing
manim -pql addressing/cache_params.py CacheParamsScene
manim -pql addressing/cache_tracing.py CacheTracingScene

# Cache associativity
manim -pql associativity/lru_scene.py LRUScene
manim -pql associativity/assoc_tracing.py TwoWayTracingScene
```

## Architecture

### Folder structure

```
single_cycle/          ← RISC-V single-cycle datapath
  *.py                 ← component classes (ALU, MUX, RegFile, …)
  utils.py             ← wire/animation helpers
  performance.py       ← single-cycle performance scene
  scenes/              ← single-cycle scenes (traces, integration, …)
pipeline/              ← pipeline datapath & performance scenes
addressing/            ← cache addressing scenes
associativity/         ← cache associativity scenes
```

### Component modules (`single_cycle/`)

Each file defines a single Manim `VGroup` subclass representing a RISC-V datapath component:

- **`ALU.py`** — `ALUComponent`: The characteristic P&H ALU trapezoid shape. Exposes ports via `get_input_a()`, `get_input_b()`, `get_output()`, `get_zero_port()`, `get_ctrl_port()`. Supports animated operations via `animate_operation(scene, op)` using `RV32I_ALU_OPS`.
- **`MUX.py`** — `MuxComponent`: 2-to-1 MUX as a rounded rectangle with labelled 0/1 inputs. Ports: `get_input_0()`, `get_input_1()`, `get_output()`, `get_ctrl_port()`.
- **`RegFile.py`** — `RegFileComponent`: Register file rectangle with read/write ports. Ports: `get_read_reg1/2()`, `get_write_reg()`, `get_write_data()`, `get_read_data1/2()`, `get_reg_write()`.
- **`InstructionMemory.py`** — `InstructionMemoryComponent`: Instruction memory with a multi-output instruction bus. Has individual field ports (`get_inst_31_26()` through `get_inst_15_0()`) plus `inst_bus_origin()` (intentionally not prefixed with `get_` to avoid Manim attribute interception).

### Wire/animation utilities (`single_cycle/utils.py`)

Central module imported by all single-cycle scenes. Key abstractions:

- **`make_ortho_wire(start, end, bend_x=, bend_ratio=)`** — Smart H→V→H orthogonal routing; use instead of raw `Line` for all datapath wires.
- **`make_bus_split(origin, trunk_x, branches)`** — Fan-out bus: draws entry wire + vertical spine + labelled branches. Returns a dict with keys `entry`, `spine`, `branches`, `dots`, `labels`, `all`. Use `animate_bus(scene, bus)` to animate it.
- **`make_wire_labelled(start, end, label, ...)`** — Returns `(wire, label_text)` tuple.
- **`signal_flow(scene, steps)`** — Drives a sequence of wire pulses and component highlights; each step dict can have `wire`, `component`, `label`, `value`, `ctrl`, `pause`, `run_time`.
- **`pulse_wire/pulse_wires`**, **`flash_component`**, **`highlight_component`** — Individual animation helpers.

### Scenes

- **`single_cycle/scenes/component_tests.py`** — One `TestXxxScene` per component for isolated visual testing.
- **`single_cycle/scenes/integration_scenes.py`** — `IfALUMuxScene`: Demonstrates a conditional branch using two ALUs and a MUX with full signal flow animation.
- **`single_cycle/scenes/datapath_base.py`** — `DatapathBase`: Full single-cycle datapath wiring base class, inherited by trace scenes.
- **`single_cycle/scenes/instruction_traces.py`** — Per-instruction trace scenes (TraceRType, TraceLW, TraceSW, TraceBeq).
- **`pipeline/pipeline_datapath.py`** — `PipelinedDatapathScene`: 5-stage pipeline layout reusing single-cycle components.
- **`pipeline/pipeline_performance.py`** — `PipelinePerformanceScene`: Pipeline timing diagram and performance analysis.

### Design conventions

- All port methods return absolute `np.ndarray([x, y, 0])` positions. After moving a component, its port methods automatically return the updated position — **never hardcode coordinates in scenes**.
- Control signals use `CTRL_COLOR` (`#4A90D9`); data signals use `SIGNAL_COLOR` (`YELLOW`).
- Manim intercepts `get_<name>()` calls internally; avoid naming non-port methods with the `get_` prefix on `VGroup` subclasses (see `inst_bus_origin()` in `InstructionMemory.py`).
