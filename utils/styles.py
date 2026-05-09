def load_css():
    return """
    <style>

    /* ================= ANSWER BOX ================= */
    .answer-box {
        background: rgba(17, 24, 39, 0.75);
        border-radius: 12px;
        padding: 16px;
        border: 1px solid rgba(255,255,255,0.05);
        line-height: 1.55;
    }

    .answer-box:hover {
        border-color: rgba(255,255,255,0.12);
        box-shadow: 0 6px 20px rgba(0,0,0,0.25);
    }

    .answer-box h3 {
        font-size: 18px;
        margin-bottom: 8px;
    }

    .answer-box p,
    .answer-box li {
        font-size: 14.5px;
    }

    /* ================= INLINE CODE ================= */
    .answer-box code {
        background: rgba(31, 41, 55, 0.9);
        border: 1px solid rgba(255,255,255,0.06);
        padding: 4px 6px;
        border-radius: 6px;
        font-size: 0.9em;
    }

    /* ================= CODE BLOCK ================= */
    pre {
        background: #0f172a !important;
        border-radius: 10px;
        padding: 12px;
        overflow-x: auto;
    }

    /* ================= CHAT INPUT ================= */
    [data-testid="stChatInput"] > div {
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 12px !important;
        box-shadow: none !important;
    }

    [data-testid="stChatInput"] > div:focus-within {
        border: 1px solid #3b82f6 !important;
        box-shadow: 0 0 0 1px #3b82f6 !important;
    }

    /* ================= CUSTOM METRICS ================= */
    .metric-box {
        padding: 6px 0;
    }

    [data-testid="stMetricLabel"] {
        font-size: 16px !important;
        font-weight: 700 !important;
    }

    [data-testid="stMetricValue"] {
        font-size: 16px !important;
        font-weight: 500 !important;
        margin-top: 2px !important;
    } 

    /* ================= SIDEBAR SPACING ================= */
    section[data-testid="stSidebar"] .stButton {
        margin-bottom: 8px;
    }

    /* ================= CAPTION ================= */
    .stCaption {
        margin-top: 8px;
        opacity: 0.75;
        font-size: 0.85rem;
    }

    /* ================= BUTTON HOVER ================= */
    button:hover {
        transform: scale(1.01);
        transition: 0.1s ease;
    }

    </style>
    """
