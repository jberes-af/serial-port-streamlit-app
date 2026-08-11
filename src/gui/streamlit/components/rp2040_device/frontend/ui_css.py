# src/gui/streamlit/components/rp2040_device/frontend/ui_css.py

CSS = """
.rp2040-device {
    width: 100%;
    font-family: var(--st-font);
}

.field {
    margin-bottom: 1rem;
}

.button-row {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 1.5rem;
}


/*
 * Streamlit-style primary button
 */

.st-primary-button {
    min-height: 2.5rem;

    padding:
        0.25rem
        0.75rem;

    border:
        1px solid
        var(--st-primary-color);

    border-radius:
        0.5rem;

    background-color:
        var(--st-primary-color);

    color:
        white;

    font-family:
        var(--st-font);

    font-size:
        1rem;

    font-weight:
        400;

    line-height:
        1.6;

    cursor:
        pointer;

    transition:
        border-color 0.15s,
        background-color 0.15s,
        color 0.15s;
}


/*
 * Hover
 */

.st-primary-button:hover:not(:disabled) {
    filter: brightness(0.9);
}


/*
 * Active / pressed
 */

.st-primary-button:active:not(:disabled) {
    filter: brightness(0.8);
}


/*
 * Disabled
 */

.st-primary-button:disabled {
    cursor:
        not-allowed;

    opacity:
        0.35;
}


#device-status {
    margin-top: 0.35rem;
    font-size: 0.9rem;
}
"""
