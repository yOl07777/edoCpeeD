import asyncio

from deepseek_code.client.load_balancer import DeepSeekLoadBalancer
from deepseek_code.config import DeepSeekConfig


def test_round_robin_and_cooldown_skip_failed_target():
    async def run() -> None:
        config = DeepSeekConfig(
            api_keys=["bad", "good"],
            models=["deepseek-chat"],
            endpoints=["https://api.deepseek.com/v1"],
            cooldown_seconds=60,
        )
        lb = DeepSeekLoadBalancer(config)

        first = await lb.next_target()
        lb.mark_failure(first, 401)
        second = await lb.next_target()

        assert second.api_key != first.api_key

    asyncio.run(run())
