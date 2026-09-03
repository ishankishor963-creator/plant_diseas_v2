import time

import streamlit as st
from PIL import Image
from ddgs import DDGS
from deep_translator import GoogleTranslator

from diagnosis import run_diagnosis, SUPPORTED_CROPS
from recommendations import RECOMMENDATIONS
from theme import apply_theme, render_header, render_footer, gauge_color

st.set_page_config(page_title="Agro Edge", page_icon="🌱", layout="centered")
apply_theme()

LANGUAGES = {"English": "en", "हिंदी": "hi", "മലയാളം": "ml", "ಕನ್ನಡ": "kn", "தமிழ்": "ta"}

UI_STRINGS = {
    "en": {
        "hero_desc": "Upload a photo of a crop leaf to detect disease and get treatment advice.",
        "upload_label": "Upload a leaf image", "camera_label": "Take a photo",
        "upload_tab": "📁 Upload", "camera_tab": "📷 Camera", "uploaded_caption": "Uploaded image",
        "analyzing_eyebrow": "Analyzing Sample",
        "scan_line1": "Extracting visual features...", "scan_line2": "Cross-referencing crop-disease profiles...",
        "scan_line3": "Computing confidence score...", "diagnosis_eyebrow": "Diagnosis",
        "not_recognized_label": "⚠ Crop Not Recognized",
        "not_recognized_msg": "This doesn't look like any of the 14 supported crops ({crops}). Try a photo of one of these crops for a reliable result.",
        "unlabeled_class_msg": "This looks like a newer disease class that hasn't been named in the app yet (index {idx}). The model detected something with {conf:.1f}% confidence, but no description is available until this class is labeled.",
        "confidence_label": "Confidence",
        "confidence_note": "Confidence is moderate — a clearer, well-lit photo of a single leaf may improve accuracy.",
        "treatment_eyebrow": "Treatment Protocol", "what_means_header": "What This Means",
        "recommended_action_header": "Recommended Action", "web_searching": "Searching the web for more information...",
        "web_info_eyebrow": "More Info from the Web", "web_no_results": "No web results found — try again in a moment.",
    },
    "hi": {
        "hero_desc": "रोग की पहचान करने और उपचार सलाह पाने के लिए फसल की पत्ती की फोटो अपलोड करें।",
        "upload_label": "पत्ती की फोटो अपलोड करें", "camera_label": "फोटो लें",
        "upload_tab": "📁 अपलोड", "camera_tab": "📷 कैमरा", "uploaded_caption": "अपलोड की गई फोटो",
        "analyzing_eyebrow": "नमूने का विश्लेषण हो रहा है",
        "scan_line1": "दृश्य विशेषताएं निकाली जा रही हैं...", "scan_line2": "फसल-रोग प्रोफाइल से तुलना हो रही है...",
        "scan_line3": "विश्वास स्कोर की गणना हो रही है...", "diagnosis_eyebrow": "निदान",
        "not_recognized_label": "⚠ फसल पहचानी नहीं गई",
        "not_recognized_msg": "यह समर्थित 14 फसलों ({crops}) में से किसी जैसी नहीं दिखती। विश्वसनीय परिणाम के लिए इनमें से किसी एक फसल की फोटो आज़माएं।",
        "unlabeled_class_msg": "यह एक नई रोग श्रेणी लग रही है जिसे अभी ऐप में नाम नहीं दिया गया है (इंडेक्स {idx})। मॉडल ने {conf:.1f}% विश्वास के साथ कुछ पहचाना, लेकिन इस श्रेणी के लेबल होने तक कोई विवरण उपलब्ध नहीं है।",
        "confidence_label": "विश्वास स्तर",
        "confidence_note": "विश्वास स्तर मध्यम है — एक स्पष्ट, अच्छी रोशनी वाली एकल पत्ती की फोटो सटीकता बढ़ा सकती है।",
        "treatment_eyebrow": "उपचार प्रोटोकॉल", "what_means_header": "इसका क्या अर्थ है",
        "recommended_action_header": "अनुशंसित कार्रवाई", "web_searching": "अधिक जानकारी के लिए वेब खोजी जा रही है...",
        "web_info_eyebrow": "वेब से अधिक जानकारी", "web_no_results": "कोई वेब परिणाम नहीं मिला — कुछ देर बाद पुनः प्रयास करें।",
    },
    "ml": {
        "hero_desc": "രോഗം കണ്ടെത്താനും ചികിത്സാ നിർദ്ദേശം ലഭിക്കാനും വിളയുടെ ഇലയുടെ ഫോട്ടോ അപ്‌ലോഡ് ചെയ്യുക.",
        "upload_label": "ഇലയുടെ ഫോട്ടോ അപ്‌ലോഡ് ചെയ്യുക", "camera_label": "ഫോട്ടോ എടുക്കുക",
        "upload_tab": "📁 അപ്‌ലോഡ്", "camera_tab": "📷 ക്യാമറ", "uploaded_caption": "അപ്‌ലോഡ് ചെയ്ത ഫോട്ടോ",
        "analyzing_eyebrow": "സാമ്പിൾ വിശകലനം ചെയ്യുന്നു",
        "scan_line1": "ദൃശ്യ സവിശേഷതകൾ എടുക്കുന്നു...", "scan_line2": "വിള-രോഗ പ്രൊഫൈലുകളുമായി താരതമ്യം ചെയ്യുന്നു...",
        "scan_line3": "വിശ്വാസ്യതാ സ്കോർ കണക്കാക്കുന്നു...", "diagnosis_eyebrow": "രോഗനിർണയം",
        "not_recognized_label": "⚠ വിള തിരിച്ചറിഞ്ഞില്ല",
        "not_recognized_msg": "ഇത് പിന്തുണയ്ക്കുന്ന 14 വിളകളിൽ ({crops}) ഏതെങ്കിലുമായി പൊരുത്തപ്പെടുന്നില്ല. വിശ്വസനീയമായ ഫലത്തിനായി ഈ വിളകളിൽ ഒന്നിന്റെ ഫോട്ടോ ശ്രമിക്കുക.",
        "unlabeled_class_msg": "ഇത് ആപ്പിൽ ഇതുവരെ പേരിടാത്ത ഒരു പുതിയ രോഗ വിഭാഗമായി തോന്നുന്നു (ഇൻഡെക്സ് {idx}). മോഡൽ {conf:.1f}% വിശ്വാസ്യതയോടെ എന്തോ കണ്ടെത്തി, പക്ഷേ ഈ വിഭാഗം ലേബൽ ചെയ്യുന്നത് വരെ വിവരണം ലഭ്യമല്ല.",
        "confidence_label": "വിശ്വാസ്യത",
        "confidence_note": "വിശ്വാസ്യത മിതമായ നിലയിലാണ് — വ്യക്തവും നല്ല വെളിച്ചമുള്ളതുമായ ഒറ്റ ഇലയുടെ ഫോട്ടോ കൃത്യത മെച്ചപ്പെടുത്തിയേക്കാം.",
        "treatment_eyebrow": "ചികിത്സാ പ്രോട്ടോക്കോൾ", "what_means_header": "ഇതിന്റെ അർത്ഥം",
        "recommended_action_header": "ശുപാർശ ചെയ്യുന്ന നടപടി", "web_searching": "കൂടുതൽ വിവരങ്ങൾക്കായി വെബ് തിരയുന്നു...",
        "web_info_eyebrow": "വെബിൽ നിന്നുള്ള കൂടുതൽ വിവരങ്ങൾ", "web_no_results": "വെബ് ഫലങ്ങളൊന്നും കണ്ടെത്തിയില്ല — അൽപ്പസമയം കഴിഞ്ഞ് വീണ്ടും ശ്രമിക്കുക.",
    },
    "kn": {
        "hero_desc": "ರೋಗ ಪತ್ತೆ ಮಾಡಲು ಮತ್ತು ಚಿಕಿತ್ಸಾ ಸಲಹೆ ಪಡೆಯಲು ಬೆಳೆಯ ಎಲೆಯ ಫೋಟೋ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ.",
        "upload_label": "ಎಲೆಯ ಫೋಟೋ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ", "camera_label": "ಫೋಟೋ ತೆಗೆಯಿರಿ",
        "upload_tab": "📁 ಅಪ್‌ಲೋಡ್", "camera_tab": "📷 ಕ್ಯಾಮೆರಾ", "uploaded_caption": "ಅಪ್‌ಲೋಡ್ ಮಾಡಿದ ಫೋಟೋ",
        "analyzing_eyebrow": "ಮಾದರಿ ವಿಶ್ಲೇಷಣೆ ನಡೆಯುತ್ತಿದೆ",
        "scan_line1": "ದೃಶ್ಯ ಲಕ್ಷಣಗಳನ್ನು ಹೊರತೆಗೆಯಲಾಗುತ್ತಿದೆ...", "scan_line2": "ಬೆಳೆ-ರೋಗ ಪ್ರೊಫೈಲ್‌ಗಳೊಂದಿಗೆ ಹೋಲಿಸಲಾಗುತ್ತಿದೆ...",
        "scan_line3": "ವಿಶ್ವಾಸ ಅಂಕವನ್ನು ಲೆಕ್ಕಹಾಕಲಾಗುತ್ತಿದೆ...", "diagnosis_eyebrow": "ರೋಗ ನಿರ್ಣಯ",
        "not_recognized_label": "⚠ ಬೆಳೆ ಗುರುತಿಸಲಾಗಲಿಲ್ಲ",
        "not_recognized_msg": "ಇದು ಬೆಂಬಲಿತ 14 ಬೆಳೆಗಳಲ್ಲಿ ({crops}) ಯಾವುದನ್ನೂ ಹೋಲುತ್ತಿಲ್ಲ. ವಿಶ್ವಾಸಾರ್ಹ ಫಲಿತಾಂಶಕ್ಕಾಗಿ ಈ ಬೆಳೆಗಳಲ್ಲಿ ಒಂದರ ಫೋಟೋ ಪ್ರಯತ್ನಿಸಿ.",
        "unlabeled_class_msg": "ಇದು ಆ್ಯಪ್‌ನಲ್ಲಿ ಇನ್ನೂ ಹೆಸರಿಸದ ಹೊಸ ರೋಗ ವರ್ಗದಂತೆ ಕಾಣುತ್ತದೆ (ಇಂಡೆಕ್ಸ್ {idx}). ಮಾದರಿ {conf:.1f}% ವಿಶ್ವಾಸದೊಂದಿಗೆ ಏನನ್ನೋ ಪತ್ತೆ ಮಾಡಿದೆ, ಆದರೆ ಈ ವರ್ಗವನ್ನು ಲೇಬಲ್ ಮಾಡುವವರೆಗೆ ಯಾವುದೇ ವಿವರಣೆ ಲಭ್ಯವಿಲ್ಲ.",
        "confidence_label": "ವಿಶ್ವಾಸ ಮಟ್ಟ",
        "confidence_note": "ವಿಶ್ವಾಸ ಮಟ್ಟ ಮಧ್ಯಮವಾಗಿದೆ — ಸ್ಪಷ್ಟವಾದ, ಚೆನ್ನಾಗಿ ಬೆಳಗಿದ ಒಂದೇ ಎಲೆಯ ಫೋಟೋ ನಿಖರತೆಯನ್ನು ಸುಧಾರಿಸಬಹುದು.",
        "treatment_eyebrow": "ಚಿಕಿತ್ಸಾ ಪ್ರೋಟೋಕಾಲ್", "what_means_header": "ಇದರ ಅರ್ಥವೇನು",
        "recommended_action_header": "ಶಿಫಾರಸು ಮಾಡಿದ ಕ್ರಮ", "web_searching": "ಹೆಚ್ಚಿನ ಮಾಹಿತಿಗಾಗಿ ವೆಬ್ ಹುಡುಕಲಾಗುತ್ತಿದೆ...",
        "web_info_eyebrow": "ವೆಬ್‌ನಿಂದ ಹೆಚ್ಚಿನ ಮಾಹಿತಿ", "web_no_results": "ಯಾವುದೇ ವೆಬ್ ಫಲಿತಾಂಶಗಳು ಕಂಡುಬಂದಿಲ್ಲ — ಸ್ವಲ್ಪ ಸಮಯದ ನಂತರ ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ.",
    },
    "ta": {
        "hero_desc": "நோயைக் கண்டறிந்து சிகிச்சை ஆலோசனை பெற பயிர் இலையின் புகைப்படத்தை பதிவேற்றவும்.",
        "upload_label": "இலையின் புகைப்படத்தை பதிவேற்றவும்", "camera_label": "புகைப்படம் எடுக்கவும்",
        "upload_tab": "📁 பதிவேற்று", "camera_tab": "📷 கேமரா", "uploaded_caption": "பதிவேற்றப்பட்ட புகைப்படம்",
        "analyzing_eyebrow": "மாதிரி பகுப்பாய்வு செய்யப்படுகிறது",
        "scan_line1": "காட்சி அம்சங்கள் பிரித்தெடுக்கப்படுகின்றன...", "scan_line2": "பயிர்-நோய் விவரக்குறிப்புகளுடன் ஒப்பிடப்படுகிறது...",
        "scan_line3": "நம்பகத்தன்மை மதிப்பெண் கணக்கிடப்படுகிறது...", "diagnosis_eyebrow": "நோய் கண்டறிதல்",
        "not_recognized_label": "⚠ பயிர் அடையாளம் காணப்படவில்லை",
        "not_recognized_msg": "இது ஆதரிக்கப்படும் 14 பயிர்களில் ({crops}) எதையும் ஒத்திருக்கவில்லை. நம்பகமான முடிவுக்கு இந்த பயிர்களில் ஒன்றின் புகைப்படத்தை முயற்சிக்கவும்.",
        "unlabeled_class_msg": "இது ஆப்பில் இன்னும் பெயரிடப்படாத ஒரு புதிய நோய் வகையாகத் தெரிகிறது (இன்டெக்ஸ் {idx}). மாடல் {conf:.1f}% நம்பகத்தன்மையுடன் ஏதோ கண்டறிந்தது, ஆனால் இந்த வகை லேபிள் செய்யப்படும் வரை விவரம் இல்லை.",
        "confidence_label": "நம்பகத்தன்மை",
        "confidence_note": "நம்பகத்தன்மை மிதமான அளவில் உள்ளது — தெளிவான, நல்ல வெளிச்சமுள்ள ஒரு இலையின் புகைப்படம் துல்லியத்தை மேம்படுத்தலாம்.",
        "treatment_eyebrow": "சிகிச்சை நெறிமுறை", "what_means_header": "இதன் பொருள் என்ன",
        "recommended_action_header": "பரிந்துரைக்கப்படும் நடவடிக்கை", "web_searching": "மேலும் தகவலுக்காக இணையத்தில் தேடுகிறது...",
        "web_info_eyebrow": "இணையத்திலிருந்து கூடுதல் தகவல்", "web_no_results": "இணைய முடிவுகள் எதுவும் கிடைக்கவில்லை — சிறிது நேரம் கழித்து மீண்டும் முயற்சிக்கவும்.",
    },
}


@st.cache_data(show_spinner=False)
def translate_text(text, lang_code):
    if lang_code == "en" or not text:
        return text
    try:
        return GoogleTranslator(source="en", target=lang_code).translate(text)
    except Exception:
        return text


@st.cache_data(show_spinner=False, ttl=3600)
def search_disease_info(query, max_results=3):
    TRUSTED_PLANT_DOMAINS = [
        "extension.org", "apsnet.org", "plantvillage.psu.edu", "ipm.ucanr.edu",
        "rhs.org.uk", "gardeningknowhow.com", "planetnatural.com", "growveg.com",
        "cabi.org", "fao.org", "agriculture.com", "britannica.com", "wikipedia.org",
        "agrilinks.org", "agric.wa.gov.au", "almanac.com", "gardenia.net",
        "missouribotanicalgarden.org", "epicgardening.com", ".edu", ".gov", ".ac.in", ".edu.in",
    ]
    try:
        with DDGS() as ddgs:
            raw_results = list(ddgs.text(query, max_results=max_results * 5))
        trusted = [r for r in raw_results if any(d in r.get("href", "").lower() for d in TRUSTED_PLANT_DOMAINS)]
        return trusted[:max_results] if trusted else raw_results[:max_results]
    except Exception:
        return []


def render_diagnosis_result(result, lang, T):
    if not result["is_named"]:
        st.markdown(f"""
        <div class="glass-card">
            <div class="label-mono"><span class="material-symbols-outlined">warning</span>{T['diagnosis_eyebrow']}</div>
            <div class="unrecognized">{T['unlabeled_class_msg'].format(idx=result['index'], conf=result['confidence'])}</div>
        </div>
        """, unsafe_allow_html=True)
        return

    display_name_t = translate_text(result["display_name"], lang)

    if result["confidence"] < 70:
        st.markdown(f"""
        <div class="glass-card">
            <div class="label-mono"><span class="material-symbols-outlined">warning</span>{T['diagnosis_eyebrow']}</div>
            <div class="unrecognized">
                <div class="unrecognized-label">{T['not_recognized_label']}</div>
                {T['not_recognized_msg'].format(crops=SUPPORTED_CROPS)}
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    color = gauge_color(result["confidence"])
    confidence_note = "" if result["confidence"] >= 85 else f'<p class="hero-desc-text" style="margin-top:0.8rem;">{T["confidence_note"]}</p>'
    st.markdown(f"""
    <div class="glass-card">
        <div class="label-mono"><span class="material-symbols-outlined">biotech</span>{T['diagnosis_eyebrow']}</div>
        <div class="result-title">{display_name_t}</div>
        <div class="label-mono" style="justify-content:space-between; margin-bottom:0.4rem;">
            <span>{T['confidence_label']}</span><span class="data-viz">{result['confidence']:.1f}%</span>
        </div>
        <div class="progress-track"><div class="progress-fill" style="width:{result['confidence']:.1f}%; background:{color};"></div></div>
        {confidence_note}
    </div>
    """, unsafe_allow_html=True)

    info = RECOMMENDATIONS.get(result["class_key"])
    if info:
        description_t = translate_text(info["description"], lang)
        treatment_t = translate_text(info["treatment"], lang)
        st.markdown(f"""
        <div class="glass-card">
            <div class="label-mono"><span class="material-symbols-outlined">medical_information</span>{T['treatment_eyebrow']}</div>
            <div class="rec-grid">
                <div class="rec-tile"><h4>{T['what_means_header']}</h4><p>{description_t}</p></div>
                <div class="rec-tile treatment"><h4>{T['recommended_action_header']}</h4><p>{treatment_t}</p></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with st.spinner(T["web_searching"]):
        search_query = f"{result['display_name']} plant disease symptoms causes treatment agriculture botany -software -app -company"
        web_results = search_disease_info(search_query)
    if web_results:
        st.markdown(f'<div class="glass-card"><div class="label-mono"><span class="material-symbols-outlined">travel_explore</span>{T["web_info_eyebrow"]}</div>', unsafe_allow_html=True)
        for r in web_results:
            title_t = translate_text(r.get("title", ""), lang)
            body_t = translate_text(r.get("body", "")[:200], lang)
            st.markdown(f"""
            <div style="margin-bottom:0.9rem; padding-bottom:0.9rem; border-bottom:1px solid var(--border);">
                <a href="{r.get('href','')}" target="_blank" class="web-link-title">{title_t}</a>
                <p class="web-link-body">{body_t}...</p>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.warning(T["web_no_results"])


# ---------------------------------------------------------------------------
# Page
# ---------------------------------------------------------------------------
lang_col, _ = st.columns([1, 2.5])
with lang_col:
    selected_lang_name = st.selectbox("Language", list(LANGUAGES.keys()), label_visibility="collapsed")
lang = LANGUAGES[selected_lang_name]
T = UI_STRINGS[lang]

render_header("Agro Edge", "eco", "AI Plant Diagnosis")
st.markdown(f'<div class="glass-card"><p class="hero-desc-text">{T["hero_desc"]}</p></div>', unsafe_allow_html=True)

upload_tab, camera_tab = st.tabs([T["upload_tab"], T["camera_tab"]])
uploaded_file = None
with upload_tab:
    uploaded_file = st.file_uploader(T["upload_label"], type=["jpg", "jpeg", "png"], label_visibility="collapsed")
with camera_tab:
    camera_file = st.camera_input(T["camera_label"], label_visibility="collapsed")
    if camera_file is not None:
        uploaded_file = camera_file

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption=T["uploaded_caption"], use_container_width=True)

    scan_placeholder = st.empty()
    scan_placeholder.markdown(f"""
    <div class="glass-card">
        <div class="label-mono"><span class="material-symbols-outlined">search</span>{T['analyzing_eyebrow']}</div>
        <div class="scan-track"><div class="scan-bar"></div></div>
        <div class="scan-line">&gt; <span>{T['scan_line1']}</span></div>
        <div class="scan-line">&gt; <span>{T['scan_line2']}</span></div>
        <div class="scan-line">&gt; <span>{T['scan_line3']}</span></div>
    </div>
    """, unsafe_allow_html=True)

    result = run_diagnosis(image)
    time.sleep(0.4)
    scan_placeholder.empty()
    render_diagnosis_result(result, lang, T)

render_footer()
