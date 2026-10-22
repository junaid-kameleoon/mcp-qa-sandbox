"""Server-side bot: simulates visitors for a Kameleoon feature flag via the Python SDK.

No browser needed. Ground truth: P(conversion) depends on the variation served, so
feature_flag_experiment_results_get can be checked against known numbers.

Credentials come from the environment (never commit them):
  KAMELEOON_CLIENT_ID, KAMELEOON_CLIENT_SECRET

Usage:
  python bots/sdk_bot.py --site a4hk2ju9x6 --flag sandbox_new_checkout --goal 434005 --visitors 200
"""
import argparse
import os
import random
import uuid

from kameleoon import KameleoonClient, KameleoonClientConfig, KameleoonClientFactory

# P(conversion) per variation key - the ground truth
RATES = {"off": 0.10, "on": 0.14}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", required=True)
    ap.add_argument("--flag", required=True)
    ap.add_argument("--goal", type=int, required=True)
    ap.add_argument("--visitors", type=int, default=100)
    ap.add_argument("--environment", default="production")
    a = ap.parse_args()

    cfg = KameleoonClientConfig(
        os.environ["KAMELEOON_CLIENT_ID"],
        os.environ["KAMELEOON_CLIENT_SECRET"],
        environment=a.environment,
    )
    client: KameleoonClient = KameleoonClientFactory.create(a.site, cfg)
    client.wait_init()

    served = {}
    for _ in range(a.visitors):
        visitor = uuid.uuid4().hex[:16]
        variation = client.get_variation(visitor, a.flag)  # also registers the exposure
        key = variation.key
        served[key] = served.get(key, 0) + 1
        if random.random() < RATES.get(key, 0.10):
            client.track_conversion(visitor, a.goal)
    client.flush()
    print("served:", served)


if __name__ == "__main__":
    main()
