# A Bidirectional Decision Loop for Tool Selection and Beyond

**Forward Sanity Check × Backward Induction × Multiple Terminals × Continuous Improvement**

---

## 1. 왜 이걸 만들었는가: 문제 정의부터

요즘 우리는 선택지가 과잉인 환경에 살고 있다.
특히 AI 도구 영역에서는 매주 새로운 툴이 쏟아지고, 대부분은 "이게 내 문제에 맞는지"를 판단하기 전에 써보는 데 비용이 든다.

이 비용은 단순한 시간 낭비가 아니다.
- 어떤 툴을 고르느냐에 따라
- 사고 방식이 바뀌고
- 워크플로우가 고정되며
- 이후 선택의 자유도(path dependency)가 줄어든다

그런데 우리는 종종 두 가지 함정에 빠진다:

**Forward-only 사고**
- 지금 할 수 있는 것만 보고 결정
- 장기적으로 의미 없는 선택이 되기 쉬움

**Backward-only 사고**
- 이상적인 미래에서 현재를 역산
- 현실 friction(시간, 비용, 에너지)을 과소평가함

나는 이 지점에서 반복적으로 같은 문제를 겪었다.

> 구조적으로는 완벽한데,
> 현실 friction이 뒤늦게 튀어나와 전체 설계를 흔든다.

그래서 목표는 명확했다.

> 의사결정 초기에 '현실 검증'을 강제로 끌어오고,
> **단일 목표가 아닌 여러 관점**을 동시에 고려하며,
> 한 번의 선택으로 끝나지 않고 계속 개선되는 결정 루프를 만들자.

---

## 2. 핵심 아이디어 요약 (TL;DR)

이 프레임은 하나의 알고리즘이라기보다 **사고 구조(template)**다.

핵심은 네 가지다:

### 2.1 Multiple Terminals (단일 목표가 아님)

이 엔진은 **단일 목표(goal)**를 전제하지 않는다.

대신, **서로 다른 성격의 종단 상태(Terminals)**를 여러 개 정의한다:

| Terminal | 이름 | 의미 | 가중치 예시 |
|----------|------|------|-------------|
| T1 | Ideal / Aspirational | 가장 잘 풀렸을 경우의 미래 | 0.3 |
| T2 | Realistic / Median | 가장 도달 확률이 높은 평균적 미래 | 0.5 |
| T3 | Minimum / Regret-Minimized | 최악은 피했지만 완벽하지는 않은 미래 | 0.2 |

**핵심**: 이 세 Terminal은 "좋음–나쁨" 스펙트럼이 **아니라**, 서로 다른 판단 기준을 가진 상태다.

- Ideal은 "야망"의 관점
- Realistic은 "확률"의 관점
- Minimum은 "후회 회피"의 관점

각각의 가중치를 조절함으로써, 의사결정자의 성향과 상황을 반영할 수 있다.

### 2.2 Backward Induction

각 Terminal에 대해 질문한다:

> "이 Terminal에 도달하려면, Option은 어떤 조건을 반드시 만족해야 하는가?"

이 조건들을 **criteria**로 구조화한다:
- `min_capability_breadth: 0.8` → 최소 0.8 이상의 범용성
- `max_monthly_cost_usd: 50` → 월 비용 $50 이하
- `has_free_tier: true` → 무료 티어 필수

Option의 features와 대조하여 적합도 점수를 산출하고, Terminal별 가중치로 합산한다.

### 2.3 Forward Sanity Check

현실 보정 장치다. 질문:

> "지금 이 Option을 현재의 나(시간, 에너지, 자원, 불확실성)가 실제로 실행할 수 있는가?"

두 단계로 작동한다:

**Hard Elimination (즉시 제거)**
- API 필수인데 없으면 → 제거
- 데이터 민감도 high인데 프라이버시 낮으면 → 제거
- 예산의 2배 초과하면서 무료 티어도 없으면 → 제거

**Soft Scoring (점수 감점)**
- 시간 feasibility: 학습 시간 vs 가용 시간
- 예산 feasibility: 비용 vs 예산
- 학습 feasibility: 난이도 vs 허용 한계
- 제약조건 compliance: 기존 스택 호환성, 리스크 tolerance

### 2.4 점수 계산: 곱셈의 의미

```
total_score = weighted_backward_score × forward_score
```

왜 곱셈인가?
- 미래 정합성이 높아도 실행 불가능하면 → 0에 수렴
- 실행 가능해도 미래에 의미 없으면 → 낮은 점수
- **둘 다 높아야** 높은 점수

이 단순한 공식이 "구조적 완벽함"과 "현실적 가능성"의 균형을 강제한다.

### 2.5 Loop 구조

```
결정 → 실행 → 피드백 → Terminal 수정 → 가중치 수정 → Option 재정의 → (반복)
```

이 엔진의 목적은 결정을 '끝내는 것'이 아니다.
**후회(regret)를 줄이기 위한 반복적 판단 구조**다.

---

## 3. 이론적 배경: 왜 단순한 Bidirectional Search는 아닌가

컴퓨터 과학을 아는 사람이라면 자연스럽게 이런 생각이 든다.

> "이거 그냥 bidirectional search 아닌가?"

부분적으로는 맞고, 결정적으로는 다르다.

### 3.1 Bidirectional Search의 전제

전통적인 bidirectional search는 다음 조건에서 강력하다:
- 시작점(start)과 **단일 목표점(goal)**이 명확
- 탐색 공간이 크고, 최단 경로가 중요
- forward와 backward 탐색이 **교차(intersect)**하면 종료

### 3.2 우리가 다루는 문제의 본질적 차이

의사결정 문제는 다르다:

| Bidirectional Search | Decision Loop |
|---------------------|---------------|
| 단일 목표 | **복수의 Terminal** (서로 다른 관점) |
| 목표 고정 | 목표가 실행 후 바뀔 수 있음 |
| 교차하면 종료 | **종료 조건 없음** (계속 개선) |
| 비용 함수 고정 | 비용 함수 동적 (학습, 전환, 심리적 마찰) |

그래서 이 프레임은 **탐색(search)**이 아니라 **조정(adaptation)**에 가깝다.

- 교차하면 끝나는 구조 ❌
- 반복하면서 정교해지는 구조 ⭕

---

## 4. 구조 개요: Decision Loop의 전체 흐름

```
┌─────────────────────────────────────────────────────────────┐
│                     DecisionContext                         │
│                   (문제 상황 설명)                            │
└─────────────────────┬───────────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    Terminal Space                           │
│              T1 (Ideal)  T2 (Realistic)  T3 (Minimum)       │
│              weight=0.3   weight=0.5     weight=0.2         │
│              criteria     criteria       criteria           │
└─────────────────────┬───────────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                  Backward Induction                         │
│         Terminal criteria × Option features → 적합도 점수   │
│         가중 합산 → weighted_backward_score                 │
└─────────────────────┬───────────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   Candidate Options                         │
│            [Option A, Option B, Option C, ...]              │
│            각 Option은 features dict를 가짐                  │
└─────────────────────┬───────────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                 Forward Sanity Check                        │
│         Hard constraints 위반 → 즉시 제거 (eliminated)       │
│         Soft evaluation → forward_score (0~1)               │
└─────────────────────┬───────────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                Scored & Ranked Options                      │
│         total = weighted_backward × forward                 │
│         eliminated 옵션은 최하위                             │
└─────────────────────┬───────────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              Decision (Provisional) + Insights              │
│         "상위 옵션들이 비슷합니다" / "명확한 선두가 있습니다"   │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      └──────────── Loop Back ────────────────┘
                      - Terminal 가중치 조정
                      - criteria 수정
                      - Option 추가/제거
                      - current_state 업데이트
```

---

## 5. Forward Sanity Check가 왜 핵심인가

### 5.1 우리가 흔히 빠지는 함정

구조를 잘 짜는 사람일수록 이런 경향이 있다:
- "이론적으로는 가능하다"
- "나중에 자동화하면 된다"
- "일단 만들고 보자"

이건 창의성의 원천이기도 하지만, 실행 단계에서 폭탄으로 돌아온다.

### 5.2 Forward Sanity Check의 이중 구조

이 엔진의 Forward Check는 **두 단계**로 작동한다:

**1단계: Hard Elimination (should_eliminate)**
```python
# API 필수인데 없으면 즉시 제거
if constraints["must_have_api"] and not features["api_availability"]:
    return eliminated=True, reason="API required but not available"
```

어떤 옵션은 점수를 매길 필요도 없이 **현실적으로 불가능**하다.
이걸 초반에 걸러낸다.

**2단계: Soft Scoring (evaluate)**
```python
# 각 factor별 점수 계산 후 가중 합산
details = {
    "time_feasibility": 0.95,      # 학습 시간 vs 가용 시간
    "budget_feasibility": 1.00,    # 비용 vs 예산
    "learning_feasibility": 0.90,  # 난이도 vs 허용 한계
    "constraint_compliance": 0.80, # 기존 스택 호환성
}
forward_score = weighted_sum(details)  # 예: 0.91
```

### 5.3 질문의 전환

Forward Sanity Check는 질문을 바꾼다:
- ❌ "이게 맞는 구조인가?"
- ⭕ "내가 지금 이걸 실행할 수 있는가?"

이걸 **의사결정 초기에 강제로 포함**시키는 게 목적이다.

---

## 6. 실제 사례: OpenClaw(구 Clawdbot) 평가

이 섹션은 Decision Loop Engine의 실제 작동 사례다.

### 6.1 배경: OpenClaw 열풍과 논란

[OpenClaw](https://github.com/clawdbot/clawdbot)(구 Clawdbot)는 2025년 11월 출시 후 GitHub 100,000+ 스타를 달성한 오픈소스 AI 비서다. WhatsApp, Telegram, Slack 연동, 자율적 코드 작성으로 기능 확장이 가능해 역대급 성장 속도를 기록했다.

하지만 동시에 심각한 보안 우려가 제기되었다:

- **42,000+ 인스턴스가 인터넷에 노출**, 93.4%가 인증 우회 취약점
- **200+ 기업 비밀 유출** (헬스케어 문서, Kubernetes 자격 증명 등)
- **Google Cloud VP가 배포 금지 권고**
- Anthropic 트레이드마크 이슈로 이름 2번 변경 (Clawdbot → Moltbot → OpenClaw)

**질문**: "OpenClaw를 써도 될까?"

이 질문에 대해 Decision Loop Engine을 실제로 돌려봤다.

### 6.2 OpenClaw Option 정의

웹 리서치를 기반으로 OpenClaw의 features를 정량화했다:

```python
OPENCLAW_OPTION = Option(
    id="openclaw",
    name="OpenClaw (구 Clawdbot)",
    features={
        # 강점
        "capability_breadth": 0.9,       # 이메일, 캘린더, 브라우저, 메시징 자동화
        "customization": 0.95,           # 오픈소스, 완전한 커스터마이징
        "integration_flexibility": 0.9,  # WhatsApp, Telegram, Slack
        "momentum": 0.98,                # 역대급 성장 속도
        "lock_in_risk": 0.95,            # 오픈소스라 lock-in 거의 없음
        "monthly_cost_usd": 0,           # 무료

        # 약점
        "learning_curve": 0.35,          # 어려움: self-hosted, 터미널 필수
        "data_privacy": 0.3,             # 심각: 42,000+ 인스턴스 노출
        "vendor_stability": 0.4,         # 이름 2번 변경, 트레이드마크 이슈
        "maturity": 0.4,                 # 2025년 11월 출시, 아직 초기
        "documentation_quality": 0.5,    # 빠른 성장으로 문서화 부족
    }
)
```

### 6.3 세 가지 사용자 시나리오 평가

#### 시나리오 1: 보안 중시 개발자 (회사 코드 다룸)

```yaml
data_sensitivity: high
risk_tolerance: 0.3
terminals:
  - Ideal: min_data_privacy: 0.7
  - Realistic: min_data_privacy: 0.6
  - Minimum: min_data_privacy: 0.7
```

**결과**:
```
Rank   Option                    Total
1      Claude (Anthropic)        0.975
2      Cline                     0.844
...
9      OpenClaw                  ELIMINATED ❌
       → "Data privacy insufficient for high sensitivity"
```

**분석**: Forward Sanity Check의 Hard Elimination이 작동. `data_privacy: 0.3`이 `data_sensitivity: high` 조건을 충족하지 못해 **즉시 제거**됨.

---

#### 시나리오 2: 얼리어답터 (개인 프로젝트, 실험 목적)

```yaml
data_sensitivity: low
risk_tolerance: 0.8
max_learning_curve: 0.7  # 어려워도 괜찮음
terminals:
  - Ideal (0.5): min_customization: 0.8, min_momentum: 0.8
  - Realistic (0.35): min_integration_flexibility: 0.7
  - Minimum (0.15): min_community_support: 0.5
```

**결과**:
```
Rank   Option                    Backward   Forward    Total
1      ChatGPT (OpenAI)          1.000      0.985      0.985
2      Claude (Anthropic)        0.979      0.975      0.955
3      OpenClaw                  1.000      0.952      0.952  ✅
4      Gemini (Google)           0.958      0.990      0.949
```

**분석**: OpenClaw가 **3위로 추천 가능**.

- Backward Score: 1.000 (모든 Terminal 완벽 충족)
  - 높은 customization, momentum, integration이 얼리어답터 Terminal과 정확히 매칭
- Forward Score: 0.952 (실행 가능)
  - 충분한 학습 시간(15시간/주)이 어려운 learning_curve를 상쇄
  - 낮은 data_sensitivity가 보안 문제를 덜 심각하게 만듦

---

#### 시나리오 3: 일반 사용자 (비개발자)

```yaml
data_sensitivity: medium
max_learning_curve: 0.3  # 쉬워야 함
available_hours_per_week: 3
terminals:
  - Ideal: min_learning_curve: 0.7
  - Realistic (0.55): min_learning_curve: 0.6
  - Minimum: min_learning_curve: 0.5
```

**결과**:
```
Rank   Option                    Backward   Forward    Total
1      ChatGPT (OpenAI)          1.000      0.942      0.942
2      Perplexity                0.982      0.940      0.923
...
9      OpenClaw                  0.788      0.621      0.489  ❌
```

**분석**: OpenClaw가 **최하위**.

- Backward Score: 0.788 (부분 충족)
  - `learning_curve: 0.35`가 모든 Terminal의 min_learning_curve 조건 미충족
- Forward Score: 0.621 (실행 어려움)
  - time_feasibility: 0.353 (주 3시간으로는 학습 불가)
  - learning_feasibility: 0.300 (난이도가 허용치 초과)

### 6.4 결과 요약

| 시나리오 | OpenClaw 순위 | 점수 | 판정 |
|---------|--------------|------|------|
| 보안 중시 개발자 | - | 0.000 | ❌ **제거됨** (보안 부적격) |
| 얼리어답터 | 3/9 | 0.952 | ✅ **추천 가능** |
| 일반 사용자 | 9/9 | 0.489 | ❌ **비추천** |

### 6.5 이 사례가 보여주는 것

Decision Loop Engine은 "OpenClaw가 좋다/나쁘다"를 말하지 않는다.

대신:
1. **당신의 상황**(Terminal, CurrentState)을 구조화하고
2. **투명한 점수 계산**으로 왜 이 결과인지 보여주고
3. **다른 설정**으로 다시 돌려볼 수 있게 한다

**만약 당신이 얼리어답터라면**: OpenClaw 3위, 고려해볼 만함
**만약 보안이 중요하다면**: 점수도 안 매기고 제거, 다른 옵션 보세요

이게 이 엔진의 설계 의도다.

---

## 7. 이 프레임의 치명적 한계

의도적으로 짚고 가야 한다.

### 7.1 Local Optimum에 갇힐 위험

Forward Sanity Check를 너무 강하게 적용하면:
- 장기적으로 좋은 선택을 배제할 수 있다
- "지금 편한 것"에 과적합될 수 있음

### 7.2 기준 설계자의 편향

어떤 friction을 중요하게 보느냐는 설계자의 성향에 강하게 의존한다.
- 잘못 설계된 criteria는 잘못된 결정을 **정교하게 자동화**한다

### 7.3 과도한 메타 사고

모든 결정을 루프로 만들면:
- 결정 자체가 늦어진다
- "결정 회피를 합리화"할 위험

→ 그래서 이 프레임은 **중요하지만 반복적인 결정**에만 쓰는 게 적절하다.

### 7.4 엔진이 보장하지 않는 것

이 엔진은 다음을 **의도적으로 하지 않는다**:

| 하지 않는 것 | 이유 |
|-------------|------|
| 자동 의사결정 | "이것을 선택하세요"라고 말하지 않음. 랭킹과 점수를 제공할 뿐 |
| "최적 선택" 단정 | 결과는 "현재 설정 기준 점수"일 뿐. 설정 바뀌면 결과도 바뀜 |
| Terminal 타당성 검증 | Terminal이 잘못 정의되면 결과도 정교하게 잘못됨. 사용자 책임 |
| 정량화 불가능한 friction | 심리적 저항, 정체성, 감정은 완전히 포착 불가 |
| Loop 무한 반복 방지 | 실행 없는 반복은 시스템이 막지 못함. 사용자의 행동적 결정 |

→ 이건 **판단 도구**이지 **판단 대체제**가 아니다.

---

## 8. 구현 관점: 왜 코드로 만들었는가

이걸 글이나 체크리스트로만 두지 않고 코드로 구현한 이유는 명확하다:

- **사고를 외주화**하기 위해
- 놓치기 쉬운 질문을 **자동으로 던지게** 하기 위해
- 결정 과정을 **기록하고 재사용**하기 위해

### 8.1 추상화 설계

```
Core (도메인 독립적)
├── BackwardEvaluator (추상 인터페이스)
├── ForwardSanityChecker (추상 인터페이스)
└── DecisionLoopEngine (오케스트레이터)

Verticals (도메인별 구현)
└── ai_tools/
    ├── AIToolBackwardEvaluator
    ├── AIToolForwardChecker
    ├── SAMPLE_AI_TOOLS (8개 도구)
    └── AI_TOOL_TERMINALS (3개 Terminal)
```

**핵심**: Core는 도메인을 모른다. Evaluator만 갈아끼우면 다른 의사결정 문제에 적용 가능하다.

### 8.2 투명성

모든 점수와 계산 과정이 기록된다:

```python
EvaluationResult(
    backward_scores={"T1": 0.98, "T2": 1.00, "T3": 1.00},
    backward_details={"T1": {"min_breadth": 1.0, "min_eco": 0.9, ...}},
    forward_score=0.98,
    forward_details={"time": 1.0, "budget": 1.0, ...},
    total_score=0.97,
)
```

왜 이 점수가 나왔는지 **역추적 가능**하다.

---

## 9. 향후 확장: 프라이버시를 존중하는 자동 진단

현재는 사용자가 직접 `current_state`를 입력해야 한다. 하지만 더 나은 경험을 위해 **자동 진단** 기능을 고려할 수 있다.

문제는: OpenClaw 사례에서 봤듯이 **사용자 데이터 수집은 프라이버시 위험**을 수반한다.

### 9.1 핵심 원칙: 데이터는 떠나지 않는다

```
❌ 피해야 할 것:
   - 사용 패턴을 서버로 전송
   - 행동 데이터 수집 및 분석
   - 프로필 생성 후 클라우드 저장

✅ 추구해야 할 것:
   - 모든 분석은 로컬에서
   - 사용자가 명시적으로 입력한 것만 사용
   - 익명화된 질문 기반 프로파일링
```

### 9.2 제안: Self-Assessment Wizard

사용자 데이터를 수집하는 대신, **구조화된 질문**을 통해 사용자가 스스로 프로필을 구성하게 한다:

```
┌─────────────────────────────────────────────────────────────┐
│              Self-Assessment: 5분 진단                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Q1. 새로운 도구를 배우는 데 주당 몇 시간 투자할 수 있나요?    │
│      ○ 3시간 미만  ○ 3-8시간  ○ 8시간 이상                  │
│                                                             │
│  Q2. 이 도구로 다룰 데이터의 민감도는?                        │
│      ○ 개인 프로젝트 (낮음)                                  │
│      ○ 일반 업무 (중간)                                      │
│      ○ 회사 기밀/고객 데이터 (높음)                          │
│                                                             │
│  Q3. 새로운 기술에 대한 태도는?                               │
│      ○ 안정성이 중요, 검증된 것 선호                          │
│      ○ 균형 추구                                             │
│      ○ 최신 트렌드를 따라가고 싶음                           │
│                                                             │
│  Q4. 도구가 갑자기 사라지거나 크게 바뀌면?                    │
│      ○ 큰 문제 (업무 의존도 높음)                            │
│      ○ 불편하지만 대체 가능                                  │
│      ○ 상관없음 (실험적 사용)                                │
│                                                             │
│  Q5. 월 예산은?                                              │
│      ○ 무료만  ○ $20 이하  ○ $50 이하  ○ 제한 없음          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                              ↓
              자동으로 current_state 생성
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  당신의 프로필 (로컬에서만 저장)                              │
│                                                             │
│  - data_sensitivity: medium                                 │
│  - risk_tolerance: 0.6                                      │
│  - available_hours_per_week: 5                              │
│  - monthly_budget_usd: 20                                   │
│                                                             │
│  [수정하기]  [이 프로필로 평가 실행]                          │
└─────────────────────────────────────────────────────────────┘
```

**장점**:
- 사용자가 자신의 데이터를 **직접** 입력
- 어떤 정보가 사용되는지 **완전히 투명**
- 서버 전송 없음, **로컬에서만** 처리
- 질문 자체가 **사고 프레임** 역할

### 9.3 제안: 사용 패턴 기반 로컬 러닝 (opt-in)

사용자가 **명시적으로 동의**한 경우에만:

```python
# 로컬에서만 실행되는 패턴 분석
class LocalUsageAnalyzer:
    """
    사용자의 CLI 사용 패턴을 로컬에서만 분석.
    어떤 데이터도 외부로 전송하지 않음.
    """

    def analyze_decision_history(self, history: list[DecisionLoopResult]):
        """
        과거 결정들을 분석하여 패턴 추출:
        - 어떤 Terminal 가중치를 자주 조정하는가?
        - 어떤 옵션을 자주 선택하는가?
        - 어떤 criteria가 반복적으로 중요한가?
        """

    def suggest_terminal_weights(self) -> dict[str, float]:
        """
        과거 패턴 기반 Terminal 가중치 제안.
        "지난 5번의 결정에서 Regret-Minimized 가중치를
         평균 0.35로 설정하셨습니다. 기본값으로 사용할까요?"
        """

    def suggest_current_state(self) -> CurrentState:
        """
        과거 입력 기반 current_state 템플릿 제안.
        "이전에 입력하신 값을 기반으로 합니다. 변경하시겠습니까?"
        """
```

**핵심**:
- **Opt-in**: 사용자가 명시적으로 켜야 함
- **로컬 전용**: 분석 결과가 기기를 떠나지 않음
- **투명성**: 어떤 데이터를 보는지 사용자가 확인 가능
- **삭제 가능**: 언제든 히스토리 삭제 가능

### 9.4 제안: 도구별 사용 가이드 생성

평가 결과를 기반으로 **맞춤형 사용 가이드** 제공:

```
┌─────────────────────────────────────────────────────────────┐
│  OpenClaw 사용 가이드 (당신의 프로필 기반)                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ⚠️ 주의사항 (당신의 data_sensitivity: medium 기준)          │
│  - 회사 자격 증명은 절대 저장하지 마세요                      │
│  - 인증을 반드시 활성화하세요 (기본값이 아님!)                │
│  - 네트워크 노출 여부를 확인하세요                           │
│                                                             │
│  ✅ 추천 사용법 (당신의 available_hours: 5시간 기준)          │
│  - 1주차: 기본 설정만, WhatsApp 연동                         │
│  - 2주차: 간단한 자동화 1개 추가                             │
│  - 무리하게 모든 기능 사용하지 말 것                         │
│                                                             │
│  🎯 당신에게 적합한 기능 (risk_tolerance: 0.6 기준)           │
│  - 캘린더 알림 (안전)                                        │
│  - 이메일 요약 (중간 위험, 민감 정보 주의)                    │
│  - 브라우저 자동화 (높은 위험, 권장하지 않음)                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 9.5 OpenClaw와의 차이: 왜 우리는 다른가

| OpenClaw 이슈 | Decision Loop Engine 접근 |
|--------------|-------------------------|
| 기본 인증 비활성화 | 데이터 수집 자체를 안 함 |
| 42,000+ 인스턴스 노출 | 서버가 없음, 로컬 전용 |
| 자격 증명 평문 저장 | 민감 정보를 저장하지 않음 |
| 사용자 데이터 중앙 집중 | 사용자 기기에서만 처리 |

**핵심 차이**:
OpenClaw는 "강력한 기능"을 위해 데이터를 요구한다.
우리는 "구조화된 질문"으로 같은 목적을 달성한다.

```
OpenClaw: "당신의 이메일을 읽게 해주세요" → 프라이버시 위험
우리:     "당신의 이메일이 얼마나 민감한가요?" → 질문만으로 충분
```

---

## 10. 앞으로의 확장 방향

### 10.1 도메인 확장

- **AI 툴 선택** → 프로젝트 구조 선택, 학습 전략, 커리어 결정까지 확장 가능
- Core는 그대로, Evaluator만 새로 구현

### 10.2 팀/조직 의사결정

- 개인용 → 팀용 → 조직 의사결정 템플릿
- 여러 stakeholder의 Terminal을 어떻게 조율할 것인가?

### 10.3 피드백 학습

- 과거 결정의 결과를 기반으로 Terminal 가중치 자동 조정
- "이 Terminal이 과대평가되었습니다" 같은 피드백

### 10.4 커뮤니티 벤치마크 (익명화)

- 옵션별 features를 커뮤니티가 함께 관리
- 새 도구가 나오면 빠르게 평가 가능
- 개인 데이터 없이, 도구 메타데이터만 공유

---

## 11. 마무리

이 프로젝트의 핵심 메시지는 단순하다.

> 좋은 의사결정은
> 한 번의 정답이 아니라
> **잘 설계된 반복 구조**에서 나온다.

그리고 이 프레임은:

1. **Multiple Terminals**로 단일 목표의 함정을 피하고
2. **Backward Induction**으로 미래 정합성을 구조화하고
3. **Forward Sanity Check**로 현실을 초기에 반영하고
4. **Loop 구조**로 계속 개선할 수 있게 한다

그 반복을 **의식적으로, 구조적으로, 코드로** 다루기 위한 시도다.

OpenClaw 사례가 보여주듯이:
- **같은 도구도 사용자에 따라 완전히 다른 평가**가 나온다
- **"좋다/나쁘다"가 아니라 "당신의 상황에서는"**이 핵심이다
- **투명한 점수 계산**이 신뢰를 만든다

그리고 이 모든 것이 **프라이버시를 침해하지 않고도** 가능하다.

---

## 부록: 실행 방법

```bash
# 설치
pip install -e .

# 데모 실행
decision-loop demo

# OpenClaw 평가 예제 실행
python examples/openclaw_evaluation.py

# 설정 파일로 실행
decision-loop run --config configs/ai_tools_example.yaml

# 대화형 모드
decision-loop interactive
```

---

**Sources**:
- [OpenClaw GitHub](https://github.com/clawdbot/clawdbot)
- [The Sovereign AI Security Crisis: 42,000 Exposed OpenClaw Instances](https://maordayanofficial.medium.com/the-sovereign-ai-security-crisis-42-000-exposed-openclaw-instances-and-the-collapse-of-1e3f2687b951)
- [The Dark Side of OpenClaw: Security Risks in Local-First AI](https://medium.com/@abivarma/the-dark-side-of-moltbot-security-risks-in-local-first-ai-4e54407d39bb)
- [OpenClaw Introduces Secure Hosted Platform](https://finance.yahoo.com/news/openclaw-introduces-secure-hosted-clawdbot-204800756.html)
