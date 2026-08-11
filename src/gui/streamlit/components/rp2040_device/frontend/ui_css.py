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
 * Buttons
 */

.st-primary-button,
.st-secondary-button {
    min-height: 2.5rem;
    padding: 0.25rem 0.75rem;

    border-radius: 0.5rem;

    font-family: var(--st-font);
    font-size: 1rem;
    font-weight: 400;
    line-height: 1.6;

    cursor: pointer;
}


/*
 * Primary button
 */

.st-primary-button {
    background-color: var(--st-primary-color);
    color: white;

    border:
        1px solid
        var(--st-primary-color);
}

.st-primary-button:hover:not(:disabled) {
    filter: brightness(0.9);
}

.st-primary-button:active:not(:disabled) {
    filter: brightness(0.8);
}


/*
 * Secondary button
 */

.st-secondary-button {
    background-color: transparent;
    color: var(--st-text-color);

    border:
        1px solid
        rgba(49, 51, 63, 0.25);
}

.st-secondary-button:hover:not(:disabled) {
    border-color: var(--st-primary-color);
    color: var(--st-primary-color);
}


/*
 * Disabled buttons
 */

.st-primary-button:disabled,
.st-secondary-button:disabled {
    cursor: not-allowed;
    opacity: 0.35;
}


/*
 * Device status
 */

#device-status {
    margin-top: 0.35rem;
    font-size: 0.9rem;
}
"""
