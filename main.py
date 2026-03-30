#!/usr/bin/env python3
"""
Usage:  python main.py [manim-flags] <SceneName>
Example: python main.py -pqk TraceRType
         python main.py -pqh LRUScene
"""
import subprocess
import sys

SCENE_MAP = {
    # single_cycle — component tests
    "TestALUScene":          "single_cycle/scenes/component_tests.py",
    "TestMuxScene":          "single_cycle/scenes/component_tests.py",
    "TestRegFileScene":      "single_cycle/scenes/component_tests.py",
    "TestIMScene":           "single_cycle/scenes/component_tests.py",
    "TestSignExtendScene":   "single_cycle/scenes/component_tests.py",
    # single_cycle — integration
    "IfALUMuxScene":         "single_cycle/scenes/integration_scenes.py",
    # single_cycle — instruction traces
    "TraceRType":            "single_cycle/scenes/instruction_traces.py",
    "TraceLW":               "single_cycle/scenes/instruction_traces.py",
    "TraceSW":               "single_cycle/scenes/instruction_traces.py",
    "TraceBeq":              "single_cycle/scenes/instruction_traces.py",
    "DebugTrace":            "single_cycle/scenes/instruction_traces.py",
    # single_cycle — performance
    "PerformanceScene":      "single_cycle/performance.py",
    # pipeline
    "PipelinedDatapathScene":   "pipeline/pipeline_datapath.py",
    "PipelinePerformanceScene": "pipeline/pipeline_performance.py",
    # cache addressing
    "CacheParamsScene":      "addressing/cache_params.py",
    "CacheTracingScene":     "addressing/cache_tracing.py",
    # cache associativity
    "LRUScene":              "associativity/lru_scene.py",
    "TwoWayTracingScene":    "associativity/assoc_tracing.py",
    "FourWayTracingScene":   "associativity/assoc_tracing.py",
    "ComparisonScene":       "associativity/comparison_scene.py",
}

def main():
    args = sys.argv[1:]
    scene_name = next((a for a in args if not a.startswith("-")), None)

    if scene_name is None:
        print("Available scenes:")
        for name, path in SCENE_MAP.items():
            print(f"  {name:30s}  {path}")
        sys.exit(0)

    if scene_name not in SCENE_MAP:
        print(f"Unknown scene: {scene_name}")
        print("Run without arguments to list all scenes.")
        sys.exit(1)

    file_path = SCENE_MAP[scene_name]
    flags = [a for a in args if a.startswith("-")]
    cmd = [sys.executable, "-m", "manim"] + flags + [file_path, scene_name]
    sys.exit(subprocess.run(cmd).returncode)

if __name__ == "__main__":
    main()
