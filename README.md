# Special Homework: Explain about Comp Arch

นายสิรภัทร ทัพภะ 6710504409

## Setup

Via `uv`:
```bash
uv sync
```

Via `pip`:
```bash
pip install -r requirements.txt
```

## Rendering

```bash
python main.py [flags] <SceneName>
```

Quality flags:
| Flag | Quality |
|------|---------|
| `-pql` | low (fast preview) |
| `-pqm` | medium |
| `-pqh` | high |
| `-pqk` | 4K |

Run without arguments to list all scenes:

```bash
python main.py
```

## Scenes

| Group | Scene |
|-------|-------|
| Single-cycle components | `TestALUScene` `TestMuxScene` `TestRegFileScene` `TestIMScene` `TestSignExtendScene` |
| Single-cycle integration | `IfALUMuxScene` |
| Single-cycle traces | `TraceRType` `TraceLW` `TraceSW` `TraceBeq` `DebugTrace` |
| Single-cycle performance | `PerformanceScene` |
| Pipeline | `PipelinedDatapathScene` `PipelinePerformanceScene` |
| Cache addressing | `CacheParamsScene` `CacheTracingScene` |
| Cache associativity | `LRUScene` `TwoWayTracingScene` `FourWayTracingScene` `ComparisonScene` |
