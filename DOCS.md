# Manim RISC-V Datapath — Component & Utils Reference

---

## Table of Contents

1. [Design conventions](#design-conventions)
2. [Components](#components)
   - [ALU](#alu)
   - [MUX](#mux)
   - [RegFile](#regfile)
   - [InstructionMemory](#instructionmemory)
   - [SignExtend](#signextend)
   - [ALUControl](#alucontrol)
   - [DataMemory](#datamemory)
   - [ShiftLeft2](#shiftleft2)
   - [PC](#pc)
   - [Control](#control)
3. [Utils](#utils)
   - [Constants](#constants)
   - [Wire builders](#wire-builders)
   - [Bus splitter](#bus-splitter)
   - [Connections](#connections)
   - [Animation helpers](#animation-helpers)

---

## Design conventions

- Every component is a `VGroup` subclass. After calling `.move_to()`, `.scale()`, or `.shift()`, all port methods return **updated absolute positions** automatically — never cache a port value before positioning.
- All port methods return `np.ndarray([x, y, 0])`.
- Port methods are **not** prefixed with `get_` only when they are not true ports, to avoid Manim's VGroup attribute interception (e.g., `inst_bus_origin()`).
- Control signals use `CTRL_COLOR = "#4A90D9"` (blue). Data signals use `SIGNAL_COLOR = YELLOW`.
- All components expose `self.shape` — the main Manim primitive — for use in `animate_data_path`.

---

## Components

---

### ALU

**File:** `ALU.py`
**Class:** `ALUComponent(VGroup)`
**Shape:** P&H trapezoid with a notch on the left for two inputs and a right-pointing tip for output.

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `width` | float | `2.2` | Width of the body |
| `height` | float | `3.0` | Height of the body |
| `body_color` | str | `"#4A90D9"` | Stroke and label color |
| `label` | str | `"ALU"` | Text displayed in center |
| `port_offset` | float | `0.15` | Gap between shape edge and port point |

#### Ports

| Method | Side | Description |
|--------|------|-------------|
| `get_input_a()` | Left (upper) | Operand A input |
| `get_input_b()` | Left (lower) | Operand B input |
| `get_output()` | Right tip | ALU result |
| `get_zero_port()` | Top-right | Zero flag output |
| `get_ctrl_port()` | Bottom | 4-bit ALU control signal |

#### Extra methods

```python
alu.set_operation("ADD")           # Updates the operation label in-place
alu.animate_operation(scene, "ADD") # Plays Indicate + FadeIn of operation label
```

**Available ops:** `ADD`, `SUB`, `AND`, `OR`, `XOR`, `SLL`, `SRL`, `SRA`, `SLT`, `SLTU`, `PASS`

#### Example

```python
alu = ALUComponent(label="ALU").scale(0.85).move_to(RIGHT * 8.0)
alu.shift(UP * (rf.get_read_data1()[1] - alu.get_input_a()[1]))  # align with port
```

---

### MUX

**File:** `MUX.py`
**Class:** `MuxComponent(VGroup)`
**Shape:** Rounded rectangle with 0/1 labels.

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `width` | float | `0.6` | Width |
| `height` | float | `1.5` | Height |
| `body_color` | str | `"#555555"` | Shape color |
| `ctrl_color` | str | `"#4A90D9"` | (reserved, not currently used) |
| `label` | str | `"MUX"` | Text rendered vertically in center |
| `port_offset` | float | `0.15` | Gap between edge and port |

#### Ports

| Method | Side | Description |
|--------|------|-------------|
| `get_input_0()` | Left upper | Input 0 |
| `get_input_1()` | Left lower | Input 1 |
| `get_output()` | Right | Output |
| `get_ctrl_port()` | Bottom | Select line |

#### Example

```python
mux = MuxComponent().move_to(LEFT * 0.9 + DOWN * 0.63)

# Auto-align ALU MUX output with ALU input B
alu_mux = MuxComponent().move_to(RIGHT * 5.8)
alu_mux.shift(UP * (alu.get_input_b()[1] - alu_mux.get_output()[1]))
```

---

### RegFile

**File:** `RegFile.py`
**Class:** `RegFileComponent(VGroup)`
**Shape:** Rectangle with 4 left-side inputs and 2 right-side outputs.

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `width` | float | `3.2` | Width |
| `height` | float | `4.2` | Height |
| `body_color` | str | `"#DDDDDD"` | Shape color |
| `ctrl_color` | str | `"#4A90D9"` | (reserved) |
| `label` | str | `"Registers"` | Bottom-right label |
| `port_offset` | float | `0.15` | Gap between edge and port |

#### Ports

| Method | Side | Description |
|--------|------|-------------|
| `get_read_reg1()` | Left (top) | Read register 1 address |
| `get_read_reg2()` | Left (upper-mid) | Read register 2 address |
| `get_write_reg()` | Left (lower-mid) | Write register address |
| `get_write_data()` | Left (bottom) | Write data |
| `get_read_data1()` | Right (upper) | Read data 1 output |
| `get_read_data2()` | Right (lower) | Read data 2 output |
| `get_reg_write()` | Top (center) | RegWrite control signal |

#### Example

```python
rf = RegFileComponent(width=3.0, height=4.2).move_to(RIGHT * 2.8)
rd1 = rf.get_read_data1()
```

---

### InstructionMemory

**File:** `InstructionMemory.py`
**Class:** `InstructionMemoryComponent(VGroup)`
**Shape:** Rectangle with one left input and a multi-port instruction bus on the right.

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `width` | float | `2.8` | Width |
| `height` | float | `3.2` | Height |
| `body_color` | str | `"#DDDDDD"` | Shape color |
| `port_offset` | float | `0.15` | Input port gap |
| `output_offset` | float | `0.15` | Output port gap |
| `port_y_overrides` | dict | `None` | Override any field port Y fractions |
| `show_port_labels` | bool | `True` | Show field labels on right side |

#### Ports

| Method | Side | Description |
|--------|------|-------------|
| `get_read_address()` | Left | PC input |
| `inst_bus_origin()` | Right | Origin point for `make_bus_split()` — **no `get_` prefix** |
| `get_inst_31_26()` | Right | Opcode field |
| `get_inst_25_21()` | Right | rs1 field |
| `get_inst_20_16()` | Right | rs2/rt field |
| `get_inst_15_11()` | Right | rd field |
| `get_inst_15_0()` | Right | Immediate / lower 16 bits |

> **Note:** Use `inst_bus_origin()` (no `get_`) as the `origin` argument for `make_bus_split()`. The `get_` prefix causes Manim to intercept the call.

#### Example

```python
im = InstructionMemoryComponent(width=2.6, height=3.8, show_port_labels=False)
im.move_to(LEFT * 4.8)
origin = im.inst_bus_origin()
```

---

### SignExtend

**File:** `SignExtend.py`
**Class:** `SignExtendComponent(VGroup)`
**Shape:** Trapezoid (narrow left, wide right).

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `width` | float | `2.0` | Width |
| `height` | float | `1.6` | Height |
| `body_color` | str | `"#DDDDDD"` | Shape color |
| `label` | str | `"Sign-\nextend"` | Center label |
| `port_offset` | float | `0.15` | Port gap |

#### Ports

| Method | Side | Description |
|--------|------|-------------|
| `get_input()` | Left | 16-bit immediate input |
| `get_output()` | Right | 32-bit sign-extended output |

---

### ALUControl

**File:** `ALUControl.py`
**Class:** `ALUControlComponent(VGroup)`
**Shape:** Rounded pill (RoundedRectangle with `corner_radius = height/2`).

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `width` | float | `2.0` | Width |
| `height` | float | `1.0` | Height |
| `body_color` | str | `"#4A90D9"` | Shape and label color |
| `label` | str | `"ALU\ncontrol"` | Center label |
| `port_offset` | float | `0.15` | Port gap |

#### Ports

| Method | Side | Description |
|--------|------|-------------|
| `get_funct_input()` | Top-left | Funct field from instruction (routed from below in datapath) |
| `get_aluop_input()` | Top-right | ALUOp from main Control unit |
| `get_alu_ctrl_output()` | Right | 4-bit ALU control signal to ALU |

#### Example

```python
alu_control = ALUControlComponent().move_to(RIGHT * 7.0 + DOWN * 3.5)

# Inst[5-0] wire routed below Sign-extend via V-H-V
"funct_ac": make_connection(
    funct_junc, alu_control.get_funct_input(),
    ctrl=True, label="Inst[5–0]",
    tip_dir=DOWN,
    wire_func=make_v_h_v_wire,
    bend_y=funct_corridor_y,
),
```

---

### DataMemory

**File:** `DataMemory.py`
**Class:** `DataMemoryComponent(VGroup)`
**Shape:** Rectangle with Address and Write data on left, Read data on right, control signals on top.

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `width` | float | `2.8` | Width |
| `height` | float | `3.8` | Height |
| `body_color` | str | `"#DDDDDD"` | Shape color |
| `ctrl_color` | str | `"#4A90D9"` | (reserved) |
| `port_offset` | float | `0.15` | Port gap |

#### Ports

| Method | Side | Description |
|--------|------|-------------|
| `get_address()` | Left (upper) | ALU result — memory address |
| `get_write_data()` | Left (lower) | Data to write (from RegFile Read data 2) |
| `get_read_data()` | Right | Data read from memory |
| `get_mem_read()` | Top-left | MemRead control signal |
| `get_mem_write()` | Top-right | MemWrite control signal |

---

### ShiftLeft2

**File:** `ShiftLeft2.py`
**Class:** `ShiftLeft2Component(VGroup)`
**Shape:** Trapezoid (same style as SignExtend).

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `width` | float | `1.6` | Width |
| `height` | float | `1.2` | Height |
| `body_color` | str | `"#DDDDDD"` | Shape color |
| `label` | str | `"Shift\nleft 2"` | Center label |
| `port_offset` | float | `0.15` | Port gap |

#### Ports

| Method | Side | Description |
|--------|------|-------------|
| `get_input()` | Left | 32-bit sign-extended immediate |
| `get_output()` | Right | Left-shifted by 2 (branch offset) |

---

### PC

**File:** `PC.py`
**Class:** `PCComponent(VGroup)`
**Shape:** Small rectangle.

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `width` | float | `1.0` | Width |
| `height` | float | `2.0` | Height |
| `body_color` | str | `"#DDDDDD"` | Shape color |
| `label` | str | `"PC"` | Center label |
| `port_offset` | float | `0.15` | Port gap |

#### Ports

| Method | Side | Description |
|--------|------|-------------|
| `get_input()` | Left | Next PC value |
| `get_output()` | Right | Current PC value (fans out to IM and PC+4 adder) |

---

### Control

**File:** `Control.py`
**Class:** `ControlComponent(VGroup)`
**Shape:** Ellipse (P&H style oval).

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `width` | float | `2.4` | Width |
| `height` | float | `3.6` | Height |
| `body_color` | str | `"#4A90D9"` | Shape and label color |
| `port_offset` | float | `0.15` | Port gap |

#### Ports

| Method | Side | Description |
|--------|------|-------------|
| `get_opcode_input()` | Left (center) | Opcode / Inst[31-26] |
| `get_reg_dst()` | Right (1/8) | RegDst |
| `get_branch()` | Right (2/8) | Branch |
| `get_mem_read()` | Right (3/8) | MemRead |
| `get_mem_to_reg()` | Right (4/8) | MemtoReg |
| `get_alu_op()` | Right (5/8) | ALUOp |
| `get_mem_write()` | Right (6/8) | MemWrite |
| `get_alu_src()` | Right (7/8) | ALUSrc |
| `get_reg_write()` | Right (8/8) | RegWrite |

Output ports are evenly spaced over 70% of the ellipse height, top to bottom.

#### Example

```python
ctrl = ControlComponent().move_to(UP * 4.0 + RIGHT * 1.0)

make_connection(ctrl.get_reg_dst(), mux.get_ctrl_port(),
                ctrl=True, label="RegDst", wire_func=make_v_h_v_wire)
```

---

## Utils

**File:** `utils.py`

---

### Constants

```python
SIGNAL_COLOR = YELLOW        # data wire pulses
CTRL_COLOR   = "#4A90D9"     # control signal wires
STROKE_WIDTH = 2.5           # default wire thickness
DOT_RADIUS   = 0.07          # junction dot radius
LABEL_FONT   = 12            # default wire label font size
LABEL_OFFSET = 0.13          # gap between wire and label
```

---

### Wire builders

All wire builders return a `VMobject` (or `_Polyline`) and accept `color` and `stroke_width`.

---

#### `make_straight_wire(start, end, color, stroke_width)`

Returns a native Manim `Line`. Use when start and end share the same x or y.

```python
wire = make_straight_wire(
    np.array([-1, 0, 0]),
    np.array([ 1, 0, 0]),
    color=WHITE,
)
```

---

#### `make_ortho_wire(start, end, *, bend_x, bend_ratio, color, stroke_width)`

**H → V → H** routing. The default wire type used by `make_connection`.

| Parameter | Default | Description |
|-----------|---------|-------------|
| `bend_x` | `None` | X position of the vertical segment. If omitted uses `bend_ratio` |
| `bend_ratio` | `0.5` | Fraction of horizontal distance for the bend. `0.0` = bend immediately, `1.0` = bend at destination |

```python
wire = make_ortho_wire(port_a, port_b, bend_x=3.0)
wire = make_ortho_wire(port_a, port_b, bend_ratio=0.3)
```

---

#### `make_v_h_v_wire(start, end, *, bend_y, bend_ratio, color, stroke_width)`

**V → H → V** routing. Use for control lines dropping from above or wires routing around components.

| Parameter | Default | Description |
|-----------|---------|-------------|
| `bend_y` | `None` | Y position of the horizontal corridor segment |
| `bend_ratio` | `0.5` | Fraction of vertical distance for the bend if `bend_y` omitted |

```python
# Route Inst[5-0] below Sign-extend up to ALU Control
wire = make_v_h_v_wire(funct_junc, ac_funct, bend_y=se_in[1] - 1.2)
```

---

#### `make_routed_wire(*waypoints, color, stroke_width)`

Explicit waypoints — you control every corner. Pass as many points as needed.

```python
wire = make_routed_wire(
    start,
    np.array([start[0], mid_y, 0]),
    np.array([end[0],   mid_y, 0]),
    end,
    color=CTRL_COLOR,
)
```

---

#### `make_feedback_wire(start, end, *, offset_y, color, stroke_width)`

**U-turn** wire for writeback or PC feedback paths. Routes below the datapath.

| Parameter | Default | Description |
|-----------|---------|-------------|
| `offset_y` | `-1.0` | Negative = corridor runs below the lower of the two endpoints |

```python
# Writeback: Data memory → RegFile write data
wire = make_feedback_wire(dm.get_read_data(), rf.get_write_data(), offset_y=-1.5)
```

---

#### `make_junction(pos, radius, color)`

Returns a filled `Dot` for T/cross junctions.

```python
dot = make_junction(np.array([x, y, 0]), color=CTRL_COLOR)
self.play(FadeIn(dot))
```

---

### Bus splitter

#### `make_bus_split(origin, trunk_x, branches, *, trunk_color, stroke_width, label_font)`

Builds an instruction bus fan-out: one entry wire, a vertical spine, and multiple labelled branches.

| Parameter | Type | Description |
|-----------|------|-------------|
| `origin` | ndarray | Start of the bus (use `im.inst_bus_origin()`) |
| `trunk_x` | float | X position of the vertical spine |
| `branches` | list[dict] | One dict per branch (see below) |

**Branch dict keys:**

| Key | Required | Description |
|-----|----------|-------------|
| `y` | yes | Y of the tap on the spine — set to destination port Y for straight runs |
| `dest` | yes | End point of the branch wire |
| `label` | no | Text label (e.g. `"Inst[25–21]"`) |
| `label_side` | no | `UP` or `DOWN` (default `UP`) |
| `bend_x` | no | X of horizontal bend for branches that must detour around other wires |
| `dot` | no | `True` (default) shows a junction dot; `False` suppresses it |
| `color` | no | Override color for this branch |

**Returns dict:**

```
{
  "entry":    VMobject,          # horizontal wire from origin to spine
  "spine":    VMobject,          # vertical bus bar
  "branches": list[VMobject],    # one wire per branch
  "dots":     list[Dot],
  "labels":   list[Text],
  "all":      list[VMobject],    # everything, for bulk FadeIn
}
```

**Animate with:**

```python
animate_bus(scene, bus, trunk_rt=0.5, branch_rt=0.7, stagger=0.15)
```

| Parameter | Default | Description |
|-----------|---------|-------------|
| `trunk_rt` | `0.5` | Run time for entry + spine |
| `branch_rt` | `0.6` | Total run time for all branches |
| `stagger` | `0.12` | Lag ratio between branches |

#### Full example

```python
bus = make_bus_split(
    origin  = im.inst_bus_origin(),
    trunk_x = im.inst_bus_origin()[0] + 0.5,
    branches = [
        {"y": rr1[1], "dest": rr1, "label": "Inst[25–21]"},
        {"y": rr2[1], "dest": rr2, "label": "Inst[20–16]", "dot": True, "bend_x": -1.5},
        {"y": se_in[1], "dest": se_in, "label": "Inst[15–0]"},
    ],
)
animate_bus(scene, bus)
```

---

### Connections

#### `make_connection(start, end, *, label, arrow, tip_length, tip_dir, label_side, label_color, color, ctrl, wire_func, **wire_kwargs)`

One-call wire + arrowhead + label. Returns a dict.

| Parameter | Default | Description |
|-----------|---------|-------------|
| `label` | `""` | Wire label text |
| `arrow` | `True` | Whether to draw a stub arrowhead at the destination |
| `tip_length` | `0.15` | Arrowhead length |
| `tip_dir` | `LEFT` | Direction the arrowhead points **into** the port (`LEFT`, `RIGHT`, `UP`, `DOWN`) |
| `label_side` | `UP` | `UP` or `DOWN` |
| `label_color` | `WHITE` | Label color (defaults to wire color) |
| `color` | `WHITE` | Wire color (overridden to `CTRL_COLOR` if `ctrl=True`) |
| `ctrl` | `False` | If `True`, colors wire + arrow with `CTRL_COLOR` |
| `wire_func` | `make_ortho_wire` | Wire routing function |
| `**wire_kwargs` | — | Forwarded to `wire_func` (e.g. `bend_x`, `bend_y`, `bend_ratio`) |

**Returns:**

```python
{
  "wire":  VMobject,
  "arrow": Arrow | None,
  "label": Text | None,
  "all":   VGroup,       # everything bundled
}
```

```python
conn = make_connection(
    rd1, alu_a,
    label="Read data 1",
)

ctrl_conn = make_connection(
    amsel + DOWN * 0.5, amsel,
    arrow=False, ctrl=True, label="ALUSrc",
    wire_func=make_straight_wire,
)

# V-H-V with custom bend_y
funct_conn = make_connection(
    funct_junc, ac_funct,
    ctrl=True, label="Inst[5–0]",
    tip_dir=DOWN,
    wire_func=make_v_h_v_wire,
    bend_y=funct_corridor_y,
)
```

---

#### `draw_connections(scene, connections, run_time)`

Batch-animates a dict of named connections in a single `scene.play()` call.

| Parameter | Default | Description |
|-----------|---------|-------------|
| `connections` | — | `dict[str, conn_dict]` — keyed by any name |
| `run_time` | `0.8` | Total run time for the batch |

```python
wires = {
    "rd1_alu":  make_connection(rd1, alu_a, label="Read data 1"),
    "rd2_am0":  make_connection(rd2, am0,   label="Read data 2"),
    "alusrc":   make_connection(amsel + DOWN * 0.5, amsel,
                                ctrl=True, arrow=False,
                                wire_func=make_straight_wire),
}
draw_connections(scene, wires, run_time=0.8)
```

---

### Animation helpers

#### `animate_data_path(scene, path, *, wire_rt, comp_rt, pause, data_color, ctrl_color)`

Drives a signal trace through a sequence of wires and components.

| Parameter | Default | Description |
|-----------|---------|-------------|
| `wire_rt` | `0.35` | Run time per wire pulse |
| `comp_rt` | `0.40` | Run time per component flash |
| `pause` | `0.15` | Wait between each step |
| `data_color` | `SIGNAL_COLOR` | Color for data wires |
| `ctrl_color` | `CTRL_COLOR` | Color for control wires |

**Step dict keys:**

| Key | Description |
|-----|-------------|
| `"wire": w` | Pulse wire in data color |
| `"wire": w, "label": "A+B"` | Pulse wire + floating value text |
| `"ctrl": w` | Pulse wire in control color |
| `"component": c` | Flash component with `Indicate` |
| `"component": c, "label": "ALU"` | Flash + show banner text above |
| `"run_time": 0.5` | Per-step override |
| `"pause": 0.3` | Per-step wait override |

```python
animate_data_path(scene, [
    {"component": im.shape, "label": "Fetch"},
    {"wire": bus["entry"]},
    {"wire": bus["spine"]},
    *[{"wire": w} for w in bus["branches"]],
    {"component": se.shape, "label": "Sign-extend"},
    {"wire": wires["se_am1"]["wire"]},
    {"ctrl": wires["alusrc"]["wire"]},
    {"component": alu_mux.shape, "label": "ALUSrc MUX"},
    {"wire": wires["amux_alu"]["wire"]},
    {"ctrl": wires["ac_alu"]["wire"]},
    {"component": alu.shape, "label": "ALU"},
    {"wire": wires["alu_out"]["wire"]},
])
```

---

#### Other helpers

```python
make_stub_arrow(port, direction=LEFT, length=1.0, color=GRAY)
# Returns an Arrow pointing into port from length away.
# Used internally by make_connection.

make_junction(pos, radius=DOT_RADIUS, color=WHITE)
# Returns a filled Dot for bus junctions.

pulse_wire(scene, wire, color=SIGNAL_COLOR, run_time=0.4, restore=True)
# Pulse a single wire, then restore its original color.

pulse_wires(scene, [w1, w2], color=SIGNAL_COLOR, run_time=0.35, restore=True)
# Pulse multiple wires simultaneously.

flash_component(scene, mob, color=SIGNAL_COLOR, scale=1.05, run_time=0.4)
# One Indicate flash.

highlight_component(scene, component, label="", run_time=0.5)
# Indicate + optional floating label above component.
```
