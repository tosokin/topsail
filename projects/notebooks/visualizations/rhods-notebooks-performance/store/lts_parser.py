import types
import json
import functools

import pytz

from .. import models
from ..models import lts as models_lts
from . import lts
from matrix_benchmarking.parse import json_dumper

def generate_lts_payload(results, import_settings, must_validate=False):

    lts_metadata = generate_lts_metadata(results, import_settings)
    lts_results = generate_lts_results(results)

    # ---

    lts_payload = types.SimpleNamespace()
    lts_payload.__dict__["$schema"] = f"urn:rhods-notebooks-perf:{models_lts.VERSION}"
    lts_payload.metadata = lts_metadata
    lts_payload.results = lts_results

    lts_payload.kpis = lts.generate_lts_kpis(lts_payload)
    lts_payload.regression_results = results.regression_results

    # ---

    json_lts = json.dumps(lts_payload, indent=4, default=functools.partial(json_dumper, strict=False))
    parsed_lts = json.loads(json_lts)

    return models.lts.Payload.parse_obj(parsed_lts)


def generate_lts_metadata(results, import_settings):
    start_time = results.start_time
    end_time = results.end_time

    if start_time.tzinfo is None:
        start_time = start_time.replace(tzinfo=pytz.UTC)
    if end_time.tzinfo is None:
        end_time = end_time.replace(tzinfo=pytz.UTC)

    lts_metadata = types.SimpleNamespace()
    lts_metadata.start = start_time
    lts_metadata.end = end_time
    lts_metadata.config = results.test_config.yaml_file
    lts_metadata.rhods_version = results.rhods_info.version
    lts_metadata.ocp_version = results.sutest_ocp_version
    lts_metadata.settings = import_settings
    lts_metadata.test = results.test_config.get('tests.notebooks.identifier') or 'unknown'
    lts_metadata.presets = results.test_config.get("ci_presets.names") or ["no_preset_defined"]
    lts_metadata.test_uuid = results.test_uuid
    lts_metadata.run_id = results.from_env.test.run_id
    lts_metadata.test_path = results.from_env.test.test_path
    lts_metadata.urls = results.from_env.test.urls
    lts_metadata.ci_engine = results.from_env.test.ci_engine
    return lts_metadata


def generate_lts_results(results):
    results_lts = types.SimpleNamespace()

    results_lts.benchmark_measures = models.lts.BenchmarkMeasures.parse_obj(results.notebook_benchmark)

    return results_lts


def get_kpi_labels(lts_payload):
    image = lts_payload.metadata.settings["image"]
    image_name, _, image_tag = image.partition(":")

    kpi = dict(
        run_id = lts_payload.metadata.run_id,
        test_path = lts_payload.metadata.test_path,
        ci_engine = lts_payload.metadata.ci_engine,
        urls = lts_payload.metadata.urls,

        rhoai_version = lts_payload.metadata.rhods_version,
        ocp_version = lts_payload.metadata.ocp_version,
        image = image,
        image_tag = image_tag, image_name=image_name,
        benchmark_name = lts_payload.metadata.settings["benchmark_name"],
        instance_type = lts_payload.metadata.settings["instance_type"],
    )

    kpi["@timestamp"] = lts_payload.metadata.start.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    kpi["test_uuid"] = lts_payload.metadata.test_uuid

    return kpi
