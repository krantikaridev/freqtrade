# Lessons from Nanoclaw

This document captures the key strategic, operational, and workflow learnings from the Nanoclaw project(https://github.com/krantikaridev/nanoclaw) so we do not repeat the same mistakes in the freqtrade system.

## 1. Strategic Learnings

- **Nanoclaw was primarily a learning/experimental project**, not a serious income-generating system.
- High-frequency on-chain rotation on small capital is inefficient due to gas, slippage, and thin edges.
- It is very difficult to scale a micro-trading bot into serious money without a significantly stronger edge or much larger capital.
- We should have reached this conclusion earlier instead of continuing to tweak and optimize for too long.

## 2. Workflow & Process Learnings

- Spending too much time on workflow optimization (Grok + Cursor/Copilot) can become a distraction if the core project direction is not strong.
- Long back-and-forth iterations with AI on the same files (README, instructions, roadmap) leads to fragmented commits and slow progress.
- It is more efficient to do planning and documentation in fewer, larger commits rather than many small revisions.
- Clear scoping of tasks/Epics dramatically improves output quality and reduces wasted effort.

## 3. Risk & Trading Philosophy

- **Quality over quantity** is especially important with small capital.
- High rotation and frequent small trades often destroy edge through costs and noise.
- Strong, explicit risk controls (play budget, adverse churn guard, drawdown throttle, operating reserve) are necessary from the beginning.
- We should design systems that make it *easy* to take fewer, higher-quality trades rather than making it easy to over-trade.

## 4. Decision Making

- It is important to regularly ask: “Is this project still aligned with the real goal (serious income)?”
- We should be willing to pivot or deprioritize earlier when data shows limited scalability.
- Capturing strategic context and hard decisions (not just code) helps future decision-making.

## 5. Application to freqtrade

- The new system should be designed with **quality-first** principles from day one.
- Risk management and trade filtering should be first-class citizens.
- We should avoid falling into the trap of constant small optimizations without clear progress toward the real goal.
- Workflow (Grok + Copilot) should support fast, focused implementation rather than long iterative refinement loops.

---

**Note**: This document should be updated whenever we learn something important during the development of the freqtrade system.
