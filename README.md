# Special Homework: Explain about Comp Arch 

นายสิรภัทร ทัพภะ 6710504409

## Available Scenes

| Group | Scenes |
| --- | --- |
| Single-cycle traces | TraceRType TraceLW TraceSW TraceBeq |
| Single-cycle | PerformanceScene DatapathBase |
| Pipeline | PipelinedDatapathScene PipelinePerformanceScene |
| Cache addressing | CacheParamsScene CacheTracingScene |
| Cache associativity | LRUScene TwoWayTracingScene FourWayTracingScene ComparisonScene |


## How to install dependencies

Via `uv`

```bash
    uv sync
```
or via `pip`

```bash
    pip install -r requirements.txt
```


## How to render a scene
To render a scene, run the following command in the terminal:

Quality options:
- `-p` : preview (opens the video after rendering)
- `-ql`: low quality (faster rendering)
- `-qm`: medium quality
- `-qh`: high quality (slower rendering)

```bash
manim -<options> main.py <SceneName>
```
