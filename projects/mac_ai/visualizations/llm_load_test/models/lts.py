from __future__ import annotations

from typing import Any, List, Optional

from pydantic import BaseModel, Field
from enum import Enum

import matrix_benchmarking.models as matbench_models
from . import kpi

KPI_SETTINGS_VERSION = "1.2"
# 1.2: add lower_better/higher_better flag
# 1.1: expose the accelerator count
# 1.0: first version

class Settings(matbench_models.ExclusiveModel):
    kpi_settings_version: str

    model_name: str
    virtual_users: int
    test_duration: int
    dataset_name: str
    streaming: bool
    urls: Optional[dict[str, str]]


class LlmLoadTestStats(matbench_models.ExclusiveModel):
    values: List[float]
    min: float
    max: float
    median: float
    mean: float
    percentile_80: float
    percentile_90: float
    percentile_95: float
    percentile_99: float


LTS_SCHEMA_VERSION = "1.0"
class Metadata(matbench_models.Metadata):
    lts_schema_version: str

    settings: Settings
    presets: List[str]

    ci_engine: str = Field(default="Not set")
    run_id: str = Field(default="Not set")
    test_path: str = Field(default="Not set")
    urls: Optional[dict[str, str]]


class Results(matbench_models.ExclusiveModel):
    streaming: bool
    throughput: float
    time_per_output_token: LlmLoadTestStats
    inter_token_latency: Optional[LlmLoadTestStats]
    time_to_first_token: Optional[LlmLoadTestStats]
    model_load_duration: Optional[float]
    failures: int


class KServeLLMPerformanceKPI(matbench_models.KPI, Settings): pass

KServeLLMPerformanceKPIs = matbench_models.getKPIsModel("KServeLLMPerformanceKPIs", __name__, kpi.KPIs, KServeLLMPerformanceKPI)


class Payload(matbench_models.ExclusiveModel):
    metadata: Metadata
    results: Results
    kpis: Optional[KServeLLMPerformanceKPIs]
