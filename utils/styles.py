def load_css():
    return """
    <style>

    /* =========================
       BASE THEME
    ========================= */
    .stApp {
        background-color: #0b0f14;
    }

    /* =========================
       CHAT MESSAGE CONTAINERS
       (Subtle, invisible-quality)
    ========================= */
    div[data-testid="stChatMessage"] {
        border: 1px solid rgba(255,255,255,0.05);
        border-radius: 14px;
        padding: 14px 16px;
        margin-bottom: 14px;
        background-color: rgba(255,255,255,0.02);
    }

    /* User slightly elevated */
    div[data-testid="stChatMessage"][data-author="user"] {
        background-color: rgba(255,255,255,0.035);
    }

    /* Assistant flatter */
    div[data-testid="stChatMessage"][data-author="assistant"] {
        background-color: rgba(255,255,255,0.02);
    }

    /* =========================
       TEXT READABILITY
    ========================= */
    div[data-testid="stMarkdownContainer"] {
        line-height: 1.6;
        font-size: 0.95rem;
    }

    /* =========================
       HEADINGS (Fix icon alignment)
    ========================= */
    h2, h3 {
        display: flex;
        align-items: center;
        gap: 8px;
        line-height: 1.3;
        margin-top: 10px;
        margin-bottom: 6px;
    }

    /* =========================
       CODE BLOCKS (Better contrast)
    ========================= */
    pre, code {
        background-color: rgba(255,255,255,0.04) !important;
        border-radius: 8px !important;
        padding: 10px !important;
        border: 1px solid rgba(255,255,255,0.06);
    }

    /* Inline code */
    code {
        padding: 2px 6px !important;
        font-size: 0.9rem;
    }

    /* =========================
       INPUT BOX (Vertical centering)
    ========================= */
    textarea {
        padding-top: 10px !important;
        padding-bottom: 10px !important;
        line-height: 1.4 !important;
    }

    /* =========================
       SMALL POLISH
    ========================= */
    hr {
        border-color: rgba(255,255,255,0.06);
    }

    </style>
    """
