# 유전 형질 예측 프로그램 (사진 인식 버전)
# 
# 추가 설치 필요:
# pip install streamlit opencv-python pillow numpy mediapipe

import streamlit as st
from collections import Counter
import cv2
import numpy as np
from PIL import Image
import io

# 페이지 설정
st.set_page_config(
    page_title="유전 형질 예측 (사진 인식)",
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
    .upload-box {
        border: 2px dashed #1f77b4;
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# 형질 데이터 - 자동/수동 구분
traits_data = [
    {
        'id': 'hair_color',
        'name': '머리카락 색',
        'auto_detect': True,  # 사진으로 자동 인식 가능
        'dominant': '검정/갈색',
        'recessive': '금발/적발',
        'options': {
            '검정/갈색 (가족 모두 어두운 머리)': 'DD',
            '검정/갈색 (가족 중 밝은 머리도 있음)': 'Dd',
            '금발/적발': 'dd'
        }
    },
    {
        'id': 'hair_texture',
        'name': '머리카락 모양',
        'auto_detect': True,
        'dominant': '곱슬머리',
        'recessive': '직모',
        'options': {
            '곱슬머리 (가족 모두 곱슬)': 'DD',
            '곱슬머리 (가족 중 직모도 있음)': 'Dd',
            '직모': 'dd'
        }
    },
    {
        'id': 'skin',
        'name': '피부색',
        'auto_detect': True,
        'dominant': '어두운 피부',
        'recessive': '밝은 피부',
        'options': {
            '어두운 피부': 'dark',
            '중간 톤 피부': 'medium',
            '밝은 피부': 'light'
        }
    },
    {
        'id': 'dimples',
        'name': '보조개',
        'auto_detect': False,  # 수동 입력 필요
        'dominant': '있음',
        'recessive': '없음',
        'options': {
            '보조개 있음 (가족 대부분 있음)': 'DD',
            '보조개 있음 (가족 중 없는 사람도 있음)': 'Dd',
            '보조개 없음': 'dd'
        }
    },
    {
        'id': 'double_eyelid',
        'name': '쌍꺼풀',
        'auto_detect': False,
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
        'auto_detect': False,
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
        'auto_detect': False,
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
        'auto_detect': False,
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
        'name': '키',
        'auto_detect': False,
        'dominant': '큰 키',
        'recessive': '작은 키',
        'options': {
            '매우 큼 (여 170cm 이상/남 180cm 이상)': 'tall',
            '중간 (여 160-170cm/남 170-180cm)': 'medium',
            '작음 (여 160cm 이하/남 170cm 이하)': 'short'
        }
    }
]

# ==========================================
# AI 분석 함수들
# ==========================================

def analyze_hair_color(image):
    """
    사진에서 머리카락 색 분석
    
    반환: 'DD', 'Dd', 'dd'
    """
    # 이미지를 numpy array로 변환
    img_array = np.array(image)
    
    # BGR로 변환 (OpenCV 포맷)
    img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
    
    # HSV로 변환 (색상 분석에 유리)
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    
    # 상단 30% 영역 (머리 영역 추정)
    height, width = hsv.shape[:2]
    hair_region = hsv[0:int(height*0.3), :]
    
    # 평균 밝기 계산 (V 채널)
    avg_brightness = np.mean(hair_region[:, :, 2])
    
    # 밝기로 분류
    if avg_brightness > 150:  # 밝은 머리 (금발/적발)
        return 'dd'
    elif avg_brightness > 100:  # 중간 (혼합 가능성)
        return 'Dd'
    else:  # 어두운 머리
        return 'DD'

def analyze_hair_texture(image):
    """
    사진에서 머리카락 모양 분석 (직모/곱슬)
    
    반환: 'DD', 'Dd', 'dd'
    """
    # 실제로는 더 복잡한 AI 모델 필요
    # 여기서는 간단한 예시
    img_array = np.array(image)
    img_gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    
    # 가장자리 검출
    edges = cv2.Canny(img_gray, 100, 200)
    
    # 상단 영역의 엣지 밀도로 곱슬 정도 추정
    height = edges.shape[0]
    hair_edges = edges[0:int(height*0.3), :]
    edge_density = np.sum(hair_edges) / hair_edges.size
    
    if edge_density > 0.15:  # 엣지 많음 = 곱슬
        return 'DD'
    elif edge_density > 0.08:
        return 'Dd'
    else:  # 엣지 적음 = 직모
        return 'dd'

def analyze_skin_tone(image):
    """
    사진에서 피부색 분석
    
    반환: 'dark', 'medium', 'light'
    """
    img_array = np.array(image)
    img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
    
    # 얼굴 중앙 영역 추출 (간단한 방법)
    height, width = img_bgr.shape[:2]
    face_region = img_bgr[
        int(height*0.3):int(height*0.7),
        int(width*0.3):int(width*0.7)
    ]
    
    # RGB 평균값 계산
    avg_color = np.mean(face_region, axis=(0, 1))
    brightness = np.mean(avg_color)
    
    if brightness < 100:
        return 'dark'
    elif brightness < 160:
        return 'medium'
    else:
        return 'light'

def analyze_photo(image):
    """
    사진을 분석하여 자동 인식 가능한 형질 추출
    
    반환: 딕셔너리 {trait_id: genotype}
    """
    results = {}
    
    try:
        results['hair_color'] = analyze_hair_color(image)
        results['hair_texture'] = analyze_hair_texture(image)
        results['skin'] = analyze_skin_tone(image)
        return results, True
    except Exception as e:
        st.error(f"사진 분석 중 오류: {str(e)}")
        return {}, False

# ==========================================
# Punnett Square 함수들 (이전과 동일)
# ==========================================

def punnett_square(g1, g2):
    if g1 in ['tall', 'medium', 'short', 'dark', 'light']:
        return predict_polygenic(g1, g2)
    
    outcomes = []
    for a1 in g1:
        for a2 in g2:
            genotype = ''.join(sorted([a1, a2], reverse=True))
            outcomes.append(genotype)
    return outcomes

def predict_polygenic(p1, p2):
    values = {'tall': 3, 'medium': 2, 'short': 1, 'dark': 3, 'light': 1}
    avg = (values.get(p1, 2) + values.get(p2, 2)) / 2
    
    if avg >= 2.5:
        return ['높음/어두움']
    elif avg >= 1.5:
        return ['중간']
    return ['낮음/밝음']

def get_phenotype(genotype):
    if genotype in ['높음/어두움', '중간', '낮음/밝음']:
        return genotype
    return '우성 형질 표현' if 'D' in genotype else '열성 형질 표현'

# ==========================================
# 세션 상태 초기화
# ==========================================

if 'page' not in st.session_state:
    st.session_state.page = 'user_upload'
if 'user_data' not in st.session_state:
    st.session_state.user_data = {}
if 'spouse_data' not in st.session_state:
    st.session_state.spouse_data = {}
if 'user_photo_analyzed' not in st.session_state:
    st.session_state.user_photo_analyzed = False
if 'spouse_photo_analyzed' not in st.session_state:
    st.session_state.spouse_photo_analyzed = False

# ==========================================
# 메인 화면
# ==========================================

st.title("🧬 유전 형질 예측 프로그램 (AI 사진 분석)")
st.markdown("📸 사진을 업로드하면 AI가 자동으로 형질을 분석합니다!")
st.markdown("---")

# ==========================================
# 사이드바
# ==========================================

with st.sidebar:
    st.header("📌 진행 상황")
    
    if st.session_state.page == 'user_upload':
        st.info("**1단계:** 본인 사진 업로드")
        st.markdown("⬜ 본인 형질 입력")
        st.markdown("⬜ 배우자 사진 업로드")
        st.markdown("⬜ 배우자 형질 입력")
        st.markdown("⬜ 결과 확인")
    elif st.session_state.page == 'user_input':
        st.success("**✅ 1단계:** 본인 사진 분석 완료")
        st.info("**2단계:** 본인 형질 입력 중")
        st.markdown("⬜ 배우자 사진 업로드")
        st.markdown("⬜ 배우자 형질 입력")
        st.markdown("⬜ 결과 확인")
    elif st.session_state.page == 'spouse_upload':
        st.success("**✅ 1-2단계:** 본인 완료")
        st.info("**3단계:** 배우자 사진 업로드")
        st.markdown("⬜ 배우자 형질 입력")
        st.markdown("⬜ 결과 확인")
    elif st.session_state.page == 'spouse_input':
        st.success("**✅ 1-3단계:** 완료")
        st.info("**4단계:** 배우자 형질 입력 중")
        st.markdown("⬜ 결과 확인")
    else:
        st.success("**✅ 모든 단계 완료!**")
        st.info("**5단계:** 결과 확인 중")
    
    st.markdown("---")
    st.markdown("""
    ### 🤖 AI 분석 항목
    - ✅ 머리카락 색
    - ✅ 머리카락 모양
    - ✅ 피부색
    
    ### ✍️ 직접 입력 항목
    - 보조개
    - 쌍꺼풀
    - 코 모양
    - 입술 두께
    - 귓볼
    - 키
    """)
    
    st.markdown("---")
    
    if st.button("🔄 처음부터 다시 시작"):
        st.session_state.page = 'user_upload'
        st.session_state.user_data = {}
        st.session_state.spouse_data = {}
        st.session_state.user_photo_analyzed = False
        st.session_state.spouse_photo_analyzed = False
        st.rerun()

# ==========================================
# 페이지별 내용
# ==========================================

# 1. 본인 사진 업로드
if st.session_state.page == 'user_upload':
    st.header("📸 본인의 사진을 업로드하세요")
    
    st.info("""
    💡 **좋은 사진 팁:**
    - 정면 사진
    - 밝은 조명
    - 머리카락이 잘 보이는 사진
    - 얼굴 전체가 나온 사진
    """)
    
    uploaded_file = st.file_uploader(
        "사진 선택 (JPG, PNG)",
        type=['jpg', 'jpeg', 'png'],
        key='user_photo'
    )
    
    if uploaded_file is not None:
        # 사진 표시
        image = Image.open(uploaded_file)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(image, caption="업로드된 사진", use_container_width=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 분석 버튼
        if st.button("🤖 AI로 사진 분석하기", type="primary", use_container_width=True):
            with st.spinner("AI가 사진을 분석하는 중..."):
                auto_results, success = analyze_photo(image)
                
                if success:
                    st.session_state.user_data.update(auto_results)
                    st.session_state.user_photo_analyzed = True
                    st.success("✅ 사진 분석 완료!")
                    
                    # 분석 결과 미리보기
                    st.markdown("### 🔍 AI 분석 결과")
                    for trait_id, genotype in auto_results.items():
                        trait = next(t for t in traits_data if t['id'] == trait_id)
                        st.info(f"**{trait['name']}**: {genotype}")
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    if st.button("▶️ 다음 단계 (나머지 입력)", type="primary"):
                        st.session_state.page = 'user_input'
                        st.rerun()

# 2. 본인 나머지 형질 입력
elif st.session_state.page == 'user_input':
    st.header("✍️ 나머지 형질을 입력하세요")
    
    # AI로 분석된 형질 표시
    st.success("✅ AI 분석 완료된 형질:")
    auto_traits = [t for t in traits_data if t['auto_detect']]
    cols = st.columns(3)
    for i, trait in enumerate(auto_traits):
        with cols[i % 3]:
            if trait['id'] in st.session_state.user_data:
                st.metric(
                    trait['name'],
                    st.session_state.user_data[trait['id']]
                )
    
    st.markdown("---")
    st.info("📝 아래 항목들을 직접 선택해주세요:")
    
    # 수동 입력 필요한 형질
    manual_traits = [t for t in traits_data if not t['auto_detect']]
    
    col1, col2 = st.columns(2)
    
    for i, trait in enumerate(manual_traits):
        col = col1 if i % 2 == 0 else col2
        
        with col:
            st.subheader(f"🧬 {trait['name']}")
            st.caption(f"우성: {trait['dominant']} / 열성: {trait['recessive']}")
            
            selected = st.selectbox(
                "선택하세요",
                options=list(trait['options'].keys()),
                key=f"user_{trait['id']}",
                label_visibility="collapsed"
            )
            
            genotype = trait['options'][selected]
            st.caption(f"유전자형: `{genotype}`")
            st.session_state.user_data[trait['id']] = genotype
            st.markdown("---")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("◀️ 사진 다시 업로드"):
            st.session_state.page = 'user_upload'
            st.rerun()
    with col3:
        if st.button("▶️ 다음 (배우자 차례)", type="primary"):
            st.session_state.page = 'spouse_upload'
            st.rerun()

# 3. 배우자 사진 업로드
elif st.session_state.page == 'spouse_upload':
    st.header("📸 배우자의 사진을 업로드하세요")
    
    st.info("""
    💡 **좋은 사진 팁:**
    - 정면 사진
    - 밝은 조명
    - 머리카락이 잘 보이는 사진
    - 얼굴 전체가 나온 사진
    """)
    
    uploaded_file = st.file_uploader(
        "사진 선택 (JPG, PNG)",
        type=['jpg', 'jpeg', 'png'],
        key='spouse_photo'
    )
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(image, caption="업로드된 사진", use_container_width=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("🤖 AI로 사진 분석하기", type="primary", use_container_width=True):
            with st.spinner("AI가 사진을 분석하는 중..."):
                auto_results, success = analyze_photo(image)
                
                if success:
                    st.session_state.spouse_data.update(auto_results)
                    st.session_state.spouse_photo_analyzed = True
                    st.success("✅ 사진 분석 완료!")
                    
                    st.markdown("### 🔍 AI 분석 결과")
                    for trait_id, genotype in auto_results.items():
                        trait = next(t for t in traits_data if t['id'] == trait_id)
                        st.info(f"**{trait['name']}**: {genotype}")
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("◀️ 이전"):
                            st.session_state.page = 'user_input'
                            st.rerun()
                    with col2:
                        if st.button("▶️ 다음 단계", type="primary"):
                            st.session_state.page = 'spouse_input'
                            st.rerun()

# 4. 배우자 나머지 형질 입력
elif st.session_state.page == 'spouse_input':
    st.header("✍️ 배우자의 나머지 형질을 입력하세요")
    
    st.success("✅ AI 분석 완료된 형질:")
    auto_traits = [t for t in traits_data if t['auto_detect']]
    cols = st.columns(3)
    for i, trait in enumerate(auto_traits):
        with cols[i % 3]:
            if trait['id'] in st.session_state.spouse_data:
                st.metric(
                    trait['name'],
                    st.session_state.spouse_data[trait['id']]
                )
    
    st.markdown("---")
    st.info("📝 아래 항목들을 직접 선택해주세요:")
    
    manual_traits = [t for t in traits_data if not t['auto_detect']]
    
    col1, col2 = st.columns(2)
    
    for i, trait in enumerate(manual_traits):
        col = col1 if i % 2 == 0 else col2
        
        with col:
            st.subheader(f"🧬 {trait['name']}")
            st.caption(f"우성: {trait['dominant']} / 열성: {trait['recessive']}")
            
            selected = st.selectbox(
                "선택하세요",
                options=list(trait['options'].keys()),
                key=f"spouse_{trait['id']}",
                label_visibility="collapsed"
            )
            
            genotype = trait['options'][selected]
            st.caption(f"유전자형: `{genotype}`")
            st.session_state.spouse_data[trait['id']] = genotype
            st.markdown("---")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("◀️ 이전"):
            st.session_state.page = 'spouse_upload'
            st.rerun()
    with col3:
        if st.button("🎯 결과 보기", type="primary"):
            st.session_state.page = 'results'
            st.rerun()

# 5. 결과 페이지 (이전과 동일)
elif st.session_state.page == 'results':
    st.header("👶 자녀 형질 예측 결과")
    st.success("🎉 AI 분석과 입력이 완료되었습니다!")
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["📊 상세 결과", "📋 요약"])
    
    with tab1:
        for trait in traits_data:
            trait_id = trait['id']
            user_gen = st.session_state.user_data.get(trait_id, 'Dd')
            spouse_gen = st.session_state.spouse_data.get(trait_id, 'Dd')
            
            outcomes = punnett_square(user_gen, spouse_gen)
            
            with st.expander(f"🧬 {trait['name']}" + (" 🤖" if trait['auto_detect'] else " ✍️"), expanded=True):
                col1, col2, col3 = st.columns([1, 0.2, 1])
                with col1:
                    st.info(f"**본인**\n\n`{user_gen}`")
                with col2:
                    st.markdown("<br>**×**", unsafe_allow_html=True)
                with col3:
                    st.info(f"**배우자**\n\n`{spouse_gen}`")
                
                st.markdown("**자녀의 예상 형질:**")
                
                if outcomes[0] in ['높음/어두움', '중간', '낮음/밝음']:
                    st.success(f"📈 **{outcomes[0]}** 경향")
                else:
                    counts = Counter(outcomes)
                    for genotype, count in counts.items():
                        prob = (count / len(outcomes)) * 100
                        phenotype = get_phenotype(genotype)
                        st.markdown(f"**{genotype}** ({phenotype})")
                        st.progress(prob / 100)
                        st.caption(f"확률: {prob:.1f}% ({count}/4)")
                
                st.markdown("---")
    
    with tab2:
        st.subheader("📋 전체 요약")
        
        st.markdown("### 🤖 AI가 분석한 형질")
        auto_analyzed = [t for t in traits_data if t['auto_detect']]
        for trait in auto_analyzed:
            col1, col2 = st.columns(2)
            with col1:
                st.metric(
                    f"본인 - {trait['name']}",
                    st.session_state.user_data.get(trait['id'], 'N/A')
                )
            with col2:
                st.metric(
                    f"배우자 - {trait['name']}",
                    st.session_state.spouse_data.get(trait['id'], 'N/A')
                )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("◀️ 배우자 재입력"):
            st.session_state.page = 'spouse_input'
            st.rerun()
    with col2:
        if st.button("🔄 처음부터 다시", type="primary"):
            st.session_state.page = 'user_upload'
            st.session_state.user_data = {}
            st.session_state.spouse_data = {}
            st.session_state.user_photo_analyzed = False
            st.session_state.spouse_photo_analyzed = False
            st.rerun()

st.markdown("---")
st.caption("💡 AI 분석은 참고용이며, 실제 유전은 더 복잡할 수 있습