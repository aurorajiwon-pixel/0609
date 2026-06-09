import streamlit as st
import json, os, threading
from datetime import datetime

# ── 기본 설정 ─────────────────────────────────────────────
st.set_page_config(
    page_title="기후변화 모의총회 포트폴리오",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

COUNTRIES  = ["중국", "인도", "투발루", "미국"]
ISSUES     = ["기후 기금의 규모", "기금의 지원 방식", "기금 부담 국가"]
Q4_CHOICES = ["충분한 재정 지원", "공정한 규칙과 기준",
               "선진국의 역사적 책임 인정", "기술 공유",
               "국가 간 신뢰 구축", "직접 작성"]
DATA_FILE  = "reflections.json"
TEACHER_PW = "earth2025"
_lock      = threading.Lock()

# ── 데이터 ─────────────────────────────────────────────────
def load_all():
    with _lock:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    return {}

def save_record(key, record):
    with _lock:
        data = load_all()
        data[key] = record
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

def get_group(g):
    return {k: v for k, v in load_all().items() if v.get("group") == g}

def ukey(g, n): return f"{g}|{n}"

# ── 세션 초기화 ─────────────────────────────────────────────
for k, d in [("in", False), ("group", None), ("name", None),
             ("teacher", False), ("rec", {})]:
    if k not in st.session_state:
        st.session_state[k] = d

# ── CSS ────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stSidebar"]          { background:#0e2a3d !important; }
[data-testid="stSidebar"] *        { color:#e8edf0 !important; }
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stTextInput label { color:#9fb8c8 !important; font-size:13px; }

.issue-banner{
  background:#fdf0f0; border:1px solid #e8b4b4;
  border-left:4px solid #7a1e1e;
  border-radius:6px; padding:10px 16px;
  margin-bottom:16px; font-size:13px; color:#7a1e1e; line-height:1.7;
}
.section-title{font-size:17px;font-weight:700;color:#0e2a3d;margin-bottom:4px;}
.section-desc {font-size:12px;color:#8a8680;margin-bottom:14px;}
.nation-head{
  background:#e8eef5; border-left:4px solid #1e3d6b;
  padding:8px 14px; border-radius:4px 4px 0 0;
  font-size:13px; font-weight:700; color:#1e3d6b;
}
.compare-wrap{
  border:1px solid #d8e0e3; border-radius:6px;
  overflow:hidden; margin-bottom:12px;
}
.compare-head{
  background:#1e3d6b; color:#fff;
  padding:8px 14px; font-size:12px; font-weight:700;
}
.ref-card{
  border:1px solid #d8e0e3; border-radius:8px;
  overflow:hidden; margin-bottom:12px;
}
.ref-head{
  background:#e8f0ea; border-bottom:1px solid #9fc9ab;
  padding:10px 14px;
}
.ref-qnum{
  display:inline-flex; align-items:center; justify-content:center;
  width:24px; height:24px; border-radius:50%;
  background:#2c5f3a; color:#fff;
  font-size:12px; font-weight:700; margin-right:8px; flex-shrink:0;
}
.ref-qtxt{font-size:14px;font-weight:700;color:#1a2814;display:inline;}
.ref-hint{font-size:12px;color:#6a8070;margin-top:4px;}
.peer-card{
  border:1px solid #d8e0e3; border-radius:8px;
  padding:14px 18px; margin-bottom:10px; background:#fff;
}
.peer-name{
  font-size:15px; font-weight:700; color:#0e2a3d;
  border-bottom:1px solid #e8e2da;
  padding-bottom:6px; margin-bottom:10px;
}
.ql{font-size:11px;color:#8a8680;margin-top:8px;}
.qa{font-size:13px;color:#1a1814;margin-top:2px;white-space:pre-wrap;}
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🌍 모의총회 포트폴리오")
    st.markdown("---")

    if not st.session_state["in"]:
        grp  = st.selectbox("📍 내 배정 국가", COUNTRIES)
        name = st.text_input("✏️ 이름", placeholder="이름을 입력하세요")

        if st.button("시작 / 이전 기록 불러오기", type="primary", use_container_width=True):
            if name.strip():
                key      = ukey(grp, name.strip())
                existing = load_all().get(key, {})
                st.session_state["in"]    = True
                st.session_state["group"] = grp
                st.session_state["name"]  = name.strip()
                st.session_state["rec"]   = existing.get("rec", {})
                st.rerun()
            else:
                st.error("이름을 입력해주세요.")

        st.markdown("---")
        pw = st.text_input("🔑 교사 뷰 비밀번호", type="password")
        if st.button("교사 뷰", use_container_width=True):
            st.session_state["teacher"] = (pw == TEACHER_PW)
            if pw != TEACHER_PW: st.error("비밀번호가 틀렸습니다.")
            else: st.rerun()

    else:
        st.markdown(f"### {st.session_state['group']} 대표단")
        st.markdown(f"**{st.session_state['name']}** 님")
        st.markdown("---")
        st.caption("각 섹션을 작성하고\n**저장** 버튼을 눌러주세요.")
        if st.button("로그아웃", use_container_width=True):
            for k in ("in","group","name","rec"):
                st.session_state[k] = False if k=="in" else ({} if k=="rec" else None)
            st.rerun()


# ════════════════════════════════════════════════════════
# TEACHER VIEW
# ════════════════════════════════════════════════════════
if st.session_state.get("teacher"):
    st.title("📋 교사 뷰 — 전체 제출 기록")
    if st.button("← 닫기"):
        st.session_state["teacher"] = False
        st.rerun()

    data = load_all()
    if not data:
        st.info("아직 제출된 기록이 없습니다.")
    else:
        for ctry in COUNTRIES:
            grp_data = {k: v for k, v in data.items() if v.get("group") == ctry}
            if not grp_data: continue
            with st.expander(f"🏴 {ctry} 모둠 ({len(grp_data)}명)", expanded=False):
                for key, entry in grp_data.items():
                    r = entry.get("rec", {})
                    st.markdown(f"<div class='peer-name'>👤 {entry.get('name','')} "
                                f"<small style='color:#aaa'>{entry.get('saved_at','')}</small></div>",
                                unsafe_allow_html=True)
                    col1, col2 = st.columns(2)
                    with col1:
                        for i in range(3):
                            nr = r.get(f"nation{i+1}", {})
                            if nr.get("name"):
                                st.markdown(f"**나라{i+1}: {nr['name']}**")
                                for iss in ISSUES:
                                    st.write(f"  {iss}: {nr.get(iss,'—')}")
                                st.write(f"  💬 {nr.get('quote','—')}")
                    with col2:
                        ref = r.get("reflection", {})
                        st.write(f"**Q1** {ref.get('q1','—')}")
                        st.write(f"**Q2** {ref.get('q2','—')}")
                        st.write(f"**Q3 전** {ref.get('q3_before','—')}")
                        st.write(f"**Q3 후** {ref.get('q3_after','—')}")
                        st.write(f"**Q4** {ref.get('q4_choice',[])} / {ref.get('q4_text','')}")
                        st.markdown(f"**한 문장** _{ref.get('closing','—')}_")
                    st.divider()
    st.stop()


# ════════════════════════════════════════════════════════
# LANDING
# ════════════════════════════════════════════════════════
if not st.session_state["in"]:
    st.title("🌍 기후변화 모의총회 — 토론 포트폴리오")
    st.markdown("> **총회를 마치고 오늘의 토론을 기록하고 성찰합니다.**")
    col1, col2, col3 = st.columns(3)
    with col1: st.info("📝 **토론 기록**\n\n다른 나라의 쟁점별 입장과 인상 깊은 발언을 기록합니다.")
    with col2: st.info("📊 **쟁점 비교**\n\n나라별 입장을 한눈에 비교해봅니다.")
    with col3: st.info("🌱 **수업 후 성찰**\n\n4가지 질문으로 오늘 배운 것을 정리합니다.")
    st.warning("👈 왼쪽에서 배정 국가와 이름을 입력하고 시작하세요.")
    st.stop()


# ════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════
grp = st.session_state["group"]
nm  = st.session_state["name"]
rec = st.session_state["rec"]

st.title(f"🌍 기후변화 모의총회 포트폴리오")
st.caption(f"배정 국가: **{grp}** 　 이름: **{nm}** 　 {datetime.now().strftime('%Y년 %m월 %d일')}")

st.markdown("""<div class='issue-banner'>
🔥 <strong>오늘 총회의 쟁점</strong> — 
기후 기금의 <strong>규모</strong>(얼마나),&nbsp;
<strong>지원 방식</strong>(공적 자금인가 민간 투자·대출도 되는가),&nbsp;
<strong>기금 부담 국가</strong>(역사적 배출국만인가, 현재 배출량 높은 나라도 포함인가)
</div>""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📝 토론 기록", "🌱 수업 후 성찰", "👥 모둠 기록 보기"])


# ────────────────────────────────────────────────────────
# TAB 1 : 토론 기록
# ────────────────────────────────────────────────────────
with tab1:
    st.markdown('<div class="section-title">다른 나라의 발언을 기록해요</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">발언한 나라를 선택하고, 쟁점별 입장과 인상 깊었던 말을 적어보세요.</div>', unsafe_allow_html=True)

    with st.form("form_records"):

        nation_data = {}
        other_countries = [c for c in COUNTRIES if c != grp]

        for i in range(3):
            nr = rec.get(f"nation{i+1}", {})
            st.markdown(f"<div class='nation-head'>나라 {i+1}</div>", unsafe_allow_html=True)
            with st.container():
                nation_opts = ["선택하세요"] + other_countries
                saved_nation = nr.get("name", "선택하세요")
                idx = nation_opts.index(saved_nation) if saved_nation in nation_opts else 0

                nation_name = st.selectbox(
                    f"나라 이름 {i+1}", options=nation_opts, index=idx,
                    key=f"nation_sel_{i}", label_visibility="collapsed"
                )

                c1, c2, c3 = st.columns(3)
                issue_vals = {}
                for j, (col, iss) in enumerate(zip([c1,c2,c3], ISSUES)):
                    with col:
                        issue_vals[iss] = st.text_area(
                            iss, value=nr.get(iss, ""), height=80,
                            key=f"iss_{i}_{j}",
                            placeholder=f"이 나라의 {iss} 입장은?"
                        )

                quote = st.text_input(
                    "💬 인상 깊었던 발언이나 제안",
                    value=nr.get("quote", ""),
                    key=f"quote_{i}",
                    placeholder="그 나라가 한 말 중 기억에 남는 것"
                )

                nation_data[f"nation{i+1}"] = {
                    "name": nation_name if nation_name != "선택하세요" else "",
                    **issue_vals,
                    "quote": quote
                }
            st.divider()

        # 쟁점 비교표
        st.markdown('<div class="section-title" style="margin-top:4px">📊 쟁점별 각국 입장 비교</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-desc">토론이 끝난 뒤, 위 기록을 참고해 채워봐요.</div>', unsafe_allow_html=True)

        cmp = rec.get("compare", {})
        # 헤더
        hcols = st.columns([1.2, 1, 1, 1])
        hcols[0].markdown("**쟁점**")
        n_names = [nation_data.get(f"nation{k+1}", {}).get("name","") or f"나라 {k+1}" for k in range(3)]
        for k, col in enumerate(hcols[1:]):
            col.markdown(f"**{n_names[k]}**")

        cmp_vals = {}
        for iss in ISSUES:
            row = st.columns([1.2, 1, 1, 1])
            row[0].markdown(f"<small>{iss}</small>", unsafe_allow_html=True)
            for k, col in enumerate(row[1:]):
                val = col.text_input(
                    "x", value=cmp.get(f"{iss}_{k}", ""),
                    key=f"cmp_{iss}_{k}", label_visibility="collapsed",
                    placeholder="한 줄 요약"
                )
                cmp_vals[f"{iss}_{k}"] = val

        saved1 = st.form_submit_button("💾 저장", type="primary", use_container_width=True)

    if saved1:
        rec.update({**nation_data, "compare": cmp_vals})
        st.session_state["rec"] = rec
        save_record(ukey(grp, nm), {
            "group": grp, "name": nm, "rec": rec,
            "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M")
        })
        st.success("저장되었습니다! ✅")


# ────────────────────────────────────────────────────────
# TAB 2 : 수업 후 성찰
# ────────────────────────────────────────────────────────
with tab2:
    st.markdown('<div class="section-title">토론을 마치고 나서</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">솔직하게, 내 생각을 자유롭게 적어봐요.</div>', unsafe_allow_html=True)

    ref = rec.get("reflection", {})

    with st.form("form_reflection"):

        # Q1
        st.markdown("""<div class='ref-card'><div class='ref-head'>
        <span class='ref-qnum'>1</span>
        <span class='ref-qtxt'>오늘 가장 설득력 있었던 나라는 어디인가요? 왜 그렇게 느꼈나요?</span>
        <div class='ref-hint'>단순히 발표를 잘했기 때문이 아니라, 그 나라의 <strong>어떤 근거나 입장</strong>이 마음을 움직였는지 생각해봐요.</div>
        </div></div>""", unsafe_allow_html=True)
        q1 = st.text_area("Q1 답변", value=ref.get("q1",""), height=100,
                          label_visibility="collapsed",
                          placeholder="나라 이름과 그 이유를 함께 써주세요.")

        st.markdown("<br>", unsafe_allow_html=True)

        # Q2
        st.markdown("""<div class='ref-card'><div class='ref-head'>
        <span class='ref-qnum'>2</span>
        <span class='ref-qtxt'>나라마다 기후 기금에 대한 입장이 다른 이유는 무엇이라고 생각하나요?</span>
        <div class='ref-hint'>역사, 경제 수준, 기후변화 피해 정도 중 어떤 요인이 가장 크게 작용한다고 느꼈나요?</div>
        </div></div>""", unsafe_allow_html=True)
        q2 = st.text_area("Q2 답변", value=ref.get("q2",""), height=100,
                          label_visibility="collapsed",
                          placeholder="가장 큰 요인이라고 생각하는 것과 그 이유를 써주세요.")

        st.markdown("<br>", unsafe_allow_html=True)

        # Q3
        st.markdown("""<div class='ref-card'><div class='ref-head'>
        <span class='ref-qnum'>3</span>
        <span class='ref-qtxt'>수업 전후로 기후변화 문제를 바라보는 내 시각이 어떻게 달라졌나요?</span>
        <div class='ref-hint'>바뀐 게 없어도 괜찮아요. 왜 바뀌지 않았는지도 중요한 생각이에요.</div>
        </div></div>""", unsafe_allow_html=True)
        col_b, col_a = st.columns(2)
        with col_b:
            st.markdown("**📌 수업 전 내 생각**")
            q3_before = st.text_area("Q3 전", value=ref.get("q3_before",""), height=110,
                                     label_visibility="collapsed",
                                     placeholder="이 수업을 시작하기 전 나는…")
        with col_a:
            st.markdown("**✨ 수업 후 내 생각**")
            q3_after = st.text_area("Q3 후", value=ref.get("q3_after",""), height=110,
                                    label_visibility="collapsed",
                                    placeholder="이 수업을 마치고 나서 나는…")

        st.markdown("<br>", unsafe_allow_html=True)

        # Q4
        st.markdown("""<div class='ref-card'><div class='ref-head'>
        <span class='ref-qnum'>4</span>
        <span class='ref-qtxt'>기후변화를 함께 해결하려면 무엇이 가장 필요하다고 생각하나요?</span>
        <div class='ref-hint'>돈, 기술, 신뢰, 공정한 규칙, 정치적 의지… 어떤 것이든 좋아요. 이유도 함께 적어봐요.</div>
        </div></div>""", unsafe_allow_html=True)

        saved_choices = ref.get("q4_choice", [])
        q4_choices = []
        cols_q4 = st.columns(3)
        for ci, ch in enumerate(Q4_CHOICES):
            with cols_q4[ci % 3]:
                if st.checkbox(ch, value=(ch in saved_choices), key=f"q4_{ci}"):
                    q4_choices.append(ch)
        q4_text = st.text_area("이유 또는 직접 작성", value=ref.get("q4_text",""), height=80,
                               placeholder="선택한 이유, 또는 다른 생각이 있다면 여기에…")

        st.markdown("<br>", unsafe_allow_html=True)

        # 한 문장 마무리
        st.markdown("#### ✏️ 오늘 토론을 한 문장으로 마무리한다면?")
        closing = st.text_input("한 문장 마무리", value=ref.get("closing",""),
                                label_visibility="collapsed",
                                placeholder="예) 기후변화는 과학 문제인 동시에 책임과 형평성의 문제이기도 하다.")

        saved2 = st.form_submit_button("💾 저장", type="primary", use_container_width=True)

    if saved2:
        rec["reflection"] = {
            "q1": q1, "q2": q2,
            "q3_before": q3_before, "q3_after": q3_after,
            "q4_choice": q4_choices, "q4_text": q4_text,
            "closing": closing
        }
        st.session_state["rec"] = rec
        save_record(ukey(grp, nm), {
            "group": grp, "name": nm, "rec": rec,
            "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M")
        })
        st.success("저장되었습니다! ✅")


# ────────────────────────────────────────────────────────
# TAB 3 : 모둠 기록 보기
# ────────────────────────────────────────────────────────
with tab3:
    st.markdown(f'<div class="section-title">👥 {grp} 모둠 기록</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">같은 모둠 친구들의 성찰을 함께 읽어봐요.</div>', unsafe_allow_html=True)

    grp_data = get_group(grp)

    if not grp_data:
        st.info("아직 제출된 기록이 없습니다. 첫 번째로 작성해보세요!")
    else:
        for key, entry in grp_data.items():
            r   = entry.get("rec", {})
            enm = entry.get("name", "")
            ref = r.get("reflection", {})

            with st.expander(
                f"👤 {enm}　　"
                f"{'✅ 기록 완료' if ref.get('closing') else '⏳ 작성 중'}",
                expanded=(enm == nm)
            ):
                col1, col2 = st.columns([1.1, 1])
                with col1:
                    st.markdown("**📝 기록한 나라**")
                    for i in range(3):
                        nr = r.get(f"nation{i+1}", {})
                        if nr.get("name"):
                            st.markdown(f"**{nr['name']}**")
                            for iss in ISSUES:
                                v = nr.get(iss,"")
                                if v: st.write(f"  {iss}: {v}")
                            if nr.get("quote"):
                                st.write(f"  💬 _{nr['quote']}_")
                with col2:
                    st.markdown("**🌱 수업 후 성찰**")
                    if ref.get("q1"):
                        st.markdown('<div class="ql">Q1 설득력 있는 나라</div>'
                                    f'<div class="qa">{ref["q1"]}</div>',
                                    unsafe_allow_html=True)
                    if ref.get("q2"):
                        st.markdown('<div class="ql">Q2 입장 차이 이유</div>'
                                    f'<div class="qa">{ref["q2"]}</div>',
                                    unsafe_allow_html=True)
                    if ref.get("q3_after"):
                        st.markdown('<div class="ql">Q3 수업 후 시각</div>'
                                    f'<div class="qa">{ref["q3_after"]}</div>',
                                    unsafe_allow_html=True)
                    if ref.get("closing"):
                        st.markdown(f'<div class="ql">한 문장 마무리</div>'
                                    f'<div class="qa" style="font-style:italic">'
                                    f'"{ref["closing"]}"</div>',
                                    unsafe_allow_html=True)

        st.caption(f"총 {len(grp_data)}명 기록")
