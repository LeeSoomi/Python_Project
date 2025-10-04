# 유전 형질 예측 프로그램 (Streamlit 버전)
# 
# 설치: pip install streamlit
# 실행: streamlit run genetics_app.py

import streamlit as st
from collections import Counter

# 페이지 설정
st.set_page_config(
    page_title="유전 형질 예측",
    page_icon="🧬",
    layout="wide"
)

# 커스텀 CSS
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        height: 3rem;
        font-size: 1.1rem;
    }
    h1 {
        color: #1f77b4;
    }
    h2 {
        color: #2ca02c;
    }
    h3 {
        color: #ff7f0e;
    }
</style>
""", unsafe_allow_html=True)

# 형질 데이터
traits_data = [
    {
        'id': 'hair_texture',
        'name': '머리카락 모양',
        'dominant': '곱슬머리',
        'recessive': '직모',
        'options': {
            '곱슬머리 (가족 모두 곱슬)': 'DD',
            '곱슬머리 (가족 중 직모도 있음)': 'Dd',
            '직모': 'dd'
        }
    },
    {
        'id': 'hair_color',
        'name': '머리카락 색',
        'dominant': '검정/갈색',
        'recessive': '금발/적발',
        'options': {
            '검정/갈색 (가족 모두 어두운 머리)': 'DD',
            '검정/갈색 (가족 중 밝은 머리도 있음)': 'Dd',
            '금발/적발': 'dd'
        }
    },
    {
        'id': 'dimples',
        'name': '보조개',
        'dominant': '있음',
        'recessive': '없음',
        'options': {
            '보조개 있음 (가족 대부분 있음)': 'DD',
            '보조개 있음 (가족 중 없는 사람도 있음)': 'Dd',
            '보조개 없음': 'dd'
        }
    },
    {
        'id': 'widows_peak',
        'name': 'M자 이마선',
        'dominant': '있음',
        'recessive': '없음',
        'options': {
            'M자 이마선 있음 (가족 대부분 있음)': 'DD',
            'M자 이마선 있음 (가족 중 없는 사람도 있음)': 'Dd',
            'M자 이마선 없음': 'dd'
        }
    },
    {
        'id': 'eyebrows',
        'name': '눈썹 연결',
        'dominant': '있음',
        'recessive': '없음',
        'options': {
            '눈썹 연결됨': 'DD',
            '눈썹 약간 연결됨': 'Dd',
            '눈썹 분리됨': 'dd'
        }
    },
    {
        'id': 'freckles',
        'name': '주근깨',
        'dominant': '있음',
        'recessive': '없음',
        'options': {
            '주근깨 많음': 'DD',
            '주근깨 약간 있음': 'Dd',
            '주근깨 없음': 'dd'
        }
    },
    {
        'id': 'eyelashes',
        'name': '속눈썹 길이',
        'dominant': '긴 속눈썹',
        'recessive': '짧은 속눈썹',
        'options': {
            '긴 속눈썹': 'DD',
            '중간 길이 속눈썹': 'Dd',
            '짧은 속눈썹': 'dd'
        }
    },
    {
        'id': 'double_eyelid',
        'name': '쌍꺼풀',
        'dominant': '있음',
        'recessive': '없음',
        'options': {
            '쌍꺼풀 있음 (진함)': 'DD',
            '쌍꺼풀 있음 (약함)': 'Dd',
            '쌍꺼풀 없음': 'dd'
        }
    },
    {
        'id': 'nose',
        'name': '코 모양',
        'dominant': '오똑한 코',
        'recessive': '낮은 코',
        'options': {
            '오똑한 코': 'DD',
            '중간 높이 코': 'Dd',
            '낮은 코': 'dd'
        }
    },
    {
        'id': 'lips',
        'name': '입술 두께',
        'dominant': '두꺼운 입술',
        'recessive': '얇은 입술',
        'options': {
            '두꺼운 입술': 'DD',
            '중간 두께 입술': 'Dd',
            '얇은 입술': 'dd'
        }
    },
    {
        'id': 'earlobe',
        'name': '귓볼',
        'dominant': '분리형',
        'recessive': '부착형',
        'options': {
            '분리형 귓볼': 'DD',
            '약간 분리된 귓볼': 'Dd',
            '부착형 귓볼': 'dd'
        }
    },
    {
        'id': 'height',
        'name': '키 (다인자 유전)',
        'dominant': '큰 키',
        'recessive': '작은 키',
        'options': {
            '매우 큼 (여 170cm 이상/남 180cm 이상)': 'tall',
            '중간 (여 160-170cm/남 170-180cm)': 'medium',
            '작음 (여 160cm 이하/남 170cm 이하)': 'short'
        }
    },
    {
        'id': 'skin',
        'name': '피부색 (다인자 유전)',
        'dominant': '어두운 피부',
        'recessive': '밝은 피부',
        'options': {
            '어두운 피부': 'dark',
            '중간 톤 피부': 'medium',
            '밝은 피부': 'light'
        }
    }
]

def punnett_square(g1, g2):
    """Punnett Square를 이용한 자녀 유전자형 계산"""
    # 다인자 유전 형질 처리
    if g1 in ['tall', 'medium', 'short', 'dark', 'light']:
        return predict_polygenic(g1, g2)
    
    # 단일 유전자 형질 처리
    outcomes = []
    for a1 in g1:
        for a2 in g2:
            genotype = ''.join(sorted([a1, a2], reverse=True))
            outcomes.append(genotype)
    return outcomes

def predict_polygenic(p1, p2):
    """다인자 유전 형질 예측"""
    values = {'tall': 3, 'medium': 2, 'short': 1, 'dark': 3, 'light': 1}
    avg = (values.get(p1, 2) + values.get(p2, 2)) / 2
    
    if avg >= 2.5:
        return ['높음/어두움']
    elif avg >= 1.5:
        return ['중간']
    return ['낮음/밝음']

def get_phenotype(genotype):
    """유전자형에서 표현형 결정"""
    if genotype in ['높음/어두움', '중간', '낮음/밝음']:
        return genotype
    return '우성 형질 표현' if 'D' in genotype else '열성 형질 표현'

# 세션 상태 초기화
if 'page' not in st.session_state:
    st.session_state.page = 'user'
if 'user_data' not in st.session_state:
    st.session_state.user_data = {}
if 'spouse_data' not in st.session_state:
    st.session_state.spouse_data = {}

# ==========================================
# 메인 화면
# ==========================================

# 타이틀
st.title("🧬 유전 형질 예측 프로그램")
st.markdown("부모의 형질을 입력하여 자녀의 유전 형질을 예측해보세요!")
st.markdown("---")

# ==========================================
# 사이드바
# ==========================================
with st.sidebar:
    st.header("📌 진행 상황")
    
    if st.session_state.page == 'user':
        st.info("**1단계:** 본인 형질 입력 중")
        st.markdown("⬜ 배우자 형질 입력")
        st.markdown("⬜ 결과 확인")
    elif st.session_state.page == 'spouse':
        st.success("**✅ 1단계:** 본인 완료")
        st.info("**2단계:** 배우자 형질 입력 중")
        st.markdown("⬜ 결과 확인")
    else:
        st.success("**✅ 1단계:** 본인 완료")
        st.success("**✅ 2단계:** 배우자 완료")
        st.info("**3단계:** 결과 확인 중")
    
    st.markdown("---")
    
    st.markdown("""
    ### 📖 사용 방법
    1. 본인의 형질을 선택
    2. 배우자의 형질을 선택
    3. 자녀의 예상 형질 확인
    
    ### 🧬 유전자형 표기
    - **DD**: 동형접합 우성
    - **Dd**: 이형접합
    - **dd**: 동형접합 열성
    
    ### 💡 팁
    가족 구성원의 형질을 참고하면
    더 정확한 유전자형을 선택할 수 있어요!
    """)
    
    st.markdown("---")
    
    if st.button("🔄 처음부터 다시 시작"):
        st.session_state.page = 'user'
        st.session_state.user_data = {}
        st.session_state.spouse_data = {}
        st.rerun()

# ==========================================
# 페이지별 내용
# ==========================================

if st.session_state.page == 'user':
    st.header("🙋 본인의 형질을 선택하세요")
    st.info("💡 가족 중에 다른 형질을 가진 사람이 있다면 이형접합(Dd)을 선택하세요.")
    
    col1, col2 = st.columns(2)
    
    for i, trait in enumerate(traits_data):
        col = col1 if i % 2 == 0 else col2
        
        with col:
            with st.container():
                st.subheader(f"🧬 {trait['name']}")
                st.caption(f"우성: {trait['dominant']} / 열성: {trait['recessive']}")
                
                selected = st.selectbox(
                    "선택하세요",
                    options=list(trait['options'].keys()),
                    key=f"user_{trait['id']}",
                    label_visibility="collapsed"
                )
                
                # 유전자형 표시
                genotype = trait['options'][selected]
                st.caption(f"유전자형: `{genotype}`")
                
                st.session_state.user_data[trait['id']] = genotype
                st.markdown("---")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("▶️ 다음 단계 (배우자 입력)", type="primary", use_container_width=True):
            st.session_state.page = 'spouse'
            st.rerun()

elif st.session_state.page == 'spouse':
    st.header("💑 배우자의 형질을 선택하세요")
    st.info("💡 배우자의 가족 구성원도 고려하여 유전자형을 선택하세요.")
    
    col1, col2 = st.columns(2)
    
    for i, trait in enumerate(traits_data):
        col = col1 if i % 2 == 0 else col2
        
        with col:
            with st.container():
                st.subheader(f"🧬 {trait['name']}")
                st.caption(f"우성: {trait['dominant']} / 열성: {trait['recessive']}")
                
                selected = st.selectbox(
                    "선택하세요",
                    options=list(trait['options'].keys()),
                    key=f"spouse_{trait['id']}",
                    label_visibility="collapsed"
                )
                
                # 유전자형 표시
                genotype = trait['options'][selected]
                st.caption(f"유전자형: `{genotype}`")
                
                st.session_state.spouse_data[trait['id']] = genotype
                st.markdown("---")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("◀️ 이전 (본인 재입력)", use_container_width=True):
            st.session_state.page = 'user'
            st.rerun()
    with col3:
        if st.button("🎯 결과 보기", type="primary", use_container_width=True):
            st.session_state.page = 'results'
            st.rerun()

elif st.session_state.page == 'results':
    st.header("👶 자녀 형질 예측 결과")
    st.success("🎉 Punnett Square를 이용한 유전 확률 분석이 완료되었습니다!")
    st.markdown("---")
    
    # 결과를 탭으로 구성
    tab1, tab2 = st.tabs(["📊 상세 결과", "📋 요약"])
    
    with tab1:
        for trait in traits_data:
            trait_id = trait['id']
            user_gen = st.session_state.user_data[trait_id]
            spouse_gen = st.session_state.spouse_data[trait_id]
            
            outcomes = punnett_square(user_gen, spouse_gen)
            
            with st.expander(f"🧬 {trait['name']}", expanded=True):
                # 부모 유전자형 표시
                col1, col2, col3 = st.columns([1, 0.2, 1])
                with col1:
                    st.info(f"**본인의 유전자형**\n\n`{user_gen}`")
                with col2:
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown("**×**", unsafe_allow_html=True)
                with col3:
                    st.info(f"**배우자의 유전자형**\n\n`{spouse_gen}`")
                
                st.markdown("**자녀의 예상 형질:**")
                
                # Punnett Square 결과
                if outcomes[0] in ['높음/어두움', '중간', '낮음/밝음']:
                    st.success(f"📈 **{outcomes[0]}** 경향을 보일 가능성이 높습니다.")
                    st.caption("※ 다인자 유전은 여러 유전자의 복합 작용으로 나타나므로 중간값 경향을 보입니다.")
                else:
                    counts = Counter(outcomes)
                    
                    # 확률 차트
                    for genotype, count in counts.items():
                        prob = (count / len(outcomes)) * 100
                        phenotype = get_phenotype(genotype)
                        
                        # 프로그레스 바로 확률 표시
                        st.markdown(f"**{genotype}** ({phenotype})")
                        st.progress(prob / 100)
                        st.caption(f"확률: {prob:.1f}% ({count}/4)")
                
                st.markdown("---")
    
    with tab2:
        st.subheader("📋 우성 형질 vs 열성 형질 요약")
        
        dominant_count = 0
        recessive_count = 0
        mixed_count = 0
        
        for trait in traits_data:
            trait_id = trait['id']
            user_gen = st.session_state.user_data[trait_id]
            spouse_gen = st.session_state.spouse_data[trait_id]
            outcomes = punnett_square(user_gen, spouse_gen)
            
            if outcomes[0] in ['높음/어두움', '중간', '낮음/밝음']:
                mixed_count += 1
            else:
                counts = Counter(outcomes)
                dominant_prob = sum(count for gen, count in counts.items() if 'D' in gen) / len(outcomes)
                
                if dominant_prob >= 0.75:
                    dominant_count += 1
                elif dominant_prob <= 0.25:
                    recessive_count += 1
                else:
                    mixed_count += 1
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("우성 형질 우세", f"{dominant_count}개")
        with col2:
            st.metric("혼합/중간", f"{mixed_count}개")
        with col3:
            st.metric("열성 형질 우세", f"{recessive_count}개")
        
        st.info("""
        **💡 해석 가이드:**
        - 우성 형질 우세: 해당 형질이 나타날 확률이 75% 이상
        - 혼합/중간: 우성과 열성이 혼합되거나 다인자 유전
        - 열성 형질 우세: 열성 형질이 나타날 확률이 75% 이상
        """)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 버튼들
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("◀️ 배우자 재입력", use_container_width=True):
            st.session_state.page = 'spouse'
            st.rerun()
    with col3:
        if st.button("🔄 처음부터 다시", type="primary", use_container_width=True):
            st.session_state.page = 'user'
            st.session_state.user_data = {}
            st.session_state.spouse_data = {}
            st.rerun()

# 푸터
st.markdown("---")
st.caption("💡 이 프로그램은 멘델 유전 법칙을 기반으로 한 간단한 예측 모델입니다. 실제 유전은 더 복잡할 수 있습니다.")