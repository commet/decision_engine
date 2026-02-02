#!/usr/bin/env python3
"""
OpenClaw Evaluation Script

실제 Decision Loop Engine을 사용하여 OpenClaw(구 Clawdbot)를
다른 AI 도구들과 비교 평가합니다.
"""

from datetime import datetime
from decision_loop.core.models import DecisionContext, Terminal, Option, CurrentState
from decision_loop.core.engine import DecisionLoopEngine
from decision_loop.verticals.ai_tools import (
    AIToolBackwardEvaluator,
    AIToolForwardChecker,
    SAMPLE_AI_TOOLS,
)

# ============================================================
# OpenClaw Option 정의 (웹 리서치 기반)
# ============================================================

OPENCLAW_OPTION = Option(
    id="openclaw",
    name="OpenClaw (구 Clawdbot)",
    description=(
        "오픈소스 로컬 AI 비서. WhatsApp/Telegram/Slack 연동, "
        "자율적 코드 작성으로 기능 확장 가능. "
        "2025년 11월 출시 후 GitHub 100,000+ 스타 달성. "
        "단, 42,000+ 인스턴스 보안 노출 사건 발생."
    ),
    features={
        # === 핵심 역량 ===
        "capability_breadth": 0.9,      # 이메일, 캘린더, 브라우저 자동화, 메시징
        "capability_depth": 0.85,       # 자기 개선 능력, 장기 메모리
        "code_generation": 0.8,         # 자율적 코드 작성으로 기능 확장
        "reasoning": 0.75,              # LLM 기반 (Claude/GPT 선택 가능)
        "creativity": 0.6,              # 자동화 중심
        "multimodal": 0.5,              # 제한적

        # === 생태계/확장성 ===
        "ecosystem_size": 0.75,         # Molthub 마켓플레이스, 빠르게 성장 중
        "api_availability": True,       # 로컬 API
        "customization": 0.95,          # 오픈소스, 완전한 커스터마이징
        "integration_flexibility": 0.9, # WhatsApp, Telegram, Slack, 브라우저

        # === 학습/접근성 ===
        "learning_curve": 0.35,         # 어려움: self-hosted, 터미널 필수, 보안 설정 복잡
        "documentation_quality": 0.5,   # 빠른 성장으로 문서화 부족
        "community_support": 0.85,      # GitHub 100k+ stars, 활발한 커뮤니티

        # === 비용 ===
        "cost_model": "free",           # 오픈소스 (자체 API 키 사용)
        "monthly_cost_usd": 0,          # 소프트웨어 자체는 무료
        "has_free_tier": True,

        # === 리스크 ===
        "vendor_stability": 0.4,        # 이름 2번 변경 (Clawdbot→Moltbot→OpenClaw), 트레이드마크 이슈
        "data_privacy": 0.3,            # 심각: 42,000+ 인스턴스 노출, 93.4% 인증 우회 취약점
        "lock_in_risk": 0.95,           # 오픈소스라 lock-in 거의 없음

        # === 현재 상태 ===
        "maturity": 0.4,                # 2025년 11월 출시, 아직 초기
        "update_frequency": "daily",     # 매우 활발
        "momentum": 0.98,               # 역대급 성장 속도

        # === OpenClaw 특수 속성 ===
        "requires_self_hosting": True,
        "security_audit_status": "critical_issues",  # 2026년 1월 보안 감사에서 심각한 문제 발견
        "google_cloud_warning": True,   # Google Cloud VP가 배포 금지 권고
    },
    metadata={
        "github_stars": "100,000+",
        "exposed_instances": "42,665",
        "vulnerable_percentage": "93.4%",
        "leaked_secrets": "200+",
        "launch_date": "2025-11",
        "rename_history": ["Clawdbot", "Moltbot", "OpenClaw"],
    }
)

# ============================================================
# 평가 시나리오 정의
# ============================================================

def create_evaluation_scenarios():
    """다양한 사용자 프로필에 대한 평가 시나리오"""

    scenarios = {
        # 시나리오 1: 보안에 민감한 개발자
        "security_conscious_dev": {
            "description": (
                "보안을 중요시하는 개발자. "
                "회사 코드나 민감한 데이터를 다루기 때문에 "
                "데이터 프라이버시가 매우 중요함."
            ),
            "current_state": CurrentState(
                resources={
                    "available_hours_per_week": 8,
                    "monthly_budget_usd": 50,
                    "existing_stack": ["vscode", "git", "slack"],
                },
                constraints={
                    "must_have_api": False,
                    "data_sensitivity": "high",  # 핵심: 높은 데이터 민감도
                    "max_learning_curve": 0.4,
                },
                preferences={
                    "risk_tolerance": 0.3,       # 리스크 회피 성향
                    "preference_for_new": 0.4,
                    "primary_use_case": "coding",
                }
            ),
            "terminals": [
                Terminal(
                    id="T1_ideal",
                    name="Ideal Future",
                    description="완전한 AI 비서 통합, 보안 유지하며 생산성 극대화",
                    weight=0.3,
                    criteria={
                        "min_capability_breadth": 0.7,
                        "min_data_privacy": 0.7,      # 프라이버시 중요
                        "min_vendor_stability": 0.6,
                    }
                ),
                Terminal(
                    id="T2_realistic",
                    name="Realistic Future",
                    description="안정적이고 안전한 도구로 일상 업무 처리",
                    weight=0.5,
                    criteria={
                        "min_data_privacy": 0.6,
                        "min_vendor_stability": 0.7,
                        "min_learning_curve": 0.5,
                        "max_monthly_cost_usd": 50,
                    }
                ),
                Terminal(
                    id="T3_minimum",
                    name="Regret-Minimized",
                    description="최소한 보안 사고는 피함",
                    weight=0.2,
                    criteria={
                        "min_data_privacy": 0.7,      # 가장 중요
                        "min_vendor_stability": 0.6,
                        "has_free_tier": True,
                    }
                ),
            ],
        },

        # 시나리오 2: 실험적인 얼리어답터
        "early_adopter": {
            "description": (
                "새로운 기술을 좋아하는 얼리어답터. "
                "개인 프로젝트 위주, 보안보다 기능이 중요. "
                "시간 투자할 의향 있음."
            ),
            "current_state": CurrentState(
                resources={
                    "available_hours_per_week": 15,  # 시간 여유
                    "monthly_budget_usd": 30,
                    "existing_stack": ["vscode", "docker", "telegram"],
                },
                constraints={
                    "must_have_api": False,
                    "data_sensitivity": "low",        # 개인 프로젝트
                    "max_learning_curve": 0.7,       # 어려워도 괜찮음
                },
                preferences={
                    "risk_tolerance": 0.8,           # 리스크 감수
                    "preference_for_new": 0.9,       # 새로운 것 선호
                    "primary_use_case": "automation",
                }
            ),
            "terminals": [
                Terminal(
                    id="T1_ideal",
                    name="Ideal Future",
                    description="최첨단 AI 자동화, 나만의 AI 비서 구축",
                    weight=0.5,                      # 이상적 미래 중시
                    criteria={
                        "min_capability_breadth": 0.8,
                        "min_customization": 0.8,
                        "min_momentum": 0.8,
                    }
                ),
                Terminal(
                    id="T2_realistic",
                    name="Realistic Future",
                    description="실제로 자동화가 작동하는 상태",
                    weight=0.35,
                    criteria={
                        "min_integration_flexibility": 0.7,
                        "min_capability_depth": 0.7,
                    }
                ),
                Terminal(
                    id="T3_minimum",
                    name="Regret-Minimized",
                    description="시간 낭비만 아니면 됨",
                    weight=0.15,
                    criteria={
                        "min_community_support": 0.5,
                        "has_free_tier": True,
                    }
                ),
            ],
        },

        # 시나리오 3: 일반 사용자 (비개발자)
        "general_user": {
            "description": (
                "기술적 배경이 적은 일반 사용자. "
                "쉬운 사용성이 중요하고, "
                "복잡한 설정은 피하고 싶음."
            ),
            "current_state": CurrentState(
                resources={
                    "available_hours_per_week": 3,   # 시간 제한
                    "monthly_budget_usd": 25,
                    "existing_stack": ["notion", "whatsapp"],
                },
                constraints={
                    "must_have_api": False,
                    "data_sensitivity": "medium",
                    "max_learning_curve": 0.3,       # 어려우면 안됨
                },
                preferences={
                    "risk_tolerance": 0.4,
                    "preference_for_new": 0.5,
                    "primary_use_case": "general",
                }
            ),
            "terminals": [
                Terminal(
                    id="T1_ideal",
                    name="Ideal Future",
                    description="AI가 일상을 편하게 만들어줌",
                    weight=0.25,
                    criteria={
                        "min_capability_breadth": 0.7,
                        "min_learning_curve": 0.7,   # 쉬워야 함
                    }
                ),
                Terminal(
                    id="T2_realistic",
                    name="Realistic Future",
                    description="간단한 작업은 AI로 처리",
                    weight=0.55,
                    criteria={
                        "min_learning_curve": 0.6,
                        "min_documentation_quality": 0.6,
                        "max_monthly_cost_usd": 30,
                    }
                ),
                Terminal(
                    id="T3_minimum",
                    name="Regret-Minimized",
                    description="최소한 쓸 수는 있어야 함",
                    weight=0.2,
                    criteria={
                        "min_learning_curve": 0.5,
                        "min_vendor_stability": 0.6,
                        "has_free_tier": True,
                    }
                ),
            ],
        },
    }

    return scenarios


def run_evaluation(scenario_name: str, scenario: dict, options: list[Option]):
    """단일 시나리오 평가 실행"""

    print(f"\n{'='*70}")
    print(f"시나리오: {scenario_name}")
    print(f"{'='*70}")
    print(f"설명: {scenario['description']}")

    context = DecisionContext(
        description=scenario["description"],
        tags=["openclaw-evaluation", scenario_name],
    )

    engine = DecisionLoopEngine(
        backward_evaluator=AIToolBackwardEvaluator(),
        forward_checker=AIToolForwardChecker()
    )

    result = engine.run(
        context,
        options,
        scenario["terminals"],
        scenario["current_state"]
    )

    # 결과 출력
    print(f"\n[Terminals]")
    for t in scenario["terminals"]:
        print(f"  {t.name}: weight={t.weight}")

    print(f"\n[Current State]")
    print(f"  data_sensitivity: {scenario['current_state'].constraints.get('data_sensitivity')}")
    print(f"  risk_tolerance: {scenario['current_state'].preferences.get('risk_tolerance')}")
    print(f"  max_learning_curve: {scenario['current_state'].constraints.get('max_learning_curve')}")

    print(f"\n[Rankings]")
    print(f"{'Rank':<6} {'Option':<25} {'Backward':<10} {'Forward':<10} {'Total':<10} {'Status'}")
    print("-" * 80)

    for rank, option_id in enumerate(result.ranked_options, 1):
        eval_result = result.get_evaluation(option_id)
        if eval_result:
            status = ""
            if eval_result.eliminated:
                status = f"ELIMINATED: {eval_result.elimination_reason}"
            elif option_id == "openclaw":
                status = "← OpenClaw"

            print(
                f"{rank:<6} {eval_result.option_name:<25} "
                f"{eval_result.weighted_backward_score:<10.3f} "
                f"{eval_result.forward_score:<10.3f} "
                f"{eval_result.total_score:<10.3f} "
                f"{status}"
            )

    # OpenClaw 상세 분석
    openclaw_eval = result.get_evaluation("openclaw")
    if openclaw_eval:
        print(f"\n[OpenClaw 상세 분석]")

        if openclaw_eval.eliminated:
            print(f"  ⚠️  ELIMINATED: {openclaw_eval.elimination_reason}")
        else:
            print(f"  Backward Score: {openclaw_eval.weighted_backward_score:.3f}")
            for tid, score in openclaw_eval.backward_scores.items():
                print(f"    {tid}: {score:.3f}")

            print(f"  Forward Score: {openclaw_eval.forward_score:.3f}")
            for factor, score in openclaw_eval.forward_details.items():
                print(f"    {factor}: {score:.3f}")

            print(f"  Total Score: {openclaw_eval.total_score:.3f}")

    return result


def main():
    """메인 실행"""

    print("=" * 70)
    print("OpenClaw (구 Clawdbot) 평가 - Decision Loop Engine")
    print("=" * 70)
    print(f"평가 시점: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    # 기존 옵션에 OpenClaw 추가
    options = SAMPLE_AI_TOOLS + [OPENCLAW_OPTION]

    print(f"\n평가 대상 도구 ({len(options)}개):")
    for opt in options:
        print(f"  - {opt.name}")

    # 시나리오별 평가 실행
    scenarios = create_evaluation_scenarios()
    results = {}

    for scenario_name, scenario in scenarios.items():
        results[scenario_name] = run_evaluation(scenario_name, scenario, options)

    # 종합 분석
    print("\n" + "=" * 70)
    print("종합 분석: OpenClaw는 언제 적합한가?")
    print("=" * 70)

    for scenario_name, result in results.items():
        openclaw_eval = result.get_evaluation("openclaw")
        openclaw_rank = result.ranked_options.index("openclaw") + 1

        print(f"\n{scenario_name}:")
        if openclaw_eval.eliminated:
            print(f"  ❌ 제거됨 - {openclaw_eval.elimination_reason}")
        else:
            print(f"  순위: {openclaw_rank}/{len(result.ranked_options)}")
            print(f"  점수: {openclaw_eval.total_score:.3f}")

            if openclaw_rank <= 3:
                print(f"  ✅ 추천 가능")
            elif openclaw_rank <= 5:
                print(f"  ⚠️ 조건부 고려")
            else:
                print(f"  ❌ 비추천")

    print("\n" + "=" * 70)
    print("결론")
    print("=" * 70)
    print("""
OpenClaw는:

✅ 적합한 경우:
   - 개인 프로젝트, 실험 목적
   - 보안보다 기능/자동화가 우선인 경우
   - 기술적 역량이 충분하고 self-hosting 가능
   - 리스크 감수 성향이 높은 얼리어답터

❌ 부적합한 경우:
   - 회사/업무용 (민감한 데이터)
   - 보안이 중요한 환경
   - 기술적 배경이 부족한 사용자
   - 안정성을 중시하는 경우

⚠️ 주의사항:
   - 42,000+ 인스턴스 보안 노출 사건
   - 93.4% 인증 우회 취약점
   - Google Cloud VP 배포 금지 권고
   - 200+ 기업 비밀 유출 사례
   - vendor_stability 낮음 (이름 2번 변경)
""")


if __name__ == "__main__":
    main()
